---
name: Civic Blueprint
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#43474d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#74777e'
  outline-variant: '#c3c6ce'
  surface-tint: '#49607c'
  primary: '#001428'
  on-primary: '#ffffff'
  primary-container: '#0f2942'
  on-primary-container: '#7991af'
  inverse-primary: '#b0c9e8'
  secondary: '#455f87'
  on-secondary: '#ffffff'
  secondary-container: '#b5d0fd'
  on-secondary-container: '#3e5980'
  tertiary: '#00170c'
  on-tertiary: '#ffffff'
  tertiary-container: '#002e1d'
  on-tertiary-container: '#00a270'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d1e4ff'
  primary-fixed-dim: '#b0c9e8'
  on-primary-fixed: '#011d35'
  on-primary-fixed-variant: '#314863'
  secondary-fixed: '#d5e3ff'
  secondary-fixed-dim: '#adc8f5'
  on-secondary-fixed: '#001c3b'
  on-secondary-fixed-variant: '#2d486d'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Public Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Public Sans
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Public Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Public Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Public Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Public Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  title-md:
    fontFamily: Public Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.025em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-sm: 1rem
  gutter-lg: 2rem
  margin: 1.5rem
  margin-sm: 1rem
  margin-lg: 3rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The design system establishes an institutional yet deeply modern aesthetic tailored for an agentic government scheme recommendation engine. The target audience encompasses diverse citizen demographics, caseworkers, and enterprise administrative users seeking rapid, unambiguous eligibility determination.

The core personality communicates:
- **Constitutional Authority:** Grounded, unshakeable trust and regulatory precision.
- **Empathetic Clarity:** Transparent decision-making and cognitive relief amid complex civic bureaucracy.
- **Agentic Efficiency:** Real-time synthesis, verifiable provenance, and explicit next-step acceleration.

The visual direction merges **Modern Institutionalism** with **Controlled Glassmorphism**. Layouts balance crisp structure, clear delineation, and subtle translucent layering. Translucency is employed sparingly on interactive overlays, agent response feeds, and floating eligibility dossiers to retain spatial awareness without sacrificing WCAG AAA contrast requirements. High-contrast structural boundaries maintain order, ensuring every recommendation feels certified and auditable.

## Colors

The color palette centers on high-authority naval tones balanced by a clinical slate foundation and deliberate semantic cues.

- **Primary (`#0F2942` - Deep Authority Navy):** Anchors headers, primary command buttons, and core application chrome. Conveys federal-grade reliability and legal certitude.
- **Secondary (`#1E3A5F` - Sub-Authority Slate Navy):** Drives secondary interactions, section dividers, active interactive strokes, and high-level card headers.
- **Tertiary / Semantic Success (`#10B981` - Emerald Scheme Verified):** Reserved strictly for validated criteria, guaranteed eligibility badges, confirmed entitlements, and successful submission states.
- **Warning / Action Needed (`#F59E0B` - Amber Clarification):** Identifies pending documentation, ambiguous citizen profile matches, and agent prompt clarifications.
- **Destructive / Ineligible (`#EF4444` - Ruby Ineligible):** Communicates statutory disqualifications, expired schemes, or critical input errors.
- **Neutral Foundation:** Standard canvas uses `#F8FAFC` (Canvas Slate), layered against `#FFFFFF` (Surface Elevated) and strokes in `#E2E8F0` / `#CBD5E1`. Body typography is set to `#0F172A` to guarantee contrast ratios surpassing 7:1.

Focus rings use an explicit dual-stroke strategy: an inner `#FFFFFF` offset and an outer `#0F2942` outline (or `#2563EB` interactive focus outline) to ensure immediate spatial visibility across assistive technologies.

## Typography

The type scale combines `Public Sans` for headlines and institutional titles with `Inter` for body copy, data summaries, and label interfaces.

- **Public Sans** lends official, government-standard legitimacy, derived directly from open, accessible civic design conventions. Its structural terminals ensure maximum legibility for scheme designations and legal headers.
- **Inter** handles high-density criteria listings, agent reasoning steps, and interactive input forms. Its tall x-height and distinct glyph design preserve clarity across low-resolution viewports and assistive screen readers.

Tabular figures (`tnum`) must be activated for scheme grant values, benefit percentages, and criterion counts to preserve alignment in structured summary lists.

## Layout & Spacing

The design system employs a **12-column responsive fluid grid** with an explicit maximum content constraint of `1440px` to prevent excessive line lengths on wide screens.

- **Breakpoints:**
  - Mobile: `< 640px` (4 columns, `margin-sm: 1rem`, `gutter-sm: 1rem`)
  - Tablet: `640px - 1024px` (8 columns, `margin: 1.5rem`, `gutter: 1.5rem`)
  - Desktop: `> 1024px` (12 columns, `margin-lg: 3rem`, `gutter-lg: 2rem`)

Layouts prioritize structured vertical rhythm:
- Spacing follows an 8pt architectural rhythm, with a supplementary 4pt step for dense tabular metadata and badge paddings.
- Dynamic conversational interfaces (Agentic Assistant feed) occupy a persistent 4-column side dossier or fluid split pane on desktop (`col-span-4` alongside `col-span-8` scheme catalogue).
- On mobile viewpoints, the AI agent prompt shifts to a fixed bottom drawer with safe-area spacing and a visible elevation boundary.

## Elevation & Depth

Visual hierarchy uses a hybrid of **Tonal Layering**, **Crisp Structural Borders**, and **Frosted Architectural Glass**. This avoids the informality of generic consumer web apps while preventing the visual stagnation of legacy government databases.

1. **Surface 0 (Base Canvas):** Set to `#F8FAFC`. Completely flat; establishes ground level.
2. **Surface 1 (Base Cards & Shells):** Crisp `#FFFFFF` surface bounded by a `1px` high-contrast outline (`#E2E8F0`). Subtly grounded by an ambient institutional drop shadow: `0 1px 3px rgba(15, 41, 66, 0.06), 0 1px 2px rgba(15, 41, 66, 0.04)`.
3. **Surface 2 (Interactive Floating / Active Dossiers):** Semi-opaque frosted slate-white (`rgba(255, 255, 255, 0.88)` with `backdrop-filter: blur(12px)`), bounded by a precision stroke of `1px solid rgba(226, 232, 240, 0.95)` and elevated with `0 10px 15px -3px rgba(15, 41, 66, 0.08), 0 4px 6px -4px rgba(15, 41, 66, 0.03)`. Used for scheme recommendation panels and conversational popovers.
4. **Surface 3 (Overlays, Modals & Critical Dialogs):** `#FFFFFF` paired with an administrative backdrop shield (`rgba(15, 41, 66, 0.65)` backdrop with `blur(4px)`). Shadow: `0 20px 25px -5px rgba(15, 41, 66, 0.12), 0 8px 10px -6px rgba(15, 41, 66, 0.06)`.
5. **Interactive Focus Elevation:** Interactive surfaces do not rely on elevation changes alone to signify focus. Focus states introduce an unmistakable high-contrast `2px` solid ring `#0F2942` with a `2px` white offset gap.

## Shapes

The design system employs a **Soft (Level 1)** geometric standard. This geometry balances modern software tactility with the stability and restraint expected of government portals.

- Base controls, buttons, text inputs, and list elements use `0.25rem` (4px).
- Containers, scheme result cards, modal dialogues, and alert banners use `rounded-lg` at `0.5rem` (8px).
- Large elevated dashboard containers use `rounded-xl` at `0.75rem` (12px).
- Status indicators, verified pills, and scheme criterion markers utilize strict geometric pill enclosures (`rounded-full`) to immediately differentiate taxonomy markers from rectangular form fields and actionable cards.

## Components

### Buttons
- **Primary:** Background `#0F2942`, text `#FFFFFF`, border `1px solid transparent`. Active/Hover: `#1E3A5F`. Focused: `2px` offset outline. Height: 44px (touch target compliant).
- **Secondary:** Background `#FFFFFF`, text `#0F2942`, border `1px solid #CBD5E1`. Hover: `#F1F5F9` with border `#0F2942`.
- **Agentic Quick-Action:** Background `rgba(30, 58, 95, 0.06)`, text `#1E3A5F`, border `1px dashed #94A3B8`. Hover: Background `rgba(30, 58, 95, 0.12)`.

### Scheme Badges & Criteria Chips
- **Verified Eligible:** Background `#ECFDF5`, text `#065F46`, border `1px solid #10B981`. Prefixed with an emerald check icon.
- **Under Review / Missing Info:** Background `#FFFBEB`, text `#92400E`, border `1px solid #F59E0B`. Prefixed with an alert icon.
- **Ineligible:** Background `#FEF2F2`, text `#991B1B`, border `1px solid #EF4444`. Prefixed with an exclusion cross icon.
- **Government Authority Tier:** Background `#0F2942`, text `#FFFFFF`, font `label-sm`, all-caps tracking (`letterSpacing: 0.04em`).

### Cards (Scheme Recommendation & Agent Dossiers)
- Composed of Surface 1 or Surface 2 with a top accent line: a 3px border top (`#10B981` for high-match eligibility, `#0F2942` for institutional notices, `#F59E0B` for pending inputs).
- Features a structured header block containing scheme agency logo/tag, match percentage pill, and primary grant amount.
- Distinct body compartment dedicated to "AI Reasoning Rationale," styled in `#F8FAFC` background with a subtle left quote border in `#1E3A5F`.

### Input Fields & Search Bars
- Background `#FFFFFF`, border `1px solid #94A3B8`. Minimum height 44px. Text `body-md` in `#0F172A`.
- Placeholder text in `#64748B`.
- Focused state: border `#0F2942`, outline `2px solid #0F2942`, offset `2px`.
- Error state: border `#EF4444`, supplementary helper text with alert indicator.

### Checkboxes & Radio Buttons
- 20px x 20px physical size with touch targets padded to 44px.
- Unchecked: `#FFFFFF` with `2px solid #64748B`.
- Checked: `#0F2942` with high-contrast `#FFFFFF` tick or dot. Focus uses the dual-stroke accessibility ring.

### Agentic Synthesis Bar & Reasoning Panel
- A distinct docked panel with frosted glass backing (`rgba(248, 250, 252, 0.95)` with `backdrop-filter: blur(8px)`).
- Outlined with `1px solid #CBD5E1`.
- Contains typing/reasoning indicator with step-by-step disclosure accordion ("Checked Income Criteria", "Verified Residency", "Scanning 14 Grants").