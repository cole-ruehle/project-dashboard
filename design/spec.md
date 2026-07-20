# Project Dashboard — City Map Design Spec

## Concept

Replace the card-based dashboard with an **interactive isometric city map**. Each project is
a unique themed 3D building. Clicking a building opens the project. The scene sits on a
bright daytime sky — deliberately light and playful, contrasting with every other tool in
the stack.

---

## Visual Style

| Property | Value |
|----------|-------|
| Projection | 2:1 isometric (standard), SVG polygon-based — no 3D library |
| Background | Day-sky gradient `#78C5E8 → #D9EFFC` with clouds and sun |
| Ground | Green grass tiles + gray road intersection, white dashed center lines |
| Outlines | Bold dark stroke `#2c2c2c`, 1.8px on all building faces |
| Feel | Google Maps cartoon × Nintendo city × developer tool |

---

## Scene Layout

```
          NW                    NE
    ┌──────────────┬─────────────────┐
    │  Prediction  │  Flight Finder  │
    │    Market    │  (Airport+Tower)│
    │  (Exchange)  │                 │
    ├──────────────┼─────────────────┤
    │  DJ Website  │ Personal Website│
    │    (Club)    │    (Home)       │
    └──────────────┴─────────────────┘
                  ↑
          Road intersection
```

Grid: 9 cols × 7 rows. Road at col 4 (e-axis) and row 3 (n-axis).

---

## Buildings

### 1. Flight Finder → Airport
- **Form**: Wide flat terminal (3w × 2d × 2h) + control tower (1w × 1d × 7h)
- **Colors**: Amber terminal (`#FBBF24` south · `#FDE68A` top · `#D97706` east), sky-blue tower (`#38BDF8`)
- **Details**: Horizontal window strip, blue glass band on terminal; observation band ring on tower
- **Grid**: `e=5, n=0`

### 2. Prediction Market → Exchange
- **Form**: Classical building (3w × 2d × 4h) with columns + pediment
- **Colors**: Indigo/violet (`#8B5CF6` south · `#C4B5FD` top · `#6D28D9` east)
- **Details**: 4 columns on south face, triangular pediment above columns, grid of windows
- **Grid**: `e=0, n=0`

### 3. DJ Website → Music Hall / Club
- **Form**: Art deco (3w × 2d × 4h)
- **Colors**: Hot pink (`#EC4899` south · `#F9A8D4` top · `#BE185D` east)
- **Details**: Awning stripe, arched door, `♪ LIVE ♪` sign text, windows
- **Grid**: `e=0, n=4`

### 4. Personal Website → Home
- **Form**: Residential (3w × 2d × 3h) with chimney
- **Colors**: Emerald (`#10B981` south · `#A7F3D0` top · `#059669` east)
- **Details**: Front door, windows, chimney rising above roofline, roof edge accent strip
- **Grid**: `e=5, n=4`

---

## Status States

| `status` field | Visual |
|----------------|--------|
| `running` | Full brightness, warm-yellow lit windows, **green dot** on label |
| `no_dockerfile` | 75% opacity, orange construction barrier prop in front of door, **orange dot** |
| `build_failed` | Gray-tinted, red warning sign prop, **red dot** |
| `clone_failed` | Same as build_failed |

---

## Interaction

- **Hover**: Group lifts `translateY(-4px)` with `transition: transform 150ms ease`; brightness 1.1
- **Click (running)**: Opens `http://<host>:<port>` in new tab
- **Click (not running)**: Shows tooltip explaining what to do (e.g. "Add a Dockerfile, then re-run setup.py")
- **Title card**: Top-left overlay — project count, how many are running

---

## Extending: Adding New Projects

Add a `building` field to each entry in `repos.json` to pick the building type:

```json
{
  "name": "new-project",
  "label": "New Project",
  "building": "exchange",
  "git_url": "https://github.com/...",
  "port": 3009
}
```

Available types: `airport`, `exchange`, `club`, `home`
(more can be added — factory, library, cafe, etc.)

---

## Implementation Approach

- Single SVG with JS-generated polygons (no canvas, no Three.js, no dependencies)
- Painter's algorithm: sort all elements by `e + n` ascending before drawing
- Isometric formula: `pt(e, n, u) = [OX + (e−n)×TW, OY + (e+n)×TH − u×FH]`
  where `TW=44, TH=22, FH=28, OX=450, OY=205`
- GPU animation: `will-change: transform` on building `<g>` elements
- Fully responsive: SVG `viewBox` scales to any width
- Data source: unchanged `projects.json` written by `setup.py`
