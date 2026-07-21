# Lieferando Menu Scraping — Price/Item Extraction

Extracting menu items (name + price) from Lieferando restaurant pages for price
comparison across all restaurants delivering to an address.

## Flow Overview

1. Navigate to delivery area: `https://www.lieferando.de/en/delivery/food/<postcode>`
2. Scroll through restaurant list (lazy-loaded) to load all cards
3. Extract restaurant slugs from `a[href*="/menu/"]` links
4. For each restaurant: navigate to `https://www.lieferando.de/en/menu/<slug>`
5. Scroll through entire menu page to lazy-load all items
6. Extract items via TreeWalker JS (see below)
7. Parse + clean + filter + sort in Python

## Restaurant List Extraction

```javascript
// After scrolling through the full list page:
const links = document.querySelectorAll('a[href*="/menu/"]');
const seen = new Set();
const restaurants = [];
for (const link of links) {
  const href = link.getAttribute('href');
  const name = link.textContent?.trim();
  if (!href || !name || name.length < 2) continue;
  const slug = href.split('/menu/')[1]?.split('?')[0];
  if (seen.has(slug)) continue;
  seen.add(slug);
  // Walk up to card container for metadata
  let card = link;
  for (let i = 0; i < 6; i++) {
    card = card.parentElement;
    if (!card) break;
    if (card.textContent?.length > 50) break;
  }
  const ct = card ? card.textContent?.trim() : '';
  // Parse: stars, time, delivery cost, min order, tags
  restaurants.push({ name, slug, cardText: ct.slice(0, 400) });
}
```

Lazy-load: scroll 8x `scroll 0 5000` with 1.5s delays until restaurant count
stabilizes (Lieferando shows "N places" in body text — match against count).

## Menu Item Extraction (TreeWalker Pattern)

Lieferando menu items are in a virtualized SPA list. Items lazy-load on scroll.
Each item card contains a text node "Item Info" — this is the stable anchor.

### Step 1: Scroll through entire menu

```bash
# Must scroll to lazy-load ALL items before extraction
for _ in range(6):
    camoufox scroll 0 2000   # 0.5s between scrolls
camoufox scroll 0 -99999      # back to top
```

### Step 2: TreeWalker extraction JS

```javascript
(function() {
  var results = [];
  var seen = {};
  var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  var itemInfos = [];
  var node;
  while (node = walker.nextNode()) {
    if (node.textContent && node.textContent.trim() === 'Item Info') {
      itemInfos.push(node.parentElement);
    }
  }
  itemInfos.forEach(function(container) {
    var card = container;
    for (var i = 0; i < 5; i++) {
      card = card.parentElement;
      if (!card) break;
      var text = card.textContent;
      if (text && text.length > 30 && text.length < 500) {
        var priceMatch = text.match(/(\d+[,.]\d+)\s*€/);
        var lines = text.split(/\n/).map(function(l) { return l.trim(); })
          .filter(function(l) {
            return l && l !== 'Item Info' &&
              !l.match(/^\d+[,.]\d+\s*€?$/) && l.length > 3;
          });
        var name = lines[0] || '';
        // Remove doubled category prefixes (e.g. "Bread - Classic in BreadBread...")
        name = name.replace(/^(.+?)\1+/, '$1');
        var price = priceMatch ? priceMatch[1].replace('.', ',') + '€' : '';
        var key = name + '|' + price;
        if (name.length > 3 && price && !seen[key]) {
          seen[key] = true;
          results.push({ name: name.slice(0, 80), price: price });
        }
        break;
      }
    }
  });
  return JSON.stringify(results);
})()
```

### Why TreeWalker, not querySelectorAll

- `document.querySelectorAll('[class*=price]')` only finds 5 items (Highlights
  section) — other category items are in virtualized/lazy containers not yet
  in DOM
- After scrolling, TreeWalker finds ALL "Item Info" text nodes (50-80 per
  restaurant) because it walks the full text node tree
- Category chips (`pie-chip` elements) do NOT expand items on click — scrolling
  is the only way to load them

## Name Cleaning

Raw extracted names contain doubled category prefixes:
`"Bread - Classic in BreadBread - Classic in BreadChicken Bread"`

Clean in Python:
```python
def clean_name(name):
    # Remove doubled prefixes
    for length in range(60, 4, -1):
        half = name[:length]
        if name.startswith(half + half):
            name = name[length:]
            break
    name = re.sub(r'Item Info.*$', '', name)
    name = re.sub(r'\d+[,.]\d+\s*€.*$', '', name)
    name = re.sub(r'^from\s+', '', name)
    return name.strip()[:80]
```

## Main Dish Filtering

Filter out toppings, extras, sides, drinks, desserts. Main dishes contain
keywords: bowl, burger, pizza, curry, döner, sushi, ramen, wrap, falafel,
tofu, schnitzel, tikka, masala, paneer, pasta, pide, etc.

Price threshold: skip items under 3.50€ (likely toppings/extras).

## Camoufox eval JSON Parsing (CRITICAL)

`camoufox eval` returns double-encoded JSON when the JS returns
`JSON.stringify(...)`:

```
{"result": "[{\"name\":\"...\",\"price\":\"...\"}]"}
```

The `result` field is a **string** containing JSON, not a parsed array.

**Correct parsing in Python:**
```python
obj = json.loads(raw)          # parse outer object
result_str = obj["result"]     # get inner string
items = json.loads(result_str) # parse inner JSON array
```

**Wrong** (returns string, not list — causes `TypeError: string indices`):
```python
obj = json.loads(raw)
items = obj["result"]  # this is a STRING, not a list
```

When calling `camoufox eval` from `subprocess.run`, pass the JS as a single
argument. Read JS from a file to avoid shell escaping issues with quotes,
backslashes, and unicode (€, \u20ac).

## Batch Scraping Pattern

For scraping 30+ restaurants, use a background script (`notify_on_complete=True`)
that:
1. Reads extraction JS from a file
2. Loops through restaurant slugs
3. For each: `goto` → sleep 3s → scroll 6x → scroll to top → `eval`
4. Parses result with double-decode pattern
5. Cleans names
6. Saves to JSON

Each restaurant takes ~10-15 seconds. 35 restaurants = ~7 minutes.
Foreground `execute_code` times out at 5 min — use background `terminal`.

## Jonathan's Food Budget Rules

When recommending meals, apply these max prices:
- Falafel in bread/wrap: ≤ 9€
- Burger: ≤ 9€
- Döner/Kebab: ≤ 9€
- Curry: ≤ 12€ (less preferred)
- Pizza: ≤ 12€ (less preferred)
- Sushi: ≤ 15€
- Bowls/noodles/Asian: ≤ 12€

Dietary: vegan, Asian, veg ramen preferred. No beans, no sweets.
Protein snacks OK.
