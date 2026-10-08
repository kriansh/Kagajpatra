# Kagajpatra

Bilingual (English / नेपाली) guide to Nepali government services — build for a
1-day hackathon. Big, accessible UI; voice input (mic) and read-aloud; AI
assistant (Gemma) grounded in the app's research-backed content; works fully
offline once the static assets are loaded.

## Demo services

1. **Birth certificate** (जन्म दर्ता) — ward office, 35-day free window
2. **House & property tax** (घर कर) — slab rates, discount/penalty windows
3. **Citizenship certificate** (नागरिकता) — DAO + ward recommendation
4. **Marriage registration** (विवाह दर्ता) — ward route or court marriage

## Stack

- **Django 6** backend, `services` + `assistant` apps
- Plain Django templates + hand-rolled CSS (no CDN runtime deps)
- Web Speech API: voice input (`ne-NP`/`en-US`) + speechSynthesis read-aloud
- AI: **Gemma via Gemini API**, automatic fallback to **local Ollama**

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# .env   (see .env.example)
GEMINI_API_KEY=...          # optional — local Ollama works without it
GEMINI_MODEL=gemma-3-27b-it # any model your project can access
OLLAMA_URL=http://localhost:11434

python manage.py migrate
python manage.py seed_demo     # loads the 4 services, hours, holidays
python manage.py runserver
```

Open http://127.0.0.1:8000/ and use the **नेपाली / English** toggle.

## AI assistant

The ask box (`/api/ask/`) builds a grounding prompt from the seeded database,
then:

1. tries **Gemini API** (`GEMINI_MODEL`, key from `.env`);
2. on any failure falls back to **Ollama** (`gemma4:e2b` → `gemma4:e4b` →
   `glm4:9b` → `qwen3.5:9b`, first one installed).

Tested: with the Gemini project denied, the app answer came from local
`glm4:9b`, in the active UI language, listing the correct grounded checklist.

## Content accuracy

All content lives in `services/management/commands/seed_demo.py` and is backed by
`docs/content-research.md` (official FAQs, gazette refs, DAO lists). Unverified
figures are intentionally vague ("amount set locally"). Notably:

- **Office hours** follow the Cabinet decision of **6 Apr 2026** (Rajpatra
  ref 26253): Mon–Fri **9 AM–5 PM**, **Sat + Sun** weekly holidays, lunch
  1:30–2:00 PM, winter hours 9 AM–4 PM from 2 Nov 2026. The old Friday
  half-day (10 AM–3 PM) ended 5 Apr 2026.
- **Holidays** come from the Nepal Rajpatra 2083 notice (ref 26242): Dashain
  block 17–23 Oct (Tika 21 Oct), Tihar 8–12 Nov (Bhai Tika 11 Nov), Chhath
  15 Nov, etc.

## Notes for the demo

- Voice input needs a browser with Web Speech API (Chrome/Edge).
- .gitignore excludes `.env`, `db.sqlite3`, `.venv`, `staticfiles`.

---

## Design system

All visual values are defined as CSS custom properties in `static/css/tokens.css`.
Components import only these tokens — no inline magic values anywhere.

### Token categories

| Category | File location | Example token |
|---|---|---|
| Colour palette | `tokens.css` | `--color-primary: #1F5F5B` |
| Semantic aliases | `tokens.css` | `--primary`, `--text`, `--border` |
| Typography | `tokens.css` | `--text-base: 1.125rem`, `--font-ui` |
| Spacing (8px grid) | `tokens.css` | `--space-4: 1rem` |
| Radii | `tokens.css` | `--radius: 0.75rem` |
| Shadows | `tokens.css` | `--shadow-sm` |
| Motion | `tokens.css` | `--duration: 160ms`, `--ease` |

Dark mode is automatic via `prefers-color-scheme` and can be forced with
`data-theme="dark"` on the `<html>` element.

### Components

| Component | CSS class | Notes |
|---|---|---|
| Button | `.btn`, `.btn--primary`, `.btn--secondary`, `.btn--ghost` | 52px min-height |
| Card | `.card`, `.card--interactive`, `.card--inset` | |
| Chip/Badge | `.chip`, `.chip--primary`, `.chip--success`, etc. | |
| Checklist item | `.check-item` | Accessible `role=checkbox` |
| Accordion | `.accordion`, `.accordion__trigger` | JS-animated max-height |
| Steps | `.steps-list`, `.step` | Connected with CSS line |
| Search bar | `.search-wrap` | Includes mic + submit |
| Voice button | `.voice-btn` | 7 states, aria-live |
| Toast | `.toast`, `window.KagajpatraToast(msg, type)` | 6s auto-dismiss |
| Before-you-go card | `.byg-card`, `.byg-grid` | Summary row on detail page |
| Skeleton | `.skeleton`, `.skeleton--text`, `.skeleton--card` | |

### View modes

- **Simple** (default): 20px+ body text, one column, big touch targets.
- **Detailed**: two-column layout, breadcrumbs, all fields at once.

Toggle is in the header. The choice is saved in `localStorage`.

### Text size

Three levels: normal / A+ / A++ (1×, 1.15×, 1.30× scale via `--ts-scale`).
Applied as `data-text-size` on `<html>`. Saved in `localStorage`.

### Contributing design

1. Add new tokens to `tokens.css` only — never hardcode colours/spacing elsewhere.
2. Test any new component at `--text-size: xlarge` and in dark mode.
3. Every interactive element needs a `min-height: 48px` touch target and a visible `:focus-visible` ring.
4. Add a string to both `en` and `ne` sections of `nagarik/i18n.py` before using it in a template.
