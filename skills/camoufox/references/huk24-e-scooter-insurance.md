# HUK24 E-Scooter Insurance — Form Flow & Selectors

Session-tested 2026-07-12. HUK24 tarifrechner is a 5-step SPA at
`mofa.tarifrechner.c.huk24.de` using custom web components (SYNACT framework).

## Vehicle Data

- **Model**: Xiaomi Electric Scooter 4 Lite (2nd Gen), BHR8050DE
- **FIN**: <FIN>
- **ABE**: P4930
- **Owner**: <FULL_NAME>, <ADDRESS>, <PLZ> <CITY>
- **Phone**: <PHONE>
- **Email**: <EMAIL>
- **HUK24 Account Password**: Scooter2026Huk

## Direct Entry URL

```
https://mofa.tarifrechner.c.huk24.de/tarifrechner/mofa?fahrzeug=escooter&herkunft=top&preselect=true&isVariantEScooter=true&fahrzeugtyp=ESCOOTER
```

## Form Steps & Selectors

### Step 1: Fahrzeugdaten
- **Versicherungsbeginn**: `input[name="versicherungsbeginn"]` — pre-filled with current month (07.2026)
- **Alle Fahrer ≥23?**: `s-choice-list-item[role="radio"]` — click index [0] for "Ja"
- **Weiter button**: `button.s-button__button` with text "Weiter"
- ⚠️ Radio is a custom `<s-choice-list-item>` web component. `click_element` works in Camoufox. Hermes browser tools (`browser_click`) do NOT register on this component — requires JS `.click()` via `eval`.

### Step 2: Angebot
- Two columns: Kfz-Haftpflicht (20,00€) vs Teilkasko inkl. Haftpflicht (40,50€)
- Click `button:has-text("wählen")` to select Kfz-Haftpflicht
- ⚠️ A "weitere Details" dialog can open and intercept the Weiter button. Press `Escape` before clicking Weiter.
- **Weiter**: `button.s-button__button:has-text("Weiter")` — NOT the "weitere Details" link button

### Step 3: Antragsdetails
- **ABE vorhanden?**: `s-choice-list-item[role="radio"]` index [0] = "Ja"
- **Hersteller**: `input[role="combobox"]` (S-COMBOBOX component) — click, type "Xiaomi", wait 1s, click `[role="option"]:has-text("XIAOMI")`
- **FIN**: `input[name="fahrgestellnummer"]` — use `fill_element`
- **Öffentlicher Dienst?**: `s-choice-list-item[role="radio"]` index [3] = "Nein"
  - ⚠️ `click_element` with `nth-of-type(4)` fails. Use `eval` JS: `document.querySelectorAll('s-choice-list-item[role="radio"]')[3].click()`
- **Weiter**: `button[type="submit"]:has-text("Weiter")` with `force=true` (aria-disabled toggles after all fields valid)

### Step 4: Login/Registrierung (Friendly Captcha)
- **E-Mail**: `input[type="email"]` — use `type` (not `fill_element`) for React event triggering
- **Captcha**: Friendly Captcha (frcapi.com), sitekey `FCMO4GHVOH1A`
  - **Camoufox headed mode auto-solves** the PoW in ~10-15s. No Capsolver needed.
  - No user interaction required — the iframe spinner runs and completes automatically.
  - **HEADLESS MODE FAILS**: Registration API returns "Es ist ein technisches Problem aufgetreten" consistently in headless. Must use headed mode (`camoufox start` without `--headless`).
- **Flow**: Type email → click "Weiter" (NOT "Benutzerkonto suchen" — that leads to wrong path) → "Kein Benutzerkonto gefunden" → click "Jetzt registrieren"
  - ⚠️ "Jetzt registrieren" button is inside `<auth-root>` which intercepts native clicks. Must use `eval` JS `.click()`.
- **Registration**: Password field (`input[type="text"]` with `placeholder="Passwort eingeben"`)
  - Password requirements: ≥8 chars, 1 number/special char, upper+lower case
- **After password**: Phone number page → type phone → "Bestätigungscode anfordern" → SMS code received
- **SMS verification**: Enter 6-digit code from SMS → verify → registration complete

### Step 5: Persönliche Daten + Übersicht
- Name, address pre-filled from registration
- Review and submit
- Plakette arrives per Post in ~5 workdays

## Key Commands (Camoufox Headed Mode)

```bash
# Start Camoufox in HEADED mode (REQUIRED for Friendly Captcha)
camoufox start  # NO --headless flag

# Accept cookies first
camoufox eval "var b=document.querySelectorAll('button');for(var i=0;i<b.length;i++)if(b[i].textContent.includes('Zustimmen')){b[i].click();break;}"

# Select radio via JS (custom web components)
camoufox eval "document.querySelectorAll('s-choice-list-item[role=\"radio\"]')[0].click()"

# Click Weiter via JS (when auth-root or dialog intercepts native clicks)
camoufox eval "var b=document.querySelectorAll('button');for(var i=0;i<b.length;i++)if(b[i].textContent.trim()==='Weiter'&&!b[i].disabled)b[i].click();"

# Type in combobox
camoufox click_element 'input[role="combobox"]'
camoufox type "Xiaomi"
camoufox click_element '[role="option"]:has-text("XIAOMI")'

# Fill FIN
camoufox fill_element 'input[name="fahrgestellnummer"]' "<FIN>"

# Wait for captcha auto-solve
sleep 12

# Click "Jetzt registrieren" via JS (auth-root intercepts native clicks)
camoufox eval "var b=document.querySelectorAll('button');for(var i=0;i<b.length;i++)if(b[i].textContent.trim()==='Jetzt registrieren')b[i].click();"
```

## SPA Architecture Notes

- The app uses SYNACT framework with custom web components (`s-choice-list-item`, `s-combobox`, `s-button`, `s-text-field`)
- The body HTML appears empty (`document.body.children` = 0) because everything renders inside Shadow DOM / Web Components
- Hermes browser tools (`browser_navigate`, `browser_click`) cannot interact with this SPA:
  - DOM is empty (all content in shadow DOM)
  - `browser_console` with `expression=` requires `browser.allow_unsafe_evaluate: true` in config.yaml
  - Even with unsafe eval, JS clicks on custom components don't trigger SYNACT's internal state
- **Camoufox is REQUIRED** for this site — native Playwright `click_element` and `type` work correctly

## Capsolver Failure

- `FriendlyCaptchaTaskProxyLess` returns `ERROR_CAPTCHA_SOLVE_FAILED` (code 1012)
- The PoW is session-bound (sess_id, comm_id, agent_id) — cannot solve out-of-band
- Capsolver is useless for Friendly Captcha — use Camoufox headed mode instead

## Alternative: Phone-Based Enrollment

When HUK24 online registration fails, call a local insurer office:
- **LVM Udo Brüning**, Falkenstraße 36, <PLZ> <CITY> — Tel: 0251 7020
- LVM charges 24,75€/year (einheitstarif, no age surcharge)
- Anteilig for 8 months (Jul→Feb): ~16,50€
- Plakette available immediately in-office
- Required: FIN, ABE number, Personalausweis
