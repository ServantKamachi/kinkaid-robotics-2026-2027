# Reused components

- **MuJoCo 3.3.7**: native physics engine, Apache-2.0. Installed package and bundled dylib.
- **Unity 6000.6.2f1**: renderer, input, native Mac application.
- **Jerry Lum Override scoring practice geometry**: https://github.com/Jerrylum/vex-v5-scoring-practice-override at `572085f57dcedb501d781db6c5485349beb887cf`. GPL-3.0 license is preserved in `Research/scoring-LICENSE` and the application's StreamingAssets/ReusedPieces/COPYING.txt. Applied GLB scene transforms, exported the two material groups, and made eight convex pin collision slices. These are community meshes, not downloaded official field CAD. Cup contact walls are still provisional, independent of the visual mesh. No publication has been performed.
- **ftcsim motor model**: https://github.com/fanaustinca/ftcsim at `b5ec647e2991faf56dbaa3407b25d9a59d9ea09a`, MIT; full notice in `Research/ftcsim-LICENSE`. Adapted its finite linear torque-speed/braking equation into `Tools/bridge.c`. V5 values replace FTC values; this is not V5 firmware emulation.
- **169C reconstructed CAD**: user's local RatchetingClaw.FCStd, preserved unchanged. Component geometry does not establish measured masses, friction or actuator configuration.

xRC is a separately installed baseline. No proprietary xRC assets were extracted or reused.
