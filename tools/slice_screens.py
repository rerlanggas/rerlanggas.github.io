#!/usr/bin/env python3
"""
Slice App Store screenshot sheets into individual phone screens.

The masters in assets/screenshots/*.jpg are four-up submission sheets: portrait
screens laid side by side on a light canvas, separated by gutters, usually with
white margins around the outside. This finds the panels so a single clean screen
can be cropped out for the portfolio card thumbnails.

No Pillow/numpy/ImageMagick on this machine, so ffmpeg decodes to a raw PPM and
the analysis is plain Python.

Usage:
    python3 tools/slice_screens.py detect            # print detected panels
    python3 tools/slice_screens.py candidates        # write every panel to /tmp
    python3 tools/slice_screens.py build             # write the chosen thumbnails
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "screenshots")
THUMB = os.path.join(SRC, "thumb")

# Which panel to use per app, chosen by eye after reviewing `candidates` output.
# Index is into the detected panel list (0-based), left to right. Picked for strong
# colour and a recognisable screen at ~108px wide, avoiding edge-clipped panels.
# (myxl 0 is reported as "clipped" only because it starts at x=0; it is complete.)
CHOICE = {
    "myxl": 0,          # NEW PACKAGE / Bebas Puas — boldest branding
    "empatkali": 2,     # Merchant — colourful product grid
    "petparade": 3,     # Furr-friends — big puppy photo
    "catfishing": 1,    # title screen with the game logo
    "askfast": 0,       # pink/teal gradient sign-in
    "teamtelefoon": 1,  # contact list, colourful avatars fill the frame
    "schoolryde": 0,    # onboarding illustration over a navy block
    "nantiaja": 1,      # brand grid — the only fully unclipped colourful panel
}


def decode(path):
    """Return (width, height, pixels) where pixels is a bytes object of RGB triples."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "image2pipe", "-vcodec", "ppm", "-"],
        capture_output=True, check=True).stdout
    # Parse the PPM header: P6 <w> <h> <maxval>, whitespace separated, then binary.
    fields, idx = [], 2
    while len(fields) < 3:
        while raw[idx:idx + 1].isspace():
            idx += 1
        if raw[idx:idx + 1] == b"#":                 # comment line
            while raw[idx:idx + 1] not in (b"\n", b""):
                idx += 1
            continue
        start = idx
        while not raw[idx:idx + 1].isspace():
            idx += 1
        fields.append(int(raw[start:idx]))
    w, h, _maxval = fields
    return w, h, raw[idx + 1:]


def column_is_background(px, w, h, x, thresh=232, ratio=0.97, flat_range=32, flat_min=205):
    """True if column x is canvas or gutter rather than content.

    Two ways to qualify. Either the column is overwhelmingly near-white, or it is
    a near-constant light colour top to bottom — EmpatKali's gutters are cream and
    NantiAja's are pale mint, and a pure-white test merges their panels together.
    """
    light = 0
    step = 2                                          # sampling every other row is plenty
    lo, hi = 255, 0
    n = 0
    for y in range(0, h, step):
        o = (y * w + x) * 3
        r, g, b = px[o], px[o + 1], px[o + 2]
        if r >= thresh and g >= thresh and b >= thresh:
            light += 1
        v = (r * 299 + g * 587 + b * 114) // 1000      # luma
        lo = v if v < lo else lo
        hi = v if v > hi else hi
        n += 1
    if light >= ratio * n:
        return True
    return (hi - lo) <= flat_range and lo >= flat_min


def row_is_background(px, w, h, y, thresh=232, ratio=0.97):
    light = 0
    step = 2
    cols = range(0, w, step)
    o0 = y * w * 3
    for x in cols:
        o = o0 + x * 3
        if px[o] >= thresh and px[o + 1] >= thresh and px[o + 2] >= thresh:
            light += 1
    return light >= ratio * len(range(0, w, step))


def runs_of_content(flags):
    """Given a per-index 'is background' list, return (start, end_exclusive) content runs."""
    out, start = [], None
    for i, is_bg in enumerate(flags):
        if not is_bg and start is None:
            start = i
        elif is_bg and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(flags)))
    return out


def analyse(path):
    w, h, px = decode(path)

    # Vertical trim first: removes the big white bands at the bottom of some sheets.
    row_bg = [row_is_background(px, w, h, y) for y in range(h)]
    rows = runs_of_content(row_bg)
    top, bottom = (rows[0][0], rows[-1][1]) if rows else (0, h)

    col_bg = [column_is_background(px, w, h, x) for x in range(w)]
    panels = [(a, b) for (a, b) in runs_of_content(col_bg) if (b - a) >= w * 0.06]

    return dict(w=w, h=h, top=top, bottom=bottom, panels=panels)


def crop_args(info, panel):
    x0, x1 = panel
    return dict(x=x0, y=info["top"], w=x1 - x0, h=info["bottom"] - info["top"])


def sheets():
    for name in sorted(os.listdir(SRC)):
        if name.endswith(".jpg"):
            yield name[:-4], os.path.join(SRC, name)


def cmd_detect():
    for key, path in sheets():
        i = analyse(path)
        clipped = []
        for n, (a, b) in enumerate(i["panels"]):
            if a <= 1 or b >= i["w"] - 1:
                clipped.append(n)
        print(f"{key:14} {i['w']}x{i['h']}  content rows {i['top']}-{i['bottom']}"
              f"  panels={len(i['panels'])}  clipped={clipped or '-'}")
        for n, p in enumerate(i["panels"]):
            c = crop_args(i, p)
            print(f"    [{n}] x={c['x']:4} w={c['w']:4}  h={c['h']:4}"
                  f"  aspect={c['w']/c['h']:.3f}"
                  + ("   <-- CLIPPED" if n in clipped else ""))


def cmd_candidates():
    out = "/tmp/panels"
    os.makedirs(out, exist_ok=True)
    for key, path in sheets():
        i = analyse(path)
        for n, p in enumerate(i["panels"]):
            c = crop_args(i, p)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path,
                            "-vf", f"crop={c['w']}:{c['h']}:{c['x']}:{c['y']}",
                            f"{out}/{key}-{n}.png"], check=True)
    print("wrote candidates to", out)


def cmd_build():
    os.makedirs(THUMB, exist_ok=True)
    total = 0
    for key, path in sheets():
        i = analyse(path)
        n = CHOICE[key]
        c = crop_args(i, i["panels"][n])
        # No upscaling: panels are 199-273px wide natively, which already covers a
        # 108px CSS box at 2x. Scaling up would only add blur and bytes.
        tmp = f"/tmp/{key}-chosen.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path,
                        "-vf", f"crop={c['w']}:{c['h']}:{c['x']}:{c['y']}",
                        tmp], check=True)
        dst = os.path.join(THUMB, key + ".webp")
        subprocess.run(["cwebp", "-quiet", "-q", "80", tmp, "-o", dst], check=True)
        size = os.path.getsize(dst)
        total += size
        print(f"{key:14} panel {n}  -> {size:6,} bytes")
    print(f"{'TOTAL':14}          {total:6,} bytes")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "detect"
    {"detect": cmd_detect, "candidates": cmd_candidates, "build": cmd_build}[cmd]()
