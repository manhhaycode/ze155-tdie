# User feedback on the Đợt 1 sandbox (for the fixer)

1. **"Tôi thấy tốc độ zoom hơi chậm"** (2026-10-05). The zoom feels slow.
   - Cause found by the orchestrator in `src/scene/CameraRig.tsx`: `<CameraControls makeDefault smoothTime={0.35} />`. That leaves:
     - the default `dollySpeed` 1;
     - `dollyToCursor` false, so the zoom goes to the orbit target and not to the cursor;
     - a heavier smoothing than the default 0.25.
     camera-controls dolly is proportional to the distance to the target, so the zoom slows down and stalls as you approach the target. On an 18 m line the target is often far from what the user wants to look at.
   - Suggested fix (tune by feel, then measure):
     - `dollySpeed` about 2;
     - `dollyToCursor` true;
     - `smoothTime` about 0.2 and `draggingSmoothTime` about 0.08;
     - consider `infinityDolly` with a sensible `minDistance` (e.g. 0.05 m), so the zoom can push past the target into close-ups such as the screw sections. If `infinityDolly` is used, keep the double-click/F `fitToSphere` behaviour unchanged.
   - Check both a mouse wheel and a trackpad pinch, if available (`wheel` events with `ctrlKey`).
   - Keep the state preset flights (`setLookAt` with transition) smooth but not slow; about 0.6–0.9 s feels right.
