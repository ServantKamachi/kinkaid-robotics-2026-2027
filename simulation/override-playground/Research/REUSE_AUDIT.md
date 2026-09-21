# Reuse-first audit — 2026-09-19

Priority: real contact behavior, useful controls and sustained speed on Apple M2 / 16 GB. CAD file conversion is not a selection criterion. No candidate has yet supplied hardware validation for this particular robot.

| Existing work | Evidence inspected | Decision for this prototype |
|---|---|---|
| [xRC Override](https://xrcsimulator.org/vex-override/) | Released game, Gatr1 Ri3D / Pushbot, skills and descoring options. Developer warns it is physics-demanding. Mac download available; no supported custom-robot import established. | Download and test as the immediate ready-made game and behavioral reference. Do not extract proprietary assets. |
| [Autodesk Synthesis](https://github.com/Autodesk/synthesis) | Open source, Jolt, Fusion and imported asset workflow; browser inspected live. Thirteen built-in fields are FIRST fields, no Override. WheelDriver uses vehicle constraints; EjectableSceneObject moves captured pieces to configured poses. | Useful existing CAD/driver practice platform, but stock intake behavior is insufficient to test this friction-grip claw. Switching would still require Override assets and contact-based mechanism modeling. |
| [VEXcode VR Override](https://api.vex.com/vr/home/playgrounds/index.html) | Official existing Override coding playground with Flex hero robot. | Good for autonomous coding exercises; no arbitrary-robot mechanical model or physical calibration workflow established. |
| [Jerry Lum Override scoring practice](https://github.com/Jerrylum/vex-v5-scoring-practice-override) | Explicitly a scoring trainer without full match dynamics. GPL-3.0 source with separate GLB pins, cup, field, toggles. Commit 572085f57dcedb501d781db6c5485349beb887cf. | Reuse meshes with attribution and source; verify scale against official drawings. Not a physics backend. |
| [ftcsim](https://github.com/fanaustinca/ftcsim) | MIT; MuJoCo, hinged rollers, finite torque-speed motor model, contact claw, test scripts. Author calls it a learning project; FTC motor figures are approximate. | Reuse/adapt suitable motor-model code and inspect wheel/contact tests. Replace FTC parameters with V5 values; not evidence that 169C or Override is calibrated. |
| [BowlerStudio VexVitaminsRobot](https://github.com/madhephaestus/VexVitaminsRobot) and [High Stakes](https://github.com/madhephaestus/VexHighStakes2024) | VEX model generators backed by MuJoCo. Code is a vitamins-based kinematic model, not the 169C assembly; field is High Stakes. No license file seen in sample repository. | Useful model/reference approach, but not an existing Override solution or verified calibrated robot. Do not copy unlicensed sample code. |
| [SimpleSim](https://github.com/timrobot/SimpleSim) | VEX Clawbot, Three.js + Ammo/Bullet, beta. | Different mechanism and no Override contact validation located. |
| [LemLib v5-sim-engine](https://github.com/LemLib/v5-sim-engine) / [vexide QEMU](https://github.com/vexide/vex-v5-qemu) | Archived engine / brain-code emulation; hardware physics incomplete. | Not a ready contact playground. |
| [RoboticsSimulator VR](https://github.com/ericyoondotcom/RoboticsSimulator) | GPL Unity/Oculus project, 2020. | No current Override or Mac-specific benefit established. |
| [Atticus Terminal](https://github.com/ozzymcg/ATTICUS_TERMINAL) | Paths, footprint collision and timing/localization. | Useful autonomous-planning tool; not 3D grasp/nesting physics. |
| Webots / Gazebo / CoppeliaSim / Drake | Existing general robotics engines and model libraries; search found MathWorks VEX Clawbot/Gazebo example, not an Override physical model. | Replacing MuJoCo alone does not supply missing measured contact or motor data. |

Reuse already present: native MuJoCo solver, Unity renderer/input/platform support, existing 169C FCStd geometry. New work should be limited to integration and the robot/game-specific gaps that existing packages do not fill. Search coverage included official VEX, simulator vendor docs, public GitHub source, and VEX/Chief Delphi community discussions; absence of a discovered model is not proof none exists.

Primary drawing references: [Pin](https://content.vexrobotics.com/docs/2026-2027/override/online-manual/assets/image/PinSpecs.png), [Cup](https://content.vexrobotics.com/docs/2026-2027/override/online-manual/assets/image/CupSpecs.png). Direct official field-CAD download still returns HTTP 403. A VEX China forum CAD attachment link returned 404. Community meshes are therefore a useful reusable geometry source, subject to inspection.

[V5 manufacturer motor data](https://kb.vex.com/hc/en-us/articles/360044325872-Understanding-V5-Smart-Motor-11W-Performance): 2.1 Nm stall is specifically the 100 RPM cartridge. Scale gearing consistently; do not use 2.1 Nm at 600 RPM. Manufacturer notes onboard control changes the torque-speed envelope, so an ordinary linear DC approximation is not a fully accurate smart-motor emulator.

## Continuation evaluation — 2026-09-19

- xRC 20.3a was opened twice and its animated Override menu inspected. Attempts to open Single Player and Settings through Computer Use did not reach a session; subsequent clicks returned `windowNotFoundAtPosition`. Keyboard quit worked. This is an automation/interaction blocker, **not evidence that xRC is unplayable or slow**. No gameplay FPS, driving, scoring or custom-robot import claim is established. Audio and volume were untouched. xRC remains installed as the ready-made full-game candidate.
- Continued the existing custom prototype because it exposes the user's robot/contact tests and can be tested directly. This is not a finding that it outperforms xRC.
- Adapted ftcsim's MIT linear motor torque-speed/braking model with provisional 600 RPM V5 cartridge, 60/36 reduction, and 0.8 transmission efficiency. Wheel stall limit is now 0.4667 Nm. Firmware velocity/current/power limiting is not emulated.
- Integrated Jerry Lum's GPL pin/cup meshes with scene transforms and material groups. Replaced incorrect pin frusta with eight convex slices of the actual community pin surface; source height 165 mm is within 0.1 mm of the drawing. Cup visual geometry is reused; hollow wall contacts remain provisional. Full geometry license is bundled with StreamingAssets/ReusedPieces.
- A visual launch exposed an underground camera. Corrected overview, follow shortcut zoom and top-view field framing. Added keyboard access to layouts and demo because native automated mouse input was unreliable.
- Pin contact-only pickup/5-second hold/release succeeded centered and ±10 mm with intake rollers active. Jaw closure alone failed to retain the centered pin. Centered cup retention failed. This is simulation evidence with estimated parameters, not hardware validation or ratchet validation.
- `Evidence/final-scene*` is superseded: first-frame loading time contaminated the simulation clock. Use `Evidence/verified-scene*` and `Evidence/final-benchmarks.json` after the corrected-clock runs complete.

## Full-product continuation audit

Version 2.0 remains identified by the current VEX manual webpage and downloaded PDF. The webpage explicitly identifies itself as a non-authoritative complement; the PDF and binding Q&A govern. Downloaded references and geometry hashes are recorded in `Research/v2/provenance-audit.json`.

The reused scorer expects preclassified ordered stacks; it does not establish dynamic geometric nesting or valid toggle seating. `Research/RULE-IMPLEMENTATION-CONTRACT.md` specifies the evidence adapter and independent fixture families required before adopting its arithmetic.

SJTU provides an Override field library, but its landing page did not establish redistribution terms. No SJTU assets were copied. Existing pinned GPL assets remain the selected reusable geometry source, subject to official-drawing verification.

### September 20: finite lift bias compensation
Official MuJoCo computation documentation https://mujoco.readthedocs.io/en/stable/computation/index.html identifies qfrc_bias as gravity, centrifugal and Coriolis generalized forces. The bridge projects those forces along the six coupled lift coordinates using their signed equality ratios, then applies the existing PD correction and the unchanged 22 Nm torque cap. This uses estimated model mass/inertia, not measured robot calibration. Evidence: Evidence/v2/lift-control.json and Evidence/v2/grip-validation.json.
