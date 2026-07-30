# Phase 2 — UI, Design System, Animation, Responsive & Accessibility

## 1. UI Requirement Document

### 1.1 Design Philosophy
- Reference class: Stripe.com, Linear.app, Framer, Notion, Apple marketing pages
- Light, airy, generous whitespace; content-first; math presented like a beautifully typeset textbook
- Every interactive element has hover, focus, active, and disabled states
- Nothing ships that looks like default Bootstrap/Material

### 1.2 Design System (Tokens)

**Color Palette (light theme only for app shell):**

| Token | Value | Usage |
|---|---|---|
| `bg-base` | #FFFFFF | Page background |
| `bg-subtle` | #F8FAFC (slate-50) | Section alternation, cards backdrop |
| `bg-muted` | #F1F5F9 (slate-100) | Table stripes, input fills |
| `primary` | #4F46E5 (indigo-600) | Primary buttons, links, active states |
| `primary-hover` | #4338CA (indigo-700) | |
| `accent-blue` | #2563EB (blue-600) | Charts, secondary accents |
| `accent-purple` | #7C3AED (violet-600) | Gradient endpoints, highlights |
| `accent-sky` | #0EA5E9 (sky-500) | Info states, chart series 2 |
| `text-primary` | #0F172A (slate-900) | Headings |
| `text-secondary` | #475569 (slate-600) | Body |
| `text-muted` | #94A3B8 (slate-400) | Captions, placeholders |
| `border` | #E2E8F0 (slate-200) | Card/input borders |
| `success` | #10B981, `warning` #F59E0B, `error` #EF4444 | Feedback |

**Signature gradients (soft, ≤ 8% saturation shift):**
- Hero: `linear-gradient(135deg, #EEF2FF → #F5F3FF → #F0F9FF)` (indigo-50 → violet-50 → sky-50)
- Primary button: `linear-gradient(135deg, #4F46E5 → #7C3AED)`
- Card glow accents: radial indigo-100/sky-100 blobs at 40% opacity behind hero and result cards

**Typography:**
- Display/UI: **Inter** (variable), tabular numerals for all numbers
- Math: **KaTeX** default (Computer Modern feel = academic credibility)
- Code/values: **JetBrains Mono** for coefficients and equation strings
- Scale: 12/14/16/18/20/24/30/36/48/60 px; line-height 1.5 body, 1.2 headings; tracking -0.02em on headings

**Shape & Depth:**
- Radii: 8 px (inputs), 12 px (buttons), 16 px (cards), 24 px (hero panels)
- Shadows: layered soft shadows only (`0 1px 2px rgba(15,23,42,.04), 0 8px 24px rgba(15,23,42,.06)`); elevated hover: `0 12px 32px rgba(79,70,229,.12)`
- Glassmorphism: navbar on scroll (`backdrop-blur-md bg-white/70 border-b border-slate-200/60`) and floating export bar only; used sparingly
- Spacing: strict 4 px grid; section padding 96 px desktop / 64 tablet / 48 mobile

**Iconography:** Lucide icons, 1.5 px stroke, 20/24 px, always with matching color tokens.

### 1.3 Page-by-Page Specification

**A. Landing Page (`/`)**
1. **Navbar** — sticky, transparent → glass on scroll; logo (gradient mark + "CurveLab"), links: Home, Workspace, Methods, Docs, GitHub; primary CTA "Open Workspace"; hamburger sheet menu on mobile
2. **Hero** — gradient mesh background with 2 slow-floating blurred blobs; H1 "Curve Fitting, Beautifully Solved."; subtitle; two CTAs (gradient primary "Start Fitting", ghost "See How It Works"); right side: live auto-animating demo chart (curve draws in on loop); floating stat chips (glass) around it
3. **Animated counters strip** — "3 Methods · Σ Every Summation Shown · 8 Export Formats · <300 ms Compute" counting up on scroll into view
4. **Feature cards** — 6 cards, 3-col grid, hover lift + gradient border reveal: Least Squares Engine, Step-by-Step Solutions, Interactive Graphs, Smart Data Import, University Reports, Instant Metrics
5. **About the Algorithms** — 3 tabs (Linear/Polynomial/Exponential) each with KaTeX formulas, normal equations, mini illustrative chart, "when to use" note
6. **Interactive mini-demo** — embedded simplified workspace with a preset dataset; editing a point refits live
7. **Contact/credits section** + **Footer** — 3 columns (project, methods, links), university/course line, copyright

**B. Workspace (`/app`) — the core product**
Layout: two-zone. Left rail (380 px, collapsible on tablet/mobile into top accordion): **Input Panel**. Main area: **Results Dashboard**.

*Input Panel:*
- Tab group: Manual | Paste | Upload | Samples
- Manual: virtualized editable grid of X/Y rows, add row (Enter), delete, reorder; live count badge
- Paste: large textarea with instant parse preview + detected delimiter chip
- Upload: drag-and-drop zone (dashed indigo border, animated on drag-over), file chip with size, parse status
- Cleaning report banner (e.g., "2 duplicates removed · 1 empty row dropped") — dismissible, amber
- Model selector: segmented control Linear | Polynomial | Exponential (+ degree stepper 2–6 when Polynomial) + "Compare All" toggle
- Precision select (2–8 decimals) and big gradient **"Fit Curve"** button (also auto-fit-on-change toggle)

*Results Dashboard (appears with staggered entrance):*
1. **Result cards row** — 4 metric cards (R², RMSE, MAE, MSE) with animated count-up, trend-style sparkline of residuals, tooltip definitions
2. **Equation card** — large KaTeX equation, copy buttons (LaTeX / plain), model badge
3. **Graph card** — main Plotly chart with toolbar (zoom/pan/reset/theme/PNG/SVG), tab to Residual Plot; equation annotation on chart
4. **Prediction card** — x input(s) → animated ŷ result, extrapolation warning badge, batch mode
5. **Tables card** — tabs: Input Data | Calculation Table | Summations; full table features (FR-5)
6. **Step-by-Step card** — vertical numbered timeline, each step a collapsible with KaTeX; "Expand all"
7. **Export bar** — floating glass bar bottom-right: PDF, DOCX, XLSX, CSV, JSON, TXT, PNG, SVG, Print; each triggers with progress micro-state
- Empty state: elegant illustration + "Load a sample dataset" shortcut
- Loading: skeleton cards, shimmering chart placeholder

**C. Methods/Docs page (`/methods`)** — long-form typeset theory per method with derivations, worked example, and "open in workspace" buttons.

**D. 404** — playful scatter-points illustration forming "404", CTA home.

### 1.4 Component Inventory (design-system level)
Button (primary-gradient/secondary/ghost/icon), Input, NumberField, SegmentedControl, Select, Tabs, Card, MetricCard, Badge, Tooltip, Toast, Modal, Drawer/Sheet, Table (with all behaviors), FileDropzone, EditableGrid, Skeleton, Stepper/Timeline, Accordion, EquationBlock (KaTeX wrapper), ChartFrame, ExportBar, Navbar, Footer, EmptyState, Callout.

---

## 2. Animation Requirement

| ID | Animation | Spec |
|---|---|---|
| AN-1 | Page transitions | Route fade+8px slide-up, 250 ms, ease-out (Framer Motion `AnimatePresence`) |
| AN-2 | Results entrance | Staggered children, 60 ms stagger, spring (stiffness 260, damping 24) |
| AN-3 | Curve draw-in | Fitted curve animates left→right over 900 ms ease-in-out on every fit; scatter points pop in with 15 ms stagger |
| AN-4 | Animated counters | Count-up 1.2 s with easing, triggered by IntersectionObserver, tabular nums (no layout shift) |
| AN-5 | Button micro-interactions | Hover: -1 px translate + shadow bloom, 150 ms; press: scale .98; primary button gradient shifts 15° on hover |
| AN-6 | Card hover | translateY(-4px) + shadow elevate + 1 px gradient border fade-in, 200 ms |
| AN-7 | Hero blobs | 20 s infinite slow drift (transform only, GPU) |
| AN-8 | Skeletons | Shimmer sweep 1.4 s linear infinite |
| AN-9 | Dropzone | Border pulse + icon bounce on drag-over |
| AN-10 | Toast/Export feedback | Slide-in from bottom-right, progress ring on export buttons while generating |
| AN-11 | Number results | ŷ prediction flips in with rolling-digit effect |
| AN-12 | Lottie | Empty state + upload success check + 404; lazy-loaded, ≤ 150 KB each |
| AN-13 | Constraint | Transform/opacity only (no layout animation); all animation ≤ 60 fps budget; **`prefers-reduced-motion` disables AN-1..12** (instant states, counters render final value) |

---

## 3. Responsive Requirement

Breakpoints (Tailwind): `sm 640 · md 768 · lg 1024 · xl 1280 · 2xl 1536`

| Range | Workspace layout |
|---|---|
| ≥ 1280 | Left input rail 380 px + fluid dashboard, 4-col metric cards |
| 1024–1279 | Rail 320 px, 2-col metric cards |
| 768–1023 | Rail becomes collapsible top panel (accordion), dashboard full-width, 2-col cards |
| < 768 | Single column; input panel as bottom-sheet triggered by FAB "Edit Data"; metric cards 2-col; tables horizontally scrollable with sticky first column; export bar becomes bottom sheet menu |
| Landscape mobile | Chart gets priority: 70vh chart mode with overlay controls |

Rules: fluid type via clamp() on display sizes; touch targets ≥ 44 px; charts re-render responsively (Plotly `responsive: true` + ResizeObserver); no horizontal page scroll ever; test matrix 360, 390, 768, 1024, 1280, 1440, 1920 px + iPad landscape.

---

## 4. Accessibility Requirement (WCAG 2.1 AA)

- AC-1 Full keyboard operability: logical tab order, visible 2 px indigo focus ring (offset 2 px), skip-to-content link, Escape closes modals/sheets, arrow-key navigation inside editable grid and tables
- AC-2 Semantics: landmarks (nav/main/footer), single H1 per page, tables with `<th scope>`, form inputs with labels + `aria-describedby` errors
- AC-3 Charts: text alternative — every chart pairs with the data table + a generated summary sentence ("Fitted line y = 2.13 + 0.87x with R² = 0.98 over 24 points"); toolbar buttons labeled
- AC-4 Math: KaTeX rendered with MathML fallback / aria labels for screen readers
- AC-5 Contrast ≥ 4.5:1 body, ≥ 3:1 large text and UI borders vs background (verified for all tokens; text-muted only for non-essential captions)
- AC-6 Never color-only meaning: residual +/- uses sign + icon; validation errors use icon + text
- AC-7 Live regions: fit completion, cleaning report, and export status announced via `aria-live="polite"`
- AC-8 `prefers-reduced-motion` respected globally (AN-13); no autoplaying content that can't be paused
- AC-9 Forms: errors summarized at top on submit, programmatically focusable
- AC-10 Tooling gate: axe-core automated checks in CI + manual NVDA/VoiceOver pass on Workspace flow
