---
name: manim-particle-visualization
description: |
  Create animated particle effects in Manim for data flow visualization. Use when:
  (1) building animated technical presentations showing data moving through pipelines,
  (2) need glowing dot effects with opacity trails, (3) visualizing processing steps
  with particles crawling along paths, (4) creating professional-looking data flow
  animations. Covers particle creation with glow, path animation, and timing patterns.
author: Claude Code
version: 1.0.0
date: 2026-01-25
---

# Manim Particle Visualization

## Problem
Creating visually compelling data flow animations in Manim requires combining multiple
techniques: glowing particles, smooth path following, and proper timing. The default
Manim primitives look flat without glow effects.

## Context / Trigger Conditions
- Building technical demo animations with Manim
- Need to show data flowing through a pipeline or architecture
- Want professional-looking particle effects (not just moving dots)
- Creating presentations for executives or conferences

## Solution

### 1. Create Glowing Particles

```python
def create_data_particle(color="#00d4ff", size=0.08):
    """Creates a glowing dot with outer halo."""
    dot = Dot(radius=size, color=color)
    glow = Dot(radius=size * 2.5, color=color, fill_opacity=0.3)
    return VGroup(glow, dot)
```

### 2. Animate Along Path

```python
# Create nodes
nodes = [Circle(radius=0.3).move_to(pos) for pos in positions]

# Create path between nodes
path = VMobject()
path.set_points_smoothly([n.get_center() for n in nodes])

# Animate particle along path
particle = create_data_particle()
particle.move_to(path.get_start())
self.play(MoveAlongPath(particle, path, run_time=3))
```

### 3. Particle with Progress Tracking

```python
# Add progress bar and timer
progress = ValueTracker(0)
timer_text = always_redraw(
    lambda: Text(f"{progress.get_value():.1f}s", font_size=24)
)
progress_bar = always_redraw(
    lambda: Rectangle(width=4 * progress.get_value() / 21, height=0.1)
)

# Animate together
self.play(
    MoveAlongPath(particle, path),
    progress.animate.set_value(21),
    run_time=3
)
```

### 4. Multiple Ambient Particles

```python
def create_ambient_particles(self, count=15, color="#00d4ff"):
    """Create background particles that drift randomly."""
    particles = VGroup()
    for _ in range(count):
        p = create_data_particle(color, size=0.04)
        p.move_to([
            np.random.uniform(-6, 6),
            np.random.uniform(-3, 3),
            0
        ])
        particles.add(p)
    return particles

# Animate with random drift
for p in particles:
    self.play(
        p.animate.shift([
            np.random.uniform(-0.5, 0.5),
            np.random.uniform(-0.5, 0.5),
            0
        ]),
        run_time=0.3,
        rate_func=smooth
    )
```

### 5. Timing with BEAT Constant

Use a base timing unit for consistent rhythm:

```python
BEAT = 1.0  # Base rhythm unit

# Use multiples for timing
self.wait(BEAT * 0.5)      # Short pause
self.play(..., run_time=BEAT)  # Standard animation
self.wait(BEAT * 2)        # Longer pause for emphasis
```

## Verification
- Particles should have visible glow (outer ring at 30% opacity)
- Movement should be smooth, not jerky
- Render with `manim -ql` for quick preview, `-qm` for 720p30

## Example

Complete scene with particle flowing through 3-node pipeline:

```python
class PipelineFlow(Scene):
    def construct(self):
        CYAN = "#00d4ff"

        # Create nodes
        nodes = VGroup(*[
            Circle(radius=0.4, color=CYAN, stroke_width=2)
            for _ in range(3)
        ]).arrange(RIGHT, buff=2)

        # Labels
        labels = VGroup(*[
            Text(name, font_size=20, color=CYAN).next_to(node, DOWN)
            for node, name in zip(nodes, ["Parse", "Transform", "Output"])
        ])

        self.play(Create(nodes), Write(labels))

        # Create path
        path = VMobject()
        path.set_points_smoothly([n.get_center() for n in nodes])

        # Particle with glow
        dot = Dot(radius=0.1, color=CYAN)
        glow = Dot(radius=0.25, color=CYAN, fill_opacity=0.3)
        particle = VGroup(glow, dot).move_to(path.get_start())

        self.play(FadeIn(particle))
        self.play(MoveAlongPath(particle, path, run_time=2))
        self.play(FadeOut(particle))
```

## Notes
- Glow opacity of 0.3 works well on dark backgrounds (#0a0a12)
- For light backgrounds, reduce glow opacity to 0.15-0.2
- Size ratio of 2.5x (glow to dot) provides good visual balance
- Use `rate_func=smooth` for natural-feeling movement
- For racing/comparison animations, use `rate_func=linear` for predictable timing

## References
- [Manim Community Documentation](https://docs.manim.community/)
- [Manim MoveAlongPath](https://docs.manim.community/en/stable/reference/manim.animation.movement.MoveAlongPath.html)
