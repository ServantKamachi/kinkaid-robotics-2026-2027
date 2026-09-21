# Override rule implementation contract

Source: locally saved Version 2.0 PDF, printed pages 14–18 (PDF pages 24–28). This is an implementation checklist, not a substitute for the manual. Latest official Q&A must still be audited before the scoring gate can close.

## Required evidence inputs

An ordered list of stack items is insufficient. The physics-to-rules adapter must provide stable IDs, pin half colors/poses, cup half inner volumes and opacity, goal inner volume and type, occupancy relationships, robot intersection with the midfield volume, robot-toggle contacts, and toggle mount seating.

Pin placement propagates from goals through valid nested cup/pin relationships. Start with actual goal-nested halves, enforce the one-half occupancy condition for each relevant goal/cup half, then resolve the relationship graph. An unanchored cyclic relationship must never create placed status by itself. Cups inherit placement through nesting with an already placed pin. Mere support, proximity, or contact does not establish nesting.

Nesting uses penetration of the opening plane into the inner volume, including tilted and partial insertion; it cannot be replaced with a centered vertical-stack test. Robot contact alone does not invalidate placement.

Visibility is a rule condition, not camera visibility or ray occlusion. Partial as well as complete insertion into an opaque cup half hides a pin half. Transparent cup halves do not hide halves. A goal's geometry alone must not be mistaken for an opaque cup.

Toggle ownership requires a seated face aligned with its mounts and no robot contact. The result defaults to yellow/unowned when either condition fails, even if its angle is near a colored detent.

Midfield membership uses intersection by any robot part with the defined volume, not root/chassis-center inclusion. Midfield yellow ownership compares alliance counts; equal counts produce no owner.

Autonomous scoring excludes robot midfield position points and midfield yellow ownership. The match-end evaluation uses rest or the five-second deadline, whichever comes first; no driving commands remain enabled during settlement. Ambiguous boundary states require a documented conservative result/explanation rather than silently promoting a live estimate to a certified result.

## Reuse decision

Pinned GPL `goalScoring.ts` supplies color mapping and ownership helpers and a scorer for a preclassified ideal stack. Reuse/adapt the simple mappings and arithmetic with attribution. Its `countVisibleStackHalves` uses immediate neighbors and excludes base bottoms by construction; it must not govern arbitrary partially nested or tilted physical arrangements. Build and test the geometric relationship adapter explicitly.

## Required fixture families (before runtime scoring implementation)

1. Unplaced pin/cup on floor: no scored halves.
2. A valid goal-nested pin with each possible color orientation.
3. Cup in clear-up versus opaque-up orientation around a placed pin.
4. Partial nesting, tilted nesting, opening-plane grazing, and just-outside placement.
5. Two pin halves in one cup-half volume: placement condition fails for affected relationships.
6. Multiple cup/pin levels; unsupported cycles; a broken nesting chain.
7. Robot contact with a legitimately placed object: does not erase placement solely for that contact.
8. Red, blue and neutral seated toggles; unseated angle; robot-touching toggle at an otherwise valid angle.
9. Yellow ownership under each toggle and tied/unequal midfield robot counts.
10. Robot arm enters midfield while chassis/root stays outside; touching boundary with numerical tolerance.
11. Autonomous totals exclude midfield position and ownership; bonus win/tie cases.
12. End-of-match coast/settlement and five-second cutoff; frozen final score; identical replay state.
13. Reset/mode switch clears scores, occupancy graph and timer snapshots.
14. Skills-specific field, ownership, loading and scoring fixtures after the Robot Skills section is audited.

Every fixture needs independently specified expected classifications and totals, then geometry-driven integration cases. Do not generate expected answers from the implementation being tested.

## Binding Q&A review, September 19, 2026

The active index is https://events.vex.com/V5RC/2026-2027/QA and its printable collection is https://events.vex.com/faqs/51/printable . Earlier RobotEvents 404 responses are superseded. Targeted rulings and independent expected cases are saved in `Research/v2/qa-audit.json` and `Tests/Fixtures/qa-expectations.json`; these are not yet executed scoring tests.

The toggle contact test must distinguish its moving assembly from fixed metal brackets (3171). The physical toggle also requires the measured vertical slot travel; a permanently fixed hinge would miss this behavior. Skills must not inherit the head-to-head Endgame placement restriction (3242). Do not reject an otherwise legal load just because the loader still touches it or because it finishes outside the loader (3235).

## Skills and source-height checks

RSC3 requires a distinct skills scorer: alliance-colored halves score only in their matching quadrant or midfield; yellow ownership in a quadrant requires the toggle to match that quadrant. Recorded early Skills Stop Time removes the ordinary settlement grace period (RSC5.e). Six additional independently specified cases now cover these distinctions.

All nine reused goal-shell top heights are within 0.5 mm of the manual nominal values; this checks height only, not opening volumes or contact surfaces. Results: `Evidence/v2/field-source-audit.json`. Base-pin-half visibility in the reused ideal-stack scorer remains a specific interpretation/geometry fixture to resolve; do not infer its correctness merely from source code.

## September 20 continuation

Seven further expected cases cover autonomous exclusions, score preservation, returned pieces, possession, quadrant labels and tape colors. These remain specification data, not passing runtime tests. Q&A 3195 contains older penalty language: reconcile against Version 2.0 and newer 3233 before implementing advisory violations.
