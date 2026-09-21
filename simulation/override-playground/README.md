# Override practice playground

This is an Apple Silicon practice simulator for the reconstructed 169C robot, with contact-driven game pieces. It is a development tool, not a complete official Override match simulator.

## Open the simulator from this repository

1. Install **Unity Hub** and Unity Editor **6000.6.2f1** with macOS build support.
2. Clone the team repository and locate `simulation/override-playground/`.
3. In Unity Hub, choose **Add project from disk** and select the `simulation/override-playground/Unity` folder.
4. Open the project with Unity 6000.6.2f1.
5. Open `Assets/Playground.unity` and press the **Play** button.

The checked-in native libraries target Apple Silicon macOS. The generated `Builds/` directory is intentionally excluded from GitHub.

To rebuild the native bridge after cloning, create a Python 3.11 virtual environment in `simulation/override-playground/.venv`, install `requirements-lock.txt`, and run `Tools/build_native.sh`. To make a standalone app from Unity, run the editor method `BuildPlayground.Build`; it writes to `Builds/Candidates/Override Playground.app` unless `OVERRIDE_BUILD_OUTPUT` is set.

## Controls

| Control | Action |
|---|---|
| W/S, A/D or arrow keys | Drive forward/reverse, turn |
| Q/E | Lower/raise lift |
| Z/X | Close/open jaws |
| F/G | Intake/reverse rollers |
| R | Reset current layout |
| Space | Pause/resume physics |
| 1 / 2 / 3 | Overview / follow / top camera |
| F1 / F2 / F3 | Claw pickup / loose-piece pile / stack layout |
| T | Start/stop demonstration |
| Escape | Stop demonstration |
| H | Hide/show controls |
| F12 | Save screenshot in the app's Evidence folder |
| Right-drag / scroll | Orbit / zoom |

For the first pickup, reset the Claw pickup layout. Its first pin is centered in front of the open claw. Hold **Z + F for about one second**, release both, then hold **E** to raise. **X** releases. Closing without intake rollers tipped the pin away in the recorded test. **T** runs a short demonstration; **R** restores a fresh trial.

## Verified and limited

The application has been launched and visually inspected after fixing an underground camera. Local validation records in `Evidence/` are intentionally excluded from GitHub; `Research/REUSE_AUDIT.md` documents the existing-solution evaluation. Pin pickup/5-second retention/release passed at center and ±10 mm offsets under the provisional parameters. The centered cup pickup test failed retention; cup grasping is not verified. Lift sag remains approximately 0.10 rad under the modeled load.

Masses, friction, cartridge selection, actuator assignments, and cup wall thickness await measurements. Drive uses a finite linear torque-speed/braking approximation adapted from ftcsim and scaled consistently with V5 cartridge gearing; it is not V5 firmware emulation. The jaw and roller controls are independent approximations; ratchet/pneumatic coupling is not modeled. Some self-collisions are disabled. No real-world performance, legal motor allocation, scoring accuracy, or complete field fidelity is claimed.

Geometry comes from the user's reconstructed CAD and licensed Jerry Lum Override community meshes. Source and license details: `THIRD_PARTY.md`. No user CAD was uploaded. Audio and volume settings were not changed.
