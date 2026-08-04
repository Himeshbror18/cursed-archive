#!/usr/bin/env python3
"""
領域展開 DOMAIN EXPANSION — Camera Hand-Sign Simulator (Python / OpenCV + MediaPipe)
=============================================================================
Show your hand to the camera. The number of raised fingers determines
which Domain Expansion you cast:

    0 ✊  -> Domain Amplification      (orange)
    1 ☝  -> Cursed Technique Ember    (gold)
    2 ✌  -> Unlimited Void            (blue)      — Satoru Gojo
    3 🤟 -> Chimera Shadow Garden     (cyan)      — Megumi Fushiguro
    4 🖖 -> Malevolent Shrine          (purple)    — Ryomen Sukuna
    5 🖐 -> Self-Embodiment of Perfection (white)  — Mahito

Effects applied to the live webcam feed:
  * Full-screen cursed-energy color grade (per domain)
  * Glowing particle storm swirling to the center
  * Rotating kanji ring + expanding domain shockwave
  * Domain name banner with character art reveal
  * White flash + shockwave ring on activation

Requirements:
    pip install opencv-python mediapipe numpy pillow

Usage:
    python3 domain_expansion_cam.py
    python3 domain_expansion_cam.py --no-mirror
    python3 domain_expansion_cam.py --camera 1
Press ESC to exit.
"""

import argparse
import math
import os
import random
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Optional Pillow — used to overlay the high-quality character art
# ---------------------------------------------------------------------------
try:
    from PIL import Image, ImageDraw, ImageFont
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

# ---------------------------------------------------------------------------
# Imports — MediaPipe
# ---------------------------------------------------------------------------
try:
    import mediapipe as mp
    HAVE_MP = True
except ImportError:
    HAVE_MP = False


# ===========================================================================
# DOMAIN DATABASE
# ===========================================================================
@dataclass
class Domain:
    fingers: int
    name: str
    kanji: str
    big_kanji: str
    user: str
    bgr: tuple            # OpenCV BGR
    hsv_shift: int        # hue rotation for the color grade
    saturation: float
    char_img: str | None  # path to character art (assets/...)
    desc: str


DOMAINS = [
    Domain(
        fingers=0, name="DOMAIN AMPLIFICATION", kanji="領域展開", big_kanji="域",
        user="BARRIER TECHNIQUE", bgr=(67, 112, 255), hsv_shift=0, saturation=1.4,
        char_img="assets/black_flash.png",
        desc="A barrier technique that coats the body in cursed energy like armor.",
    ),
    Domain(
        fingers=1, name="CURSED TECHNIQUE EMBER", kanji="術式解放", big_kanji="術",
        user="SORCERER'S RELEASE", bgr=(79, 213, 255), hsv_shift=15, saturation=1.5,
        char_img="assets/cursed_energy.png",
        desc="One finger raised — the seal of a sorcerer about to release their technique.",
    ),
    Domain(
        fingers=2, name="UNLIMITED VOID", kanji="無量空処", big_kanji="無",
        user="SATORU GOJO", bgr=(247, 195, 79), hsv_shift=90, saturation=1.6,
        char_img="assets/gojo.png",
        desc="The endless void floods the target's mind with infinite information.",
    ),
    Domain(
        fingers=3, name="CHIMERA SHADOW GARDEN", kanji="嵌合暗翳庭", big_kanji="影",
        user="MEGUMI FUSHIGURO", bgr=(218, 198, 38), hsv_shift=140, saturation=1.5,
        char_img="assets/megumi.png",
        desc="The world becomes living shadow, and shikigami tear free from every surface.",
    ),
    Domain(
        fingers=4, name="MALEVOLENT SHRINE", kanji="伏魔御厨子", big_kanji="魔",
        user="RYOMEN SUKUNA", bgr=(255, 136, 179), hsv_shift=200, saturation=1.8,
        char_img="assets/sukuna.png",
        desc="Cleave and Dismantle rain down as an unavoidable storm. Nothing survives.",
    ),
    Domain(
        fingers=5, name="SELF-EMBODIMENT OF PERFECTION", kanji="自閉円頓裹", big_kanji="円",
        user="MAHITO", bgr=(220, 220, 207), hsv_shift=260, saturation=0.9,
        char_img="assets/mahito.png",
        desc="The dome of countless hands. Idle Transfiguration — a guaranteed hit.",
    ),
]

DOMAIN_BY_FINGERS = {d.fingers: d for d in DOMAINS}


# ===========================================================================
# FINGER COUNTING (MediaPipe landmark logic — same as the web version)
# ===========================================================================
def count_fingers(landmarks) -> int:
    """Count raised fingers from a MediaPipe hands landmark list (21 pts)."""
    tips = [4, 8, 12, 16, 20]
    pips = [3, 6, 10, 14, 18]

    count = 0
    wrist = landmarks[0]
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    # thumb extended when further from wrist than its IP joint
    if abs(thumb_tip.x - wrist.x) > abs(thumb_ip.x - wrist.x) + 0.03:
        count += 1
    # other fingers: tip y above pip y
    for f in range(1, 5):
        tip = landmarks[tips[f]]
        pip = landmarks[pips[f]]
        if tip.y < pip.y - 0.03:
            count += 1
    return count


# ===========================================================================
# UTILITIES
# ===========================================================================
def apply_color_grade(frame: np.ndarray, domain: Domain) -> np.ndarray:
    """Tint / hue-rotate / saturate the frame toward the domain's color."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 0] = (hsv[:, :, 0] + domain.hsv_shift) % 180
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * domain.saturation, 0, 255)
    frame = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    # subtle overlay tint
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), domain.bgr, -1)
    frame = cv2.addWeighted(overlay, 0.12, frame, 0.88, 0)

    # vignette
    h, w = frame.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    center = (w // 2, h // 2)
    cv2.ellipse(mask, center, (int(w * 0.52), int(h * 0.52)), 0, 0, 360, 255, -1)
    mask = cv2.GaussianBlur(mask, (151, 151), 0)
    dark = np.zeros_like(frame)
    dark[:] = (10, 10, 10)
    frame = np.where(mask[:, :, None] > 0, frame, cv2.addWeighted(dark, 0.7, frame, 0.3, 0))
    return frame


def draw_glow_text(frame, text, org, font_scale, color, thickness=2, glow_color=None, glow=6):
    """Draw text with an outer glow."""
    glow_color = glow_color or color
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, font_scale, glow_color, thickness + glow)
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
    return frame


def load_char_overlay(domain: Domain, base_dir: Path, size=(380, 480)):
    """Load the character PNG as an RGBA overlay, resized, centered on transparent."""
    if not HAVE_PIL:
        return None
    path = base_dir / domain.char_img
    if not path.exists():
        return None
    try:
        img = Image.open(str(path)).convert("RGBA")
    except Exception:
        return None
    img.thumbnail((size[0], size[1]), Image.LANCZOS)
    canvas = Image.new("RGBA", img.size, (0, 0, 0, 0))
    canvas.paste(img, (0, 0), img)
    return np.array(canvas, dtype=np.uint8)


def overlay_rgba(frame, rgba, x, y):
    """Blit an RGBA image onto a BGR frame at (x, y)."""
    ih, iw = rgba.shape[:2]
    h, w = frame.shape[:2]
    x = int(max(0, min(x, w - 1)))
    y = int(max(0, min(y, h - 1)))
    rh = min(ih, h - y)
    rw = min(iw, w - x)
    if rh <= 0 or rw <= 0:
        return frame
    roi = frame[y : y + rh, x : x + rw]
    ov = rgba[:rh, :rw].astype(np.float32)
    fg = ov[:, :, :3]
    alpha = (ov[:, :, 3] / 255.0)[:, :, None]
    frame[y : y + rh, x : x + rw] = (roi * (1 - alpha) + fg * alpha).astype(np.uint8)
    return frame


def put_text_cjk(frame, text, org, font_scale, color, thickness=2):
    """Draw text — falls back to simple font if the glyph isn't supported."""
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)


# ===========================================================================
# PARTICLE SYSTEM
# ===========================================================================
@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    r: float
    life: float
    decay: float
    color: tuple
    base_x: float
    base_y: float


def spawn_particle(w, h, domain):
    base_x = w * (0.15 + random.random() * 0.7)
    base_y = h * (0.15 + random.random() * 0.7)
    return Particle(
        x=base_x, y=base_y,
        vx=(random.random() - 0.5) * 2.0,
        vy=(random.random() - 0.5) * 2.0,
        r=random.random() * 3.2 + 1.0,
        life=1.0,
        decay=0.003 + random.random() * 0.008,
        color=domain.bgr,
        base_x=base_x, base_y=base_y,
    )


def update_particles(particles, w, h, domain, swirl=True):
    for p in particles:
        p.x += p.vx
        p.y += p.vy
        p.life -= p.decay
        if p.life <= 0:
            particles.remove(p)
            continue
        if swirl:
            dx = w / 2 - p.x
            dy = h / 2 - p.y
            dist = math.hypot(dx, dy) or 1.0
            p.vx += (dx / dist) * 0.06
            p.vy += (dy / dist) * 0.06
            p.vx *= 0.985
            p.vy *= 0.985
        if p.x < 0 or p.x > w or p.y < 0 or p.y > h:
            particles.remove(p)


def draw_particles(frame, particles):
    for p in particles:
        alpha = max(0.0, min(1.0, p.life))
        color = tuple(int(c * alpha) + int(255 * (1 - alpha) * 0.05) for c in p.color)
        cv2.circle(frame, (int(p.x), int(p.y)), max(1, int(p.r * alpha)), color, -1, cv2.LINE_AA)
        # glow dot
        cv2.circle(frame, (int(p.x), int(p.y)), max(2, int(p.r * 2.5 * alpha)),
                   (color[0] // 3, color[1] // 3, color[2] // 3), -1, cv2.LINE_AA)


# ===========================================================================
# MAIN APP
# ===========================================================================
class DomainExpansionCam:
    def __init__(self, camera_id: int = 0, mirror: bool = True, char_dir: str | None = None):
        self.mirror = mirror
        self.domain: Domain | None = None
        self.prev_domain: Domain | None = None
        self.last_finger_count = -1
        self.stable_since = 0.0
        self.activation_time = 0.0
        self.frames_seen = 0
        self.particles: list[Particle] = []
        self.base_dir = Path(char_dir) if char_dir else Path(__file__).resolve().parent
        if not (self.base_dir / "assets").exists():
            # try to locate cursed-archive/assets relative to the repo root
            for candidate in [
                Path(__file__).resolve().parent.parent / "assets",
                Path(__file__).resolve().parent / ".." / "assets",
                Path.cwd() / "cursed-archive" / "assets",
                Path.cwd() / "assets",
            ]:
                if candidate.exists():
                    self.base_dir = candidate
                    break
        self.char_cache: dict[str, np.ndarray | None] = {}

        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            print("[!] Could not open camera", camera_id)
            sys.exit(1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.mphands = None
        if HAVE_MP:
            mp_hands = mp.solutions.hands
            self.mphands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            print("  [ok] MediaPipe Hands loaded")

        self.window_name = "領域展開 DOMAIN EXPANSION SIMULATOR"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 1280, 800)

        # banner font metrics
        self.banner_h = 0
        self.banner_w = 0

    # -- finger signal -------------------------------------------------------
    def on_finger_count(self, count: int, now: float):
        if count == self.last_finger_count:
            if self.stable_since == 0.0:
                self.stable_since = now
            held = now - self.stable_since
            if held > 0.45:
                if self.domain and self.domain.fingers == count:
                    return
                d = DOMAIN_BY_FINGERS.get(count)
                if d and d is not self.domain:
                    self.trigger_domain(d)
        else:
            self.last_finger_count = count
            self.stable_since = now if count >= 0 else 0.0

    def trigger_domain(self, d: Domain):
        self.prev_domain = self.domain
        self.domain = d
        self.activation_time = time.time()
        print(f"\n  領域展開 — {d.name} ・ {d.kanji}  ({d.user})")
        # replenish particles
        self.particles = [
            spawn_particle(self.frame_w, self.frame_h, d) for _ in range(160)
        ]

    # -- rendering ----------------------------------------------------------
    def render_frame(self, frame: np.ndarray, hand_landmarks=None) -> np.ndarray:
        h, w = frame.shape[:2]
        self.frame_w, self.frame_h = w, h

        if self.mirror:
            frame = cv2.flip(frame, 1)

        # --- color grade ---
        if self.domain:
            frame = apply_color_grade(frame, self.domain)
        else:
            frame = np.clip(frame.astype(np.float32) * 0.92, 0, 255).astype(np.uint8)

        # --- particles ---
        if self.domain:
            target = 160
            while len(self.particles) < target:
                self.particles.append(spawn_particle(w, h, self.domain))
            update_particles(self.particles, w, h, self.domain, swirl=True)
            draw_particles(frame, self.particles)
        else:
            target = 60
            while len(self.particles) < target:
                self.particles.append(spawn_particle(w, h, DOMAINS[4]))
            update_particles(self.particles, w, h, DOMAINS[4], swirl=False)
            draw_particles(frame, self.particles)

        # --- domain kanji ring + shockwave ---
        if self.domain:
            t = time.time() - self.activation_time
            # expanding shockwave
            ring_t = (t % 2.4) / 2.4
            radius = int(30 + ring_t * min(w, h) * 0.7)
            cv2.circle(frame, (w // 2, h // 2), radius, self.domain.bgr, 2, cv2.LINE_AA)
            # rotating kanji
            R = int(min(w, h) * 0.22)
            for i in range(8):
                a = t * 0.6 + i * math.pi / 4
                x = int(w / 2 + math.cos(a) * R)
                y = int(h / 2 + math.sin(a) * R)
                alpha = 0.5 + 0.5 * math.sin(t * 2 + i)
                color = tuple(int(c * alpha + 40 * (1 - alpha)) for c in self.domain.bgr)
                cv2.putText(frame, self.domain.big_kanji, (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2, cv2.LINE_AA)
            # center kanji stamp
            draw_glow_text(frame, self.domain.kanji, (w // 2 - 60, h // 2),
                           2.0, self.domain.bgr, 3, glow=8)

        # --- hand skeleton overlay ---
        if hand_landmarks:
            mp_drawing = mp.solutions.drawing_utils
            mp_hands = mp.solutions.hands
            for lm in hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, lm, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(200, 200, 255), thickness=1)
                )

        # --- info bar ---
        self.draw_ui(frame)

        # --- activation flash ---
        if self.domain:
            elapsed = time.time() - self.activation_time
            if elapsed < 0.5:
                strength = (1.0 - elapsed / 0.5) * 0.55
                white = np.full_like(frame, 255, dtype=np.uint8)
                frame = cv2.addWeighted(white, strength, frame, 1 - strength, 0)
            if elapsed < 1.1:
                ring_t = elapsed / 1.1
                radius = int(20 + ring_t * max(w, h) * 0.8)
                cv2.circle(frame, (w // 2, h // 2), radius, (255, 255, 255), 3, cv2.LINE_AA)
                cv2.circle(frame, (w // 2, h // 2), radius, self.domain.bgr, 1, cv2.LINE_AA)

        return frame

    def draw_ui(self, frame: np.ndarray):
        h, w = frame.shape[:2]

        # --- top banner ---
        banner_h = 74
        self.banner_h, self.banner_w = banner_h, w
        color = self.domain.bgr if self.domain else (255, 255, 255)
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, banner_h), (5, 5, 10), -1)
        cv2.line(overlay, (0, banner_h - 1), (w, banner_h - 1), color, 2)
        frame = cv2.addWeighted(overlay, 0.85, frame, 0.15, 0)

        if self.domain:
            draw_glow_text(frame, self.domain.name, (18, 34), 0.9, color, 2, glow=4)
            cv2.putText(frame, self.domain.kanji, (w - 140, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2, cv2.LINE_AA)
        else:
            cv2.putText(frame, "FORM YOUR HAND SIGN TO CAST A DOMAIN", (18, 34),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (180, 180, 200), 2, cv2.LINE_AA)

        # finger count pill (top-right of frame area)
        finger = self.last_finger_count
        label = "HAND SIGN: --" if finger < 0 else f"HAND SIGN: {finger}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        px = 12
        py = banner_h + 30
        cv2.rectangle(frame, (px, py - 22), (px + tw + 20, py + 8), (10, 10, 20), -1)
        cv2.rectangle(frame, (px, py - 22), (px + tw + 20, py + 8), (120, 120, 140), 1)
        cv2.putText(frame, label, (px + 10, py), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 220, 240), 2, cv2.LINE_AA)

        # --- status pill (bottom center) ---
        status = self.domain.name if self.domain else "AWAITING HAND SEAL"
        (stw, sth), _ = cv2.getTextSize(status, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)
        sx = w // 2 - stw // 2 - 20
        sy = h - 55
        cv2.rectangle(frame, (sx, sy - 24), (sx + stw + 40, sy + 12), (10, 10, 20), -1)
        cv2.rectangle(frame, (sx, sy - 24), (sx + stw + 40, sy + 12), color, 1)
        cv2.putText(frame, status, (sx + 20, sy), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    color, 2, cv2.LINE_AA)

        # --- character art reveal (right side) ---
        if self.domain:
            overlay_img = self.get_char_overlay(self.domain)
            if overlay_img is not None:
                ih, iw = overlay_img.shape[:2]
                x = w - iw - 16
                y = h - ih - 16
                # soft drop shadow
                shadow = np.zeros_like(overlay_img)
                shadow[:, :, 3] = (overlay_img[:, :, 3] * 0.35).astype(np.uint8)
                frame = overlay_rgba(frame, shadow, x + 6, y + 6)
                frame = overlay_rgba(frame, overlay_img, x, y)

        # --- legend (bottom-left) ---
        legend_y = h - 120
        cv2.putText(frame, "0:FIST  1:INDEX  2:PEACE  3:THREE  4:FOUR  5:PALM",
                    (12, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (160, 160, 180), 1, cv2.LINE_AA)
        cv2.putText(frame, "ESC/ Q: QUIT", (12, legend_y + 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 120, 140), 1, cv2.LINE_AA)

    def get_char_overlay(self, domain: Domain):
        if domain.char_img in self.char_cache:
            return self.char_cache[domain.char_img]
        img = load_char_overlay(domain, self.base_dir)
        self.char_cache[domain.char_img] = img
        return img

    # -- main loop -----------------------------------------------------------
    def run(self):
        print("=" * 62)
        print("  領域展開 DOMAIN EXPANSION — camera hand-sign simulator")
        print("=" * 62)
        if not HAVE_MP:
            print("  [!] mediapipe not installed — run:")
            print("      pip install opencv-python mediapipe numpy pillow")
            sys.exit(1)

        while True:
            ok, frame = self.cap.read()
            if not ok:
                break
            self.frames_seen += 1
            now = time.time()

            # --- hand tracking ---
            hand_landmarks = None
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.mphands.process(rgb)
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks
                lm = results.multi_hand_landmarks[0].landmark
                count = count_fingers(lm)
                self.on_finger_count(count, now)
            else:
                self.on_finger_count(-1, now)

            out = self.render_frame(frame, hand_landmarks)
            cv2.imshow(self.window_name, out)

            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord('q'), ord('Q')):
                break

        self.cap.release()
        cv2.destroyAllWindows()
        if self.mphands:
            self.mphands.close()
        print("\n  ✦ Domain closed. See you next expansion.")


# ===========================================================================
# ENTRY POINT
# ===========================================================================
def main():
    parser = argparse.ArgumentParser(
        description="領域展開 — Hand-sign Domain Expansion camera simulator"
    )
    parser.add_argument("--camera", type=int, default=0, help="camera device index (default 0)")
    parser.add_argument("--no-mirror", action="store_true", help="disable mirrored preview")
    parser.add_argument(
        "--assets",
        type=str,
        default=None,
        help="path to the cursed-archive directory containing an assets/ folder",
    )
    args = parser.parse_args()

    app = DomainExpansionCam(
        camera_id=args.camera,
        mirror=not args.no_mirror,
        char_dir=args.assets,
    )
    app.run()


if __name__ == "__main__":
    main()