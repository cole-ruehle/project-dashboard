# Codeville — City Design Plan
*Definitive reference for Three.js implementation*

---

## V1 Scope

**IN**: Roads, all district buildings, project buildings, future-slot ghost buildings,
trees, airport complex (runways, terminal, gates, tower), port water + docks, Central Park.
**OUT for v1**: Streetlights, parked cars, interior details, animated people.
**Future slots**: Rendered as semi-transparent gray placeholder structures.
**Runways**: East–West orientation confirmed.

---

## Coordinate System

```
         -z  NORTH  (screen top)
          |
  -x ─────┼───── +x   EAST (screen right)
 WEST     |
         +z  SOUTH  (screen bottom)

Camera: position (60, 60, 60)  ·  lookAt (10, 0, -5)
Isometric view from SE corner looking NW.
  Screen top-right  = NE (Airport)
  Screen top-left   = NW (Finance / Industrial)
  Screen bottom-left = SW (Port)
  Screen bottom-right = SE (Residential / Home)
```

---

## Road Network

### Primary Boulevards — 5 units wide, concrete `#B8B8B4`

| Name              | Axis | Position | Runs          |
|-------------------|------|----------|---------------|
| Western Blvd      | N–S  | x = −44  | z −55 → +50   |
| Finance Ave       | N–S  | x = −22  | z −55 → +44   |
| Central Ave       | N–S  | x =   0  | z −44 → +44   |
| Tech Ave          | N–S  | x = +22  | z −44 → +44   |
| Airport Pkwy      | N–S  | x = +44  | z −22 → +44   |
| East Bypass       | N–S  | x = +66  | z −55 → −22   |
| North Ring Rd     | E–W  | z = −44  | x −44 → +75   |
| Airport Blvd      | E–W  | z = −22  | x −44 → +75   |
| Main Street       | E–W  | z =   0  | x −55 → +66   |
| South Blvd        | E–W  | z = +22  | x −55 → +44   |
| Southern Ring     | E–W  | z = +44  | x −44 → +44   |

### Secondary Streets — 3 units wide, asphalt `#7A7A78`

| District    | Street                                         |
|-------------|------------------------------------------------|
| Finance     | x = −33 (N–S, z −44→−22)  ·  z = −33 (E–W, x −44→0) |
| CBD         | x = +11 (N–S, z −44→−22)                      |
| Entertain.  | z = +11 (E–W, x −44→−22)                      |
| Residential | x = +11 (N–S, z +22→+44)  ·  x = +33 (N–S)  ·  z = +33 (E–W, x −22→+44) |
| Tech        | z = +11 (E–W, x +22→+66)  ·  x = +55 (N–S, z −22→+22) |
| Port access | x = −44 (already boulevard)  ·  z = +33 (E–W, x −55→−22) |

### Road markings
- Centre-line dashes: 2.5 × 0.12, every 5 units, white `#FFFFFF`, polygonOffset −4
- Boulevard centre dashes: 3.0 × 0.14
- All markings at y = 0 with polygonOffset, no y-offset needed

---

## District Map

```
Block grid. Each cell ≈ 18 × 18 units. Block centres every 22 units.
Block centre columns: x = −55, −33, −11, +11, +33, +55
Block centre rows:    z = −55, −33, −11, +11, +33

          x=−55   x=−33   x=−11   x=+11   x=+33   x=+55   x=+77
z=−55   [  ···  ][  AIR  ][  AIR  ][  AIR  ][  AIR  ][  AIR  ][  ···  ]
         ───────────────── North Ring Rd  z=−44 ──────────────────────────
z=−33   [ IND   ][ FIN   ][ CBD   ][ CBD   ][ AIR-T ][ AIR-G ][ TWR   ]
         ─ West ──── Fin ─── Cent ──── Tech ──── Airport Pkwy ───────────
z=−11   [ IND   ][ ENT   ][ CIV   ][ CIV   ][ TCH   ][ TCH   ][  ···  ]
         ─────────────────── Main Street  z=0 ───────────────────────────
z=+11   [ ENT   ][ CLB★  ][ CIV   ][ TCH   ][ TCH   ][ FUT   ][  ···  ]
         ─────────────────── South Blvd  z=+22 ──────────────────────────
z=+33   [ PRT   ][ PRT   ][ RES   ][ RES   ][ HME★  ][ FUT   ][  ···  ]
         ─────────────────── Southern Ring z=+44 ──────────────────────────
z=+50   [ PRT   ][ PRT   ][ RES   ][ RES   ][  ···  ][  ···  ][  ···  ]

★ = current project building
AIR   = Airport complex        AIR-T = Airport terminal block
AIR-G = Airport gate apron     TWR   = Control tower + east apron
FIN   = Financial district     XCH   = Exchange (Prediction Market) ← inside FIN block
CBD   = Central Business Dist  IND   = Industrial
ENT   = Entertainment          CLB   = DJ Club ← inside ENT block
CIV   = Civic / Midtown        PRK   = Central Park ← inside CIV block
TCH   = Tech Campus            FUT   = Future project slots
RES   = Residential            HME   = Home ← inside RES block
PRT   = Port / Waterfront
```

---

## District Specifications

Each building listed with: **center position (x, z)** · **footprint w×d** · **height h** · **colors**.
Heights are in units (≈ 1 unit = 3 m).

---

### AIRPORT — Flight Finder ★

*Oslo-style: long barrel-vault terminal, glass-and-steel, clinical white/grey.*
**Zone**: x ∈ [20, 77]  ·  z ∈ [−22, −62]

#### Terminal Main Hall
- Center: (44, −32) · Footprint 40 × 10 · h 6
- Body: MeshStandard, south `#CDD8DE`, east `#C0CCD4`, top `#BDC8D0`
- Roof: 7 barrel-vault arches (CylinderGeometry r=2.5, len=5.6, thetaStart π×0.85, thetaLen π×1.3, rotated Z)
  Each arch at x = 26, 31.3, 36.6, 41.9, 47.2, 52.5, 57.8  ·  center z = −32  ·  y = 7.2
- South glass wall: 40 × 3 × 0.3, glassT `#BAE6FD` 70% opacity
- Entry canopy: 9 × 4 × 0.4 at (36, −23.5)  ·  y = 6.2  ·  steel `#94A3B8`
- Canopy posts: 2 × (0.3 × 0.3 × 6) at (31, −24.5) and (41, −24.5)

#### Airport Hotel (west end of terminal)
- Center: (24, −30) · Footprint 8 × 8 · h 12
- Color: cream `#E8D4B0` south, `#D9C8A4` east, `#EDE0C4` top
- Window rows: 4 floors × 3 windows each face (visual grid only, no actual geometry needed beyond color)
- Skybridge to terminal at y = 5: (29, −28.5)  ·  5 × 1.5 × 1.2

#### West Concourse
- Bridge: center (34, −26) · 16 × 2 · h 1.5 · y = 4.5 · steel `#C4CDD4`
- Gate Pier W1: center (27, −20) · 5 × 11 · h 4 · pier `#C8D4DA`
- Gate Pier W2: center (34, −20) · 5 × 11 · h 4
- Gate Pier W3: center (41, −20) · 5 × 11 · h 4
- Glass south wall on each pier: 5 × 0.3 · h 3 · glassT `#BAE6FD` 72% opacity · y = 1.5
- Aircraft at W1: fuselage (1 × 0.25 × 13), wings (18 × 0.25 × 1) center (27, −14) white `#F0F4F8`
- Aircraft at W2: same, center (34, −14)
- Aircraft at W3: same, center (41, −14)

#### East Concourse
- Bridge: center (58, −26) · 18 × 2 · h 1.5 · y = 4.5 · steel `#C4CDD4`
- Gate Pier E1: center (51, −20) · 5 × 11 · h 4 · pier `#C8D4DA`
- Gate Pier E2: center (58, −20) · 5 × 11 · h 4
- Gate Pier E3: center (65, −20) · 5 × 11 · h 4
- Glass + aircraft same spec as West Concourse

#### Control Tower
- Shaft: center (72, −30) · 2.5 × 2.5 · h 28 · sky-blue `#38BDF8`
- Obs ring: center (72, −30) · 6.5 × 6.5 · h 1.5 · y = 28.8 · light blue `#7DD3FC`
- Cab: 2.5 × 2.5 · h 1.4 · y = 30.5 · bright `#BAE6FD`
- Beacon sphere: r = 0.4 · y = 32.2 · red `#EF4444`

#### Apron & Tarmac
- Main apron: center (48, −34) · 55 × 14 · dark tarmac `#52555C`  (y=0, polygonOffset −1)
- East apron: center (60, −26) · 25 × 10 · same
- Taxiway A: center (34, −38) · 2.5 × 24 · tarmac + yellow CL dashes
- Taxiway B: center (54, −38) · 2.5 × 24 · same

#### Runway A
- Center (48, −50) · 56 × 5 · very dark `#404448`  (polygonOffset −1)
- Threshold bars (white 2 × 4): both ends at x = 21 and x = 75
- CL dashes: 2.8 × 0.18 every 4.5 units along x = 21→75

#### Runway B
- Center (48, −59) · 56 × 5 · same as A
- Same markings

#### Fuel Farm (NE corner)
- 4 cylindrical tanks, r = 1.8, h = 4, at (66, −42), (69, −42), (66, −45), (69, −45)
- Color: `#778899` with dark top cap
- Pipe connectors: thin boxes between them

#### Airport Perimeter Fence
- Continuous thin wall (0.15 × 1.8) along z = −62, x = 18 → 78
- Color: `#8A9BAA`
- Tree row: 8 trees at z = −63, x = 24, 30, 36, 42, 48, 54, 60, 66

---

### FINANCIAL DISTRICT

*Dense mid-rise to high-rise offices. Marble, dark glass, warm stone. 10–18h.*
**Zone**: x ∈ [−44, −22]  ·  z ∈ [−44, −22]

#### Exchange Building — Prediction Market ★
- Center: (−31, −33) · Footprint 11 × 7 · h 13
- Body: south `#8B5CF6`, east `#6D28D9`, top `#C4B5FD`
- 6 columns south face: CylinderGeometry r=0.38, h=11, at x=−34.5→−27.5 evenly spaced · `#A78BFA`
- Pediment: 12 × 0.6 × 1.8 at y = 13.3 · `#DDD6FE`
- Steps (2 risers): 12 × 0.35 × 2 at y=0.18, z=−29 and 12 × 0.35 × 1 at y=0.55, z=−29.6
- Side wings: 4 × 5 × 9 at (−37, −33) and (−25, −33) · matching colors
- Rooftop parapet: 11.4 × 0.5 × 0.4 at y=13 · `#C4B5FD`

#### North Capital Tower
- Center: (−36, −39) · 5 × 5 · h 17 · slate `#4B5563` / `#374151` / `#6B7280` (S/E/top)

#### Meridian House
- Center: (−36, −28) · 6 × 5 · h 13 · sandstone `#B08D57` / `#92703F` / `#C4A572`

#### Atlas Building
- Center: (−25, −39) · 5 × 5 · h 15 · dark glass `#1E3A5F` / `#162D4A` / `#2563EB` tinted top

#### Prospect Tower
- Center: (−25, −28) · 5 × 5 · h 11 · steel blue `#3B82F6` / `#2563EB` / `#93C5FD`

#### Finance Fill (4 smaller buildings between above)
- (−31, −39): 5 × 5 · h 9 · `#64748B`
- (−31, −28): 5 × 5 · h 8 · `#64748B`
- (−36, −33): 5 × 4 · h 6 · `#94A3B8`  ← parking podium
- (−25, −33): 4 × 4 · h 7 · `#94A3B8`

#### Finance Trees
- Row along z = −44 boundary: 5 trees at x = −42, −38, −34, −30, −26
- Planters in plaza between Exchange and towers

---

### CENTRAL BUSINESS DISTRICT (CBD)

*City's tallest buildings. Glass and concrete. 12–24h.*
**Zone**: x ∈ [−22, +22]  ·  z ∈ [−44, −22]

#### Pinnacle Tower (tallest)
- Center: (−5, −36) · 5 × 5 · h 24 · glass-blue `#1D4ED8` / `#1E40AF` / `#60A5FA`
- Spire: CylinderGeometry r 0.4→0, h 4 at y = 24 · `#93C5FD`

#### Meridian Plaza
- Center: (+8, −36) · 6 × 6 · h 20 · charcoal `#1F2937` / `#111827` / `#374151`
- Glass band top 30%: 6 × 6 · h 6 at y = 16 · glassT `#93C5FD` 80% opacity

#### Commerce Centre
- Center: (+8, −28) · 7 × 5 · h 16 · steel `#374151` / `#1F2937` / `#4B5563`

#### Exchange Annex
- Center: (−5, −28) · 8 × 5 · h 13 · warm gray `#9CA3AF` / `#6B7280` / `#D1D5DB`

#### East Tower
- Center: (−5, −42) · 5 × 5 · h 18 · teal glass `#0F766E` / `#0D9488` / `#5EEAD4`

#### Mid-block fill (airport-facing z ≈ −23)
- 5 buildings along z = −23, x = −18, −10, −2, +6, +14 · each 5 × 4 · h 6–10 (varied)
- Colors: gray palette `#6B7280`, `#9CA3AF`, `#78909C`

#### Reflecting Pool / Plaza
- Ground feature at (2, −32): 6 × 4 flat water `#1D4ED8` 60% opacity · y = 0.1

---

### INDUSTRIAL DISTRICT

*Factories, warehouses. Utilitarian. Red brick, corrugated metal. 5–8h.*
**Zone**: x ∈ [−60, −44]  ·  z ∈ [−44, 0]

#### Factory A (large)
- Center: (−52, −38) · 14 × 10 · h 7 · dark brick `#78350F` / `#6B2D0B` / `#92400E`
- Sawtooth roof profile: 3 ridge boxes 14 × 0.5 × 0.5 at y=7.5, 8, 8.5 stepped
- Smokestack: CylinderGeometry r=0.9→0.7, h=15 at (−48, −38) · `#57534E`

#### Factory B (medium)
- Center: (−52, −28) · 10 × 8 · h 6 · corrugated `#71717A` / `#52525B` / `#A1A1AA`
- Smokestack: r=0.7, h=12 at (−50, −25) · `#57534E`

#### Warehouse Row (3 units)
- W1: (−52, −16) · 12 × 7 · h 5 · `#78716C` / `#57534E` / `#A8A29E`
- W2: (−52, −8) · 12 × 7 · h 5 · `#6B7280` / `#4B5563` / `#9CA3AF`
- W3: (−48, −38) · 8 × 6 · h 4 · `#92400E` / `#78350F` / `#B45309`  ← next to stack

#### Rail Yard
- Rail tracks: 3 × 0.15 pairs running E–W at z = −20, x = −58→−44 · dark `#374151`
- 2 boxcar shapes: 6 × 2.5 × 2.5 at (−55, −20) and (−50, −20) · red `#DC2626` / blue `#1D4ED8`

#### Industrial perimeter
- Low chain-link fence suggestion: thin wall 0.1 × 1.5 along x = −44 boundary

---

### ENTERTAINMENT QUARTER

*Bars, clubs, theaters. Warm, colorful, 3–8h. Street-level life.*
**Zone**: x ∈ [−44, −22]  ·  z ∈ [−22, +22]

#### DJ Club — DJ Website ★ (anchor building)
- Center: (−31, +11) · Footprint 9 × 7 · h 12
- Body: south `#EC4899`, east `#BE185D`, top `#F9A8D4`
- Art deco vertical fins (8): each 0.35 × 0.5 × 12, evenly across south face, color `#BE185D`
- Marquee canopy: 10 × 2.5 × 0.45 at y = 8 · `#F472B6`
- Sign panel: 4.5 × 1.3 × 0.2 at y = 7 · warm `#FDE68A` (acts as lit sign)
- Arched entrance: 2 × 3.5 × 0.2 at y = 1.75 · `#831843`
- Corner neon tubes: 4 × (0.15 × 0.15 × 12) at corners · magenta `#FF00AA`
- Side windows: 2 × tall boxes cut 1 × 3 per side face (visual, not actual hole)

#### Grand Theater
- Center: (−36, −5) · 10 × 8 · h 9 · burgundy `#7F1D1D` / `#6B1414` / `#991B1B`
- Arched facade: 3 arch outlines in lighter `#B91C1C` on south face (box strips)
- Marquee: 11 × 2 × 0.4 at y = 5.5 · `#C2410C`

#### Food Hall
- Center: (−36, +5) · 9 × 6 · h 5 · terracotta `#C2410C` / `#9A3412` / `#EA580C`
- Awning: 9.5 × 2 × 0.3 at y = 4 · `#F97316`

#### Neon Row (entertainment strip along z = +11 secondary street)
- Bar A: (−42, +11) · 6 × 5 · h 5 · coral `#F87171` / `#DC2626`
- Bar B: (−38, +11) · 5 × 5 · h 6 · amber `#F59E0B` / `#D97706`
- Lounge: (−34, +11) · 5 × 5 · h 4 · lime `#4ADE80` / `#16A34A`
- Bar C: (−25, +11) · 6 × 5 · h 5 · sky `#38BDF8` / `#0284C7`
- Bar D: (−25, +1)  · 6 × 5 · h 4 · violet `#A78BFA` / `#7C3AED`

#### Entertainment fill
- 6 small buildings 3–5h scattered throughout zone, warm/bright colors, varied widths 4–7
- Trees along z = +11 pedestrian strip (6 trees)
- 3 trees at corner of Western Blvd and Main St

---

### CIVIC & MIDTOWN

*Public buildings + Central Park. Open, lower density. Cream, stone, glass. 4–10h.*
**Zone**: x ∈ [−22, +22]  ·  z ∈ [−22, +22]

#### City Hall
- Center: (0, +8) · 12 × 9 · h 9 · cream `#FEF9C3` / `#FEF08A` / `#FDE047`
- Portico: 4 columns (r=0.5, h=8) across south face at y=0 · `#FEFCE8`
- Dome: SphereGeometry r=2, half-sphere at y=9 · `#EAB308`
- Steps: 13 × 0.35 × 3 at y=0.2 z=3

#### Central Library
- Center: (+12, +5) · 9 × 7 · h 7 · warm stone `#D6B896` / `#B8966E` / `#E8CCA8`
- Colonnade: 3 columns south face r=0.45, h=6 · `#E8CCA8`
- Sign lintel: 9 × 0.5 × 0.3 at y=7 · `#C4A572`

#### Art Museum
- Center: (−14, +5) · 14 × 9 · h 6 · modern white `#F1F5F9` / `#E2E8F0` / `#F8FAFC`
- Wide, low, contemporary form
- Glass strip along south: 14 × 3 × 0.25 at y=1.5 · glassT 75% opacity
- Skylight boxes: 3 × (3 × 2 × 0.3) on roof at y=6.3

#### Central Park
- Grass area: x ∈ [−14, −2] · z ∈ [+14, +22] · bright grass `#5BBF4A` · polygonOffset −2
- Fountain: CylinderGeometry r=2, h=0.4 at (−8, +17) · water blue `#38BDF8`
- Fountain spray: r=0.3, h=1.5 atop · `#BAE6FD`
- Trees: 8 trees scattered in park
- Path: 2-unit wide gray strips through park

#### Civic fill
- Hospital (+11, −14) · 10 × 7 · h 9 · white `#F8FAFC` / `#E2E8F0` · red cross on roof
- Mixed retail row: 4 buildings at z = +18, x = −22→−8 · each 5 × 4 · h 4 · warm varied

---

### TECH CAMPUS

*Modern campus architecture. Glass, white, minimal. 6–14h.*
**Zone**: x ∈ [+22, +66]  ·  z ∈ [−22, +22]

#### Campus Green
- Manicured grass: x ∈ [+24, +54] · z ∈ [−4, +10] · bright `#6DB855` · polygonOffset −2
- 10 trees arranged in avenue rows
- Path network: 1.5-unit wide light `#D4CEC8`

#### FUTURE SLOT 1 — Campus HQ A
- Center: (+33, −5) · 8 × 7 · h 10 · ghost: `#C8D4DC` 50% opacity
- Style when occupied: glass tower, minimal, bright accent at top

#### FUTURE SLOT 2 — Campus HQ B
- Center: (+50, −5) · 7 × 6 · h 13 · ghost: `#C8D4DC` 50% opacity
- Style: slab tower with horizontal bands

#### FUTURE SLOT 3 — Research Lab
- Center: (+50, +11) · 9 × 8 · h 7 · ghost: `#C8D4DC` 50% opacity
- Style: low wide campus pavilion, heavy glass

#### FUTURE SLOT 4 — Tech Annex
- Center: (+33, +11) · 7 × 7 · h 9 · ghost: `#C8D4DC` 50% opacity

#### Campus Cafe (permanent)
- Center: (+41, +3) · 6 × 5 · h 3 · warm glass `#FED7AA` south · `#FDBA74` east · `#FFF7ED` top
- Patio: 6 × 4 at (+41, −1.5) · same ground as campus green

---

### RESIDENTIAL DISTRICT

*Houses, low apartments, gardens. Warm palette, 2–6h. Organic feel.*
**Zone**: x ∈ [−22, +44]  ·  z ∈ [+22, +50]

#### Home — Personal Website ★
- Center: (+33, +33) · Footprint 9 × 7 · h 7
- Body: south `#10B981`, east `#059669`, top `#A7F3D0`
- Chimney: 1.2 × 1.2 · h 4 at (+36, +30) · y = 5 · `#9CA3AF`
- Roof ridge accent: 9.4 × 0.5 × 7.4 at y = 7.3 · `#6EE7B7`
- Garage: 4.5 × 4.5 · h 4.5 at (+38, +33) · `#059669`
- Front porch canopy: 3.5 × 2 × 0.35 at y = 5 · `#A7F3D0`
- Garden fence: white pickets 0.2 × 1.2 × 0.2 every 1.5u along south face
- 3 garden trees surrounding
- Driveway: 2.5 × 6 at (+38, +37) · light `#D1D5DB`

#### Townhouse Row West
- 4 buildings at z = +29, x = +5, +11, +17, +23 · each 5 × 6 · h 6
- Colors: cream `#FEF3C7`, sage `#BBF7D0`, terracotta `#FECACA`, beige `#FEF9EE`

#### Townhouse Row East
- 4 buildings at z = +29, x = +39, +44, +49 · each 5 × 6 · h 5
- Colors: warm varied

#### Apartment Blocks (south of Home)
- A1: (+11, +40) · 8 × 7 · h 8 · `#DDE2F0` / `#C9D1E8`
- A2: (+22, +40) · 7 × 6 · h 6 · `#D4E4D4` / `#B8D4B8`
- A3: (+11, +29) · 7 × 6 · h 5 · `#F0E4D4` / `#E4D0B8`

#### Corner Houses
- H1: (−5, +29) · 6 × 5 · h 4 · `#FDE68A` / `#FCD34D`
- H2: (−5, +40) · 6 × 5 · h 4 · `#DDD6FE` / `#C4B5FD`
- H3: (+1, +29) · 5 × 5 · h 5 · `#FCA5A5` / `#F87171`

#### Residential Trees
- 14 trees distributed through district, 3 per street block
- Small park at (+17, +35) · 5 × 5 grass area with 2 trees

---

### PORT & WATERFRONT

*Bottom-left of the city (SW screen corner). Harbor, docks, containers, cranes.*
*Geographic read: city sits on a river/bay with port to the south-west.*
**Zone**: x ∈ [−60, −22]  ·  z ∈ [+22, +55]

#### Water Plane
- Flat mesh: x ∈ [−62, −22] · z ∈ [+23, +57] · y = −0.5
- Color: deep harbor `#1E3A6E` · slight transparency 90% · polygonOffset +5 (renders below ground edges)

#### Main Dock Platform
- Long concrete dock: x ∈ [−58, −24] · z = +26 · 2 units wide · h 0.8 · `#9CA3AF`
- Dock face wall: same width · h 1.2 · `#6B7280`

#### Warehouse A (dockside)
- Center: (−50, +30) · 15 × 8 · h 6 · `#78716C` / `#57534E` / `#A8A29E`

#### Warehouse B
- Center: (−36, +30) · 12 × 8 · h 5 · `#6B7280` / `#4B5563` / `#9CA3AF`

#### Crane A
- Base: 2 × 2 · h 16 at (−54, +26) · `#374151`
- Horizontal arm: 12 × 1 · h 1 at y = 16 · same
- Cable guide: thin 0.3 × 0.3 · h 5 hanging at arm end

#### Crane B
- Same spec at (−40, +26)

#### Container Stack A (west)
- 5 containers: each 5 × 2 · h 2.5, stacked 2-high at (−53, +36) → (−49, +36)
- Colors: red `#DC2626`, blue `#1D4ED8`, orange `#EA580C`, green `#16A34A`, yellow `#CA8A04`

#### Container Stack B (east)
- 4 containers stacked at (−33, +36) · 2 layers
- Colors varied

#### Port Office Building
- Center: (−26, +30) · 7 × 6 · h 8 · blue-gray `#334155` / `#1E293B` / `#475569`
- Port authority: windows, flagpole suggestion

#### Fishing/Small Boat Docks
- 3 boat shapes (6 × 2 × 1) at z = +30, x = −56, −52, −48 · white `#F1F5F9`
- Dock fingers: thin boards 0.8 × 5 × 0.3 perpendicular to main dock

#### Port Trees / Perimeter
- 4 trees along x = −22 boundary
- Sparse industrial landscaping

---

## Tree Placement Summary

Trees use 2-tier cone (ConeGeometry) + cylinder trunk. Scale varies 0.7–1.0.

| Location                        | Count | Scale |
|---------------------------------|-------|-------|
| Airport perimeter (z = −63)     |   8   | 0.70  |
| Finance district (street edge)  |   8   | 0.80  |
| CBD plaza (reflecting pool area)|   4   | 0.85  |
| Entertainment pedestrian strip  |   6   | 0.75  |
| Central Park                    |   8   | 0.90  |
| Industrial (sparse)             |   3   | 0.70  |
| Tech campus avenue rows         |  10   | 0.85  |
| Residential district            |  14   | 0.80  |
| Home garden                     |   3   | 0.80  |
| Port perimeter                  |   4   | 0.70  |
| **Total**                       | **68**|       |

---

## Future Project Slots — Ghost Buildings

Rendered with `transparent: true, opacity: 0.45, color: #C8D4DC`.
When a project is assigned, the ghost is replaced with the actual themed building.

| Slot | Center (x, z) | Dims     | h  | Suggested Theme        |
|------|---------------|----------|----|------------------------|
| 1    | (+33, −5)     | 8 × 7    | 10 | Tech glass tower       |
| 2    | (+50, −5)     | 7 × 6    | 13 | Slab tower w/ bands    |
| 3    | (+50, +11)    | 9 × 8    |  7 | Low campus pavilion    |
| 4    | (+33, +11)    | 7 × 7    |  9 | Tech annex             |
| 5    | (−36, −38)    | 5 × 5    | 16 | Finance tower          |
| 6    | (−25, −44)    | 5 × 5    | 12 | Finance annex          |
| 7    | (−52, −8)     | 10 × 7   |  5 | Industrial / factory   |
| 8    | (+22, +33)    | 7 × 6    |  5 | Residential landmark   |

---

## Material Constants

```javascript
// Ground layers (polygonOffset prevents z-fighting)
grass    #6DB855  roughness 0.88  metalness 0.02  polygonOffset factor +2
road     #B0B0B0  roughness 0.82  metalness 0.06  polygonOffset factor −1
sidewalk #D4CEC8  roughness 0.82  metalness 0.06  polygonOffset factor −1
tarmac   #52555C  roughness 0.95  metalness 0.04  polygonOffset factor −1
runway   #404448  roughness 0.95  metalness 0.02  polygonOffset factor −1
marking  #FFFFFF  roughness 0.90  metalness 0.00  polygonOffset factor −4
yellow   #F0C030  roughness 0.90  metalness 0.00  polygonOffset factor −4

// Glass
glassT: color #BAE6FD  roughness 0.10  metalness 0.35  transparent true  opacity 0.72

// Ghost (future slots)
ghost:  color #C8D4DC  roughness 0.80  metalness 0.05  transparent true  opacity 0.45

// Lighting
AmbientLight  0xCCDDFF  intensity 1.1
DirectionalLight (sun)  0xFFF5E0  intensity 2.6  pos (40, 70, 30)  castShadow  mapSize 4096
DirectionalLight (fill) 0xAABBFF  intensity 0.5  pos (−30, 25, −15)
```

---

## Implementation Order

Build in this sequence — each step is a visible checkpoint.

1. **Road grid** — all boulevards + secondary streets + markings
2. **Ground zones** — district-tinted grass patches, tarmac, water plane
3. **Airport** — terminal body → barrel-vault arches → concourses → runways → tower
4. **Exchange** — columns, pediment, wings
5. **CBD towers** — Pinnacle → Meridian → fill
6. **DJ Club** — body, fins, marquee, neon corners
7. **Home** — body, chimney, garage, fence, garden
8. **City Hall + Library + Museum** — civic district
9. **Finance fill** — 4 towers + small fill
10. **Industrial** — 2 factories + warehouses + stacks + rail
11. **Entertainment** — theater, food hall, neon row, fill
12. **Tech campus** — green, ghost slots, cafe
13. **Residential** — townhouse rows, apartments, corner houses
14. **Port** — water plane, dock, warehouses, cranes, containers
15. **Trees** — all 68, seeded random variation
16. **Central Park** — grass patch, fountain, paths
17. **Labels + status** — HTML overlay tracked to building centers
18. **Camera** — center on (10, 0, −5), zoom 0.9
