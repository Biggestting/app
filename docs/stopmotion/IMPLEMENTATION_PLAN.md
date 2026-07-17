# Stop-Motion iOS — Implementation Plan

> An iOS app that turns a video into a stop-motion animation, entirely on-device.
> Pipeline: import → extract frames → filter for stable/clean frames (CV) → select
> keyframes → encode → preview/export. See the companion architecture brief for the
> pipeline and RF-DETR → Core ML detail.

**Stack:** Native Swift · SwiftUI · AVFoundation · Vision · Core ML (ANE)
**No backend in the critical path.** Marginal cost per user ≈ $0. Distribution: Apple Developer Program ($99/yr).

---

## Guiding principles

1. **De-risk the model first.** The one High risk is detector latency on the ANE. Prove it in Phase 0 before building anything else — everything downstream assumes it works.
2. **Vertical slice early.** Get import → dumb stop-motion → export working end-to-end (no CV) before adding intelligence. Always have a runnable app.
3. **Cheap work on every frame, expensive work on survivors.** The pipeline ordering is the product; it's what keeps "1 minute to animate" true.
4. **Test on the floor device, not the newest.** The oldest supported phone defines quality and speed.
5. **Cancellable, async, off the main thread.** Video/CV is heavy; the UI must stay live and every long task must be cancellable.

---

## Phase 0 — Foundations & model spike  ·  ~1 week

**Goal:** answer the one question that decides scope — *does detection hit the latency budget on a floor-class device?*

- [ ] Create Xcode project (SwiftUI app, Swift, min target **iOS 16**). Set up git, SwiftLint, CI build.
- [ ] Decide the **device floor** (recommend iPhone 12 / A14) and acquire/borrow one for real-device testing.
- [ ] **Spike A — Vision built-in:** prototype hand rejection with `VNDetectHumanHandPoseRequest`. Measure latency per frame on the floor device. *If this is good enough, the custom-model path may be unnecessary.*
- [ ] **Spike B — RF-DETR → Core ML:** run the `PyTorch → ONNX → coremltools (mlprogram, fp16)` path. Open the `.mlpackage` in Xcode's **Core ML Performance report**; confirm the backbone lands on ANE, not CPU. Measure per-frame latency.
- [ ] Confirm the **license** on the exact RF-DETR checkpoint you export (base = Apache 2.0).

**Decision gate G0:** pick the detector (Vision hand-pose vs. RF-DETR vs. a YOLO-style fallback) based on measured latency + accuracy. Record the number. If nothing hits budget, revisit scope (shorter clips, fewer candidates) *now*.

---

## Phase 1 — Core pipeline vertical slice  ·  ~2 weeks

**Goal:** a working app that imports a clip and exports a (naive) stop-motion. No CV yet.

- [ ] **Import** — `PHPickerViewController` (no permission prompt). Copy asset to app scratch space.
- [ ] **Extraction** — `AVAssetImageGenerator` with `requestedTimeToleranceBefore/After = .zero`. Sample every Nth frame; keep `CVPixelBuffer`s. Handle orientation/transform.
- [ ] **Naive selection** — uniform time-spaced sampling (placeholder for Phase 2 scoring).
- [ ] **Encode** — `AVAssetWriter`, hold each frame for a fixed duration, output MP4 (H.264/HEVC).
- [ ] **Pipeline architecture** — model the flow as an `async` sequence of stages with a shared cancellation token; run off-main via actors/`Task`. Progress reporting hooks.
- [ ] Minimal SwiftUI: pick → progress → preview → save.

**Milestone M1:** end-to-end video → stop-motion export on a real device.

---

## Phase 2 — CV intelligence  ·  ~2 weeks

**Goal:** the "magic" — auto-select stable frames, drop hand frames.

- [ ] **Stability filter (stage 03)** — frame-to-frame difference / optical-flow magnitude via Accelerate/Vision to reject blur and cluster near-duplicates. This shrinks ~900 frames → 30–80 candidates *before* detection.
- [ ] **Detection pass (stage 04)** — run the Phase-0 detector via `VNCoreMLRequest` **only on survivors**. Feed `CVPixelBuffer`s directly (zero-copy). Reject frames where a hand/arm intrudes.
- [ ] **Keyframe selection (stage 05)** — score survivors on sharpness + temporal spacing + subject presence; pick an evenly paced set.
- [ ] **Cache** detection results so re-runs of selection/encode are instant.
- [ ] Tune thresholds against a small internal clip set; add a debug overlay to visualize picks/drops.

**Milestone M2:** clean, hand-free, evenly-paced stop-motion from a raw clip.

---

## Phase 3 — UX & controls  ·  ~2 weeks

**Goal:** something a beta tester enjoys using.

- [ ] **Preview** — looping `AVPlayer`; live re-render on control changes (cheap, thanks to the cache).
- [ ] **Controls** — frame count, playback speed, optional onion-skin / ease timing for a hand-animated feel.
- [ ] **Progress & cancellation** — per-stage progress, cancel button, graceful failure messages ("no stable frames found — try a steadier clip").
- [ ] **Export/share** — save to Photos, share sheet, choose format/quality.
- [ ] **Onboarding** — one-screen "how to shoot for best results."
- [ ] Empty/error states, haptics, polish.

**Milestone M3:** feature-complete beta candidate.

---

## Phase 4 — Beta hardening & TestFlight  ·  ~1–2 weeks

**Goal:** ship the beta you're already teasing.

- [ ] **Performance** — validate the per-clip time budget on the floor device; profile thermals on long clips; enforce a max clip length or chunk processing.
- [ ] **Memory** — stream frames; never hold 900 `CGImage`s at once. Instruments pass for leaks/peaks.
- [ ] **Crash/analytics** — lightweight, privacy-respecting (or none, to keep the "no data collected" label clean).
- [ ] **Privacy** — truthful App Privacy label ("no data collected"); confirm no network calls at runtime.
- [ ] **TestFlight** — Apple Developer Program, App Store Connect record, internal + external testing, invite flow (matches your "DM for an invite" beta).
- [ ] Icon, screenshots, beta review notes.

**Milestone M4:** live on TestFlight.

---

## Cross-cutting workstreams

- **Architecture:** stages as composable `async` steps; `actor`-isolated heavy work; single cancellation token threaded through; protocol-based detector so Vision/RF-DETR/YOLO are swappable.
- **Performance instrumentation:** a lightweight timer around each stage, logged in debug — the time budget is a living measurement, not a one-time check.
- **Testing:** unit tests for selection/scoring logic; a fixture set of real clips for regression; snapshot tests on the debug overlay.
- **Device matrix:** floor device (A14) + one current device, every milestone.

---

## Timeline summary

| Phase | Focus | Duration | Gate / Milestone |
|-------|-------|----------|------------------|
| 0 | Model spike & foundations | ~1 wk | **G0** — detector chosen, latency proven |
| 1 | Core pipeline vertical slice | ~2 wk | **M1** — end-to-end export |
| 2 | CV intelligence | ~2 wk | **M2** — clean auto stop-motion |
| 3 | UX & controls | ~2 wk | **M3** — beta candidate |
| 4 | Hardening & TestFlight | ~1–2 wk | **M4** — live on TestFlight |

**~8–9 weeks** solo to a polished TestFlight beta, with Phase 0 the true risk gate.

---

## Immediate next actions

1. Stand up the Xcode project + repo skeleton.
2. Run **Spike A** (`VNDetectHumanHandPoseRequest`) — cheapest possible answer to the detection question.
3. Only if A is insufficient, run **Spike B** (RF-DETR → Core ML) and compare.
4. Lock the detector at **G0**, then start the Phase 1 vertical slice.
