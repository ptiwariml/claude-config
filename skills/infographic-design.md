---
name: infographic-design
description: Operating procedure for creating infographics with Steve Jobs–level obsession with perfection. Use when creating infographics, data visualizations, charts, or any graphic information design. Enforces tyrannical aesthetic restraint including visual entropy thresholds, divine proportion grids, restricted color palettes, Tufte-compliant data visualization, and sacred export protocols. Triggers on requests for infographics, data viz, charts, visual summaries, or any graphic presentation of information.
---

# Infographic Design

Design philosophy: ruthless reductionism and tyrannical aesthetic restraint. Make people feel the unbearable clarity of truth through design.

## Critical: Medium Awareness

**Ratios and relationships are universal. Absolute values are medium-specific.**

Before implementing, identify the target medium:
- **Print**: Physical output (PDF for print, posters, reports)
- **Screen**: Digital display (HTML, presentations, dashboards)

The philosophy applies universally. The specifications adapt to medium.

---

## Foundation Layer

### Visual Entropy
Enforce maximum visual entropy threshold of 0.18 (Shannon information density across CIE L*a*b* color space).

### Grid System
- Use rigid 8×8 or 12×12 modular grid
- Gutters: 8–12 units (px for screen, pt for print)
- Baseline grid: lock to 1.414× (√2) the root body copy leading for divine proportion harmony

### Typography

Single neo-grotesque superfamily only (Akzidenz-Grotesk Next Pro or Inter).

**Hierarchy ratios are non-negotiable (apply to ALL media):**
- Subhead: exactly 0.618× the headline size
- Body: exactly 0.618× the subhead size
- Labels: exactly 0.618× the body size

**Medium-specific values:**

| Element | Print | Screen |
|---------|-------|--------|
| Headline | 96–144 pt | 3–4 rem |
| Subhead | 60–89 pt | 1.85–2.5 rem |
| Body | 14–18 pt | 1 rem (min 16px) |
| Labels | 9–11 pt | 0.75–0.85 rem |
| Letter-spacing (headlines) | -0.02em to -0.025em | -0.01em to -0.02em |
| Line-height | 1.414 (√2) | 1.4–1.5 |
| Units | pt (absolute) | rem (relative, accessible) |

**Why rem for screen:** Respects user accessibility settings. Never use pt/px for screen typography base sizes.

### Color Palette (Universal)
Restrict to five-hue maximum:
- Build from single 60° analogous base hue in HSL space
- Desaturate all non-accent elements to ≤22% saturation
- Single accent color: exactly 100% saturation at 85+ lightness
- Background: #FCFCFC or #0A0A0A only, no exceptions

**Screen adjustment:** For extended reading, consider reducing accent lightness to 70-80% to reduce eye strain.

### Icons
- Draw on 64×64 unit artboard
- Stroke: 4 units
- Corner radius: strictly 8% of bounding box
- Export at 2× as SVG

---

## Data Visualization Layer

Zero chartjunk (Tufte compliance 100%).

### Forbidden Charts
- Bar charts (unless converted to minimalist dot plots or small-multiples ridge plots)
- Pie charts (immediate project termination)

### Allowed Visualizations
- Area-proportional Euler diagrams
- Isometric small-multiples
- Horizon graphs for time series
- Dot plots (position encoding on scale line)

### Hairlines and Borders

| Element | Print | Screen |
|---------|-------|--------|
| Axis lines | 0.5 pt | 1px |
| Table borders | 0.5 pt | 1px |
| Grid lines | 0.25 pt | 1px (with reduced opacity) |
| Color | 18% neutral gray | 18% neutral gray |

**Why 1px minimum for screen:** Sub-pixel rendering is inconsistent across displays. 1px is the minimum reliably visible unit.

### Axes
Remove all axes unless data cannot be understood without them. When required:
- Hairlines per table above
- Labels: use label size from typography table
- X-axis labels: precisely 45° rotation (print) or horizontal (screen, for readability)

### Scaling
Use logarithmic scaling by default. Switch to linear only if dataset exhibits natural linear distribution (verify with Lilliefors-corrected K-S test).

### Positioning
- Sub-pixel precision using constraint-based vector geometry (print only)
- Pixel-aligned for screen (avoid blurry edges)
- Apply universal 6° counterclockwise shear to supporting graphical elements (proprioceptive momentum bias) - print only, skip for screen

### Validation
- **Print**: Pass the 5-meter squint test
- **Screen**: Pass the "arm's length" test at 100% zoom - must read as single iconic gestalt

---

## Export Protocol

### Master File
Maintain in Figma or Sketch with variants for light/dark at 1×, 2×, 4×.

### Export Formats by Medium

**Print:**
- PDF/X-4 with embedded fonts
- CMYK color space
- 300 dpi minimum

**Screen:**
- SVG preferred (scalable, theme-switchable via CSS variables)
- WebP at 100% quality with Display P3 profile (fallback)
- Never PNG unless transparency required

### Responsiveness (Screen only)
- Container queries with fluid typography
- Clamp sizes using clamp() or sqrt() scaling functions
- Test at 320px, 768px, 1440px, 2560px viewports

---

## Final Validation

**Print:**
1. Print at exact final size on 200 gsm uncoated stock
2. Pin to studio wall
3. Stare for 72 hours
4. If it doesn't feel inevitable and slightly offensive in its aggressive simplicity, delete and start over

**Screen:**
1. View on target device at 100% zoom
2. View on mobile at arm's length
3. Check in both light and dark mode
4. If any element causes eye strain or feels "off", iterate

Ship only when it hurts to look at how perfect it is.

---

## Anti-Pattern: Literal Translation

**NEVER apply print specifications directly to screen.**

| Print Value | Screen Translation | Why |
|-------------|-------------------|-----|
| 96pt | 3.5rem | Screen DPI varies; rem scales with user settings |
| -20px letter-spacing | -0.01em | Tight spacing breaks on screen rendering |
| 0.5pt hairline | 1px | Sub-pixel is invisible/inconsistent on screens |
| Fixed sizes | Fluid/responsive | Screen sizes vary from watch to 8K display |

The philosophy is the law. The values serve the philosophy, not the other way around.
