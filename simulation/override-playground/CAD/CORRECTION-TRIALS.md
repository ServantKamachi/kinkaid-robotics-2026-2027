# Clearance corrections and reachable-intake development

The original CAD remains unchanged. The coherent reachable-intake layout below is now adopted in the separate simulation copy and generated development assets; it is not hardware-validated or release-certified.

## Coherent reachable-intake simulation layout — September 21

The collider-only layout was replaced with connected source-CAD geometry. Both jaw subtrees advance 25.4 mm together with the fixed coupling gears, pivot shafts, pawls, release cylinders, fittings, tubing and bridge. Four 3.2 mm bridge tabs support the relocated pivot line. The lift motors, pinions and reduction gears move rearward together by an additional 63.5 mm on new side plates. The lower claw tie moves forward/up, and the lower-arm tie pair is remounted as a vertically spaced rear pack.

The front drive motor bodies move inward 50.8 mm, but a direct extension shaft was rejected because exact solids crossed the lowered claw uprights. The adopted simulation geometry keeps the original outer gear planes and uses a two-chain dogleg through forward jackshafts, paired outboard bearing plates and raised side rails. These added parts are source-CAD simulation features with `hardwareValidated: false`; dimensions are development values, not a claim about the physical robot.

Both nonadjacent and joint-interface native sweeps pass 2,715 poses over lift -0.72 to 0.0873 rad and jaws 10 to 80 degrees. The targeted exact audit of new high-risk interfaces has 8 passes, 0 failures and 4 unresolved tie/arm pairs that exceeded the bounded worker timeout. It is not a full continuous solid certificate. Evidence: `assembly-collider-sweep-expanded.json`, `assembly-collider-sweep-interfaces-expanded.json`, and `reachable-solid-audit.json`.

Ordinary commands reach lift -0.7176 rad and jaw 1.39626 rad. A lengthwise sideways pin picks up and releases at approach Y 0.67, 0.68 and 0.69 m; Y 0.70 and 0.71 fail, and crosswise pins fail all five. Upright pin/cup and lengthwise pin pass at Y 0.68; lengthwise cup pickup and crosswise pin pickup fail, while a crosswise cup picks up but does not release. The older centered/offset upright suite now has a repeatable slow-release regression for the +10 mm pin offset: pickup succeeds, but floor release takes about 5 seconds rather than the 2-second criterion. Evidence: `coherent-reachable-pin-offsets.json`, `coherent-reachable-mixed-pickup.json`, and `grip-coherent-reachable.json`.

## Rear upper cross tie

Exact failures42/43 place rear tie `I_channel2_015` through the two upper parallel arms at the lowered pose. Its local height266.7mm coincides with the upper rear hinge height. Prepare a38.1mm downward shift to228.6mm, between the177.8mm and266.7mm hinge rows. This uses three12.7mm hole pitches and avoids extending above the upright.

The isolated exact-pair input is `work/v2/solid-candidates-rear-tie-lowered-trial.json`; run `work/v2/check_rear_tie_trial.py` in FreeCAD after the extended audit finishes. The shifted body transform in this two-pair fixture represents only the tie; it is not a proposal to translate the entire rear assembly.

Before adoption: test the full arm sweep, both rear uprights, diagonal braces, chain envelope, shaft/bearing clearances, and tie fastener mounting. The current export does not identify dedicated tie fasteners, so their connectivity cannot be assumed. Any accepted change must update the CAD, rendering and contacts together, then pass pickup and performance regressions.

## Tower and claw hinges

Do not apply the earlier isolated tower inset as a complete correction. It changes shaft spans, upright spacing, ties and supports. Claw/upright overlap occurs at several lift angles; moving only a collision plate or excluding a body pair would hide the interference. Resolve these as mounting assemblies after the remaining exact results are available.

## Expanded-range follow-up

The50.8mm rear-tie relocation passes a543pose native distance screen across lift-0.72to0.0873rad and jaws10/45/80degrees (82689explicit distance queries). Detailed CAD and mounting validation remain pending; no production relocation adopted.

A four-phase native command test on the user-test build shows commanded lift-0.72rad reaches only-0.60496rad, while commanded jaw80degrees reaches about72.5degrees when lowered. There are no numerical warnings. Thus the expanded targets do not establish expanded reachable motion. A forced-pose screen at-0.72rad finds up to29.37mm arm/motor-housing overlap. Correct support and transmission geometry before claiming this travel works. Evidence: expanded-controls-response.json and expanded-ground-access-screen.json.

## Reachable-intake feasibility result

Native contact evidence isolates opening obstruction to rollerR contacts against upper-arm plates I_channel2_010/011, and lowering obstruction to upper arm I_channel2_010 against lift motor I_motor007. Evidence: motion-blocking-contacts.json.

The original unadopted feasibility combination moved jaw subtrees forward25.4mm, lift housings rearward63.5mm, front drive housings inward50.8mm, tower tie I_channel3_23 rearward50.8mm and claw bottom tie I_channel2_19 upward50.8mm. It moved colliders without complete transmissions or mounts and must not be confused with the later coherent source-CAD implementation above. Three lift-housing offsets passed15sampled native poses; a command screen at76.2mm setback reached lift-0.71797rad and jaw1.39626rad without structural blocking contacts.

At63.5mm setback, ordinary lower/open/close/intake/lift/release commands pick up a lengthwise sideways pin at approachY0.67,0.68,0.69m with intake during lift;0.70/0.71m fail. Crosswise pins fail all five. At0.68m, upright pin and upright cup also pass pickup/release; side-long cup fails pickup and side-cross cup fails release. These are initial fixtures, not continuous recovery or robust manipulation acceptance. Reports lowered-clear-pin-offsets.json and lowered-clear-mixed-pickup.json.

Source CAD inspection confirmed LeftJaw/RightJaw contain their wheel stacks; fixed LeftClawGear/RightClawGear and vertical pivot shafts are separate children of Claw. The coherent implementation above therefore moves the complete pivot/release module and supplies a dogleg front-drive transmission rather than leaving those interfaces disconnected.
