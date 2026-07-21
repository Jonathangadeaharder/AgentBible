# Amazon SPA `a-declarative` Framework Limitation

## Problem

Amazon's return form (`/spr/returns/cart`) uses the `a-declarative` JavaScript framework for custom dropdowns. The `<select>` element has `data-action="a-dropdown-select"` and is wrapped in a `.a-declarative` container.

When you use Playwright's `selectOption()` or JS `dispatchEvent(new Event('change'))`, the `<select>` value is set correctly, but Amazon's SPA framework does NOT react — the "Weiter" (Next) button is never rendered.

## What Doesn't Work

| Method | Result |
|--------|--------|
| `element.dispatchEvent(new Event('change'))` | `select.value` set, but no Weiter button |
| `element.dispatchEvent(new Event('a:dropdown:selected'))` | No effect |
| `element.dispatchEvent(new Event('a:change'))` | No effect |
| Playwright `selectOption('RO_AMZ-PG-BAD-DESC')` via REST API | `select.value` set, but no Weiter button |
| Playwright `selectOption()` via standalone `camoufox-js` script | `select.value` set, but no Weiter button |
| Native value setter (`Object.getOwnPropertyDescriptor`) | No effect |
| `form.submit()` / `HTMLFormElement.prototype.submit.call(form)` | 404 — missing hidden CSRF/session inputs |
| `form.requestSubmit()` | Redirects to `/spr/returns/resolutions` but 404 — missing hidden inputs |
| JS `element.click()` on Weiter button | `isTrusted=false`, SPA ignores it |
| Playwright `click({force:true})` on Weiter button | "Element is not visible (no bounding box)" |

## Root Cause

Amazon's `a-declarative` framework registers event listeners that require **trusted events** (user-initiated). Programmatic events (`isTrusted=false`) are silently ignored. The SPA's "Weiter" button is only rendered after the framework processes a genuine dropdown selection event.

Additionally, the "Weiter" button in Amazon's `a-button` widget has no bounding box (hidden by Amazon CSS) — making Playwright `click()` fail even with `force:true`.

## Standalone Script Template

When the REST API can't trigger the SPA, use a standalone `camoufox-js` script:

```javascript
// Save as ~/projects/camofox-browser/amazon_return.cjs
// Run: cd ~/projects/camofox-browser && eval "$(fnm env)" && fnm use 22 && node amazon_return.cjs
const { Camoufox } = require('camoufox-js');
const fs = require('fs');

(async () => {
  const browser = await Camoufox({ headless: true, humanize: true });
  const page = await browser.newPage();

  // Load cookies
  const cookieData = JSON.parse(fs.readFileSync('/tmp/amazon_fresh.json', 'utf8'));
  await page.context().addCookies(cookieData.cookies);

  // Navigate to return page
  await page.goto('https://www.amazon.de/spr/returns/cart?itemId=<ITEM_ID>&orderId=<ORDER_ID>');
  await page.waitForTimeout(3000);
  console.log('URL:', page.url());

  // Click checkbox
  await page.locator('#<ITEM_ID>-orc-item-selection-checkbox').click();
  await page.waitForTimeout(2000);

  // Use native selectOption with specific ID
  const selectId = '#<ITEM_ID>-questionnaire-widget-native-dropdown';
  await page.locator(selectId).selectOption('RO_AMZ-PG-BAD-DESC');
  await page.waitForTimeout(2000);

  // Fill comment
  const textareaId = '#<ITEM_ID>-RO_AMZ-PG-BAD-DESC-AC_REQUIRED_WHAT_IS_WRONG_WITH_WEBSITE';
  await page.locator(textareaId).fill('Stecker passt nicht');
  await page.waitForTimeout(2000);

  // Check for Weiter button (excluding Rufus)
  const weiter = page.locator('button:has-text("Weiter")')
    .filter({ hasNot: page.locator('#zumaRufusContinueToSite-announce') });
  const count = await weiter.count();
  console.log('Weiter buttons (non-Rufus):', count);

  if (count > 0) {
    await weiter.first().click({ force: true });
    await page.waitForTimeout(5000);
    console.log('After Weiter URL:', page.url());
  } else {
    console.log('No Weiter button — SPA did not render it');
    // Try form submit as fallback
    await page.evaluate(() => {
      const form = document.getElementById('items-section-form-v2');
      if (form) HTMLFormElement.prototype.submit.call(form);
    });
    await page.waitForTimeout(5000);
    console.log('After submit URL:', page.url());
  }

  await browser.close();
})().catch(e => console.error('Error:', e.message));
```

## Future Fix: REST API `selectOption` Endpoint

The camoufox-browser REST server (`~/projects/camofox-browser/server.js`) needs a new endpoint:

```
POST /tabs/:tabId/selectOption
{"userId": "...", "selector": "select#mySelect", "value": "optionValue"}
```

This would call `page.locator(selector).selectOption(value)` natively, which triggers the browser's native `change` event (trusted). However, even this may not solve the Amazon SPA problem since `selectOption` was already tested via standalone script and the Weiter button still didn't render.

The real fix may require clicking the **custom dropdown widget** (the `a-button` that opens the dropdown list) rather than the native `<select>`, then clicking the option from the dropdown list — simulating a real user interaction.

## Debugging Commands

```bash
# Check select value
camoufox loop --inline 'eval (function(){var s=document.querySelector("select[aria-label*=Warum]");return s?("value:"+s.value):"none"})()'

# Check if Weiter button exists (excluding Rufus)
camoufox loop --inline 'eval (function(){var all=document.querySelectorAll("a,button,input");for(var i=0;i<all.length;i++){var t=(all[i].textContent||all[i].value||"").trim();if(t.indexOf("Weiter")>=0){var p=all[i];var inRufus=false;while(p){if(p.className&&p.className.indexOf("rufus")>=0){inRufus=true;break}p=p.parentElement}if(!inRufus){return"found:"+all[i].disabled}}}return"none"})()'

# Check all form fields
camoufox loop --inline 'eval (function(){var form=document.getElementById("items-section-form-v2");if(!form)return"no form";var inputs=form.querySelectorAll("input,select,textarea");var data={};for(var i=0;i<inputs.length;i++){if(inputs[i].name)data[inputs[i].name]=inputs[i].value.substring(0,30)}return JSON.stringify(data)})()'
```
