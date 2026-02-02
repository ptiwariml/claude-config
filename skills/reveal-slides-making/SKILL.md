---
name: reveal-slides-making
description: |
  Create professional presentation slides using Reveal.js with AI-generated diagrams.
  Use when: (1) building VC pitch decks, investor presentations, or professional slide decks,
  (2) creating Reveal.js HTML presentations with custom styling and embedded images,
  (3) generating diagrams with Nano Banana / Gemini for slide visuals,
  (4) exporting standalone single-file HTML presentations with base64-embedded assets,
  (5) structuring narrative-driven slide decks with chapter arcs.
  Helps with: slides, presentation, pitch deck, reveal.js, VC pitch, investor deck,
  keynote-style, HTML slides, standalone export, AI diagrams, Gemini image generation,
  slide design, professional presentation, conference talk, demo day slides.
  Solves: consistent slide styling, AI diagram quality, standalone HTML export,
  narrative structure for technical pitches, screenshot integration in slides.
author: Claude Code (Claudeception)
version: 1.0.0
date: 2026-01-28
---

# Reveal.js Slide Making

## Problem

Creating professional presentation slides (especially VC pitch decks) requires coordinating
multiple concerns: Reveal.js configuration, consistent visual design, AI-generated diagrams
that match each other aesthetically, app screenshots that look polished on slides, narrative
structure that tells a compelling story, and finally packaging everything into a single
standalone HTML file for easy distribution. Each of these has non-obvious pitfalls that cost
hours of iteration if not known upfront.

## Context / Trigger Conditions

- User asks to create a presentation, slide deck, or pitch deck
- User mentions Reveal.js or HTML-based slides
- User wants to generate diagrams or visuals for slides using AI (Gemini / Nano Banana)
- User needs a standalone single-file HTML presentation for sharing
- User is preparing for a VC pitch, demo day, conference talk, or investor meeting
- User wants to embed app screenshots into slides with professional styling
- User says "make slides", "create a deck", "build a presentation"
- User has an existing Reveal.js project and wants to improve it

## Solution

### Step 1: Reveal.js Configuration for Professional Slides

Use these settings for VC-quality presentations:

```javascript
Reveal.initialize({
    width: 1280,
    height: 720,
    margin: 0.05,
    center: true,
    hash: true,
    transition: 'fade',
    transitionSpeed: 'default',
    plugins: []
});
```

Key configuration decisions:
- **1280x720** (HD 16:9) -- compatible with PowerPoint, Keynote, and projectors
- **margin: 0.05** -- tight margins maximize slide real estate
- **center: true** -- content stays vertically centered
- **transition: 'fade'** -- cleanest transition for professional context

### Step 2: Light Theme CSS for Professional Look

White/light themes read better for VC pitches than dark themes. Set up CSS variables:

```css
:root {
    --r-background-color: #FAFAFA;
    --r-main-font: 'Inter', 'Segoe UI', system-ui, sans-serif;
    --r-main-font-size: 18px;
    --r-main-color: #2D3748;
    --r-heading-color: #1A202C;
    --r-heading-font: 'Inter', 'Segoe UI', system-ui, sans-serif;
    --r-link-color: #0066CC;
}

.reveal {
    font-family: var(--r-main-font);
    font-size: var(--r-main-font-size);
    color: var(--r-main-color);
}
```

Color system for consistent meaning across all slides and diagrams:

| Color   | Hex       | Usage                              |
|---------|-----------|------------------------------------|
| Blue    | `#0066CC` | Neutral / informational / links    |
| Green   | `#00A86B` | Success / positive / pass states   |
| Red     | `#D32F2F` | Problems / failures / pain points  |
| Amber   | `#FF8C00` | Bottlenecks / warnings / caution   |
| Dark    | `#1A202C` | Headings                           |
| Body    | `#2D3748` | Body text                          |
| BG      | `#FAFAFA` | Slide background                   |

### Step 3: Narrative Arc Structure

Structure slides as chapters with a story arc. Each slide gets:

```html
<section>
    <div class="chapter-number">Chapter N</div>
    <h2>Slide Title</h2>
    <p class="subtitle">Supporting subtitle text</p>
    <!-- Visual content: diagram, screenshot, or data -->
    <div class="key-message">
        <strong>Key takeaway in one sentence</strong>
    </div>
</section>
```

Recommended narrative arc for VC pitch decks:

1. **Problem** -- The pain point your audience recognizes
2. **Status Quo** -- How people currently deal with it (badly)
3. **The Trap** -- Why obvious solutions fail
4. **Insight** -- Your unique insight or approach
5. **Architecture** -- How your solution works
6. **Proof** -- Demo, screenshots, live evidence
7. **Comparison** -- Before vs. After / You vs. Alternatives
8. **Quality / Results** -- Metrics, outcomes, validation

CSS for chapter labels:

```css
.chapter-number {
    font-size: 0.7em;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: #0066CC;
    margin-bottom: 0.3em;
    font-weight: 600;
}

.subtitle {
    font-size: 0.85em;
    color: #718096;
    margin-top: -0.3em;
}

.key-message {
    margin-top: 1.2em;
    padding: 0.6em 1.2em;
    background: rgba(0, 102, 204, 0.06);
    border-left: 3px solid #0066CC;
    border-radius: 0 6px 6px 0;
    font-size: 0.85em;
}
```

### Step 4: AI Diagram Generation (Nano Banana / Gemini)

Use the Nano Banana skill with `gemini-3-pro-image-preview` for best text rendering.

**CRITICAL rules for AI diagram prompts:**

1. **Spell out words letter-by-letter** in prompts to prevent misspelling:
   ```
   "Label reads B-O-T-T-L-E-N-E-C-K (Bottleneck)"
   "Text says V-A-L-I-D-A-T-I-O-N (Validation)"
   ```
   AI image models frequently misspell words. Spelling them out dramatically reduces errors.

2. **Specify pure white background explicitly:**
   ```
   "Pure white background (#FFFFFF), not cream, not beige, not off-white"
   ```
   Models default to warm/cream backgrounds if not told otherwise.

3. **Use card-style containment for consistency:**
   ```
   "Content in a card with subtle shadow (0 4px 12px rgba(0,0,0,0.08)),
    rounded corners (8px radius), white margins (40px) around card"
   ```

4. **Always specify 16:9 aspect ratio:**
   ```
   "16:9 landscape aspect ratio, 1280x720 pixels"
   ```

5. **Create a unified DESIGN_SYSTEM constant** for batch generation:

```python
DESIGN_SYSTEM = """
Professional infographic style. Clean, modern, minimal.
Pure white background (#FFFFFF).
Card container with subtle shadow and rounded corners.
Font: clean sans-serif (like Inter or Helvetica).
Color palette:
  - Blue (#0066CC) for neutral/info elements
  - Green (#00A86B) for success/positive
  - Red (#D32F2F) for problems/failures
  - Amber (#FF8C00) for warnings/bottlenecks
  - Dark gray (#2D3748) for body text
  - Near-black (#1A202C) for headings
16:9 landscape, 1280x720 pixels.
"""
```

6. **Batch generate with rate limiting** (5-second delay between calls):

```python
import time

SLIDES = {
    "slide_01_problem": "Diagram showing... [specific prompt]",
    "slide_02_statusquo": "Diagram showing... [specific prompt]",
    # ...
}

for name, prompt in SLIDES.items():
    full_prompt = f"{DESIGN_SYSTEM}\n\n{prompt}"
    generate_image(full_prompt, output_path=f"images/{name}.png")
    time.sleep(5)  # Rate limiting between Gemini calls
```

### Step 5: App Screenshots in Slides

When embedding dark app screenshots on light slide backgrounds:

```css
.screenshot-container {
    position: relative;
    display: inline-block;
}

.screenshot {
    max-width: 85%;
    max-height: 420px;
    border-radius: 6px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    border: 1px solid #E0E0E0;
}
```

For status badge overlays (e.g., PASS/FAIL indicators):

```css
.status-badge {
    position: absolute;
    top: 12px;
    right: 12px;
    padding: 4px 12px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 0.75em;
    letter-spacing: 1px;
}

.badge-pass {
    background: #00A86B;
    color: white;
}

.badge-fail {
    background: #D32F2F;
    color: white;
}
```

HTML pattern:

```html
<div class="screenshot-container">
    <img src="screenshot.png" class="screenshot" alt="App screenshot">
    <span class="status-badge badge-pass">PASS</span>
</div>
```

**Consistency rule:** When showing PASS/FAIL or Before/After states, capture all
screenshots from the same app at the same viewport size. Use identical CSS styling
(same `max-width`, `max-height`, shadow, border-radius) for all screenshot elements.

### Step 6: Standalone HTML Export

Package the entire presentation as a single self-contained HTML file:

```python
import base64
from pathlib import Path

def create_standalone_html(slides_html, image_dir, output_path):
    """Create standalone HTML with embedded base64 images and inlined reveal.js."""

    # 1. Read the slides HTML
    html = Path(slides_html).read_text()

    # 2. Embed images as base64 data URIs
    for img_file in Path(image_dir).glob("*.png"):
        img_data = base64.b64encode(img_file.read_bytes()).decode()
        data_uri = f"data:image/png;base64,{img_data}"
        # Use string .replace(), NOT re.sub() -- avoids backslash escaping issues in JS
        html = html.replace(f"images/{img_file.name}", data_uri)

    # 3. Inline reveal.js CSS from CDN
    # Fetch and embed: reveal.css, white.css (theme)
    reveal_css = fetch_url("https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css")
    theme_css = fetch_url("https://cdn.jsdelivr.net/npm/reveal.js@5/dist/theme/white.css")
    html = html.replace(
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css">',
        f"<style>{reveal_css}</style>"
    )

    # 4. Inline reveal.js JavaScript
    reveal_js = fetch_url("https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.esm.js")
    # IMPORTANT: Use string .replace() not re.sub() for JS content
    # re.sub() interprets backslashes in JS code as regex escapes, corrupting the output
    html = html.replace(
        'src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.esm.js"',
        ""
    )

    # 5. Write standalone file
    Path(output_path).write_text(html)
    print(f"Standalone HTML: {output_path} ({Path(output_path).stat().st_size / 1024 / 1024:.1f}MB)")
```

**Key gotcha:** Use Python `str.replace()` instead of `re.sub()` when replacing content
that contains JavaScript. The `re.sub()` function interprets backslash sequences in the
replacement string as regex groups, which corrupts minified JS code.

Typical standalone file size: ~5MB for 8 slides with embedded PNG images.

Font errors from theme CSS (`@font-face` rules that reference external files) are cosmetic
only -- system fallback fonts render correctly.

### Step 7: Iterative Diagram Fixing

AI-generated diagrams typically need 2-3 iterations. Common issues and fixes:

| Issue                    | Fix Strategy                                           |
|--------------------------|--------------------------------------------------------|
| Wrong background color   | Re-prompt with explicit "#FFFFFF pure white, NOT cream" |
| Misspelled words         | Re-prompt spelling letter-by-letter: "V-A-L-I-D"       |
| Inconsistent sizing      | Add pixel dimensions to prompt: "1280x720"              |
| Wrong visual weight      | Compare side-by-side, adjust shadow/margin specs        |
| Missing elements         | Be more explicit; list every element by name            |

**Fix only broken slides, not all.** Regenerating everything wastes time and API quota.
Compare by opening slides side-by-side and checking visual weight and proportions.

### Step 8: Content Accuracy Review

Before finalizing slides, verify:

1. **Technical claims match actual behavior** -- do not overstate what a system does
2. **Use precise language:**
   - "monitors quality" (not "catches edge cases") if the system observes but does not prevent
   - "measures quality" (not "prevents bad data") if the system reports but does not block
3. **Screenshots must show real output** -- never mock up fake results
4. **Metrics must be reproducible** -- cite the source or test that produced them

## Verification

1. Open the HTML file in a browser and navigate through all slides with arrow keys
2. Check that all images load (no broken image icons)
3. Verify consistent styling: chapter numbers, fonts, colors match across slides
4. Check AI diagrams for misspellings, wrong backgrounds, or inconsistent card styles
5. Test standalone export by opening the single HTML file in a fresh browser (no server)
6. Verify text is readable at presentation distance (18px base is minimum)
7. Check that screenshots have consistent dimensions and styling
8. Confirm narrative flow reads as a coherent story from first to last slide

## Example

**Scenario**: Creating a VC pitch deck for a CrowdStrike OCSF data quality tool.

**Slide structure:**

```
slides/
  index.html          # Main Reveal.js presentation
  images/
    slide_01_problem.png
    slide_02_statusquo.png
    slide_03_trap.png
    slide_04_insight.png
    slide_05_architecture.png
    slide_06_demo_pass.png
    slide_06_demo_fail.png
    slide_07_comparison.png
    slide_08_quality.png
  generate_diagrams.py  # Batch Gemini generation script
  export_standalone.py  # Base64 embedding export script
```

**Example slide HTML:**

```html
<section>
    <div class="chapter-number">Chapter 1</div>
    <h2>The Problem</h2>
    <p class="subtitle">Security data pipelines break silently</p>
    <img src="images/slide_01_problem.png" class="slide-diagram" alt="Problem diagram">
    <div class="key-message">
        <strong>Bad OCSF data wastes analyst time and creates blind spots</strong>
    </div>
</section>
```

**Example Gemini prompt for a diagram:**

```text
Professional infographic style. Clean, modern, minimal.
Pure white background (#FFFFFF).
Card with subtle shadow and rounded corners.

Show a security data pipeline with 3 stages:
1. Left: "C-R-O-W-D-S-T-R-I-K-E (CrowdStrike)" source box in blue (#0066CC)
2. Middle: "O-C-S-F  M-A-P-P-I-N-G (OCSF Mapping)" transform box in amber (#FF8C00)
3. Right: "S-I-E-M (SIEM)" destination box in blue (#0066CC)

Red (#D32F2F) warning icon between stages 2 and 3 with label
"S-I-L-E-N-T  F-A-I-L-U-R-E (Silent Failure)"

Arrows connecting the boxes left to right.
16:9 landscape, 1280x720 pixels.
```

## Notes

- **Dark vs Light themes:** Light (`#FAFAFA`) is better for VC pitches, board meetings,
  and well-lit rooms. Dark themes work better for developer conferences and demo environments.

- **Font loading:** System fonts (`Inter`, `Segoe UI`, `system-ui`) load instantly with no
  FOUT. Avoid Google Fonts in standalone exports -- they require network access.

- **Image format:** PNG for diagrams with text (lossless). JPEG for photo screenshots if
  file size is a concern. WebP has inconsistent support in offline HTML viewers.

- **Slide count:** 8-12 slides is ideal for a 10-minute VC pitch. Each slide should be
  visible for 45-90 seconds.

- **Do NOT use `re.sub()` for JS replacement** in standalone export scripts. This is the
  single most common bug -- it silently corrupts the JavaScript and the presentation fails
  to initialize with no useful error message.

- **Rate limiting for Gemini:** 5-second delay between image generation calls prevents
  429 errors. For large batches (10+ images), increase to 8-10 seconds.

- **When NOT to use this skill:** For simple text-only slides, use Google Slides or Keynote
  instead. Reveal.js shines when you need custom CSS, embedded code, or programmatic
  generation. It is overkill for a 3-slide status update.

- **Related skills:**
  - `NANO-BANANA-SKILL.md` -- Gemini image generation (used for diagram creation)
  - `manim-particle-visualization` -- Animated presentations (different tool, animated not static)
  - `infographic-design.md` -- Static infographic design principles
