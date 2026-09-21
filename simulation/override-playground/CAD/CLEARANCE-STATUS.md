# Current assembly clearance findings

## Reachable-intake update — September 21

Current simulation CAD SHA256: `dcda446aacddc8348f7f60cc622357dd7be61a3a2787473cb7a9fea477f22b29`.

The coherent reachable-intake simulation copy passes two 2,715-pose native structural sweeps over the expanded lift/jaw range. A bounded exact audit of the new high-risk mounting/transmission interfaces records 8 pass, 0 fail and 4 unresolved complex tie/arm pairs. This does not supersede the full exact ledger below or turn unresolved pairs into passes. The original source CAD SHA256 remains `7a33d80ab9555b5ecf278acd6ca8075220f6aa73cab19dcad9d39dd5c44de5ab`.

The older full ledger below describes the previous simulation-CAD hash and remains preserved as historical failure evidence until a complete current-CAD rerun replaces it.

Exact solids at the selected maximum bounding-box-overlap pose for each pair. This is not a continuous clearance certificate or a mounting-connectivity check. A failed clearance target can mean either intersection or less than 1 mm clearance.

CAD SHA256: `1639641075bd35fd1212ff872cc2c46a5d7373af48132412fa10b2786293f7f2`

20 fail, 74 pass, 7 unresolved.

## Failed checks by mechanism

| Pair | Bodies | Parts | Intersection (mm³) | Minimum distance (mm) |
|---|---|---|---:|---:|
| 25 | lower0 / rear | I_channel2_27 / I_channel3_008 | 6.340 | 0.0000 |
| 26 | lower1 / rear | I_channel2_007 / I_channel3_008 | 6.340 | 0.0000 |
| 30 | lower1 / rear | I_channel2_009 / I_gear014 | 0.000 | 0.8800 |
| 42 | rear / upper1 | I_channel2_015 / I_channel2_011 | 115.813 | 0.0000 |
| 43 | rear / upper1 | I_channel2_015 / I_channel2_013 | 117.435 | 0.0000 |
| 10 | robot / lower0 | I_channel3_33 / I_channel2_27 | 475.474 | 0.0000 |
| 17 | robot / lower0 | I_channel3_002 / I_channel2_008 | 0.000 | 0.0000 |
| 11 | robot / lower1 | I_channel3_33 / I_channel2_007 | 471.468 | 0.0000 |
| 18 | robot / lower1 | I_channel3_002 / I_channel2_009 | 0.000 | 0.0000 |
| 13 | robot / upper0 | I_motor006 / I_channel2_012 | 0.000 | 0.0000 |
| 49 | upper0 / claw | I_channel2_010 / I_channel2_016 | 140.902 | 0.0000 |
| 50 | upper0 / claw | I_channel2_010 / I_channel2_017 | 27.473 | 0.0000 |
| 52 | upper0 / claw | I_channel2_010 / I_cylinder001 | 0.171 | 0.0000 |
| 58 | upper0 / claw | I_channel2_012 / I_channel2_15 | 140.902 | 0.0000 |
| 59 | upper0 / claw | I_channel2_012 / I_channel2_017 | 0.000 | 0.0000 |
| 53 | upper1 / claw | I_channel2_011 / I_channel2_016 | 98.762 | 0.0000 |
| 54 | upper1 / claw | I_channel2_011 / I_channel2_018 | 97.456 | 0.0000 |
| 61 | upper1 / claw | I_channel2_013 / I_channel2_15 | 98.762 | 0.0000 |
| 62 | upper1 / claw | I_channel2_013 / I_channel2_018 | 0.000 | 0.0000 |
| 96 | upper1 / claw | I_channel2_011 / I_cylinder001 | 70.218 | 0.0000 |

## Unresolved checks

14, 21, 24, 27, 29, 44, 55

Retain the original CAD and tested app. Any part spacing correction must also update its shafts, bearings, ties and fasteners before adoption; moving an isolated collider does not fix an assembly.
