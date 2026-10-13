#!/usr/bin/env python3
"""
Build a neofetch-style info card SVG to sit beside the ASCII portrait:
terminal-style key/value rows for role, stack, and highlights.

Lines fade/slide in on a stagger so it feels like the panel is printing in real-time.
STATIC=1 emits a frozen state for static previews.
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

# Sized to align cleanly beside portrait
W, H = 840, 880
PAD = 36
TITLEBAR_H = 40
KEY_X = PAD + 10
VAL_X = PAD + 190
LINE_H = 34

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
KEY = "#ffa657"      # orange keys (neofetch style)
SECTION = "#58a6ff"  # blue section headers
GREEN = "#3fb950"
ACCENT = "#22d3ee"

ROWS = [
    ("host",),
    ("kv", "OS", "Batcomputer Tactical OS (Arch Linux x64)"),
    ("kv", "Role", "Full Stack Developer & DAM Engineer"),
    ("kv", "Focus", "High-Performance Web Architecture & UI/UX"),
    ("kv", "Degree", "Técnico Superior DAM (Multiplatform Apps)"),
    ("gap",),
    ("sec", "Core Tech Stack"),
    ("kv", "Frontend", "Next.js 14 (App Router), React, TypeScript"),
    ("kv", "Styling & 3D", "Tailwind CSS, Three.js, GSAP, Framer Motion"),
    ("kv", "Backend", "Java / JavaFX, Node.js, Python, Supabase"),
    ("kv", "Databases", "PostgreSQL, MongoDB, SQLite, HikariCP"),
    ("kv", "DevOps & Tools", "Docker, Git, Vercel, Linux, Postman"),
    ("gap",),
    ("sec", "Highlights & Projects"),
    ("bul", "BatPortfolio — cinematic 3D & tactical interactive portfolio"),
    ("bul", "Clean code, modular architecture & relentless optimization"),
    ("bul", "Daily commits & active software crafting"),
]


def esc(s):
    return html.escape(s)


def rise(inner, i):
    if STATIC:
        return f"<g>{inner}</g>"
    delay = 0.15 + i * 0.07
    return (f'<g opacity="0" transform="translate(0,6)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.45s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 6" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.45s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<defs>'
    f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*20}" cy="{TITLEBAR_H/2}" r="6" fill="{dotcol}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 5}" fill="{MUTED}" font-size="14" '
             f'text-anchor="middle">ayoxb1@github: ~$ neofetch</text>')

y = TITLEBAR_H + 46
for i, row in enumerate(ROWS):
    kind = row[0]
    if kind == "gap":
        y += LINE_H * 0.4
        continue
    if kind == "host":
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" font-size="20" font-weight="700">'
                 f'<tspan fill="{GREEN}">ayoub</tspan><tspan fill="{MUTED}">@</tspan>'
                 f'<tspan fill="{ACCENT}">batcomputer</tspan></text>'
                 f'<line x1="{KEY_X+260}" y1="{y-6:.1f}" x2="{W-PAD}" y2="{y-6:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    elif kind == "sec":
        title = esc(row[1])
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="17" font-weight="700">'
                 f'&#8212; {title}</text>'
                 f'<line x1="{KEY_X + 24 + len(row[1])*11}" y1="{y-6:.1f}" x2="{W-PAD}" y2="{y-6:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    elif kind == "kv":
        key, val = esc(row[1]), esc(row[2])
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="16" font-weight="700">{key}</text>'
                 f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="16">{val}</text>')
    elif kind == "bul":
        txt = esc(row[1])
        inner = (f'<circle cx="{KEY_X+6}" cy="{y-5:.1f}" r="3.5" fill="{GREEN}"/>'
                 f'<text x="{KEY_X+22}" y="{y:.1f}" fill="{INK}" font-size="16">{txt}</text>')
    else:
        continue
    parts.append(rise(inner, i))
    y += LINE_H

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", W, "x", H, "content_bottom", round(y))
