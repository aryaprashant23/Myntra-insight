---
name: Neon Synth
colors:
  surface: '#10131a'
  surface-dim: '#10131a'
  surface-bright: '#363940'
  surface-container-lowest: '#0b0e14'
  surface-container-low: '#191c22'
  surface-container: '#1d2026'
  surface-container-high: '#272a31'
  surface-container-highest: '#32353c'
  on-surface: '#e1e2eb'
  on-surface-variant: '#e3bdc0'
  inverse-surface: '#e1e2eb'
  inverse-on-surface: '#2e3037'
  outline: '#ab888b'
  outline-variant: '#5b4042'
  surface-tint: '#ffb2ba'
  primary: '#ffb2ba'
  on-primary: '#670021'
  primary-container: '#ff4f74'
  on-primary-container: '#5a001c'
  inverse-primary: '#bd0043'
  secondary: '#d3fbff'
  on-secondary: '#00363a'
  secondary-container: '#00eefc'
  on-secondary-container: '#00686f'
  tertiary: '#cdbdff'
  on-tertiary: '#370096'
  tertiary-container: '#9a7bff'
  on-tertiary-container: '#2f0084'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffd9dc'
  primary-fixed-dim: '#ffb2ba'
  on-primary-fixed: '#400011'
  on-primary-fixed-variant: '#910031'
  secondary-fixed: '#7df4ff'
  secondary-fixed-dim: '#00dbe9'
  on-secondary-fixed: '#002022'
  on-secondary-fixed-variant: '#004f54'
  tertiary-fixed: '#e8deff'
  tertiary-fixed-dim: '#cdbdff'
  on-tertiary-fixed: '#20005f'
  on-tertiary-fixed-variant: '#4f00d0'
  background: '#10131a'
  on-background: '#e1e2eb'
  surface-variant: '#32353c'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '800'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1'
    letterSpacing: 0.05em
  code-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  container-max: 1440px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style

The design system is engineered for a high-performance, AI-driven environment. It targets developers and data scientists who require a sophisticated, "command center" aesthetic that feels both futuristic and professional.

The style is a synthesis of **Modern Corporate** and **Glassmorphism**, elevated by **Vaporwave** color accents. It utilizes deep ebony surfaces contrasted against translucent glass panels. UI elements should evoke a sense of digital precision through the use of high-contrast glowing strokes, subtle background blurs, and hyper-clean layouts. The emotional response should be one of "powerful intelligence" and "unlimited data scale."

## Colors

This design system utilizes a high-contrast dark palette to emphasize the vibrant functional colors.

- **Primary (#ff3f6c):** Used for primary actions, critical data highlights, and brand presence. It represents the energy of the scraping engine.
- **Secondary (#00f0ff):** A neon electric blue used for "active" states, successful data fetches, and glowing accents.
- **Tertiary (#7c4dff):** A deep violet used for secondary visual interest, AI-specific features, and background gradients.
- **Neutral (#0b0e14):** The foundational ink-black. Surface colors are derived from this base with varying levels of transparency.

**Semantic Colors:**
- **Success:** Secondary Blue.
- **Error:** Primary Pink.
- **Surface:** `rgba(255, 255, 255, 0.03)` with a `20px` backdrop-blur.

## Typography

The typography system relies on **Inter** for its incredible legibility and neutral, systematic feel, ensuring that complex data remains readable. **Geist** is introduced for labels and code-heavy sections to lean into the developer-centric, technical nature of the product.

Headlines should use tight letter-spacing to appear more "locked-in" and authoritative. Body text maintains standard spacing for maximum comfort during long data-review sessions. Technical labels always use uppercase with slight tracking to distinguish them from interactive text.

## Layout & Spacing

The design system employs a **Fluid-Fixed Hybrid** grid. The sidebars and navigation elements occupy fixed widths (e.g., 280px for primary navigation), while the central dashboard workspace scales fluidly up to a 1440px maximum width.

A strict **8px modular scale** governs all spacing. 
- Elements within a group use 8px or 16px gaps.
- Distinct sections use 32px, 48px, or 64px gaps.
- On mobile, margins compress to 16px, and the 12-column grid collapses into a single-column vertical stack with 16px gutters.

## Elevation & Depth

Depth is conveyed through **Glassmorphism** and **Luminosity** rather than traditional shadows.

1.  **Base Layer:** The deepest `#0b0e14` background.
2.  **Surface Layer:** `rgba(255, 255, 255, 0.05)` with `blur(12px)`. This is used for cards and main panels.
3.  **Floating Layer:** `rgba(255, 255, 255, 0.1)` with `blur(24px)` and a `1px` stroke. Used for modals and dropdowns.
4.  **The Glow:** Active elements should use a `0 0 15px` outer glow using the Primary or Secondary color at 30% opacity to simulate light emitting from the screen.

## Shapes

The shape language is "Soft-Technical." Corners are noticeably rounded but not overly playful, maintaining a professional tool-like appearance.

- **Small Components (Buttons, Inputs):** 4px (`rounded-sm`).
- **Standard Cards/Panels:** 8px (`rounded-md`).
- **Large Modals/Containers:** 12px (`rounded-lg`).
- **Interactive Elements:** Always include a `1px` inner border (stroke) at `rgba(255, 255, 255, 0.1)` to define the glass edges against the dark background.

## Components

### Buttons
- **Primary:** Solid Primary Pink background, white text, subtle pink glow on hover.
- **Secondary:** Transparent with a 1px Secondary Blue border. On hover, background fills with 10% Blue.
- **Ghost:** No border, secondary blue text, highlight on hover.

### Input Fields
Darker than the surface (`rgba(0,0,0,0.3)`), 1px border. On focus, the border glows Secondary Blue and the label shifts to the Secondary color.

### Chips / Status Badges
Used for scraper status (e.g., "Running", "Failed"). These use high-saturation backgrounds with 20% opacity and a solid-colored dot for status indication.

### Data Cards
The "Glass" card is the primary container. It must have a `1px` border (top and left slightly brighter than bottom and right) to simulate a light source from the top-left.

### Progress Indicators
Thin, high-precision bars using the Secondary Blue. For AI-processing states, use a "scanner" animation—a vertical or horizontal gradient line that sweeps across the glass panel.