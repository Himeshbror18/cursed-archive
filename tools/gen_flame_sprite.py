#!/usr/bin/env python3
"""
Anime-style cursed energy flame sprite sheet generator (pure Python, no deps).
Generates an 8-frame horizontal sprite sheet of a flickering flame with
fractal turbulence, layered core/glow, per-character colors.
"""
import zlib, struct, math, random, os

OUT = "/home/himesh/Documents/pt2/cursed-archive/assets/ce"
os.makedirs(OUT, exist_ok=True)

FW, FH, FRAMES = 160, 200, 8  # per-frame size, number of frames

def write_png(path, w, h, rgb_rows):
    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)
        return c
    raw = b"".join(b"\x00" + row for row in rgb_rows)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)

def value_noise(w, h, seed, octaves=5, scale=0.03):
    rnd = random.Random(seed)
    gw = max(2, int(w * scale) + 2)
    gh = max(2, int(h * scale) + 2)
    grid = [[rnd.random() for _ in range(gw)] for _ in range(gh)]
    def sample(px, py):
        gx = px * scale
        gy = py * scale
        x0 = int(gx) % gw
        y0 = int(gy) % gh
        x1 = (x0 + 1) % gw
        y1 = (y0 + 1) % gh
        tx = gx - int(gx)
        ty = gy - int(gy)
        tx = tx * tx * (3 - 2 * tx)
        ty = ty * ty * (3 - 2 * ty)
        return (grid[y0][x0] * (1 - tx) + grid[y0][x1] * tx) * (1 - ty) + \
               (grid[y1][x0] * (1 - tx) + grid[y1][x1] * tx) * ty
    noise = [[0.0] * w for _ in range(h)]
    amp = 1.0
    freq = 1.0
    total = 0.0
    for o in range(octaves):
        for y in range(h):
            for x in range(w):
                noise[y][x] += sample(x * freq, y * freq) * amp
        total += amp
        amp *= 0.5
        freq *= 2.0
    for y in range(h):
        for x in range(w):
            noise[y][x] /= total
    return noise

def flame_frame(w, h, frame_idx, seed, rgb, glow_rgb, core_rgb):
    """Render one flame frame. frame_idx 0..7 drives the flicker phase."""
    r_r, r_g, r_b = rgb
    gl_r, gl_g, gl_b = glow_rgb
    co_r, co_g, co_b = core_rgb
    # evolving seed per frame -> organic flicker
    noise = value_noise(w, h, seed + frame_idx * 101, octaves=6, scale=0.04)
    cx, cy = w * 0.5, h * 0.72
    # phase-driven wobble / height
    ph = (frame_idx / FRAMES) * math.tau
    sway = math.sin(ph) * 0.06
    lunge = math.sin(ph * 2) * 0.08  # flame height pulsing
    rows = []
    for y in range(h):
        row = bytearray()
        for x in range(w):
            dx = (x - cx) / (w * 0.5) + sway
            dy = (y - cy) / (h * 0.60) - lunge
            d = math.sqrt(dx * dx + dy * dy)
            # anime-style flame shape: wide base, tapering split tips
            taper = 1.0 - abs(dx) * (0.65 + 0.85 * (1 - y / h))
            n = noise[y][x]
            # layered turbulence
            val = max(0.0, 1.0 - d * (1.1 + 0.45 * (n - 0.5)))
            flame = val ** 2.0 * (0.6 + 0.65 * n) * taper
            # two-tip anime flame: secondary lobe
            d2 = math.sqrt((dx - 0.22) * (dx - 0.22) + (dy + 0.25) * (dy + 0.25))
            flame2 = max(0.0, 1.0 - d2 * 1.8) ** 2.4 * (0.4 + 0.4 * n)
            flame = max(flame, flame2)
            # inner core (bright white-hot)
            core = max(0.0, 1.0 - d * 2.8) ** 1.7
            # outer glow
            glow = max(0.0, 1.0 - d * 0.95) ** 2.6
            r = int(min(255, r_r * flame + gl_r * glow * 0.8 + co_r * core))
            g = int(min(255, r_g * flame + gl_g * glow * 0.8 + co_g * core))
            b = int(min(255, r_b * flame + gl_b * glow * 0.8 + co_b * core))
            row += bytes((r, g, b))
        rows.append(bytes(row))
    return rows

def make_sprite(name, rgb, glow_rgb, core_rgb, seed):
    """Render FRAMES frames side by side into one sprite sheet PNG."""
    sheet_w, sheet_h = FW * FRAMES, FH
    # pre-render each frame as list-of-rows
    frames = [flame_frame(FW, FH, i, seed, rgb, glow_rgb, core_rgb) for i in range(FRAMES)]
    rows = []
    for y in range(FH):
        row = bytearray()
        for f in frames:
            row += f[y]
        rows.append(bytes(row))
    write_png(os.path.join(OUT, name), sheet_w, sheet_h, rows)
    print(f"OK {name} ({sheet_w}x{sheet_h}, {FRAMES} frames)")

# Character cursed-energy flames (anime-style saturated colors)
flames = [
    ("flame_blue.png",    (80, 150, 255), (120, 200, 255), (230, 248, 255), 101),
    ("flame_crimson.png", (255, 70, 80),  (255, 120, 130), (255, 230, 230), 202),
    ("flame_purple.png",  (175, 95, 255), (215, 155, 255), (255, 235, 255), 303),
    ("flame_teal.png",    (45, 205, 215), (85, 235, 240), (220, 250, 250), 404),
    ("flame_orange.png",  (255, 125, 45), (255, 175, 95), (255, 238, 205), 505),
    ("flame_green.png",   (85, 215, 115), (135, 240, 155), (230, 255, 240), 606),
    ("flame_gold.png",    (255, 195, 65), (255, 220, 125), (255, 247, 220), 707),
    ("flame_violet.png",  (145, 75, 225), (185, 115, 250), (242, 224, 255), 808),
]

for args in flames:
    make_sprite(*args)
print("=== FLAME SPRITES DONE ===")