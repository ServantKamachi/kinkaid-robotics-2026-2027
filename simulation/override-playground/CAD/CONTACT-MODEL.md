# Robot contact model — development candidate

The renderer follows the corrected simulation CAD. MuJoCo is the only contact authority. Original CAD is read-only. This document describes current limitations; it is not a gate-B completion certificate.

- C channels use three 1.6 mm plates, preserving their open cross section. Small screw holes are omitted from contacts.
- Four diagonal braces use convex hulls of their source geometry. Source and hull volumes agreed to better than 0.0001%; these were previously missing from collision detection.
- Omni wheels use ten freely rotating capsule rollers per wheel. Their visible detailed wheel meshes are not collision meshes.
- Intake wheels use cylindrical contacts. Soft tread and friction remain estimated; no object attachments are used.
- Polycarbonate panels and mounting plates use local oriented boxes. Ten motor/electronics housing hulls now provide native contacts. They expose a real lift-motor/upper-arm CAD interference at the lowered pose; exact OCCT confirms intersection. Moving both lift transmissions rearward 50.8 mm restores the native sweep and 18 pickup trials. The expanded exact audit nevertheless remains incomplete and has found tower/lower-arm intersections. Gears and fasteners are detailed visually, with gear motion enforced by joint relationships rather than tooth-level dynamic contacts.

## Connected-interface exclusions

Explicit body exclusions are robot/lower1, lower1/rear, rear/upper1, upper1/claw, claw/rollerL, claw/rollerR, and robot with each omni-wheel roller. These avoid contact between connected hinge/shaft envelopes and channel proxies without holes. MuJoCo also filters parent-child contacts by default. These body-wide exclusions are broader than individual bearing interfaces; exact CAD audits therefore include adjacent body pairs, and must not be described as dynamic contact validation of every adjacent surface.

The solid audit distinguishes nine known meshing gear pairs, four square-shaft clearance-bore interfaces, and two seated spacers from non-contact members. Small clearance at those mechanical interfaces is intentional. All other sampled pairs retain the 1 mm design target. Broad-phase candidate boxes are expanded by 1 mm so nearby nonintersecting parts are not silently omitted. The audit still selects representative poses; it is not a continuous collision proof.

## Control approximation

Lift commands change a bounded angle target. Model gravity/Coriolis compensation plus position/velocity feedback share the existing 22 Nm cap. No integral term accumulates while blocked. The six coupled lift coordinates project generalized bias forces into the powered lift coordinate. Masses, inertia, cartridge selection, friction and ratchet/pneumatic behavior require physical measurements before a hardware-fidelity claim.

Remaining gate-B work includes mounting connectivity, flexible cable routing, pose overlays and scrutiny of broad connected-body exclusions. Full-field loading, scoring and release performance remain separate gates.

## User-requested control response — September 20 evening

The faster development profile multiplies lift/jaw target rates and drive free-speed target by 1.5, and intake/outtake target speed by 2. Torque caps, joint limits, geometry, and simulation timestep remain unchanged. These are explicitly uncalibrated gameplay targets, not measured V5 motor specifications. The renderer reverses A/D and left/right arrow steering as requested; the native command convention stays stable for reproducible diagnostics. Speed changes require manipulation and rendered regressions.

## September21 drive and exact-clearance follow-up

Removed inherited generic damping on twelve wheel/motor-gear joints. The motor torque-speed model remains finite, with explicit capped active braking at zero input; controller gain remains estimated. All18grip fixtures and ten continuous alternating-direction cup cycles pass. Pin ground recovery remains unresolved.

Expanded exact CAD checks at lift=-0.6rad confirm tower I_channel3_33 overlaps lower arms I_channel2_27 and I_channel2_007 by475.47 and471.47mm³ respectively. These are real simulation-copy assembly intersections, not acceptable bearing interfaces. Do not treat the non-excluded native contact sweep as clearance certification. The remaining exact audit and mounting corrections are still required.

## User test travel — September21

At the user's request, the downward lift target now reaches-0.72rad (previously-0.60), with joint limit-0.721rad; each jaw opens to80degrees (previously60). Reset poses remain unchanged. Existing contact geometry and torque caps remain active. Previous full-sweep and20minute results do not validate this expanded range; the user requested personal testing before more engineering checks.
