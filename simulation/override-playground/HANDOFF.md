# Override playground continuation — current state

Work in `/Users/kamachi/Documents/OverridePlayground`. User's priorities: smooth M2 / 16 GB performance, credible real contact behavior, reuse existing solutions before new implementation. No audio/volume changes, CAD uploads, publication, or cleanup are authorized by this continuation. User's original robot `/Users/kamachi/Downloads/RatchetingClaw.FCStd` remains unchanged.

## Current application

`Builds/Override Playground.app` is an Apple Silicon Unity 6000.6.2f1 renderer with native MuJoCo 3.3.7 physics. The application **has now been launched and visually inspected**, after finding and fixing an underground camera. Latest build: `Evidence/build8.log`, `PLAYGROUND_BUILD_SUCCESS`. `README.md` contains controls. Main entry points: `Unity/Assets/Scripts/Playground.cs`, `Tools/bridge.c`, `Tools/generate_model.py`.

Three practice layouts: claw pickup, loose-piece pile, stack/release. 12 pins, six cups, three practice pegs; not the complete official field or a scoring simulator. Robot geometry retains the existing 238 included CAD parts / 34 simplified meshes. No proprietary xRC geometry is used.

Keyboard: WASD/arrows drive; Q/E lower/raise; Z/X close/open; F/G intake/reverse; R reset; Space pause; 1/2/3 overview/follow/top; F1/F2/F3 layouts; T demo; Escape stop demo; H help. Right-drag/scroll orbit/zoom. Keyboard layout/demo access was added because automated native mouse input was unreliable. Follow shortcut now changes zoom consistently with its button; top view fits the field to viewport aspect.

For a centered pin: start/reset layout 0, hold Z+F for approximately one second, release, raise with E, then open with X. Native tests retained a pin about 0.40 m above its initial position for five seconds before release. Do not generalize that to cups or hardware.

## Evidence and tests

- `Evidence/native-validation.json`: 30 simulated seconds in each of three layouts; finite states, zero BADQACC/BADQPOS warnings; forward/reverse displacement and lift/jaw motion assertions passed. `Tools/validate_runtime.py` reproduces these checks.
- `Evidence/grip-validation.json`: contact-only centered and ±10 mm pin pickup/5-second hold/release passed with rollers during closure. Centered cup retention FAILED. `Evidence/grip-no-rollers.json`: centered pin closure without rollers failed. `Tools/check_grip.py` reproduces current contact fixtures; placement happens only before stepping, never via attachment/weld.
- `Evidence/verified-scene0`, `verified-scene1`, `verified-scene2`: separate 65-second graphics runs at 1280×820, no overlapping simulator/build workloads. `Evidence/final-benchmarks.json` consolidates completed runs. `Tools/benchmark.py` reproduces them.
- `Evidence/final-scene*` is superseded: Unity's first frame included loading time, incorrectly advancing the simulation and causing artificial startup backlog. Fixed by starting stepping and an independent stopwatch at the first Update. Keep evidence, but do not use those runs as final benchmarks.
- `Evidence/baseline` was the original underground-camera run. `Evidence/corrected` was the first visible build, before final camera/control fixes. Neither replaces the final three-layout benchmark.

## Physics limitations

Actual total/component masses, inertias, friction, motor count/cartridges/ports, pneumatics and ratchet coupling remain unknown. Read `/Users/kamachi/Downloads/169C_Simulation_Handoff/` for authoritative model-supported facts and unknowns. Six modeled drive motors are not confirmation of a competition-legal hardware allocation.

Drive now adapts ftcsim's MIT finite linear torque-speed/braking equation, with provisional 600 RPM V5 cartridge, 60/36 reduction and 0.8 transmission efficiency: 0.4667 Nm wheel stall limit and 360 RPM ideal wheel speed. VEX's 2.1 Nm figure is for 100 RPM. Firmware control/current/power/thermal behavior is not emulated.

Lift still sags approximately 0.10 rad from the upper target. It uses constrained approximate linkage and torque-limited position control. Independent jaw/roller actuators are provisional; actual ratchet/pneumatic coupling is not implemented. Some robot self-collisions are disabled. Cup grip currently fails; do not increase friction or invent attachment behavior merely to force a passing result.

## Reused assets and baseline

Read `Research/REUSE_AUDIT.md` and `THIRD_PARTY.md` before new research or platform changes.

- xRC 20.3a remains at `Research/xRC/xRC Simulator.app`. Animated Override menu was inspected after reopening. Automated Single Player/Settings actions did not enter a session; later Computer Use clicks returned `windowNotFoundAtPosition`. Keyboard quit worked. **No xRC gameplay performance/physics comparison was completed.** This is an automation blocker, not a verdict on xRC. Audio/volume were untouched. xRC remains the ready-made full-game candidate; no supported custom-robot import is established.
- Jerry Lum GPL-3 geometry at commit `572085f57dcedb501d781db6c5485349beb887cf` is now integrated. `Tools/reuse_pieces.py` applies GLB graph transforms, exports material groups, and creates eight convex pin slices preserving the hex flange. Scene pin height 165 mm matches the official drawing within 0.1 mm. Full license and source attribution are bundled in StreamingAssets/ReusedPieces. Cup visuals are reused, but hollow wall collision thickness remains provisional.
- ftcsim motor model at commit `b5ec647e2991faf56dbaa3407b25d9a59d9ea09a` is adapted with MIT notice in Research/ftcsim-LICENSE. No unlicensed Bowler code or proprietary xRC assets were copied.
- Synthesis/Fusion/Jolt and other alternatives were previously evaluated; see audit. No evidence establishes a platform switch as an improvement.

## Build and next work

Unity: `/Applications/Unity/Hub/Editor/6000.6.2f1/Unity.app/Contents/MacOS/Unity`. Python: `.venv/bin/python`. Native rebuild: `zsh Tools/build_native.sh`. Preserve dylib install names/ad-hoc signing. Build with `-batchmode -nographics -projectPath /Users/kamachi/Documents/OverridePlayground/Unity -executeMethod BuildPlayground.Build -quit -logFile <new path>`.

Useful next work: diagnose cup retention from model-supported geometry and measured contact inputs; resolve real actuator/ratchet behavior; complete xRC baseline interaction with functioning UI input; obtain hardware measurements and full official geometry before realism/scoring claims. Avoid speculative engine rewrites and cosmetic changes without a concrete issue.
