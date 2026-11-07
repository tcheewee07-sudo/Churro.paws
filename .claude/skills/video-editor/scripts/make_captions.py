#!/usr/bin/env python3
"""Turn a Whisper word-timestamp JSON into brand-styled .ass captions.

Usage:
  make_captions.py transcript.json out.ass [--width 1080] [--height 1920]
                   [--offset 0.0] [--max-words 3] [--font "Plus Jakarta Sans ExtraBold"]

Burn in with:  ffmpeg -i in.mp4 -vf "ass=out.ass" ...
Brand defaults come from the "Saved brand" table in SKILL.md.
"""
import argparse, json, re

def ass_color(hex_rgb):  # "#ffb37b" -> "&H007BB3FF" (ASS is BGR)
    h = hex_rgb.lstrip("#")
    return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}".upper()

def ts(t):
    t = max(t, 0)
    h, rem = divmod(t, 3600); m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"

p = argparse.ArgumentParser()
p.add_argument("json"); p.add_argument("out")
p.add_argument("--width", type=int, default=1080)
p.add_argument("--height", type=int, default=1920)
p.add_argument("--offset", type=float, default=0.0, help="seconds to shift captions")
p.add_argument("--max-words", type=int, default=3)
p.add_argument("--font", default="Plus Jakarta Sans ExtraBold")
p.add_argument("--text", default="#f7f4ff")
p.add_argument("--highlight", default="#ffb37b")
p.add_argument("--outline", default="#150f26")
a = p.parse_args()

words = [w for s in json.load(open(a.json))["segments"] for w in s.get("words", [])]

# Group into short chunks, breaking after punctuation.
chunks, cur = [], []
for w in words:
    cur.append(w)
    if len(cur) >= a.max_words or re.search(r"[.!?,]$", w["word"].strip()):
        chunks.append(cur); cur = []
if cur: chunks.append(cur)

vertical = a.height > a.width
size = round(a.width * (0.085 if vertical else 0.05))
margin_v = round(a.height * (0.28 if vertical else 0.08))  # above platform UI on 9:16
style = (f"Style: Brand,{a.font},{size},{ass_color(a.text)},{ass_color(a.text)},"
         f"{ass_color(a.outline)},&H64000000,-1,0,0,0,100,100,3,0,1,"
         f"{max(4, size // 14)},2,2,60,60,{margin_v},1")

lines = [
    "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {a.width}", f"PlayResY: {a.height}",
    "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
    "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
    "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    style, "", "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
]
hi = ass_color(a.highlight)
for ci, ch in enumerate(chunks):
    chunk_end = chunks[ci + 1][0]["start"] if ci + 1 < len(chunks) else ch[-1]["end"] + 0.4
    chunk_end = min(chunk_end, ch[-1]["end"] + 0.6)
    for wi, w in enumerate(ch):
        start = w["start"]
        end = ch[wi + 1]["start"] if wi + 1 < len(ch) else chunk_end
        text = " ".join(
            (f"{{\\c{hi}}}{x['word'].strip().upper()}{{\\r}}" if j == wi else x["word"].strip().upper())
            for j, x in enumerate(ch))
        lines.append(f"Dialogue: 0,{ts(start + a.offset)},{ts(end + a.offset)},Brand,,0,0,0,,{text}")

open(a.out, "w").write("\n".join(lines) + "\n")
print(f"{len(chunks)} caption chunks, {len(words)} words -> {a.out}")
