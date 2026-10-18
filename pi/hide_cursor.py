#!/usr/bin/env python3
"""Hide the mouse pointer on the kitchen screen.

The Pi's desktop (labwc, Wayland) ignores `unclutter`, so instead this installs a cursor
theme where every pointer is a transparent pixel, and tells labwc (and the browser it
starts) to use it. Takes effect after a reboot. Undo: delete ~/.config/labwc/environment
lines starting with XCURSOR_ and reboot.
"""
import os
import struct

THEME = "kitchen-blank"
SIZES = (16, 24, 32, 48, 64)
NAMES = """left_ptr default arrow top_left_arrow right_ptr text xterm ibeam pointer hand hand1 hand2
watch wait progress left_ptr_watch half-busy crosshair cross tcross move fleur grab grabbing openhand
closedhand dnd-none dnd-move dnd-copy dnd-link dnd-ask all-scroll not-allowed no-drop crossed_circle
help question_arrow whats_this context-menu cell vertical-text alias copy zoom-in zoom-out X_cursor
pirate n-resize s-resize e-resize w-resize ne-resize nw-resize se-resize sw-resize ew-resize ns-resize
nesw-resize nwse-resize col-resize row-resize sb_h_double_arrow sb_v_double_arrow h_double_arrow
v_double_arrow size_hor size_ver size_bdiag size_fdiag size_all top_side bottom_side left_side
right_side top_left_corner top_right_corner bottom_left_corner bottom_right_corner split_h split_v
pencil draft color-picker center_ptr""".split()


def xcursor_blank():
    """An Xcursor file holding one fully transparent 1x1 image per nominal size."""
    IMG, n = 0xFFFD0002, len(SIZES)
    header = struct.pack("<4sIII", b"Xcur", 16, 0x10000, n)
    chunk_len = 36 + 4                               # image header + one ARGB pixel
    toc, chunks = b"", b""
    for i, size in enumerate(SIZES):
        pos = 16 + 12 * n + i * chunk_len
        toc += struct.pack("<III", IMG, size, pos)
        chunks += struct.pack("<IIIIIIIII", 36, IMG, size, 1, 1, 1, 0, 0, 0) + struct.pack("<I", 0)
    return header + toc + chunks


def main():
    home = os.path.expanduser("~")
    base = os.path.join(home, ".local/share/icons", THEME)
    cur = os.path.join(base, "cursors")
    os.makedirs(cur, exist_ok=True)
    with open(os.path.join(base, "index.theme"), "w") as f:
        f.write(f"[Icon Theme]\nName={THEME}\nComment=Invisible pointer for the kitchen screen\n")
    blank = os.path.join(cur, "left_ptr")
    with open(blank, "wb") as f:
        f.write(xcursor_blank())
    for name in NAMES:
        p = os.path.join(cur, name)
        if name != "left_ptr" and not os.path.exists(p):
            os.symlink("left_ptr", p)
    legacy = os.path.join(home, ".icons", THEME)                 # older lookup path
    os.makedirs(os.path.dirname(legacy), exist_ok=True)
    if not os.path.exists(legacy):
        os.symlink(base, legacy)

    # labwc reads ~/.config/labwc/environment; a user file replaces the system one, so copy that first.
    env = os.path.join(home, ".config/labwc/environment")
    os.makedirs(os.path.dirname(env), exist_ok=True)
    lines = []
    if os.path.exists(env):
        lines = open(env).read().splitlines()
    elif os.path.exists("/etc/xdg/labwc/environment"):
        lines = open("/etc/xdg/labwc/environment").read().splitlines()
    lines = [l for l in lines if not l.startswith(("XCURSOR_THEME=", "XCURSOR_SIZE="))]
    lines += [f"XCURSOR_THEME={THEME}", "XCURSOR_SIZE=24"]
    with open(env, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("Pointer hidden after the next reboot:  sudo reboot")


if __name__ == "__main__":
    main()
