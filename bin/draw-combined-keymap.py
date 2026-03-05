#!/usr/bin/env python3
"""Generate a combined keymap YAML showing all layers on one keyboard.

Reads the parsed keymap YAML and creates a single-layer view where each key
displays its bindings across all layers using the key legend slots:
  - tap (center): base layer
  - shifted (top): layer 3 (symbols)
  - hold (bottom): layer 4 (nav/numpad)
  - left: VIM layer
  - right: DE layer
"""

import sys
import yaml


# Map of layer names to key legend positions
# Adjust these to control which layer goes where on each key
LAYER_SLOTS = {
    0: "t",       # default -> center (tap)
    1: "s",       # NEO_LAER_3 -> top (shifted)
    2: "h",       # NEO_LAYER_4 -> bottom (hold)
    5: "left",    # VIM -> left
    4: "right",   # DE -> right
    # mod (3) is omitted - rarely needed on cheat sheet
}

LAYER_LABELS = {
    0: "Base",
    1: "Sym",
    2: "Nav",
    3: "Mod",
    4: "DE",
    5: "Vim",
}

SKIP_TYPES = {"trans", "held"}


def get_tap(key):
    """Extract the tap legend from a key spec."""
    if isinstance(key, str):
        return key
    if isinstance(key, dict):
        return key.get("t", key.get("tap", key.get("center", "")))
    return ""


def is_transparent(key):
    """Check if a key is transparent or held."""
    if isinstance(key, dict):
        return key.get("type", "") in SKIP_TYPES
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: draw-combined-keymap.py <input.yaml> [output.yaml]", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = yaml.safe_load(f)

    layers = data.get("layers", {})
    layer_names = list(layers.keys())
    layer_keys = list(layers.values())
    num_keys = len(layer_keys[0]) if layer_keys else 0

    combined = []
    for ki in range(num_keys):
        key_spec = {}
        for li, slot in LAYER_SLOTS.items():
            if li >= len(layer_keys):
                continue
            key = layer_keys[li][ki]
            if is_transparent(key):
                continue
            legend = get_tap(key)
            if not legend:
                continue
            # For base layer hold-taps, show hold modifier in tap legend
            if li == 0 and isinstance(key, dict) and key.get("h"):
                hold = key["h"]
                # Shorten common modifier names
                hold = (hold.replace("LEFT ", "L").replace("RIGHT ", "R")
                        .replace("CONTROL", "Ctl").replace("COMMAND", "Cmd")
                        .replace("SHIFT", "Sft").replace("ALT", "Alt"))
                key_spec["t"] = f"{legend}\n[{hold}]"
                continue
            key_spec[slot] = legend

        if not key_spec:
            combined.append("")
        elif len(key_spec) == 1 and "t" in key_spec:
            combined.append(key_spec["t"])
        else:
            combined.append(key_spec)

    # Build header showing slot legend
    header = "Base=center | Sym=top | Nav=bottom | Vim=left | DE=right"

    output = {
        "layout": data.get("layout", {}),
        "draw_config": {
            "footer_text": header,
            "key_h": 72,
            "key_w": 72,
            "n_columns": 1,
            "line_spacing": 1.0,
            "small_pad": 2,
            "shrink_wide_legends": 5,
        },
        "layers": {
            "All Layers": combined,
        },
    }

    out_file = sys.argv[2] if len(sys.argv) > 2 else None
    if out_file:
        with open(out_file, "w") as f:
            yaml.safe_dump(output, f, width=200, sort_keys=False, default_flow_style=None, allow_unicode=True)
    else:
        yaml.safe_dump(output, sys.stdout, width=200, sort_keys=False, default_flow_style=None, allow_unicode=True)


if __name__ == "__main__":
    main()
