#!/usr/bin/env python3
"""
Procedural Cursed Energy flame texture generator (pure Python, no deps).
Writes RGBA PNG via zlib+struct. Produces layered, glowing cursed-energy
flames with fractal noise, color per character, for the JJK page.
"""
import zlib, struct, math, random, os

OUT = "/home/himesh/Documents/pt2/jjk_panels_ce"
os.makedirs(OUT, exist_ok=True)

def write_png(path, w, h, rgb_rows):
    """rgb_rows: list of rows, each row is bytes of RGB triplets (no alpha)."""
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

def value_noise(w, h, seed, octaves=5, scale=0.02):
    rnd = random.Random(seed)
    grid_w = max(2, int(w * scale) + 2)
    grid_h = max(2, int(h * scale) + 2)
    grid = [[rnd.random() for _ in range(grid_w)] for _ in range(grid_h)]
    def sample(px, py):
        gx = px * scale
        gy = py * scale
        x0 = int(gx) % grid_w
        y0 = int(gy) % grid_h
        x1 = (x0 + 1) % grid_w
        y1 = (y0 + 1) % grid_h
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

def flame_texture(name, w, h, rgb, glow_rgb, core_rgb, seed):
    """Generate a flame/energy burst with radial falloff + noise turbulence."""
    r_r, r_g, r_b = rgb
    gl_r, gl_g, gl_b = glow_rgb
    co_r, co_g, co_b = core_rgb
    noise = value_noise(w, h, seed, octaves=6, scale=0.035)
    cx, cy = w * 0.5, h * 0.75  # base of flame at bottom-center
    rows = []
    for y in range(h):
        row = bytearray()
        for x in range(w):
            dx = (x - cx) / (w * 0.5)
            dy = (y - cy) / (h * 0.65)
            d = math.sqrt(dx * dx + dy * dy)
            # flame body: rises upward, narrower near top
            taper = 1.0 - abs(dx) * (0.7 + 0.6 * (1 - y / h))
            n = noise[y][x]
            # fractal turbulence displaces the flame shape
            val = max(0.0, 1.0 - d * (1.15 + 0.35 * (n - 0.5)))
            flame = val ** 2.2 * (0.65 + 0.6 * n) * taper
            # inner core (bright)
            core = max(0.0, 1.0 - d * 2.6) ** 1.8
            # outer glow (soft, additive)
            glow = max(0.0, 1.0 - d * 1.1) ** 2.5
            r = int(min(255, r_r * flame + gl_r * glow * 0.75 + co_r * core * 0.9))
            g = int(min(255, r_g * flame + gl_g * glow * 0.75 + co_g * core * 0.9))
            b = int(min(255, r_b * flame + gl_b * glow * 0.75 + co_b * core * 0.9))
            row += bytes((r, g, b))
        rows.append(bytes(row))
    write_png(os.path.join(OUT, name), w, h, rows)
    print(f"OK {name} {w}x{h}")

# Character cursed-energy colors (manga aesthetics: bright saturated energy)
flames = [
    # name, w, h, body_rgb, glow_rgb, core_rgb, seed
    ("ce_blue.png",     400, 480, (70, 140, 255), (100, 190, 255), (220, 245, 255), 11),  # Gojo / Itadori blue
    ("ce_purple.png",   400, 480, (170, 90, 255), (210, 150, 255), (255, 230, 255), 22),  # Sukuna purple
    ("ce_teal.png",     400, 480, (40, 200, 210), (80, 230, 235), (215, 250, 250), 33),   # Megumi teal
    ("ce_orange.png",   400, 480, (255, 120, 40), (255, 170, 90), (255, 235, 200), 44),   # Nobara orange
    ("ce_green.png",    400, 480, (80, 210, 110), (130, 235, 150), (225, 255, 235), 55),  # Toji green
    ("ce_gold.png",     400, 480, (255, 190, 60), (255, 215, 120), (255, 245, 215), 66),  # Nanami gold
    ("ce_crimson.png",  400, 480, (255, 60, 70),  (255, 110, 120), (255, 225, 225), 77),  # Itadori red
    ("ce_violet.png",   400, 480, (140, 70, 220), (180, 110, 245), (240, 220, 255), 88),  # Geto violet
]

for args in flames:
    flame_texture(*args)
print("=== CE GENERATION DONE ===")