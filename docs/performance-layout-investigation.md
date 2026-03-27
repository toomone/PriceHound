# Performance & layout investigation (PriceHound)

## Goal

Reduce **CLS** (layout shift), **INP** (interaction delay), and **LCP** regressions reported in Datadog RUM for `service:pricehound` (especially `env:prod`).

## Datadog RUM — useful queries

- Views with frustration: `service:pricehound env:prod @view.frustration.count:>0`
- Web vitals on views: filter RUM Explorer by **View** events and inspect `@view.largest_contentful_paint`, `@view.cumulative_layout_shift`, `@view.inp` (field names follow your RUM version).
- Session Replay: replay sessions with high CLS or frustration on the main quote URL.

## Suspected sources (codebase)

| Area | Risk | Notes |
|------|------|--------|
| `+layout.svelte` | INP / paint | Full-page `gradient-bg` paints large gradients; acceptable cost but shows up in profiles. |
| `CostDistributionChart` + `layerchart` | LCP / JS | Heavy chunk; chart mount can shift content if container height not reserved. |
| Billing comparison grid | CLS | `grid-template-columns: repeat(N, 1fr)` changes when toggling Annually / Monthly / On-Demand. |
| Get Started `slide` transition | CLS | Expanding panel adds height below the fold. |
| Fixed “View Summary” bar | UX / scroll | Overlays content; mitigated with `scroll-padding-bottom` on `html` in `app.css`. |
| Google Fonts (JetBrains Mono) | CLS / FOIT | `preconnect` in `app.html`; ensure `display=swap` (or `optional`) on font links. |
| Theme (`ModeWatcher`) | Flash | Possible one-frame theme/layout flash on load. |

## Already applied (mitigations)

- `html { scroll-padding-bottom: 5rem }` — aligns scroll targets with the fixed bottom bar.
- `min-h-[280px]` on the cost distribution block — reserves space before the donut chart mounts.
- Root layout wrapper is `<main class="gradient-bg">` for a single landmark and clearer structure.

## Next steps (recommended)

1. **Local Lighthouse** (Performance): `npm run build && npm run preview`, then run Lighthouse against `http://localhost:4173` — inspect **Performance** + **Diagnostics** (unused JS, layout shifts).
2. **Bundle**: `vite-bundle-visualizer` or `rollup-plugin-visualizer` on the client build — target `layerchart` for lazy/dynamic import from `CostDistributionChart.svelte`.
3. **Billing grid**: If RUM shows CLS on the summary card, consider a **minimum height** for the billing options row when 1–3 columns are visible, or animate height with explicit `min-height` between states.
4. **INP**: Profile interactions on `gradient-bg`, product search, and quote title (`h3`); defer non-critical work off the critical path of `click` / `input` handlers.

## Reproduce locally

```bash
cd frontend && npm run build && npm run preview
# Lighthouse CLI (optional): npx lighthouse http://localhost:4173 --only-categories=performance
```
