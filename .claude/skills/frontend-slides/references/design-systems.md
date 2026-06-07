# Design Systems for Frontend Slides

Use this reference when the user wants a slide deck styled from the project `design-systems/` library.

## Discovery

Design systems are stored as:

```text
design-systems/<slug>/DESIGN.md
```

Each `DESIGN.md` usually contains:

- H1 title
- `> Category: ...`
- short summary line
- visual theme and atmosphere
- color palette and roles
- typography rules
- component stylings
- layout principles
- depth/elevation
- do/don't guidance
- responsive behavior

Run the helper from the project root:

```bash
python3 .claude/skills/frontend-slides/scripts/list_design_systems.py
python3 .claude/skills/frontend-slides/scripts/list_design_systems.py --query "ai developer editorial"
python3 .claude/skills/frontend-slides/scripts/list_design_systems.py --slug apple
```

## Selection Heuristics

Use these mappings when the user does not name a specific slug:

| Need | Good candidates |
|---|---|
| executive, premium, product launch | `apple`, `bmw`, `bugatti`, `ferrari`, `lamborghini`, `tesla` |
| AI, model, agent, developer platform | `claude`, `cohere`, `mistral-ai`, `ollama`, `replicate`, `together-ai`, `voltagent`, `x-ai` |
| developer tools, infra, API | `cursor`, `linear-app`, `supabase`, `vercel`, `warp`, `hashicorp`, `mongodb` |
| SaaS product education | `airtable`, `cal`, `intercom`, `mintlify`, `notion`, `resend`, `zapier` |
| finance, crypto, business metrics | `stripe`, `wise`, `revolut`, `coinbase`, `binance`, `mastercard` |
| editorial, long-form, workshop teaching | `warm-editorial`, `notion`, `wired`, `theverge`, `apple` |
| creator, visual design, prototype | `figma`, `framer`, `miro`, `webflow`, `pinterest` |
| consumer brand, lifestyle | `airbnb`, `nike`, `spotify`, `starbucks`, `uber` |

Prefer `default` or `warm-editorial` when the user needs a neutral professional deck and has no brand direction.

## Adaptation Procedure

1. Read only the selected `DESIGN.md`.
2. Extract tokens:
   - background, text, muted text, accent, surface, border
   - display/body/mono font families
   - radius scale
   - spacing/grid rhythm
   - shadow/elevation rules
3. Translate to slide CSS variables:

```css
:root {
  --bg-primary: ...;
  --bg-secondary: ...;
  --surface: ...;
  --text-primary: ...;
  --text-secondary: ...;
  --accent: ...;
  --border: ...;
  --font-display: ...;
  --font-body: ...;
  --radius: ...;
}
```

4. Convert component guidance into slide components:
   - hero slide
   - section title slide
   - feature grid
   - comparison table
   - timeline/process
   - quote/callout
   - checklist/action slide
   - code or terminal panel
5. Preserve viewport fitting:
   - every `.slide` uses `height: 100vh; height: 100dvh; overflow: hidden;`
   - every font and spacing scale uses `clamp()`
   - split dense content instead of shrinking below readability

## Guardrails

- Brand-inspired systems are aesthetic references, not official brand assets.
- Do not use logos, product images, or official marks unless supplied by the user.
- Do not claim affiliation with the referenced brand.
- Do not copy web page structures blindly. Convert them into slide-native layouts.
- If a design system conflicts with frontend-slide rules, viewport fitting and accessibility win.
- The global frontend guidance says letter spacing should be `0`; follow that unless explicitly told otherwise.

