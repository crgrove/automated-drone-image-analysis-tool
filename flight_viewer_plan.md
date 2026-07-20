# ADIAT Flight Viewer — Desktop Implementation Plan

A new viewer mode that lets an off-site observer (IC, mission coordinator, second analyst) pair with one *or more* ADIAT Mobile drone tablets in the field over the public internet — no shared LAN, no media server in the middle — and watch each operator's live camera feed with detector overlays already rendered on it. Each feed lives in its own resizable, floatable, full-screen-capable tile inside a dynamic canvas. Detector promotions (the gallery rows ADIAT Mobile already produces from confirmed tracks) flow alongside the video over a WebRTC DataChannel, and surface in both a per-tile detection list and an aggregate Mission Gallery panel.

This plan covers the desktop receiver side only. The paired mobile publisher work is tracked separately in ADIAT_Mobile.

## Status — 2026-05-21

The desktop receiver is implemented and the signaling backend is live. Mobile + Worker have completed a resilience pass that the desktop can now rely on (see §18). The remaining v1 work is the end-to-end pairing smoke test (§14) against a real ADIAT_Mobile publisher, plus two small desktop-side items called out in §18 → *Desktop residual work*.

| Component | State | Notes |
|---|---|---|
| `adiat-flight-signaling` Cloudflare Worker | **Live + resilience pass** | Deployed at `https://signal.adiat.app` (custom domain, Cloudflare DNS active for `adiat.app`). Workers.dev fallback URL: `https://adiat-flight-signaling.<account>.workers.dev`. Source: https://github.com/crgrove/adiat-flight-signaling. Now bumps DO TTL on every signaling touch; accepts ICE-restart re-offers via `PUT /v1/sessions/:code/offer`; tolerates desktop's `{sdp}` / wrapped-`{candidate}` body shapes (§8). |
| Desktop receive stack (`WebRTCStreamService`, `DetectionFeedService`, `FlightTile`, `FlightViewerWindow`, `MissionGalleryDock`, `FlightPairingDialog`, `HttpSignalingChannel`) | **Implemented** | Default `base_url` points at `https://signal.adiat.app`; operator can override via `config.toml` for self-hosting. ICE-restart re-offer handling and snapshot-request channel are already wired in `WebRTCStreamService`. |
| ADIAT_Mobile publisher (`OverlayCompositor`, `FlightViewerPublishSessionImpl`, `HttpSignalingChannel`, frame pump from `LiveViewViewModel`) | **Implemented + resilience pass** | `BuildConfig.SIGNALING_URL` defaults to `https://signal.adiat.app` and matches the desktop default. Now monitors `IceConnectionState`, triggers publisher-initiated ICE restart (debounced 5 s on `DISCONNECTED`, immediate on `FAILED`), replies to `detections.snapshot_request` with the current promoted-track set, and only deletes the signaling session on explicit operator stop. Tracked in `ADIAT_Mobile/flight_viewer_publish_plan.md`. |
| End-to-end pair-and-stream smoke (§14) | **Pending** | Next milestone — real M4E tablet + real desktop, voice-radio code handoff, SAS confirm, multi-tile canvas exercise. Now also exercises ICE restart and snapshot replay (§14 step 13 onwards). |
| Desktop WS reconnect + gallery snapshot wire-up | **Pending** | Two small follow-ups that complete the resilience story on the desktop side. See §18 → *Desktop residual work*. |
| Detector boxes burned into the published video | **Implemented** | `:feature:liveview` now caches per-detector overlays from `StreamOrchestrator.results` and pumps them through `FramePublishSink.pushFrame` so remote viewers see the operator's HUD. |
| Session continuity (reconnect-with-same-code) | **Planned** | Desktop can be closed and reopened without losing the session, detection history, or pairing code. Spans mobile + Worker + desktop. See §20. |

This file is the design-of-record; sections below describe the architecture as-built. The phasing in §15 is annotated with status; the open questions in §16 are pruned to what is genuinely still undecided. §18 captures the resilience contract that mobile + worker now uphold and the small desktop changes that complete it end-to-end. §20 specs the next planned milestone — *session continuity* — which extends the resilience contract from "survive a transient network blip" to "survive a desktop app close".

## 1. Goal & non-goals

**Goal.**
- N concurrent WebRTC video sessions from one desktop ("multi-feed": one IC watching several drones), each ~sub-500ms glass-to-glass.
- Up to 3 concurrent desktops paired to the same drone ("multi-viewer": IC + 1–2 analysts on the same feed), pure P2P with a soft cap enforced publisher-side.
- Each session is its own resizable / floatable / full-screen-capable tile in a dock-style canvas.
- Mobile-rendered detector boxes appear burned into the video; *additionally*, every gallery promotion (thumbnail + class + confidence + GPS + timestamp) arrives over a DataChannel and populates a per-tile list plus an aggregate Mission Gallery.
- No shared network or media relay required; signaling rides a thin mailbox that never carries pixels.

**Non-goals (v1).**
- Running desktop-side detectors on incoming streams (clean-feed variant is a future drop-in; the receive stack supports it without rework).
- TURN relay. The ~5–10% of double-symmetric-NAT pairs that need it will fail with a "switch networks" message.
- Recording. Frames arrive as `np.ndarray`; recording can plug into existing `VideoRecordingService` later.
- More than 3 concurrent viewers per mobile feed. v1 supports up to 3 desktops paired to the same drone via pure P2P (each is a separate end-to-end peer connection). Beyond that the tablet's uplink saturates — scaling past 3 viewers is a Phase-2 SFU question, not a v1 question. See §4 → *Multi-viewer per feed*.

## 2. Architecture

```
Mobile A (publisher — separate plan)        Desktop (receiver — this plan)
─────────────────────────────────           ────────────────────────────────────────
StreamOrchestrator                          FlightViewerWindow  ← QMainWindow, dock host
  → FramePacket fan-out                       │
  → OverlayCompositor (boxes drawn)           │ adds/removes  ┌─────────────────────┐
  → WebRTC VideoSource ────H.264─────►        ├──────────────► FlightTile  (dock A) │
  → PromotionPublisher  ───JSON+JPEG────►     │              │  ├ video pane       │
       (per track promote/update)             │              │  └ detection list   │
                                              │              └─────────────────────┘
Mobile B …                                    │              ┌─────────────────────┐
   …same shape… ────────────────────────►     ├──────────────► FlightTile  (dock B) │
                                              │              │  ├ video pane       │
                                              │              │  └ detection list   │
                                              │              └─────────────────────┘
                                              │
                                              └► Mission Gallery (dock) ◄── aggregates from all tiles
```

Each `FlightTile` owns a private `WebRTCStreamService` and `DetectionFeedService` — no multiplexing, no shared peer connection. Adding a feed = constructing a new tile and docking it. Closing a tile tears down its services cleanly.

### Receive stack

| Component | Library |
|---|---|
| WebRTC over asyncio | **`aiortc`** (MIT) |
| H.264 decode | **`PyAV`** (transitive via aiortc) |
| Asyncio ↔ Qt event loop | **`qasync`** |
| Dock framework | Built-in `QDockWidget` (PySide6) |
| QR (signaling) | **`qrcode`** (M3); OpenCV already present for scan |
| Signaling | **Cloudflare Worker** at `adiat-flight-signaling` (HTTPS + WebSocket; public URL, no credentials) |

The aiortc event loop runs inside a per-tile QThread. Frame arrivals convert to `bgr24` `np.ndarray` and emit on `frameReady` — identical contract to `RTMPStreamService`, so the existing display patterns work unchanged.

## 3. Module layout

```
app/
├── core/
│   ├── services/
│   │   └── streaming/
│   │       ├── WebRTCStreamService.py             ← new (per-feed; mirrors RTMPStreamService)
│   │       ├── DetectionFeedService.py            ← new (DataChannel JSON + JPEG demux)
│   │       └── signaling/
│   │           ├── __init__.py                    ← new
│   │           ├── SignalingChannel.py            ← new (abstract base)
│   │           ├── HttpSignalingChannel.py        ← new (HTTPS + WebSocket to adiat-flight-signaling Worker)
│   │           ├── QRSignalingChannel.py          ← new (M3)
│   │           └── pairing.py                     ← new (codes + SAS derivation)
│   ├── controllers/
│   │   ├── FlightViewerController.py              ← new (main-window orchestrator)
│   │   ├── FlightTileController.py                ← new (per-tile lifecycle)
│   │   └── MissionGalleryController.py            ← new (aggregator)
│   └── views/
│       ├── FlightViewerWindow.py                  ← new (QMainWindow + dock area)
│       ├── FlightTile.py                          ← new (QDockWidget subclass; video + per-tile list)
│       ├── MissionGalleryDock.py                  ← new (QDockWidget; aggregate gallery)
│       ├── DetectionRowWidget.py                  ← new (thumb · class · conf · GPS · timestamp)
│       └── FlightPairingDialog.py                 ← new (code entry, SAS confirm)
└── tests/streaming/
    ├── unit/
    │   ├── test_webrtc_stream_service.py          ← new
    │   ├── test_detection_feed_service.py         ← new
    │   ├── test_signaling_pairing.py              ← new
    │   └── test_signaling_mailbox.py              ← new
    └── integration/
        ├── test_flight_viewer_lifecycle.py        ← new (single tile)
        └── test_multi_tile_canvas.py              ← new (multi-feed canvas)

resources/views/
├── flight_viewer.ui                               ← new (main window shell)
├── flight_tile.ui                                 ← new (per-tile pane)
├── mission_gallery_dock.ui                        ← new
├── detection_row.ui                               ← new
└── flight_pairing.ui                              ← new
```

Per CLAUDE.md §2.6, `*_ui.py` files are regenerated via `python setup.py build_res` and never hand-edited.

## 4. Dynamic canvas — multi-feed UI

### Container

`FlightViewerWindow` is a `QMainWindow`. The central widget is a placeholder (`QLabel "Add a feed →"`). All feeds and the Mission Gallery live as `QDockWidget`s docked to the main window, which means for free:

- Drag tiles between dock zones (top/bottom/left/right) and dock-onto-dock to tab them.
- Float a tile into its own OS window (`setFloating(True)`).
- Resize via the splitter handles between docks.
- Full-screen a tile: `tile.setFloating(True); tile.showFullScreen()` — Esc returns to docked.
- Close a tile (calls service cleanup, removes from canvas).

The toolbar carries: **+ Add Feed**, **Mission Gallery** (toggle dock visibility), **Layout** (save/restore named arrangements via `QMainWindow.saveState`/`restoreState` to QSettings — M2).

### `FlightTile`

A `QDockWidget` containing:

- Title bar: prefer `telemetry.last_envelope["aircraft_name"]` (operator's drone nickname / DJI model name) and fall back to the pairing code when the name is null (typical for the first second of a pairing, before the mobile's `ProductState` has populated). When both are present, the title reads `"<aircraft_name> · <code>"`. Operator-recognizable identifiers come first; the code is the disambiguator. ICE state pill still rides on the title bar.
- Central video pane: `QLabel` with `setPixmap(QImage(ndarray, ...))`. Reuses the existing pattern from `RTMPColorDetectionViewer`.
- Right-side strip (collapsible): per-tile detection list — most-recent first, scrollable, click to enlarge thumbnail.
- Footer status strip: resolution · FPS · bitrate · one-way latency · peer SAS phrase. The serial number from `telemetry.last_envelope["aircraft_serial"]` lives in this strip's tooltip (or the dock title's `whatsThis`) so the operator can disambiguate two identically-named drones if it ever comes up.

Tile menu (right-click on the dock title):
- Full Screen (toggle)
- Float / Dock
- Mute Detections in Gallery (excludes this tile's detections from the aggregate gallery without disconnecting)
- Reconnect
- Close

### Adding a feed

`+ Add Feed` → `FlightPairingDialog` (modal):
1. **Code entry** — 6-char alphanumeric pairing code typed in. Code is generated mobile-side and read out by the operator.
2. **Negotiating** — progress with ICE state transitions; cancellable.
3. **SAS confirm** — both screens display the same 4-word phrase (derived from the canonical hash of both DTLS fingerprints). User accepts only if they match.
4. On accept → a new `FlightTile` is constructed, its services started, and it's docked into the canvas (default zone: right side, tabbed with existing tiles if any).

Multiple `FlightPairingDialog`s can be open simultaneously (each modal-to-its-own-flow but not to the window) so the IC can add several feeds in quick succession.

### Concurrency budget

- Each peer connection = its own aiortc loop, its own H.264 decoder slot, its own RTP receiver.
- Modern desktop: 4–8 concurrent 1080p30 H.264 decodes via dxva2/d3d11/vaapi is comfortable.
- Network inbound: 2–4 Mbps per feed; 8 feeds ≈ 16–32 Mbps inbound. Within any reasonable home/office connection.
- aiortc's asyncio is single-threaded per loop; each tile owns one QThread + one asyncio loop, so feeds genuinely run in parallel.

### Multi-viewer per feed

A single mobile feed accepts up to **3 concurrent desktop pairings** in v1, enforced publisher-side. The desktop requires no special handling — each desktop pairs normally, gets its own code, its own end-to-end DTLS-SRTP connection. A 4th desktop attempting to pair sees a clear "drone has reached maximum viewers (3)" error in `FlightPairingDialog`.

**Rationale.** Pure P2P uplink scales linearly on the publisher: each viewer adds another full copy of the bitstream leaving the tablet's link (typically ~2–4 Mbps per viewer). Tablet uplinks max around 5–15 Mbps on cellular and 10–20 Mbps on residential WiFi, so 3 viewers is the realistic envelope before quality degrades for everyone. There is no media relay — every viewer is end-to-end encrypted directly to the publisher (DTLS-SRTP per peer).

**Growth path (out of v1 scope).** If field experience shows the IC team routinely exceeds 3 watchers, the desktop receive code does not change — viewers still terminate against a peer connection. The growth path is to introduce an SFU (self-hosted, e.g. mediasoup or livekit on a $5/mo VPS) that mobile publishes to once and viewers connect to. Simulcast (mobile encoding 1080p / 720p / 360p layers) becomes worth doing in that mode so slow viewers don't pull fast viewers down. Tracked as Open Question #7 in §16.

**UX surface on desktop.**
- M1: A 4th pairing attempt resolves to a clear modal error in `FlightPairingDialog`: *"This drone already has 3 viewers connected. Ask one to disconnect, or try again later."*
- M2: When fetching the offer succeeds but the cap is approaching, the dialog shows a *"drone has 2/3 viewers"* hint.
- The hint and error string both come from a publisher-side response code on the mailbox `offer:{code}` record; the desktop never enforces the cap itself.

## 5. `WebRTCStreamService` (per-tile)

Extends `StreamType`:

```python
class StreamType(Enum):
    RTMP = "rtmp"
    HLS = "hls"
    FILE = "file"
    HDMI_CAPTURE = "hdmi_capture"
    WEBRTC = "webrtc"   # ← new
```

Public surface mirrors `RTMPStreamService`:

```python
class WebRTCStreamService(QThread):
    # mirrored shape
    frameReady              = Signal(np.ndarray, float, int)
    connectionStatusChanged = Signal(bool, str)
    streamStatsChanged      = Signal(dict)
    errorOccurred           = Signal(str)

    # WebRTC-specific
    iceStateChanged         = Signal(str)
    peerFingerprintReceived = Signal(str)        # SHA-256 hex
    sasReady                = Signal(list)       # ["salmon","orbit","cliff","marble"]

    # DataChannel surface (consumed by DetectionFeedService)
    dataChannelOpened       = Signal(str)        # channel label
    dataChannelMessage      = Signal(str, bytes) # label, payload

    def __init__(self, signaling: SignalingChannel, pairing_code: str): ...
    def request_connect(self): ...
    def confirm_sas(self, accept: bool): ...
    def request_disconnect(self): ...
    def reset(self) -> None: ...    # CLAUDE.md §2.2.1 lifecycle
    def cleanup(self) -> None: ...  # CLAUDE.md §2.2.1 lifecycle
```

Frame path:

```python
frame: av.VideoFrame = await track.recv()
arr = frame.to_ndarray(format="bgr24")
ts  = frame.time or time.monotonic()
self.frameReady.emit(arr, ts, self._frame_n)
```

## 6. Detection gallery sync — WebRTC DataChannel

### Why DataChannel

Same peer connection as video → same NAT traversal already proven, same DTLS-SRTP encryption, same authentication (DTLS fingerprint already verified). No new signaling, no new endpoint, no new auth. Bandwidth is plenty for SAR-scale promotion rates (10s of tracks per hour, ~50KB thumbnails).

### Channel contract

Two channels are opened by mobile right after the video track:

| Channel | Type | Direction | Payload |
|---|---|---|---|
| `detections.meta` | ordered, reliable | mobile → desktop | UTF-8 JSON envelopes, one per promote/update event |
| `detections.thumb` | ordered, reliable | mobile → desktop | binary JPEG bytes; preceded by a `detections.meta` envelope carrying the `track_key` + content length |

**`detections.meta` envelope shape** (proposed; subject to ADIAT_Mobile alignment):

```json
{
  "event": "promote" | "update",
  "track_key": "person|<sessionId>|<trackId>",
  "detector_id": "person",
  "class_name": "person",
  "confidence": 0.87,
  "bbox_norm": [0.41, 0.55, 0.12, 0.18],
  "captured_at_ms": 1737310912345,
  "location": {
    "lat": 30.2672,
    "lon": -97.7431,
    "altitude_msl_m": 312.4,
    "horizontal_accuracy_m": 2.5
  },
  "thumb": {
    "channel": "detections.thumb",
    "bytes": 48211,
    "sha256": "…"
  }
}
```

Thumbnail bytes follow on `detections.thumb`; the receiver pairs them by `sha256` and a short timeout. Promotions without a thumb (e.g. mobile fails to crop) still surface — the row just shows a placeholder.

### Reliability & flow control

- Ordered + reliable mode on both channels. WebRTC's SCTP handles backpressure transparently; we don't need to engineer congestion control.
- If the channel disconnects, the desktop drops the in-flight thumb and waits for the next promote. No retroactive replay v1 — track lifecycle is short and re-promoting is cheaper than buffering.
- M3: optional `detections.snapshot` request channel — desktop asks mobile for the current set of promoted tracks on (re)connect.

### `DetectionFeedService`

```python
class DetectionFeedService(QObject):
    detectionPromoted = Signal(dict)              # parsed envelope + thumb_bytes (or None)
    detectionUpdated  = Signal(dict)
    feedError         = Signal(str)

    def __init__(self, stream_service: WebRTCStreamService): ...
    # subscribes to dataChannelMessage; demuxes by label;
    # pairs meta envelopes with thumb payloads; emits parsed events.
```

One instance per `FlightTile`. Lives in the same QThread as the stream service; no extra event loop.

## 7. Mission Gallery (aggregate)

A `QDockWidget` (`MissionGalleryDock`) that subscribes to every active `DetectionFeedService` via `FlightViewerController`. Each row is a `DetectionRowWidget`:

```
┌──────────────────────────────────────────────────────────────────┐
│ [128×96  ] PERSON  87%   30.2672, -97.7431   312.4m  03:14:22pm  │
│ [thumb   ]         TEXSAR-01 (K3F9PM)                  [👁] [⤴]  │
└──────────────────────────────────────────────────────────────────┘
```

- The aircraft name on the second line comes from `tile.telemetry_feed_service.last_envelope["aircraft_name"]` cached per tile — not from anything stamped into the detection meta envelope on the wire. The pairing code stays as a disambiguator in parentheses. Fall back to `"Feed <code>"` when `aircraft_name` is still null.
- `[👁]` — open larger view (modal `QDialog` with full-size thumb + metadata, including `aircraft_serial` for unambiguous identification).
- `[⤴]` — copy lat/lon to clipboard in operator-preferred format (DD, DM, MGRS). DD only in M1; DM/MGRS in M2.
- Filter strip at the top: by feed, by class, by min-confidence; date/time slider in M2.
- Persistence: in-memory only for v1. Cleared on session end. M3 will offer "export selected to standard ADIAT gallery."

Per-tile detection list is the same widget pattern, scoped to the tile.

### Per-track lifecycle — PROMOTE creates, UPDATE refreshes (NOT duplicates)

The mobile wire protocol distinguishes two `event` values on `detections.meta`:

| `event` | Meaning | Gallery behavior |
|---|---|---|
| `"promote"` | A new track has just confirmed (`TrackerParams.confirmFrames` consecutive associated frames). | **Insert** a new gallery row keyed by `track_key`. |
| `"update"` | An existing track produced a better view — peak confidence improved by `policy.updateMinConfidenceDelta`, OR `policy.updateMinIntervalMs` elapsed (so the operator sees current position for a moving target). | **Refresh** the existing row identified by `track_key` in place. Do **not** spawn a new row. |

`track_key` is `"{detector_id}|{publisher_session_id}|{track_id}"` and is stable for the lifetime of the track. Mobile's `PromotionPublisher` emits one PROMOTE per confirmed track and many UPDATEs for the same `track_key` thereafter; both go to the same `detections.meta` channel in arrival order.

**Why this matters operationally.** SAR targets aren't always stationary — a moving vehicle, person walking, or animal can stay in-track for minutes. The UPDATE stream is how the desktop's gallery row keeps its GPS, confidence, and thumbnail current. Without UPDATEs the row stays pinned to the confirmation-frame position; without dedup the gallery accumulates one row every few seconds per target and floods the operator with apparent duplicates. The per-track collapse keeps both behaviors right: one row per target, latest known state always visible.

**Dedup contract (`MissionGalleryController.add_detection`).** Both `detectionPromoted` and `detectionUpdated` flow into the same slot; the dispatch is by `event` field on the envelope (or, equivalently, by whether a row with the incoming `track_key` already exists). Pseudocode:

```python
def add_detection(self, feed_id: str, detection: dict) -> None:
    track_key = detection.get("track_key")
    ts = self._timestamp(detection)

    # 1. Thumbnail cache (existing logic — keep)
    self._cache_or_restore_thumb(detection, track_key)

    # 2. Per-track collapse: refresh in place if we've seen this track_key.
    #    PROMOTE arriving for a track_key we already have is treated the
    #    same as UPDATE — the publisher's UPDATE-vs-PROMOTE distinction
    #    is informational; the dedup is keyed on track_key, not event.
    if isinstance(track_key, str) and track_key:
        for i, (_existing_ts, existing) in enumerate(self._detections):
            if existing.get("track_key") == track_key:
                merged = {**existing, **detection}
                # Preserve fields the UPDATE didn't carry (e.g. context
                # frame JPEG captured at promote-time) by letting the
                # right-hand side win only where present.
                self._detections[i] = (ts, merged)
                self._notify_row_changed(i)
                return

    # 3. New track — append.
    self._detections.append((ts, dict(detection)))
    self._notify_row_inserted(len(self._detections) - 1)
    # ... existing detector-registry / cap / sort logic ...
```

**Field merge semantics.** UPDATEs from mobile carry the full envelope shape (the publisher rebuilds it from the live `PromotionEvent` each time), so they include `confidence`, `bbox_norm`, `captured_at_ms`, `frame_ts_ns`, `location`, `session_id`, `seq`, and a fresh `thumb_bytes`. PROMOTE-time-only fields the desktop attaches locally — like `context_frame_jpeg` from `_attach_context_frame` — should be preserved across UPDATEs (don't let an UPDATE that lacks them overwrite to null). The `{**existing, **detection}` merge above does this when the missing field is simply absent from the UPDATE envelope; if the UPDATE carries a key with a `None` value, guard with `{k: v for k, v in detection.items() if v is not None}` before the merge.

**Sorted order.** When a row refreshes, its `(ts, …)` tuple is replaced with a fresher `ts`. The gallery's render order is whatever sort `MissionGalleryController.detections()` (or equivalent) applies — typically newest-first. The refresh naturally bubbles an actively-updating track to the top, which matches operator expectation ("the target I'm watching right now is at the top").

**Both signal wires stay connected.** Existing wiring in `FlightViewerController`:

```python
controller.detectionPromoted.connect(self.gallery.add_detection)
controller.detectionUpdated.connect(self.gallery.add_detection)
```

…remains correct under this spec. Both signals enter the same dedup-keyed method. The other subscribers — the in-tile video overlay (`tile.detection_overlay.on_track_event`) and `DetectionThumbCropper.on_track_event` — also already key on `track_key` for their own state, so they're already correct for the moving-target case; this spec just makes the gallery match.

**SQLite persistence.** `FlightSessionStore.append_detection` is already idempotent on `(session_id, seq)` and writes both PROMOTE and UPDATE rows (each event has a unique `seq`). The gallery dedup is purely a presentation concern — the persistence layer keeps full history for cross-session replay. On `_restore_session_detections`, the loader should collapse the SQLite rows back into one-row-per-`track_key` (latest `seq` wins) before feeding them to the gallery so a relaunched desktop sees the same one-row-per-target view as a continuously-running one.

## 8. Signaling

The signaling backend is the `adiat-flight-signaling` **Cloudflare Worker** (separate repo: https://github.com/crgrove/adiat-flight-signaling, deployed to a public URL).

The Worker URL is the only configuration in the desktop receiver — there are **no client-side credentials** in either ADIAT Mobile (closed) or ADIAT Desktop (open-source). This was the deciding constraint: an earlier design used Supabase, but embedding the Supabase anon key in OSS source — even though it's a permission-scoped JWT designed to be public — was unsuitable (drive-by abuse of free-tier quota, looks like a credential leak to scanners, couples ADIAT's availability to one Supabase project).

### Wire shape

| HTTP | Path | Purpose |
|---|---|---|
| `POST` | `/v1/sessions` | Mobile publishes its offer, gets a server-allocated 6-char code |
| `GET` | `/v1/sessions/:code/offer` | Desktop fetches the offer; returns `{type:"offer", sdp}` |
| `PUT` | `/v1/sessions/:code/offer` | **Mobile** publishes an ICE-restart re-offer; Worker resets `answer`, broadcasts `{type:"offer", sdp, iceRestart:true}` to `role=desktop` watchers (§18). |
| `POST` | `/v1/sessions/:code/answer` | Desktop submits the answer. Accepts `{sdp}` or `{answer_sdp}`. Second answer is accepted only after a `PUT /offer` (post-restart). |
| `POST` | `/v1/sessions/:code/ice/:role` | Either side submits ICE; `role` ∈ `mobile|desktop`. Accepts flat `{candidate, sdpMid, sdpMLineIndex}` or wrapped `{candidate: {…}}`. |
| `WS` | `/v1/sessions/:code/subscribe?role=mobile|desktop` | Streams JSON messages: `{type:"offer", sdp, iceRestart?}` (desktop only), `{type:"answer", sdp}` (mobile only), `{type:"ice", candidate:{…}}`, `{type:"closed", reason}` |
| `DELETE` | `/v1/sessions/:code` | Operator-initiated teardown |

State lives in a single Durable Object per pairing code, self-destructing via alarm after 30 seconds **of inactivity**. The Worker re-arms the alarm on every signaling touch (init, GET /offer, PUT /offer, POST /answer, POST /ice, WS subscribe), so a session in active use is never evicted while clients are still talking to it. The DO holds: offer SDP, answer SDP (when posted), ICE candidates from each side, and the WebSocket watchers for each side. No persistent storage beyond TTL.

### Python `SignalingChannel`

```python
class SignalingChannel(ABC):
    async def get_offer(self, code: str) -> str: ...
    async def post_answer(self, code: str, sdp: str) -> None: ...
    async def post_ice(self, code: str, role: str, candidate: dict) -> None: ...
    def subscribe(self, code: str, role: str) -> AsyncIterator[dict]: ...
    async def delete_session(self, code: str) -> None: ...
```

`HttpSignalingChannel(base_url=BUILTIN_DEFAULT)` is the only impl. Pure HTTPS + one `websockets.connect` per pairing. No DB SDK, no auth headers, no credentials.

### Code allocation

The Worker generates the 6-char code from a 31-character no-confusables alphabet (`A-Z` minus `I/L/O`, `2-9`) and CAS-claims it via a Durable Object name lookup. The desktop *receives* a typed code from the operator (read aloud out-of-band); it never generates one.

### QR / paste fallback (M3, low priority)

QR-encoded bundled SDP+ICE+fingerprint, scanned via OpenCV or pasted. Same `SignalingChannel` interface — `FlightPairingDialog` gains a tab to choose the channel. Note: in practice neither DJI tablets nor desktop machines have convenient camera access for scan, so realistic only as a paste-the-blob fallback for fully-offline pairing. Deprioritized.

## 9. Pairing & authentication

Per feed:

1. **6-char pairing code.** Allocated server-side by the Worker (see §8 → *Code allocation*) — the tablet receives the code in the `POST /v1/sessions` response and displays it. 31-character no-confusables alphabet (`A-Z` minus `I/L/O`, plus `2-9`); single-use; 30s TTL. Displayed in a large monospace font on the tablet for the operator to transmit out-of-band to the desktop user — voice radio, phone, SMS, in-app chat, whatever ops channel the team already uses. The desktop never types into the tablet and vice versa; the human handoff is the *only* path from publisher to viewer for the code itself.
2. **SAS** — 4 words from `EFF-short-1296[ canonical_hash(fp_mobile, fp_desktop) ]`. Both screens display; both users confirm match. Defends against an active MitM on the mailbox.
3. **TOFU (M3)** — persist remote fingerprint after first accept, keyed by a long-form device name; warn on mismatch.

Pairing dialog states: `awaiting-code` → `fetching-offer` → `negotiating` → `sas-confirm` → `connected` | `failed`.

### Code lifecycle on the desktop

1. User types code into `FlightPairingDialog` (`awaiting-code`).
2. Dialog calls `signaling.get_offer(code, timeout=30s)` (`fetching-offer`). Three terminal outcomes:
   - **Found**: SDP returned, proceed to ICE/DTLS (`negotiating`).
   - **Not found / expired**: error "Code not found — confirm with the operator and try again."
   - **Already answered**: error "This code has already been used. Ask the operator to generate a new one." (Distinct error because it suggests possible interception or race; see *Trust model* below.)
3. On `connected`, the desktop does **not** call `signaling.delete_session(code)`. The Durable Object must stay alive so the publisher can post ICE-restart re-offers and the desktop's post-restart answer can flow back over the same WS subscription (§18). `delete_session` is only called from `_tear_down` — i.e. on explicit operator stop, peer-initiated `closed`, or a hard error. The Worker's 30 s inactivity TTL (bumped on every touch) handles genuinely abandoned sessions.

### Trust model: what an eavesdropper on the code can and can't do

The pairing code is transmitted by humans over an unsecured channel (voice radio is the most realistic). The code is not a secret in any cryptographic sense. The trust chain stays sound because:

- Reading `offer:{code}` reveals the publisher's SDP, including its DTLS certificate fingerprint and ICE candidates. None of this is sensitive; the SDP is *meant* to be public-ish (it's how peers find each other).
- An attacker who hears the code could **race** the legitimate viewer to post an answer. The publisher would then attempt to DTLS-handshake with the attacker.
- The publisher's screen would show an SAS derived from `canonical_hash(attacker_fingerprint, publisher_fingerprint)`. The legitimate viewer's screen would show a *different* SAS. The operator and the legit viewer would see the mismatch on a voice readback and reject. Connection does not proceed to media.
- The race also leaves a tell on the desktop side: if the legitimate viewer arrives after the attacker, their `await_offer` returns "already answered" (because the attacker already posted to `answer:{code}`). That error path is distinct from "expired" specifically so the operator can be alerted: *"generate a new code, the previous one was used unexpectedly."*

This is good enough for the SAR threat model. Code interception is detectable and forces a retry rather than silently compromising the session. It is **not** good enough for, e.g., banking-grade adversaries; if that threat model ever applies, the path forward is pre-shared device identities (M3 TOFU + signed pairing tokens) rather than secret codes.

## 10. Integration with the existing streaming pipeline

`FlightTile` does **not** route frames through `StreamAnalyzeService` — overlays are already burned in by mobile, and gallery items arrive via DataChannel rather than detection. The tile's `frameReady` slot does only:

1. `np.ndarray` → `QImage` (existing helper).
2. `setPixmap` on the video pane.
3. Update the status strip (FPS / ICE state / bitrate / latency).

CLAUDE.md §2.2.1 governs algorithm-running viewers; this viewer is documented in `FlightTileController`'s module docstring as exempt by design, with a forward pointer to the future "clean-feed → desktop ML" extension that will route the same `WebRTCStreamService` through `StreamAnalyzeService` with `enable_algorithms=True`.

## 11. Dependencies (requirements.txt additions)

```
aiortc>=1.9
qasync>=0.27
httpx>=0.27        # HTTPS client for HttpSignalingChannel
websockets>=13     # WebSocket client for the Worker subscribe endpoint
```

`PyAV`, `aiohttp`, `aioice`, `pyee` arrive transitively via `aiortc`. `opencv-python` is already a requirement. `requirements-dev.txt`: add `pytest-asyncio` if not present.

`qrcode[pil]` is **not** a v1 requirement — QR signaling is deferred (§8 → *`QRSignalingChannel`*). Add only if/when that channel is actually built.

## 12. Testing

Per CLAUDE.md §2.9 / §3.2.

### Unit (`app/tests/streaming/unit/`)

`test_webrtc_stream_service.py`
- QThread start/stop/cleanup with stubbed `RTCPeerConnection`.
- Frame conversion path: synthetic `av.VideoFrame` → emits ndarray with shape `(H,W,3)`, dtype `uint8`, monotonic counter.
- Failure paths (signaling timeout, ICE failure, DTLS fingerprint mismatch) each emit context-bearing `errorOccurred` and transition cleanly.

`test_detection_feed_service.py`
- Meta-only promotion (no thumb) surfaces via `detectionPromoted` with `thumb=None`.
- Meta + thumb (correct order) surfaces with bytes attached.
- Thumb arriving before its meta envelope is buffered and matched.
- Malformed envelope emits `feedError`, no crash, channel stays open.
- Sha256 mismatch between envelope and thumb bytes drops the row + logs.

`test_signaling_pairing.py`
- 6-char code generator distribution sanity (no obvious collisions over 10k).
- SAS derivation determinism: same fingerprints → same words; argument swap → same words; one-bit fingerprint change → entirely different words.

`test_signaling_mailbox.py`
- Mailbox channel against an in-memory fake backend (no network).
- `await_offer` returns the SDP on a hit, raises `CodeNotFound` on a miss, raises `CodeAlreadyAnswered` when `answer:{code}` exists before the read (distinct error path per §9 → *Code lifecycle / Trust model*).
- `await_offer` honors timeout and stops waiting cleanly.
- TTL expiry behavior, single-use enforcement (delete-on-connect from desktop side), ICE candidate ordering across publish/subscribe.

### Integration (`app/tests/streaming/integration/`, pytest-qt)

`test_flight_viewer_lifecycle.py` (single tile)
- Pairing dialog happy path with a mocked service → tile appears docked → connected state shown.
- Disconnect cleans up service thread + asyncio loop + DataChannels with no leaked warnings under `-W error`.
- Reject-SAS path tears down before media plays.
- **Cap-reached path**: mocked signaling returns the publisher-side "viewers full (3/3)" response code on the `offer:{code}` fetch → dialog displays the localized error and stays open for retry; no peer connection is constructed.
- **Code-not-found path**: `await_offer` raises `CodeNotFound` → dialog shows "Code not found — confirm with the operator and try again" and stays open.
- **Code-already-answered path**: `await_offer` raises `CodeAlreadyAnswered` → dialog shows the distinct "code already used" message recommending a fresh code (per §9 trust model).

`test_multi_tile_canvas.py` (multi-feed)
- Add two tiles in sequence; both visible in canvas.
- Float one tile; both continue to receive frames (uses fake `WebRTCStreamService` emitting frames at 10fps for 2s).
- Close one tile; aggregate Mission Gallery stops listing that feed's detections, the other tile is unaffected.
- Aggregate gallery merges detections from both feeds in monotonic timestamp order regardless of arrival order.

A real two-peer end-to-end aiortc test is possible but historically flaky on local-loopback ICE; defer to manual smoke (§14).

## 13. Translations (CLAUDE.md §2.8) and lint

All new user-facing strings go through `self.tr(...)` or `QCoreApplication.translate(...)`. Internal values (state enums, mailbox role names, DataChannel labels) are stable English. After implementation:

```
python scripts/extract_translations.py
python scripts/extract_translations.py --compile
flake8 app/
```

## 14. Manual smoke checklist

Used until full end-to-end automation is stable.

1. Mobile and desktop on different networks (cellular + home WiFi).
2. Operator opens "Share to Flight Viewer" on mobile A → code displays.
3. Desktop → + Add Feed → enters code → progress shows ICE checking → SAS phrase shown on both sides → accept.
4. Tile A appears, docked right. Live video within 5s. Status strip non-zero FPS, sane bitrate.
5. Mobile draws a detector box (move drone over a person) → desktop sees the box on the same frame; promotion event also shows in Tile A's detection list and the Mission Gallery, with thumbnail and GPS.
6. Repeat with mobile B → Tile B appears, both feeds run concurrently.
7. Drag Tile B onto Tile A's title → tabbed dock; both still receiving frames.
8. Float Tile A, full-screen it, Esc back → still connected.
9. Close Tile A → its services tear down; Tile B unaffected; Mission Gallery drops Tile A's rows.
10. Kill mobile B's WebRTC → Tile B transitions to `disconnected` cleanly; Reconnect from the tile menu works without app restart.
11. **Multi-viewer cap**: with mobile A already serving Tile A, a second desktop pairs to mobile A → both desktops receive frames concurrently; pair a third → still works; a fourth pair attempt shows the "drone has reached maximum viewers (3)" modal error and the dialog stays open for retry.
12. Quit desktop window → no leaked threads (Qt/asyncio warnings clean).

### Resilience smoke (§18)

13. **ICE-restart on cellular blip.** With Tile A connected and streaming, toggle the operator's tablet airplane mode on for ~15 s, then off. Mobile detects sustained `DISCONNECTED` (or `FAILED`), creates an ICE-restart offer on the same `RTCPeerConnection`, PUTs it to the Worker, desktop receives `{type:"offer", iceRestart:true}` and posts a fresh answer. Tile A status strip transitions through `ICE disconnected; awaiting recovery` → `ice-restart` → `ICE recovered`; video resumes within a few seconds without a fresh pairing-code dance and without rebuilding the peer connection. SAS phrase is unchanged.
14. **Snapshot replay after blip.** During the blip in step 13, the operator's drone surfaces 1–2 new gallery promotions. After ICE recovery, the desktop fires `_send_snapshot_request`; Tile A's detection list (and the Mission Gallery) catches up with the promotions that fired during the blackout. (Pending §18 → *Desktop residual work* item 2 until the snapshot signal is wired into the gallery UI.)
15. **DTLS-fingerprint guard.** If a publisher's DTLS identity ever changes mid-session (would indicate a bug or MitM, not a normal occurrence), the desktop's `_handle_reoffer` rejects the re-offer with "Peer DTLS fingerprint changed mid-session — closing for safety." This can't be triggered by a real network event; verify by running a synthetic re-offer through the test harness with a doctored fingerprint.
16. **Worker DO survives a 5+ minute session.** Hold a paired tile for at least 5 minutes with the operator's tablet idle for stretches > 30 s. The Worker's per-touch alarm bumping should keep the DO alive (no `closed: ttl expired` arrives on the WS). Verifies the resilience pass §18 TTL behavior.

## 15. Phasing

### M1 — Receiver online, single feed, docked shell (**Implemented**)

- ✅ `WebRTCStreamService` end-to-end against `aiortc`'s example publisher.
- ✅ `HttpSignalingChannel` against the `adiat-flight-signaling` Cloudflare Worker (URL from config; default `https://signal.adiat.app`).
- ✅ `FlightViewerWindow` as `QMainWindow` dock host. **Architecture supports multi-feed from day one even though M1 ships one.**
- ✅ One `FlightTile` working end-to-end with video display + status strip + pairing dialog.
- ✅ Add-Feed button in toolbar (exercises the multi-feed plumbing on day one).
- ✅ Unit tests for service lifecycle, signaling, pairing.
- 🔲 **DoD residual** — real ADIAT_Mobile publisher end-to-end pairing. Loopback + mocked-publisher paths are green; cross-app smoke against a tablet is the next gate (see §14).

### M2 — Detection sync + Mission Gallery

- DataChannel contract finalized with ADIAT_Mobile team.
- `DetectionFeedService` decodes meta + thumb pairs.
- Per-tile detection list.
- `MissionGalleryDock` aggregating across tiles; class/feed/confidence filters; DD/DM/MGRS coordinate copy.
- pytest-qt integration tests for multi-tile + gallery merge.
- **DoD:** Live mission with two feeds; promotions on either feed appear in their tile's list and merge in time order in the aggregate gallery. Detection thumbnails render. GPS copies in operator-preferred format.

### M3 — Robustness & polish

- ✅ **Publisher-initiated ICE restart** with sustained-`DISCONNECTED` debounce and immediate-on-`FAILED` trigger. End-to-end across mobile + Worker + desktop (§18). Same `RTCPeerConnection` survives the restart so SAS does not need re-confirmation.
- ✅ **`detections.snapshot` request channel** for state recovery after a reconnect — mobile replies with the current promoted-track set; desktop's `DetectionFeedService.detectionSnapshot` signal carries the list.
- ✅ **Don't tear down on transient hiccups** — mobile no longer deletes the signaling session on `FAILED`/`DISCONNECTED`; Worker re-arms the TTL alarm on every touch.
- 🔲 **WS reconnect with backoff** on the desktop's `HttpSignalingChannel.subscribe` — spec'd in §19.1.
- 🔲 **Mission Gallery snapshot consumer** — wire `DetectionFeedService.detectionSnapshot` into the per-tile gallery handler; spec'd in §19.2.
- 🔲 **Live telemetry HUD** consumer for the mobile-side `telemetry` DataChannel — spec'd in §19.3.
- 🔲 **Detection box overlay (timestamp-matched)** — desktop draws bboxes on the video tile, locked to the source frame via `frame_ts_ns`. Replaces the mobile-burnt-in path. §19.4.
- 🔲 Saved layouts (`QMainWindow.saveState` / `restoreState` via QSettings) — §19.5.1.
- 🔲 Full-screen-per-tile UX polish — §19.5.2.
- 🔲 TOFU fingerprint persistence — §19.5.3.
- 🔲 Map widget for detection locations (single dock; clicking a row centers the map) — §19.5.4.
- 🔲 Optional export of mission gallery into standard ADIAT image-mode gallery format — §19.5.5.
- 🔲 Recording via existing `VideoRecordingService` — §19.5.6.
- 🔲 `QRSignalingChannel` — §19.5.7.

## 16. Open questions for the desktop team

Status legend: ✅ resolved · 🟡 codified in v1 implementation, revisit after smoke · 🔲 still open.

1. ✅ **Signaling backend.** **Cloudflare Worker + Durable Objects** in the `adiat-flight-signaling` companion repo, deployed live at `https://signal.adiat.app`. Public Worker URL only — no client-side credentials anywhere. The desktop ships with the canonical URL as a default; operators can override in `config.toml` for self-hosting. *Originally Supabase; swapped because the desktop is OSS and we can't embed any backend credentials, even permission-scoped JWTs.*
2. ✅ **Codec policy.** **H.264-only.** Forces mobile hardware encode, decodes cleanly in PyAV. Worth the small fraction of edge cases where a viewer can't H.264.
3. 🟡 **Default dock layout.** v1 ships with first tile docking right; subsequent tiles tab into the same zone (per original recommendation). Revisit if ops feedback prefers a grid auto-layout.
4. 🟡 **Mission Gallery scope.** v1 ships per-session ephemeral (cleared on session end). Persistence across sessions is M3+; revisit when ops feedback comes in.
5. 🔲 **TURN policy.** Skip v1 (accept ~5–10% NAT failures), revisit once field failure rate is known. Recommendation still: **skip v1**.
6. 🔲 **DataChannel reliability vs. priority for thumbs.** Reliable+ordered (current proposal) vs. partial-reliability on `detections.thumb` to avoid blocking meta envelopes on a slow JPEG. Recommendation still: **reliable+ordered v1** (simpler; thumb sizes are small); reconsider if measurements show head-of-line stalls.
7. 🔲 **SFU growth path.** When/if field experience shows >3 viewers per drone is routine, the v1 pure-P2P-capped-at-3 model needs to evolve into an SFU-fronted model (see §4 → *Multi-viewer per feed*). Which SFU (mediasoup / livekit / ion-sfu / janus), and where is it hosted (operator-owned VPS / org-managed appliance / cloud)? Recommendation still: **defer the choice until v1 field data justifies it**; pre-deciding the SFU shape adds scope before it adds value.

## 17. Debugging & operations

### Worker URL configuration

| Surface | Variable / setting | Default |
|---|---|---|
| Desktop (`HttpSignalingChannel`) | `signaling.base_url` in `config.toml` (or constructor arg in tests) | `https://signal.adiat.app` |
| ADIAT_Mobile (`HttpSignalingChannel`) | `BuildConfig.SIGNALING_URL` (populated from `local.properties`) | `https://signal.adiat.app` |

Both sides ship with the same default — point both at the same URL when self-hosting. The `workers.dev` URL of any given Worker deploy is a usable fallback if the custom domain DNS is misconfigured.

### Tailing the Worker

The fastest pairing-flow debug aid is the Worker's live request log:

```
npx wrangler tail --name adiat-flight-signaling
```

Each `POST /v1/sessions`, `GET /offer`, `POST /answer`, `POST /ice/...`, and the WebSocket `subscribe` open/close appears in real time with status code, headers, and request body. Run it on the operator machine before starting a smoke pair; the absence of any request is itself diagnostic (network or wrong base URL on the client).

### Common failure modes

| Symptom | Likely cause | Where to look |
|---|---|---|
| Desktop "Code not found — confirm with the operator" | Code expired (>30s) or operator misread it; or mobile and desktop are pointed at different Worker URLs | `wrangler tail` will show whether the `GET /offer` for that code hit the Worker at all; cross-check `BuildConfig.SIGNALING_URL` vs desktop `config.toml` |
| Desktop "This code has already been used" | Race with another desktop, or the operator restarted the session and reused the code by accident — see §9 *Trust model* | Worker tail shows the timestamp of the first `POST /answer`; treat as a security signal, regenerate code |
| Pairing reaches `negotiating` then stalls | ICE connectivity check failure (double-symmetric NAT) — §1 non-goal | Worker tail shows the `POST /ice/...` candidates from both sides; if only one side ever posts, signaling is wrong, otherwise it's NAT |
| Pairing accepts but no video | SAS mismatch (operator/viewer should reject) or no media flowing because the publisher's track is disabled | Mobile side: `OverlayCompositor` requires `getOrCreateTrack` to have been called and `setEnabled(true)` after SAS confirm |
| Worker returns 5xx | Durable Object error in the Worker; `wrangler tail` shows the stack | Tag a release and roll back via `wrangler rollback` if it's a regression |
| Tile stuck on "ICE disconnected; awaiting recovery" for >5 s | Publisher's ICE-restart re-offer never arrived. Either the mobile didn't detect the failure, the WS connection from mobile to Worker is down, or the desktop's WS subscription has dropped silently (see §18 → *Desktop residual work* #1) | `wrangler tail` should show a `PUT /v1/sessions/:code/offer` from mobile within ~5 s of the disconnect. If absent, problem is mobile-side. If present but desktop didn't react, problem is the desktop's WS subscription. |
| Tile stuck on "ice-restart" indefinitely | Re-offer arrived but `_handle_reoffer` failed — typically `setRemoteDescription` rejecting a malformed SDP, or the DTLS-fingerprint guard tripping | Check the desktop log for `Peer DTLS fingerprint changed mid-session` (security close) or aiortc exception messages from `_handle_reoffer` |
| Worker `{type:"closed", reason:"ttl expired"}` arrives mid-session | TTL alarm wasn't bumped on a signaling touch (Worker bug) or the session was genuinely idle for > 30 s. Post-resilience-pass the latter shouldn't happen during normal use | Check `wrangler tail` for the chain of touches leading up to the close timestamp; if the gap > 30 s, that's the cause |

### Cost monitoring

Cloudflare's free tier is 100k Worker requests/day. A SAR mission averages on the order of 20 signaling requests per pairing (offer + answer + ~6 ICE candidates per side + a few subscribe round-trips). Even at 100 missions/day with 3 viewers each, that's ~6k requests — well inside free tier.

If `wrangler tail` ever shows a sustained burst that looks like abuse (same IP, same code attempted repeatedly), the Worker's per-DO TTL alarm self-cleans within 30s, but Cloudflare's standard rate-limiting rules can be applied at the zone level.

## 18. Resilience contract (ICE restart, snapshot replay, transient-failure tolerance)

This is the cross-app contract that mobile + Worker landed in May 2026 to keep a paired session alive across cellular blips, brief NAT reshuffles, and short network outages. The desktop side already implements most of its half; this section documents the contract and lists the two small follow-ups still needed on the desktop.

### What mobile does

1. **Watches `IceConnectionState`** on every peer connection (libwebrtc's per-ICE-agent state, not the aggregate `PeerConnectionState`).
2. **On sustained `DISCONNECTED`** (>= 5 s) **or any `FAILED`** state, generates an ICE-restart offer on the **same** `RTCPeerConnection` (Android's libwebrtc preserves the DTLS identity automatically when the `IceRestart: true` constraint is passed to `createOffer`). The munged H.264-only SDP goes to the Worker via `PUT /v1/sessions/:code/offer`.
3. **Recovery** (`CONNECTED` / `COMPLETED`) cancels any pending restart timer.
4. **Never deletes the signaling session** on transient ICE state changes. `DELETE /v1/sessions/:code` only fires from operator-initiated `stopSession` / `disconnectViewer` (or initial-handshake timeout).
5. **Snapshot replies.** Opens an outbound `detections.snapshot` DataChannel during pairing. On every `{"type":"request_snapshot"}` message that arrives on the desktop-opened `detections.snapshot_request` channel, replies on `detections.snapshot` with the current set of promoted tracks serialized as a JSON array of meta envelopes (thumb descriptors stripped, per §6 — "too bulky").
6. **Post-restart answer.** Subscribes to a long-lived `subscribeAnswers(code)` flow that surfaces every answer the desktop posts, in order. `awaitAnswer` consumes the first; a `drop(1)` collector consumes subsequent ones and applies them via the existing `peerConnection.acceptAnswer(sdp)` path (libwebrtc handles in-place renegotiation).
7. **WS reconnect with backoff.** The mobile's WS subscription is wrapped in a retry-with-backoff loop (1 s → 2 s → 4 s, capped at 30 s; reset on each successful connect). A transient WS drop during an active session no longer leaves the publisher deaf to ICE candidates or post-restart answers — the loop reattaches automatically and the Worker replays current state (stored answer + opposite-role ICE candidates) on each reconnect. Duplicate answer replays are deduplicated by SDP value so the session impl's re-offer collector only fires on genuine new answers. The loop exits only on scope cancellation (operator stop) or a server-sent `{type:"closed"}` (Durable Object genuinely gone).

### What the Worker does

1. **Bumps the DO inactivity alarm to `now + 30 s`** on every signaling touch (init, GET /offer, PUT /offer, POST /answer, POST /ice, WS subscribe). Long sessions no longer race the alarm.
2. **`PUT /v1/sessions/:code/offer`** replaces the stored offer with the publisher's re-offer SDP, **clears the stored answer** (so the next POST /answer is accepted rather than 409'd), and broadcasts `{type:"offer", sdp, iceRestart:true}` to every `role=desktop` watcher. Returns 200 on success, 404 if the session has already TTL'd.
3. **Schema tolerance.** `POST /answer` accepts either `{sdp}` or `{answer_sdp}`; `POST /ice/:role` accepts either flat `{candidate, sdpMid, sdpMLineIndex}` or wrapped `{candidate: {…}}`. This unblocks the existing desktop schema — no client-side changes required to fix the previous mismatch.
4. **`GET /offer` envelope.** Now returns `{type:"offer", sdp, offer_sdp}`. The legacy `offer_sdp` field is preserved for any existing reader; new code should read `sdp` to match the WS broadcast shape.

### What the desktop already does (no change required)

The receive code is already shaped for the contract:

- `WebRTCStreamService.iceconnectionstatechange` differentiates `disconnected` / `failed` / `closed` and refuses to give up on the first two — it waits up to `DEFAULT_ICE_RESTART_GRACE_SECONDS` (60 s) for a publisher-initiated re-offer.
- `_consume_signaling` already handles `msg_type == "offer"` via `_handle_reoffer`, which runs `setRemoteDescription` → `createAnswer` → `setLocalDescription` → `post_answer`, **without** rebuilding the peer connection.
- `_handle_reoffer` guards against DTLS-fingerprint changes mid-session ("Peer DTLS fingerprint changed mid-session — closing for safety"), defending against a hypothetical mid-session key swap.
- `_send_snapshot_request` fires on a `disconnected → connected` ICE recovery transition; `DetectionFeedService._handle_snapshot` decodes the reply as a list of meta envelopes and emits `detectionSnapshot`.
- `_tear_down` is the only call site for `signaling.delete_session`, so the desktop is already on the "delete only on explicit teardown" side of the contract.

### Desktop residual work

Two resilience items still owned by the desktop side, both spec'd in detail in §19:

1. **WebSocket reconnect with backoff** in `HttpSignalingChannel.subscribe` — without it, a brief WS drop during an active session leaves the desktop deaf to ICE candidates and re-offers. See §19.1.
2. **Mission Gallery snapshot consumer** — `DetectionFeedService.detectionSnapshot` is emitted but not yet wired into a tile/gallery handler, so the desktop misses promotions that fired during an ICE-restart blackout. See §19.2.

Both can ship independently of any further mobile/Worker work.

### Trust model addendum

The ICE-restart flow does **not** weaken the SAS-based MitM defense: the publisher reuses the same DTLS identity across the restart (Android's libwebrtc preserves the certificate as long as the same `RTCPeerConnection` instance is used), so the fingerprint the desktop captured during initial pairing matches the one in the re-offer's SDP. `_handle_reoffer` enforces this equality check explicitly and closes the session on mismatch. An attacker who somehow injected a re-offer with a different fingerprint would trigger the safety close, not a silent key-swap.

The Worker contributes no new trust surface — it only transports the SDP. An attacker with access to the Worker's database could read the offer/answer SDPs but cannot impersonate either peer without their DTLS private key.

## 19. Outstanding desktop specs

Specs for the four outstanding pieces of desktop work. Each is sized to ship as its own small PR; the four are independent of each other.

### 19.1 WebSocket reconnect with backoff

**Files.** `app/core/services/streaming/signaling/HttpSignalingChannel.py` (primary); `app/core/services/streaming/WebRTCStreamService.py` (consumer, no functional change but verify generator-cancel semantics).

**Problem.** `HttpSignalingChannel.subscribe` today is a single-shot async generator: it opens the WS, iterates `async for raw in ws`, and silently `return`s on the first exception. The consuming `_consume_signaling` task in `WebRTCStreamService` exits along with it, so a transient WS drop (idle timeout at Cloudflare's edge, brief cellular loss, server-initiated reset) leaves the desktop deaf to ICE candidates *and* deaf to any publisher-initiated `iceRestart` re-offer — even though the Worker is still alive and the publisher's WS is reconnecting.

**Solution.** Wrap the connect-and-iterate in a retry loop, matching the mobile-side fix already shipped in `ADIAT_Mobile/core/flightpublish/HttpSignalingChannel.kt`. Sketch:

```python
INITIAL_WS_BACKOFF = 1.0
MAX_WS_BACKOFF = 30.0

async def subscribe(self, code: str, role: str) -> AsyncIterator[dict]:
    _require_websockets()
    import websockets

    ws_url = self._http_to_ws(self._base_url)
    url = f"{ws_url}/v1/sessions/{code}/subscribe?role={role}"
    backoff = INITIAL_WS_BACKOFF

    while True:
        try:
            async with websockets.connect(
                url,
                ping_interval=20,        # detect dead connections
                ping_timeout=20,
                close_timeout=5,
            ) as ws:
                backoff = INITIAL_WS_BACKOFF   # reset on successful connect
                async for raw in ws:
                    msg = self._decode_frame(raw)
                    if msg is None:
                        continue
                    yield msg
                    if msg.get("type") == "closed":
                        return                 # terminal — DO gone
        except asyncio.CancelledError:
            raise                              # consumer cancel — propagate
        except Exception as exc:
            self.logger.debug(
                f"HttpSignalingChannel.subscribe: WS drop for "
                f"{code}/{role}: {exc}; retry in {backoff:.1f}s"
            )

        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, MAX_WS_BACKOFF)
```

**Exit conditions.**
- Server-sent `{type:"closed"}` (Durable Object torn down) — yield it so the consumer can react, then `return` cleanly.
- `CancelledError` (consumer task cancelled, e.g. `_tear_down` cancels `_signaling_task`) — re-raise; do not catch.
- Any other exception — log + sleep + retry.

**Worker companion fix.** The Worker now stores an `offerWasReplaced` flag (set on each `PUT /v1/sessions/:code/offer`). A reconnecting `role=desktop` watcher receives a replayed `{type:"offer", sdp, iceRestart:true}` *only* when this flag is set — so the happy-path reconnect (no restart happened during the drop) does not fire `_handle_reoffer` spuriously. If the publisher did restart while the desktop was disconnected, the reattach picks up the new offer transparently and `_consume_signaling`'s existing `msg_type == "offer"` branch applies it. Already deployed in `adiat-flight-signaling`.

**Dedup considerations.** ICE candidates are already idempotent in aiortc (`addIceCandidate` deduplicates). The desktop's `role=desktop` subscription never receives `answer` messages (those go to mobile), so no answer-replay dedup is required on this side.

**Testing.**
- Unit: `test_signaling_http_channel.py` — fake `websockets.connect` that yields a fixed sequence then raises, assert the generator retries.
- Integration: `test_flight_viewer_lifecycle.py` — driver flips a mock signaling backend off and on mid-session, assert the tile stays alive and ICE recovers.

**Sizing.** ~50 lines in `HttpSignalingChannel.subscribe` + ~80 lines of tests.

### 19.2 Mission Gallery snapshot consumer

**Files.** `app/core/controllers/flight/FlightTileController.py` (primary handler); `app/core/controllers/MissionGalleryController.py` (verify dedup at the aggregate layer).

**Problem.** `DetectionFeedService.detectionSnapshot` is emitted with a `list[dict]` payload (each element is a meta envelope, identical shape to `detections.meta`, with `thumb` descriptor stripped per publisher §6). It is currently not connected — so when `WebRTCStreamService._send_snapshot_request()` fires on ICE recovery and the publisher replies, the desktop receives the snapshot bytes, decodes them, emits the signal, and the signal is dropped on the floor. Any promotions that fired on the publisher side while the desktop's WS was disconnected stay missing from the per-tile detection list and the aggregate Mission Gallery.

**Solution.** Connect `detectionSnapshot` in `FlightTileController` and feed each envelope through the same path as a normal `detectionPromoted`, with `thumb_bytes=None`. Dedupe by `track_key` so a snapshot that includes a track the desktop already saw via live promotion is a no-op.

```python
class FlightTileController(QObject):
    def __init__(self, ...):
        ...
        self._known_track_keys: set[str] = set()
        self.detection_feed_service.detectionPromoted.connect(self._on_promotion)
        self.detection_feed_service.detectionUpdated.connect(self._on_update)
        self.detection_feed_service.detectionSnapshot.connect(self._on_snapshot)

    def _on_promotion(self, envelope: dict) -> None:
        track_key = envelope.get("track_key")
        if track_key:
            self._known_track_keys.add(track_key)
        self._render_promotion(envelope)
        # MissionGalleryController is connected separately to the
        # service's signals; do not double-emit here.

    def _on_snapshot(self, envelopes: list[dict]) -> None:
        for env in envelopes:
            track_key = env.get("track_key")
            if track_key and track_key in self._known_track_keys:
                continue                       # already shown via live promote
            if track_key:
                self._known_track_keys.add(track_key)
            merged = dict(env)
            merged["thumb_bytes"] = None
            self._render_promotion(merged)
```

**Edge cases.**
- Empty list `[]` from the publisher is a valid reply (no current tracks). No-op.
- Snapshot may arrive multiple times in a session (one per ICE recovery). Dedup by `track_key` is what keeps repeated snapshots from spawning duplicate rows.
- The publisher's snapshot envelopes preserve `event: "promote"` or `event: "update"` from the original PromotionEvent kind. `_render_promotion` treats both the same — the row already exists or it doesn't. The desktop should not emit a `detectionUpdated` for an unseen track from a snapshot; collapse to a single "promote" path.
- A `track_key` that arrives via snapshot **then** receives a live `detectionUpdated` later: the existing update flow already updates the row in place. Verify `MissionGalleryController` keys its row updates by `track_key` (it should; check at implementation time).

**Trigger paths.**
- `WebRTCStreamService.iceconnectionstatechange` already calls `_send_snapshot_request()` on `disconnected → connected` transition (§18). No new trigger plumbing required.
- Optional M3+: also call `_send_snapshot_request()` once on initial connect (post-SAS approval) so a desktop joining an in-progress session catches up on prior promotions. Currently the publisher only emits live promotions from the moment the desktop attaches, so an in-progress session catch-up is missing detections; the snapshot-on-attach pattern fixes that without extra protocol.

**Sizing.** ~60 lines in the controller + ~80 lines of pytest-qt tests.

### 19.3 Live telemetry HUD

**Files.** New `app/core/services/streaming/TelemetryFeedService.py`; new view `app/core/views/TelemetryHud.py`; small render hook in `FlightTile.py` / `FlightTileController.py`.

**Background.** Mobile now publishes a `telemetry` DataChannel alongside `detections.meta` / `.snapshot`. Payloads are UTF-8 JSON envelopes pushed at ~4 Hz (publisher-side throttle in `LiveViewViewModel`'s `combine(flightTelemetry, gimbalState, productState, deviceHealthState).sample(250 ms)`). The desktop has a placeholder comment at `FlightViewerController.py:169` but no consumer; the channel's bytes hit the floor.

**Wire format** (from `ADIAT_Mobile/core/flightpublish/TelemetryPublisher.kt → TelemetryEnvelope`):

```json
{
  "captured_at_ms": 1737310912345,
  "aircraft_name": "TEXSAR-01",
  "aircraft_serial": "1ZNDH6V0011234",
  "aircraft_latitude": 30.2672,
  "aircraft_longitude": -97.7431,
  "aircraft_altitude_msl_m": 312.4,
  "aircraft_altitude_agl_m": 25.6,
  "aircraft_yaw_deg": 90.5,
  "aircraft_pitch_deg": -1.2,
  "aircraft_roll_deg": 0.3,
  "gimbal_yaw_deg": 91.0,
  "gimbal_pitch_deg": -30.0,
  "gimbal_roll_deg": 0.0,
  "battery_percent": 82,
  "horizontal_speed_ms": 4.3,
  "vertical_speed_ms": -0.5,
  "is_flying": true,
  "flight_mode": "Normal"
}
```

Every field except `captured_at_ms` is nullable. Receivers must treat `null` (and missing keys) as "unknown" and not interpolate.

**Aircraft identity (`aircraft_name`, `aircraft_serial`).** Mobile sources `aircraft_name` from `ProductState.displayName` — the operator-set custom drone nickname when present, otherwise the DJI model name (e.g. `"M4E"`). `aircraft_serial` comes from `FlightControllerKey.KeySerialNumber` via `DeviceHealthState.serialNumber`. Both are sent on every envelope so a desktop joining mid-session, or one whose telemetry-cache flushed on reconnect, recovers the identity within ~250 ms. Both are `null` until the SDK reports a connected product (typical first second of any session).

These fields drive the desktop UX in two places:
- **Tile title** (see §4 *FlightTile*): prefer `aircraft_name` over the pairing code, falling back to the code when the name is null. `aircraft_serial` lives in the tile's right-click menu / status tooltip so the operator can disambiguate two identically-named drones if it ever matters.
- **Detection rows / Mission Gallery**: each per-tile detection list row is already implicitly scoped to its tile, so the aircraft identity comes for free. The **aggregate** Mission Gallery (§7) shows the source aircraft on every row using `tile.telemetry_feed_service.last_envelope["aircraft_name"]` — the live cache, not anything stamped into the meta envelope on the wire. This keeps the `detections.meta` payload lean while still letting the gallery show "PERSON · 87% · TEXSAR-01" instead of "PERSON · 87% · Tile-A".

**Service.** Mirror `DetectionFeedService`'s shape — a `QObject` that turns DataChannel bytes into a typed signal:

```python
TELEMETRY_LABEL = "telemetry"

class TelemetryFeedService(QObject):
    telemetryReceived = Signal(dict)   # parsed envelope
    feedError = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.logger = LoggerService()
        self._last_envelope: dict | None = None

    def handle_message(self, label: str, payload: bytes) -> None:
        if label != TELEMETRY_LABEL:
            return
        try:
            envelope = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.feedError.emit(f"malformed telemetry envelope: {exc}")
            return
        if not isinstance(envelope, dict):
            return
        self._last_envelope = envelope
        self.telemetryReceived.emit(envelope)

    @property
    def last_envelope(self) -> dict | None:
        return self._last_envelope
```

Wire it from `FlightTileController` the same way `DetectionFeedService` is wired:

```python
self.telemetry_feed_service = TelemetryFeedService(parent=self)
self.stream_service.dataChannelMessage.connect(
    self.telemetry_feed_service.handle_message
)
self.telemetry_feed_service.telemetryReceived.connect(self._on_telemetry)
```

`handle_message` filters by label, so connecting the unified `dataChannelMessage` signal to both `DetectionFeedService` and `TelemetryFeedService` is safe — each ignores labels it doesn't own.

**HUD render.** Lightweight transparent overlay on top of the video pane (Qt `QFrame` with `Qt.WA_TransparentForMouseEvents`), or a footer extension to the existing status strip. Operator preference: a compact two-row strip in the bottom of the tile, with optional pop-out into a dedicated dock when the operator wants more detail.

Suggested layout (compact):

```
LAT 30.2672  LON -97.7431  ALT 312 m MSL / 26 m AGL
HDG 091°     SPD 4.3 m/s   ↓0.5 m/s  BAT 82%   FLY · Normal
```

Field formatting:
- Coordinates: respect the operator's preferred format (DD / DM / MGRS) — pull from `Settings`. DD is fine for M1; DM/MGRS in M2 alongside the Mission Gallery's coordinate formatter (§7).
- Altitude: prefer the unit operator-preference in `Settings` (m vs. ft).
- Heading: degrees + a cardinal letter (N/NE/E/…); pad to 3 digits.
- Battery: append a colored chip — green ≥ 50, amber 20–49, red < 20.
- `is_flying = true` shows a small "FLY" pill; absent / `false` hides it.
- `flight_mode` rendered as-is (it's already the DJI display name from `FlightMode.displayName` on mobile).
- Null fields: render `—` (em dash) at that position. Don't hide the row — the layout shouldn't reflow with every missing field.

**Staleness.**
- 4 Hz is publisher-throttled; on a healthy session the HUD updates 4×/sec.
- If no envelope arrives for > 5 seconds, render the whole strip dimmed and append a small "stale Xs" badge — likely indicates the telemetry DataChannel is closed or the publisher is briefly offline; ICE may still be alive, but the HUD value is no longer fresh. Recover automatically on next arrival.

**Translations.** All visible labels go through `self.tr(...)` per CLAUDE.md §2.8.

**Sizing.** ~80 lines for `TelemetryFeedService` + ~150 lines for the HUD widget + ~100 lines of tests (envelope parsing edge cases + Qt render snapshot).

### 19.4 Detection box overlay (timestamp-matched, drone-motion safe)

**Files.** New `app/core/views/DetectionOverlayWidget.py`; wiring in `FlightTileController.py`.

**Background.** Mobile no longer burns detector boxes into the video stream — that path was costing the controller ~80–150 ms of single-threaded CPU per frame and capping the encoder at ~12 fps. Boxes now travel as plain `bbox_norm` over the `detections.meta` DataChannel; the desktop renders them on top of the video tile.

**The sync problem this spec solves.** The naive approach — "draw the latest box on the latest video frame" — has a fatal flaw for a moving drone. The meta envelope and its source video frame travel different transports: RTP video carries ~150 ms of total encoder + jitter buffer + decoder latency; SCTP DataChannel carries ~50 ms. So the meta arrives ~100 ms *before* the matching frame, and drawing it on the latest displayed frame puts the box ~100 ms behind. At a 5 m/s flight speed that's 0.5 m of camera motion — the box trails the actual target by half a meter in image space. Unacceptable for SAR where the operator needs to know exactly where the detector saw what.

**Solution: timestamp-matched display.** Mobile stamps every meta envelope with the source frame's publisher clock (`frame_ts_ns`, the same value passed to `VideoFrame.timestampNs`). Desktop learns the publisher↔RTP-clock offset once at session start, then for every meta finds the matching incoming video frame and draws the box on it. Sub-frame alignment, no drift regardless of drone speed.

**Wire contract.**

```json
{
  "event": "promote" | "update",
  "track_key": "person|<sessionId>|<trackId>",
  "detector_id": "person",
  "class_name": "person",
  "confidence": 0.87,
  "bbox_norm": [0.41, 0.55, 0.12, 0.18],
  "captured_at_ms": 1737310912345,
  "frame_ts_ns": 1737310912000000000,
  "location": { ... },
  "thumb": { ... }
}
```

`frame_ts_ns` is already shipping in the mobile build that includes this plan. Older publishers that omit it send `0` — desktop falls back to "latest box on latest frame" with documented drift.

**Components.**

```python
@dataclass
class ActiveTrack:
    envelope: dict
    frame_ts_ns: int            # source frame on the publisher clock
    received_at: float          # time.monotonic() of meta arrival
    bbox_norm: tuple[float, float, float, float]  # left, top, w, h

class DetectionOverlayWidget(QWidget):
    """Transparent child of FlightTile's video pane.

    paintEvent draws every active track's bbox scaled to the pane's
    current size, color-coded by detector_id. The render path is
    invoked from the controller right after the video QLabel updates
    its pixmap; both ride the same frame_ts_ns lookup, so the box and
    the frame appear together.
    """

    FRESHNESS_S = 5.0            # drop tracks not refreshed in this window
    OFFSET_SAMPLES = 5           # frames used to seed calibration
    OFFSET_REFINE_ALPHA = 0.05   # EWMA on offset after first seed
    PALETTE = {
        "person": (0xFB, 0x5E, 0x1C),
        "color-range": (0x58, 0xB7, 0xFF),
        "color-hsv":   (0x58, 0xB7, 0xFF),
        "motion":      (0xFF, 0xD5, 0x4F),
        "dji-native":  (0x4C, 0xAF, 0x50),
    }
```

**Calibration: learning the publisher↔RTP offset.**

libwebrtc converts `VideoFrame.timestampNs` to RTP timestamp by `rtp_ts = ns * 90_000 / 1_000_000_000 + session_random_offset`. aiortc exposes the RTP timestamp as `frame.time` (seconds, with the same random offset applied). The desktop doesn't know the offset a priori, but it can learn it from a single meta+frame pair:

```
offset_s = (meta.frame_ts_ns / 1_000_000_000) - matched_frame.frame_time_s
```

The challenge is identifying the "matched frame" the first time. Trick: when the desktop has buffered ~5 recent frames and the first meta envelope arrives, the meta's source frame is **the next one to arrive** (meta beats video by ~100 ms). So:

1. Buffer incoming frames into `recent_frames: deque[(frame_time_s, ndarray, local_arrival_s)]` (size ~30 ≈ 1 s at 30 fps).
2. On meta arrival when offset is `None`: stash the meta as `_pending_first_meta`.
3. On next frame arrival when `_pending_first_meta` is set:
   - Compute `offset_s = pending.frame_ts_ns / 1e9 - frame.time_s`.
   - Apply this as the initial offset.
   - Process the pending meta normally.
4. On subsequent metas: refine the offset via EWMA each time a near-match succeeds — small clocks drifts get corrected gradually without overshooting on a stale outlier.

**Per-frame render.**

`FlightTileController._on_frame_ready(ndarray, frame_time_s, frame_n)` runs after `WebRTCStreamService.frameReady` emits:

```python
def _on_frame_ready(self, ndarray, frame_time_s, frame_n):
    self._video_label.setPixmap(self._to_qpixmap(ndarray))
    # Drive the overlay AFTER pixmap update so QPainter sees the new
    # video frame underneath.
    self._overlay.on_video_frame(frame_time_s)

# In DetectionOverlayWidget:
def on_video_frame(self, frame_time_s: float) -> None:
    # Match each active track to whether this frame is "its" frame.
    # If the track's frame_ts_ns is within ±FRAME_WINDOW_NS of this
    # frame's mapped publisher time, the box is fresh for this frame.
    if self._publisher_offset_s is None:
        return                  # not calibrated yet
    self._current_frame_pub_s = (
        frame_time_s + self._publisher_offset_s
    )
    self.update()               # triggers paintEvent
```

`paintEvent` walks `self._tracks` and draws only those whose `frame_ts_ns / 1e9` is within `FRAME_WINDOW_S` (~50 ms = ~1.5 frames at 30 fps) of `self._current_frame_pub_s`. Tracks outside the window are skipped this frame — they appear on their own frame when it's the displayed one. With the calibration in place that lines up.

**Stale-track cleanup.** A track that hasn't received a Promote/Update for `FRESHNESS_S` is removed from `self._tracks` on the next `on_video_frame` — keeps the active set bounded and prevents long-gone targets from continuing to render.

**Resize behavior.** `bbox_norm` is normalized; `paintEvent` multiplies by `self.width()` / `self.height()` at draw time. Resizing the tile (or going full-screen per §19.5.2) just makes the boxes scale with the video pane — no recomputation, no resync work.

**Pane-sizing prerequisite (the "jumping tile" fix).** Today the video QLabel takes its size from the incoming pixmap. libwebrtc starts the encoder at a conservative resolution and ramps up to native over ~10–30 s (this is its bandwidth-estimation logic; not a bug). With the QLabel pixmap-sized, the whole tile visibly grows as the encoded resolution increases — and the detection overlay can't position boxes deterministically while the underlying pane is in motion. Fix on the desktop side: make the video pane a **fixed size** driven by the dock layout, and scale the incoming pixmap to fit. Specifically in `FlightTile.py`:

```python
# In __init__:
self._video_label = QLabel(parent=self)
self._video_label.setMinimumSize(640, 360)              # never collapse below 360p
self._video_label.setScaledContents(True)               # pixmap scales to label size
self._video_label.setSizePolicy(
    QSizePolicy.Expanding, QSizePolicy.Expanding,       # follow the dock layout
)
self._video_label.setAlignment(Qt.AlignCenter)
```

`setScaledContents(True)` makes Qt scale the pixmap (with nearest-neighbor by default; bilinear if Qt was built with `qsmoothpixmaptransform`). The aspect-ratio drift across libwebrtc resolution steps is hidden by the dock-layout-driven label size, so the tile and the overlay stay rock-solid through the encoder ramp.

If you want explicit aspect-ratio preservation regardless of dock layout, prefer:

```python
def _on_frame_ready(self, ndarray, frame_time_s, frame_n):
    pixmap = self._to_qpixmap(ndarray)
    scaled = pixmap.scaled(
        self._video_label.size(),
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation,
    )
    self._video_label.setPixmap(scaled)
    self._overlay.on_video_frame(frame_time_s)
```

The bitmap conversion runs once per frame and the smooth transform is GPU-accelerated on most platforms.

**Subscribed signals.**

```python
detection_feed_service.detectionPromoted.connect(overlay.on_track_event)
detection_feed_service.detectionUpdated.connect(overlay.on_track_event)
detection_feed_service.detectionSnapshot.connect(overlay.on_snapshot)
webrtc_stream_service.frameReady.connect(controller._on_frame_ready)
```

`on_track_event(envelope)` upserts `self._tracks[track_key] = ActiveTrack(...)`. `on_snapshot(list[envelope])` does the same in bulk, ignoring `track_key`s already present (live promote wins over a replayed snapshot).

**Failure modes.**

| Symptom | Cause | Behavior |
|---|---|---|
| Meta `frame_ts_ns == 0` | Legacy publisher (pre-this-PR) | Skip calibration; render every active track on every frame (drift returns; document as legacy mode). |
| Calibration `None` after 2 s | No meta arrived in the calibration window | Don't render boxes yet; calibration completes on the first promotion. |
| Offset drift | Long session, publisher clock skew | EWMA refine on each match keeps offset within a few ms over hours. |
| Track stays after target leaves frame | `last_seen` not refreshed for `FRESHNESS_S` | Auto-prune; no UI work needed. |

**Sizing.** ~250 lines for `DetectionOverlayWidget` + ~50 lines of `FlightTileController` wiring + ~120 lines of tests covering: calibration with simulated meta+frame pairs, EWMA refinement convergence, stale pruning, render-time scaling against synthetic pane sizes, and the `frame_ts_ns == 0` legacy fallback.

#### 19.4.1 Desktop-side thumbnail cropping (replaces mobile-sent JPEGs)

**Why.** Today every Promote/Update fires a ~30–50 KB JPEG on the `detections.thumb` DataChannel — cropped on the publisher by `BboxCropper.cropForTrack` and re-encoded on the M4E tablet. For SAR over cellular this is the difference between "smooth video" and "video stuttering because the JPEG burst saturated the uplink": at a 5 Hz detector cadence with 2–3 active tracks, that's 300–750 KB/s on top of the video. The desktop already has the source video frame (it's literally rendering it), it has spare CPU, and with the `frame_ts_ns` calibration we just plumbed for the box overlay it can pixel-lock the crop to the exact frame the detector saw. Cropping on the desktop side is a strict architectural improvement once the frame-buffer infrastructure is in place.

The mobile gallery is unaffected — `BboxCropper` continues to produce the crop locally for `AppPromotedResultPersistenceController` (Room + filesystem JPEG). The only thing going away on mobile is the JPEG encode + DataChannel send to remote viewers.

**What the desktop already has from §19.4.** The overlay widget maintains `recent_frames: deque[(frame_time_s, ndarray, local_arrival_s)]` (≈ 1 s of frames at 30 fps) and learns the publisher↔RTP offset on the first matched meta. Reuse the same buffer + offset for cropping.

**Component.** New `DetectionThumbCropper` (sibling of `DetectionOverlayWidget`, lives in the controller layer so its output is delivered to whichever consumer wants the row image — per-tile detection list, Mission Gallery, future export):

```python
class DetectionThumbCropper:
    """Crop per-detection thumbnails from the live video frame buffer.

    Subscribes to the same meta events as DetectionOverlayWidget. On
    each promote/update, finds the source frame in the overlay's
    recent_frames buffer (via the same publisher↔RTP offset), crops
    bbox_norm * frame.shape with a padding fraction (matches mobile's
    BboxCropper default of 20%), and emits a fully-formed gallery row
    payload identical to what the mobile-side JPEG path used to
    deliver.
    """

    PADDING_FRACTION = 0.20             # matches mobile BboxCropper
    MIN_PIXEL_EDGE = 96                 # matches mobile BboxCropper
    JPEG_QUALITY = 85                   # slightly higher than mobile's 80 — desktop has cycles

    thumbReady = Signal(str, bytes)     # (track_key, jpeg_bytes)

    def __init__(
        self,
        overlay: DetectionOverlayWidget,    # shares recent_frames + offset
        parent: QObject | None = None,
    ):
        ...

    def on_track_event(self, envelope: dict) -> None:
        frame_ts_ns = envelope.get("frame_ts_ns") or 0
        if frame_ts_ns == 0:
            # Legacy publisher (or snapshot replay) — fall back to
            # whatever the overlay's most recent frame is. Less accurate
            # but it's the same fallback the box overlay uses.
            ndarray = self._overlay.latest_frame()
        else:
            ndarray = self._overlay.frame_at_publisher_ts(frame_ts_ns)
            if ndarray is None:
                # Frame already evicted from the ring; drop this thumb.
                # The next Update will catch up.
                return
        bbox = self._scale_bbox(envelope["bbox_norm"], ndarray.shape)
        crop = self._crop_with_padding(ndarray, bbox)
        ok, buf = cv2.imencode(".jpg", crop, [int(cv2.IMWRITE_JPEG_QUALITY), self.JPEG_QUALITY])
        if not ok:
            return
        self.thumbReady.emit(envelope["track_key"], bytes(buf))
```

**Wiring.**

```python
overlay = DetectionOverlayWidget(parent=video_label)
cropper = DetectionThumbCropper(overlay=overlay, parent=self)
detection_feed_service.detectionPromoted.connect(overlay.on_track_event)
detection_feed_service.detectionPromoted.connect(cropper.on_track_event)
detection_feed_service.detectionUpdated.connect(overlay.on_track_event)
detection_feed_service.detectionUpdated.connect(cropper.on_track_event)
cropper.thumbReady.connect(detection_list.upsert_thumb)
cropper.thumbReady.connect(mission_gallery_controller.upsert_thumb)
```

The detection list and Mission Gallery row-upsert APIs are unchanged from what the mobile-cropped path fed them — they get a `track_key` + `jpeg_bytes`, key by `track_key`, replace the existing JPEG on each update.

**Edge cases**

| Case | Handling |
|---|---|
| Snapshot reply on ICE recovery | Mobile snapshot replies already strip thumb descriptors (per `PromotionPublisher.snapshotJson()`). Desktop's overlay populates `_tracks`; the cropper sees the snapshot event with `frame_ts_ns` but a frame that old isn't in `recent_frames` → no thumb until the next live Update. Same UX as today. |
| Track promoted while desktop tile is hidden / minimized | Frames still arrive; ring still updates. No regression. |
| Multi-tile (one drone → multiple desktops, multiple drones → one desktop) | Each `FlightTileController` owns its own overlay+cropper pair. Per-tile frame buffer; no cross-tile coupling. |
| `frame_ts_ns` calibration not yet learned | Fall back to "latest frame," same as the box overlay. |
| Bbox extends past frame edges (after padding) | Clamp to `[0, frame.shape]`; min-pixel-edge guarantee from mobile's BboxCropper carries over. |

**Mobile-side change (separate, follow-up)**

Once the desktop ships §19.4.1, the mobile publisher should stop sending the JPEG. The change is small:

```kotlin
// PromotionPublisher.publish:
//   - skip event.croppedThumbnail?.encodeToJpegOrNull(...)
//   - omit thumb descriptor from envelope (envelope.thumb = null)
//   - skip sink.sendThumb(thumbBytes)
// ViewerPeerConnection.start:
//   - keep creating the detections.thumb DataChannel for one release
//     of backwards-compat (desktops mid-upgrade ignore it cleanly);
//     remove the channel and the THUMB_CHANNEL_LABEL constant in the
//     release after that.
```

Until that lands, the desktop can ignore the incoming `detections.thumb` traffic and prefer its locally-cropped version. The architectural change ships on the desktop side; the bandwidth savings activate when mobile is updated to match.

**Sizing.** ~120 lines for `DetectionThumbCropper` + reuse-existing for the frame buffer + ~80 lines of tests (synthetic frames + envelopes verifying crop coordinates, padding, JPEG round-trip).

### 19.5 M3 polish — specs

Each item is sized to ship independently. Names map to the M3 bullets in §15.

#### 19.5.1 Saved layouts

**File.** `app/core/views/FlightViewerWindow.py` + a `QSettings` namespace per CLAUDE.md.

`closeEvent` calls `saveState()` / `saveGeometry()` into `QSettings("ADIAT", "FlightViewer")` under keys `state/v1` and `geometry/v1`. `showEvent` restores. The `/v1` suffix lets future structural changes invalidate stored state cleanly. Named-preset support (multiple layouts the operator can switch between via the toolbar) is a stretch — implement only the single-state restore in M3, add named presets after ops feedback.

Sizing: ~40 lines.

#### 19.5.2 Full-screen-per-tile polish

**File.** `app/core/views/FlightTile.py`.

Add an `F11` shortcut and a "Full Screen" entry to the tile's right-click menu. Toggle behavior:
- Enter full-screen: `self.setFloating(True); self.showFullScreen()`
- Exit (Esc or toggle again): `self.showNormal(); self.setFloating(prev_floating_state)`

Track the prior floating state so Esc returns the operator to the layout they had before, not always docked. Verify video keeps rendering during the floating-window transition (aiortc/Qt occasionally hiccups on widget reparent).

Sizing: ~30 lines.

#### 19.5.3 TOFU (trust-on-first-use) fingerprint persistence

**Files.** New `app/core/services/streaming/FingerprintStore.py` (SQLite-backed); hook into `FlightPairingDialog.confirm_sas`; warning UI in the dialog.

**Schema.**

```sql
CREATE TABLE IF NOT EXISTS peer_fingerprints (
    device_label TEXT PRIMARY KEY,        -- operator-assigned name
    sha256 TEXT NOT NULL,                 -- "sha-256 AB:CD:..." (full line)
    first_seen_epoch_s REAL NOT NULL,
    last_seen_epoch_s REAL NOT NULL,
    notes TEXT
);
```

**Flow.**
1. On the first successful SAS confirm, the dialog prompts the operator to give the publisher a label ("Operator A's M4E", "Tablet 3", …) and stores `(label, fingerprint, now, now)`.
2. On every subsequent connect that the user identifies as the *same* device (selected from a recent-devices dropdown in the pairing dialog), compare the incoming fingerprint to the stored one:
   - Match → update `last_seen_epoch_s`; proceed silently.
   - Mismatch → prominent warning modal: *"Device 'Operator A's M4E' presented a different DTLS fingerprint than the last time you paired with it. This could mean the tablet was reset, a different tablet is using the label, or somebody is impersonating it. Reject if you weren't expecting this."* Operator can Reject (close session) or Accept (overwrite the stored fingerprint with a note).
3. New pairings without a stored label are first-use and skip the comparison.

**UI.** Two surfaces in `FlightPairingDialog`: a "remember this device" checkbox + label field on first connect; a "recent devices" dropdown on subsequent connects.

Sizing: ~250 lines (store + dialog + tests).

#### 19.5.4 Map widget for detection locations

**Files.** New `app/core/views/MapDock.py` + `app/core/controllers/MapDockController.py`. Reuse whichever map library the rest of ADIAT Desktop already uses; check the existing map-using view (likely `ImageViewer` or `VideoReview`) for the library and pin-rendering helpers.

**Behaviour.**
- Single `QDockWidget`, toggled from the toolbar like Mission Gallery.
- Subscribes to `MissionGalleryController`'s row signal.
- One pin per detection with `aircraft_latitude` / `aircraft_longitude` (yes — pulls coords from each promotion envelope's `location` block, falling back to the telemetry envelope's last-known position if `location` is null).
- Pin color matches the per-detector palette mobile uses (`person` orange, `color-range` blue, `motion` amber, `dji-native` green). The palette is documented in `OverlayCompositor.kt → colorForDetector`.
- Click a Mission Gallery row → map pans + zooms to the corresponding pin.
- Click a pin → highlight the corresponding Mission Gallery row.

**Bounds.**
- Pure rendering — no edit / annotate flow in M3.
- Pins persist for the session, cleared on session end (same lifecycle as Mission Gallery).

Sizing: ~400 lines + tests.

#### 19.5.5 Export Mission Gallery to ADIAT image-mode gallery

**Files.** New `app/core/services/MissionGalleryExporter.py`; toolbar button in `MissionGalleryDock`.

**Format.** Match the existing ADIAT image-mode gallery on-disk layout (verify by reading the existing exporter / importer; it's likely a directory of JPEGs plus a metadata JSON). For each row in the Mission Gallery:
1. Write `<output_dir>/<track_key>.jpg` from the stored `thumb_bytes` (decoded from the meta envelope's `thumb` JPEG bytes, or skipped if the row has no thumb).
2. Append a `<output_dir>/manifest.json` line with the full envelope plus EXIF-style metadata (lat/lon if present, captured_at_ms → ISO timestamp).

**UI.** "Export…" entry on the Mission Gallery dock's overflow menu; standard `QFileDialog.getExistingDirectory`; progress bar for large galleries (rare — usually < 100 rows).

Sizing: ~150 lines + tests.

#### 19.5.6 Recording integration

**Files.** Hook in `FlightTileController.py`; reuse `app/core/services/streaming/VideoRecordingService.py` (the existing RTMP / file recorder).

**Flow.**
1. Tile context menu / toolbar: "Start Recording" toggle.
2. Start: instantiate `VideoRecordingService`, connect `WebRTCStreamService.frameReady` → `recorder.write_frame(ndarray, ts)`, set output path `~/Videos/ADIAT/<pairing-code>-<YYYYMMDDhhmmss>.mp4`.
3. Stop: disconnect the signal, `recorder.cleanup()`.
4. Tile shows a red "REC" badge while active.

**Caveats.**
- WebRTC frame timestamps are aiortc's monotonic-ish `frame.time`; the existing `VideoRecordingService` expects monotonic seconds — already compatible.
- A reconnect during recording resumes appending; if `VideoRecordingService` doesn't support resume on the same file, close + open a `-partN.mp4` continuation.

Sizing: ~150 lines + tests.

#### 19.5.7 QR / paste fallback signaling

**Files.** New `app/core/services/streaming/signaling/QRSignalingChannel.py` (implements `SignalingChannel`); new "Manual / Offline" tab in `FlightPairingDialog`.

**Use case.** Fully-offline pairing — no Worker, no internet — the operator and viewer are co-located on a LAN with no shared route to `signal.adiat.app`. The mobile generates an offer + ICE candidates, encodes them into a single blob, displays it as a QR code on the tablet and also as a long string in the clipboard. The desktop scans / pastes the blob, generates the answer, encodes that back, the operator scans / pastes it on the tablet. Two-way QR scan is rare in practice (neither device has a convenient camera angle), so paste is the realistic primary path; QR is a "nice to have".

**Format.** Single base64-encoded JSON blob:

```json
{
  "v": 1,
  "role": "offer" | "answer",
  "sdp": "v=0...",
  "ice": [
    {"candidate":"candidate:1 ...", "sdpMid":"0", "sdpMLineIndex":0},
    ...
  ],
  "fingerprint": "sha-256 AB:CD:..."
}
```

Size: typical SDP is ~2 KB; with full ICE candidate set ~3-4 KB. QR encodes up to ~3 KB at QR version 40 + low correction; for paste there is no practical limit.

**Implementation.** `QRSignalingChannel.get_offer` / `post_answer` / etc. become user-interaction-driven: the channel pops up the dialog tab asking the operator to scan/paste; nothing goes over the network. ICE trickle is not supported in this mode — all candidates must be gathered before encoding (set a `iceGatheringTimeout` of ~2 s, then encode whatever was collected).

**Bounds.**
- M3 is for the paste path with manual blob exchange. QR scan is M3+ stretch — depends on the desktop machine having a webcam at the right angle.
- TURN unsupported in this mode; only works on the same LAN.
- No SAS step needed — the human-driven blob exchange is the trust anchor in this flow (the operator is physically present with the viewer or has an established trust channel).

Sizing: ~400 lines (channel + dialog tab + tests). Deprioritized — operators with internet access have the much-easier Worker path; this is for fully-offline ops.

## 20. Session continuity (reconnect-with-same-code)

A planned follow-up to §18 that lets a desktop be closed and reopened — accidentally or deliberately — and resume the same publish session without the field operator doing anything. Same pairing code, same video, all prior detections still visible.

**Operational driver.** SAR scenes: a search coordinator's laptop battery dies, their power adapter is in the truck, or they accidentally close the window mid-flight. Making them walk to the controller for a fresh code is unacceptable on an active mission — the operator is busy flying. §18 covers transient network blips on a live peer connection; §21 covers the harder case where the entire desktop process has gone away.

### Lifecycle states

Three states replace today's two:

| State | Mobile | Worker | Desktop |
|---|---|---|---|
| **Active** | publishing video + telemetry + detections | answer posted, WS bridged | rendering live |
| **Awaiting** *(new)* | publishing continues; that viewer's PC torn down; offer kept fresh | offer retained, answer slot cleared, TTL extended | not connected |
| **Ended** | publish toggle off OR aircraft gone OR operator-clicked Disconnect | DO deleted | reconnect impossible |

Operator-initiated stop, aircraft-disconnect, and operator-clicked **Disconnect** on a per-viewer row all go straight to **Ended** for that viewer. A desktop crash / app close transitions that viewer's slot **Active → Awaiting** instead. Other viewers' slots are unaffected.

### Authorization model

The pairing code is the only credential. Possession = permission; there is no viewer identity binding. This is deliberate:

- A desktop drops; another viewer with the same code can step in.
- A desktop crashes permanently; the operator doesn't need to issue a new code.
- The cost is that anyone who knows the code can attach during an Awaiting window — but the code is already a shared secret distributed verbally / by text on-mission; this trust model is unchanged from v1.

Race resolution at the mobile session impl:

| Mobile slot state when a new answer arrives | Behavior |
|---|---|
| **Active** (someone already attached on this slot) | Reject with `409 already_attached`. Desktop UI: *"Another viewer is connected — wait or ask them to disconnect."* |
| **Awaiting** | Accept. First answer wins; a later auto-resume from the original viewer sees `409` and the operator-facing *"Session taken over by another viewer."* |

### Mobile changes (`:core:flightpublish`)

1. **Session-id stamp.** Generate a UUID at `startSession()`. Include `session_id` on every MetaEnvelope, TelemetryEnvelope, and signaling write. Desktop uses it to distinguish "this is a fresh mobile session, discard history" from "same session, dedupe by seq".
2. **Monotonic event sequence.** `PromotionPublisher` assigns `seq: Long` to every promote/update event. Persisted alongside the in-memory state.
3. **Session history ring buffer.** Bounded (default 1000 events) of all MetaEnvelopes since `startSession()` — *not* just live tracks held by `currentEnvelopes`. This is the source of truth for backfill on reconnect.
4. **Per-viewer Awaiting state.** Today's `ViewerPhase` gains an `AwaitingReconnect` variant. When a specific viewer's WS orphan-close arrives:
   - Tear down that viewer's `PeerConnection` (releases the encoder slot, saves battery).
   - Keep the viewer row in the slot list with its code preserved.
   - Flip status to `AwaitingReconnect`.
   - Other viewers' slots are unaffected.
5. **Publisher-side telemetry continues.** Telemetry collection, detector pipeline, and the history ring buffer keep running while *any* slot is Awaiting — so a returning viewer gets fresh state immediately. Only H.264 encoding for that slot pauses (no PC = no sink).
6. **Resume handshake.** The previous PC was torn down on `viewer_left`, so the slot needs a fresh PC + offer before any new answer can be applied to a working ICE/DTLS context. Two triggers can start the rebuild — whichever fires first wins; the second is a no-op:
   - **Primary — `viewer_returning`**: the Worker broadcasts this when a `role=desktop` WS reattaches in the awaiting state. Mobile builds a fresh PC + offer and PUT's it to the Worker, which broadcasts a `{type:"offer", iceRestart:true}` to the desktop. The desktop's `_handle_reoffer` path applies the new SDP and POSTs a fresh answer.
   - **Fallback — stale-answer arrival**: the desktop's auto-resume flow calls `GET /offer` on the Worker and may POST an answer against the *stale* stored offer before `viewer_returning` round-trips back to mobile. Mobile detects this (answer arrives while the slot is in `AwaitingReconnect`), **discards the stale answer**, and kicks off the same rebuild. The desktop's existing `_handle_reoffer` then picks up the fresh offer broadcast on its WS and POSTs a fresh answer.

   Either way, the slot transitions `AwaitingReconnect → Negotiating` once the fresh offer is published, then `Negotiating → Active` when the fresh answer arrives. The ICE-restart path from §18 is *not* reused — this is a full new PC because the previous one was disposed.

   **Phase update ordering matters.** The slot must enter `Negotiating` *before* the fresh offer is PUT to the Worker. The desktop's fresh answer can otherwise race the phase update; the answer collector keys off phase to decide accept-vs-discard, and an answer arriving while still `AwaitingReconnect` would be treated as another stale-offer answer (which only triggers a no-op rebuild since one is already in flight).
7. **Backfill responder.** New inbound messages on the existing `detections.snapshot_request` / `detections.snapshot` channel pair, distinguished by a `kind` field:
   - Desktop sends `{kind: "resume", session_id, last_seq}` on `snapshot_request`.
   - If `session_id` matches the current mobile session, mobile streams all history-ring events where `seq > last_seq` on `detections.meta` in order, then sends `{kind: "resume_complete", session_id, last_seq: <highest>}`.
   - If `session_id` doesn't match (fresh mobile session, stale desktop), mobile replies `{kind: "session_changed", new_session_id}` and desktop discards its local history for the old session.
8. **No auto-timeout.** Awaiting slots stay Awaiting indefinitely. The operator clears them with the existing per-viewer **Disconnect** button on the share popout. Toggling the whole share off clears every Awaiting slot. (See *Decisions locked* below.)

### Worker changes (`adiat-flight-signaling`)

1. **No eager orphan teardown.** When the last `role=desktop` watcher for a slot leaves *after* an answer was posted, don't call `teardown`. Instead clear the slot's `answer` field, set the slot to `state: "awaiting_viewer"`, and refresh the TTL alarm. The mobile heartbeat keeps the DO warm; if mobile *also* goes away, the DO genuinely TTLs and the slot disappears.
2. **Mobile-driven teardown is authoritative.** Only operator stop or `DELETE /v1/sessions/:code` from mobile (or the mobile heartbeat dropping past the TTL window) tears the DO down.
3. **`GET /v1/sessions/:code/state`** *(new)* — returns `{state: "active"|"awaiting_viewer"|"ended", session_id?, has_offer}`. Desktop calls this on reconnect to confirm the code is still alive *before* re-prompting the operator.
4. **Existing `PUT /v1/sessions/:code/offer`** covers the case where mobile needs to publish a fresh offer for a reconnecting viewer (same shape as the ICE-restart path from §18; the Worker doesn't need to distinguish them).

### Desktop changes (`adiat_ai`)

1. **Persisted session.** On every successful pairing, write `{worker_url, code, session_id, ts}` to QSettings (encrypted via the existing keychain helper if available). Clear the entry on operator-initiated disconnect.
2. **Auto-resume on launch.** If a persisted session exists, call `GET /v1/sessions/:code/state`:
   - `awaiting_viewer` + `session_id` matches → skip the pairing dialog, post a new answer, show a non-blocking "Reconnecting…" overlay with a Cancel button.
   - `active` (some other viewer attached) → show the normal pairing dialog with the last code pre-filled; operator can ask the other viewer to step aside, or wait.
   - `ended` / 404 → clear the persisted entry, show the empty pairing dialog.
3. **Local detection store.** Append every MetaEnvelope to SQLite keyed by `(session_id, seq)`. Snapshot JPEGs (the desktop-cropped per-track thumbnails from §19.4.1) stay on disk keyed the same way. This is what survives an accidental app close.
4. **Resume message on reconnect.** Once the data channels reopen, send `{kind: "resume", session_id, last_seq}` on `detections.snapshot_request`. Render incoming backfill events on `detections.meta` as if they arrived live; rows insert in order, deduplicated by `(session_id, seq)`.
5. **Session-mismatch path.** If mobile replies `{kind: "session_changed", new_session_id}`, prompt the operator: *"Mobile started a new flight. Archive previous detections, or discard?"* Default: archive (rename SQLite session bucket; start a fresh one for the new session_id).
6. **Stale-code fallback.** If `GET /state` returns 404 or `ended`, show the empty pairing dialog (the persisted entry has already been cleared in step 2's logic).

### Wire format additions

```text
# Every MetaEnvelope gains:
session_id: "<uuid>"
seq: <long, monotonic per publish session>

# Every TelemetryEnvelope gains:
session_id: "<uuid>"

# Desktop → mobile on detections.snapshot_request:
{ kind: "resume", session_id: "<uuid>", last_seq: <long> }

# Mobile → desktop on detections.meta (in response to resume):
# - stream of backfill MetaEnvelopes (each carries its own session_id + seq), in order, followed by:
{ kind: "resume_complete", session_id: "<uuid>", last_seq: <long> }
# OR, if session_id is stale:
{ kind: "session_changed", new_session_id: "<uuid>" }

# New Worker endpoint:
GET /v1/sessions/:code/state
→ 200 { state: "active"|"awaiting_viewer"|"ended", session_id?: "<uuid>", has_offer: bool }
→ 404 if the session doesn't exist or has fully TTL'd
```

### UI

The mobile-side share popout is the only visible change. The per-viewer row gains an "Awaiting reconnect" label — amber dot using `AdiatColors.SignalAmber`, text in `TextSecondary`. The existing **Disconnect** button on the row is still the operator's explicit "drop this slot" action. No toast, no sidebar badge, no countdown.

The desktop's "Reconnecting…" overlay during auto-resume is a small non-blocking indicator; no operator action is required unless the Worker reports the session has ended.

### Decisions locked

| # | Decision | Choice |
|---|---|---|
| 1 | Awaiting timeout | None. Operator manages via per-viewer **Disconnect**; toggling share off clears all Awaiting slots. |
| 2 | History ring buffer size | 1000 events (~hours of typical SAR detection rate). |
| 3 | Auto-resume freshness | Whatever the Worker reports — no client-side freshness check beyond `GET /state`. |
| 4 | Multi-desktop policy | Code is the credential; possession = permission. Active rejects with 409; Awaiting accepts first answer. |
| 5 | Encode while Awaiting | Pause H.264 encode for that slot only. Detector pipeline + telemetry keep running so a returning viewer gets fresh state. |
| 6 | Aircraft loss during Awaiting | Flushes every slot (Active *and* Awaiting) to Ended. No aircraft = nothing to publish. |

### Sequencing

This is a planned milestone, separate from the §18 resilience contract that's already shipped. The pieces are independent and can ship in this order:

1. **Worker** — non-teardown-on-orphan + `GET /state` endpoint. Ships first because it's backward-compatible: existing clients don't notice the change.
2. **Mobile** — session_id + seq stamping, history ring buffer, `AwaitingReconnect` viewer state, backfill responder, UI label. Ships second.
3. **Desktop** — persisted session, auto-resume on launch, local SQLite store, resume message on reconnect, session-mismatch prompt. Ships third (depends on 1 + 2).

## 21. References

- `CLAUDE.md` — engineering standards.
- `app/core/services/streaming/RTMPStreamService.py` — public surface to mirror.
- `app/core/services/streaming/contracts.py` — algorithm-side contracts (referenced for the future clean-feed variant).
- aiortc: https://aiortc.readthedocs.io/
- WebRTC trust model: RFC 8826 (Security Considerations), RFC 5763 (DTLS-SRTP).
- WebRTC DataChannel: RFC 8831.
- `adiat-flight-signaling` Worker source: https://github.com/crgrove/adiat-flight-signaling
- Companion mobile publisher plan: `ADIAT_Mobile/flight_viewer_publish_plan.md`.
