# Stadium implementation checkpoint

The user explicitly requires real-life appearance and exact measurements. This is an in-progress development model, not dimensionally certified or release-ready.

## Sources and nominal dimensions

`specification.json` transcribes Override manual v2 Appendix A5-A15. Native coordinates are meters, X audience-right, Y toward audience, Z up. The selected portable perimeter is 3566.4 mm inside, 50.8 mm wide, and 293 mm high. The prior 200 mm practice-wall height is not reused by the stadium. The metal-perimeter alternative has different dimensions and is not silently mixed into the portable specification.

Official public CAD download was retried on September 20 at `https://link.vex.com/docs/26-27/v5rc/field-cad`; terminal returned 403 and the in-app browser blocked the download. The licensed pinned Jerry Lum meshes remain the geometry source, checked against official drawings. Do not claim that the original official STEP assembly has been obtained.

## Implemented

- Stable 119-piece ledger and build-time C# contract checks; 73 active field pieces, 4 preloads, 42 reserves. Reserve/preload objects are not hidden physical bodies.
- Separate `stadium.xml`, retaining the same robot/controller; source-derived open goal and loader contact partitions.
- Source-derived cup wall sectors in the stadium, replacing the provisional uniform 2 mm cup wall used in practice. Practice now uses the same source-derived cup sectors; all18 pickup/hold/release regression cases pass (Evidence/v2/grip-source-cup.json).
- Colored pin variants and cup orientation. All 24 perimeter cups are opaque-up; twelve inner cups are clear-up. Source RedBlue pin is red-up in its canonical orientation.
- Drawing-backed goal/cluster centers. Contact-fitted vertical and radial free-piece reset offsets are recorded explicitly; they are not exact official-CAD pose evidence.
- Stadium/practice native model switching, renderer remapping, reset and follow camera; stadium starts paused because physical acceptance is unfinished.
- Source mesh welding and bounded 0.15 mm simplification before normal reconstruction. This tolerance describes simplification only; source tessellation accuracy and contact error are separate.

## Release blockers

1. Validate all source/contact surfaces against official dimensions. Angular convex sections can fill concave rib details; their error is NOT yet certified. Automatic CoACD trial produced 3259 parts for one shell and was rejected as impractical.
2. Check full loader geometry and mounts, extended state, opening, physical insertion and reserve transactions. Current contact sections do not cover all loader components. Two red loader colored/acrylic panels had a measured +7.79846 mm source vertical offset; presentation correction is explicit and requires visual comparison.
3. Four toggles remain visual only. Slot travel, seating, moving contacts and ownership are not implemented.
4. Final source-backed free-piece resting poses. Individual horizontal-pin radial offsets are contact-fit estimates; A12 supplies cluster positions, not those inferred offsets. Initial draft poses failed with large overlaps. Do not promote them to exact dimensions.
5. Full-field native and rendered performance. Initial native diagnostic failed overlaps and startup performance. Later tests supersede only their recorded scopes; `stadium-native.json` is not a 65-second steady-state or 20-minute stress acceptance test.
6. Physical loading, scoring evidence adapter, timed modes, UI/controller completion and integrated manipulation tests remain incomplete.
7. All previously documented robot CAD clearance, mounting, re-pickup and expanded exact-audit blockers remain active.

## September 21 reachable-intake robot update

The separate simulation CAD now contains a coherent lower/wider intake layout rather than collider-only relocation: jaw pivots, gears, shafts, pawls and release hardware move together; lift transmissions use complete rearward assemblies and side plates; inset front motors retain the outer drive planes through forward jackshafts and chain stages. The original FCStd remains unchanged.

Preflight and both 2,715-pose native structural sweeps pass through lift -0.72 to 0.0873 rad and jaws 10 to 80 degrees. Targeted exact checks of new interfaces are 8 pass, 0 fail, 4 unresolved by timeout. Ordinary-command lengthwise sideways-pin pickup/release passes at three nearby approaches, while crosswise pin pickup and two cup orientations remain limited. A +10 mm offset upright pin releases in roughly 5 seconds rather than the existing 2-second fixture criterion. These results justify a development user-test candidate, not Gate B completion or a release-ready claim.

Candidate `20260921T210127Z` was built from commit `f4ef437`. Cold startup, stadium capture and five scene-switch cycles pass, and the capture was visually inspected. A 65-second scripted practice pickup run at 1280x820 passes the recorded performance budget: frame p99 17.59 ms, maximum 36.51 ms, physics p99 3.47 ms, zero frames over 50 ms and zero numerical warnings. This candidate-specific screen does not clear the manipulation limitations or unresolved exact-solid pairs above.

## Reproduction

Generate scenario, export piece meshes, export source cup contacts, export field contacts, generate stadium model, fit initial contacts, regenerate stadium model, run native diagnostic, export stadium presentation, then build a candidate. Do not regenerate the unfitted scenario after fitting unless fitting is rerun. `Tools/fit_field_start.py` changes initial setup only, never pieces during gameplay. It is a development fixture construction tool, not a grasp aid.

## September 20 evening validation

Candidate 20260920T215552Z cold startup and five scene-switch cycles passed; stadium capture inspected. Benchmark initialization was disabling scripted commands; repaired before collecting new dynamic evidence. Candidate 20260921T021011Z passed 65-second active stadium rendering at1280x820 (p99 17.59ms, physics p99 4.57ms, no frames over50ms or numerical warnings). This is not the20-minute stress gate.

Goal contact section audit across83 heights found max21.6377mm boundary mismatch against the normalized licensed source. The source has open section paths, so no enclosed-area assumption was made. A connected-patch partition trial reduced maximum to17.0663mm but was rejected; original236 shared contacts restored. Reports: Evidence/v2/goal-contact-sections-before.json and goal-contact-sections-split-trial.json. Large invisible contact fill remains a confirmed release blocker.

Drive/reapproach test uses real commands and no between-cycle object edits. First pickup and >20mm carry succeeded for pin and cup; second pickup failed. Pin approach aligned; cup approach did not. Evidence/v2/reapproach-screen.json.

## Official source and contact follow-up

Official manual v2.0 was downloaded directly from https://content.vexrobotics.com/docs/2026-2027/override/files/override-2.0.pdf (SHA256 f694684deae414b222f18c48bdceb28284fca4c0ad610947ad700db805209860). Direct official PinSpecs, CupSpecs, GoalSpecs, ToggleSpecs and LoaderSpecs drawings were visually checked; additional nominal dimensions are recorded in specification.json. Individual piece masses and friction remain estimates; the combined scoring-kit shipping/product weight does not validate individual masses.

The full source toggle bracket section includes a closed oblong slot that the significant-component filter had omitted. Its fitted center travel is12.2191mm with maximum radial residual0.1431mm; this is a source-mesh measurement, not an official nominal clearance. Evidence/v2/toggle-slot-fit.json records the endpoints. Physical slot travel and seating still need implementation.

A height-aligned connected-patch goal trial reduced sampled boundary error to7.4669mm but required4456 shared hulls and was not adopted. A surface-prism trial also remains unadopted. Production remains236 shared contacts with the previously documented hollow-space error. Trials write only work/v2; use Tools/export_stadium_contacts.py --trial-shell explicitly for the height trial.

## Resumed validation

Candidate20260921T024601Z also passes65second practice pile and stack checks (p99 respectively17.61ms and17.59ms), cold stadium startup, capture, and five scene-switch cycles. Contact-export parity passes against an independently loaded MuJoCo contact fixture (five contacts; zero distance/force discrepancy). The initial parity fixture was corrected because the unstepped reset intentionally has zero contacts.

A ten-cycle continuous cup pickup/carry/release run passes when the operator lowers the lift before opening the claw. Carried distances were26.6–34.0mm per cycle; no piece reset or pose edit occurred between cycles. This is an ordinary-command diagnostic, not an app autopilot. Pin re-pickup still fails; lower/place releases tip the pin onto its side. Evidence/v2/reapproach-lower-release.json and reapproach-place-release.json preserve the limits. Lowest intake wheel is approximately90mm above the floor at the current safe lift stop; sideways-piece ground access needs a separate geometry diagnosis, not increased grip force.

Experimental source-facet contact patches reduce sampled shell boundary mismatch to0.8523mm using8922 thin patches per goal, with0.1mm reported simplification error and0.05mm contact-sheet thickness. Native runtime/containment tests remain pending; this is not adopted. A coarser0.5mm simplification creates6.8624mm section mismatch and is rejected. Radial partitions produce10.2066mm mismatch and are also not adopted. Production remains unchanged until a replacement passes geometry, contact and performance checks.

The fine surface trial completed30simulated seconds with no numerical warnings, but physics cost was15.96ms p99 per20ms batch and XML load184.6s: rejected for performance. A4695-part radial5mm/height trial still had6.3824mm sampled mismatch,118.7s XML load and8.12ms p99 per20ms batch; also not adopted. Native reports are goal-facet-fine-native.json and stadium-radial-5mm-trial-native.json. Sampling traced slow XML load to MuJoCo model-signature work during geometry insertion; omitting geom names did not resolve it. These screens do not establish containment or manipulation acceptance. Do not repeat these exact decompositions unchanged.

## September21 drivetrain correction

Wheel and motor-gear joints inherited the generic structural damping0.025Nm/(rad/s). The geared drag dominated the commanded drive response. Set explicit zero bearing damping on these12joints; motor torque-speed losses remain active. Added explicit zero-input active braking (gain0.08Nm/(rad/s), capped by the existing motor stall torque). This is an uncalibrated controller estimate, not V5 firmware. No motor torque limit increased.

First-second full-input travel improved from0.1703m to0.8471m. Clear-lane braking travel measured0.3711m. Both drive cases contact the wall and have zero negative contact separation during their final half-second; no numerical warnings. Reports: drive-response-before.json, drive-response-active-brake.json, drive-response-wall.json. All18grip regressions pass. Ten continuous cup cycles with alternating carry direction pass (reapproach-cup-faster-alternate.json). Alternating avoids backing into the wall; the prior one-direction run is not a carry-distance acceptance pass.

Ground access remains blocked. Current lowest roller bottom measured97.0mm in the kinematic lowered pose. Extending lift past-.606rad causes upper-arm/motor interference. Lowered jaw mounts and trial motor relocations/extra lift travel did not recover sideways pins; no geometry trial was adopted. Trial reports preserve incomplete scope, missing mounting validation and failed grasps. Production CAD and lift stop remain unchanged.

Candidate20260921T145154Z cold startup and five scene switches PASS; captured stadium view inspected. All three65second practice graphics runs pass at1280x820, p99 about17.59ms and no frames over50ms or physics warnings. First stadium run had one66.67ms frame (physics p993.94ms) and failed; retained as stadium-first-run-summary.json. One repeat passed (p9917.58ms, max30.69ms, physics p993.83ms). This does not clear intermittent hitch or20minute stress acceptance.

## September21 later collision trials

Normal-separated hull trials were rejected:633 joined hulls still21.6377mm sampled boundary error;4927 simplified connected hulls9.7879mm. Source winding is inconsistent (1826 reversed near-coplanar adjacencies), but repairing it did not sufficiently reduce part count. No production field contacts changed.

MuJoCo official documentation supports rigid flex triangle contacts for non-convex surfaces (https://mujoco.readthedocs.io/en/latest/modeling.html#deformable-objects). Isolated rigid-flex trial uses10136triangles per goal,0.025mm contact radius,0.1mm simplification limit. Across83source sections, max mismatch0.8436mm; this is sampled geometry evidence, not an official-CAD or whole-surface certificate. Load1.10s is much faster than thousands of separate hulls, but30simulated seconds took72.71s,20ms-stepbatch p9951.34ms and median45.97ms, zero warnings. Rejected for performance. Contact API must handle geom=-1/flex IDs before any future adoption. Reports goal-rigid-flex-sections.json, goal-rigid-flex-native.json and isolated goal-rigid-flex-probes.json.

Four isolated1mm rigid-flex sphere probes pass for outside, underside cavity, outer wall and central opening. The first outer-wall fixture incorrectly used maximum base width at9.25mm height; source section gives x=69.9852mm there, not71.25mm. Both fixture reports retained. A10micrometer vertex-merge trial produced the same10136triangles, so it was not benchmarked again.

## September21 twenty-minute stadium run

Candidate20260921T145154Z completed1200.002s of scripted stadium motion at1280x820.71116measured frames, frame p9919.20ms, maximum26.19ms, zero frames over50ms; physics p994.123ms, maximum13.229ms. Simulation/wall ratio0.999870, no BADQACC/BADQPOS warnings. This passes the recorded long-duration performance check. It does not certify Retina/resize behavior, physical manipulation, goal fidelity or resolve the earlier isolated66.7ms hitch. Evidence: performance-20260921T145154Z/stadium-summary-1200s.json.
