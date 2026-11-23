#!/usr/bin/env python3
"""Generate the Cloud Glass content tree from the upstream checkout.

Cloud Glass 1.1.0 (1.21.1) registers sixteen `CloudGlassBlock`s, one per
vanilla dye colour (`CloudRegistry.java:14-46`). Each is a plain
`TransparentBlock` with an empty collision shape, `noOcclusion`, glass sound,
0.3 hardness and a self-drop loot table (`CloudLootProvider.java:29-34`), plus
two shaped recipes (`CloudRecipeProvider.java:32-78`) and one creative tab
(`CloudRegistry.java:48-58`).

Textures, models and lang are copied from the upstream repository (MIT); the
models' sprite references gain 26.3's `force_translucent`. Data files are
rewritten into the 26.3 formats Sunrise reads.

Usage:
    python3 tools/gen_content.py --upstream <CloudGlass checkout>

The output is the flat SDK package's own content tree: `assets/` and `data/` at the port
root, beside the hand-written `sunrise-mod.toml`.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

# (name, MapColor id) in CloudRegistry registration order. The ids are the
# vanilla DyeColor.getMapColor() values the block's `.mapColor(color)` uses.
COLOURS = [
    ("white", 8),  # MapColor.SNOW
    ("orange", 15),  # MapColor.COLOR_ORANGE
    ("magenta", 16),  # MapColor.COLOR_MAGENTA
    ("light_blue", 17),  # MapColor.COLOR_LIGHT_BLUE
    ("yellow", 18),  # MapColor.COLOR_YELLOW
    ("lime", 19),  # MapColor.COLOR_LIGHT_GREEN
    ("pink", 20),  # MapColor.COLOR_PINK
    ("gray", 21),  # MapColor.COLOR_GRAY
    ("light_gray", 22),  # MapColor.COLOR_LIGHT_GRAY
    ("cyan", 23),  # MapColor.COLOR_CYAN
    ("purple", 24),  # MapColor.COLOR_PURPLE
    ("blue", 25),  # MapColor.COLOR_BLUE
    ("brown", 26),  # MapColor.COLOR_BROWN
    ("green", 27),  # MapColor.COLOR_GREEN
    ("red", 28),  # MapColor.COLOR_RED
    ("black", 29),  # MapColor.COLOR_BLACK
]

# Each colour's declaration copies the vanilla stained glass of its dye: a
# TransparentBlock with upstream's strength 0.3, glass sound, hat instrument,
# dye map colour, no occlusion, no spawning, no redstone conduction, no
# suffocation and no view blocking (CloudRegistry.java:31-45). The one
# property stained glass lacks, noCollission, is the empty collision table.
TEMPLATE = "minecraft:{colour}_stained_glass"


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value)
    else:
        path.write_text(json.dumps(value, indent=2, sort_keys=False) + "\n")


def ingredient(value):
    """A 1.21.1 ingredient object as the 26.3 string/tag form."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return [ingredient(v) for v in value]
    if "item" in value:
        return value["item"]
    if "tag" in value:
        return "#" + value["tag"]
    raise ValueError(f"unknown ingredient shape: {value!r}")


def upgrade_recipe(old: dict) -> dict:
    """Rewrite one 1.21.1 recipe into the 26.3 recipe schema."""
    new = {"type": old["type"]}
    for key in ("category", "group", "cookingtime", "experience"):
        if key in old:
            new[key] = old[key]
    if "pattern" in old:
        new["pattern"] = old["pattern"]
    if "key" in old:
        new["key"] = {k: ingredient(v) for k, v in old["key"].items()}
    result = old["result"]
    new["result"] = {"id": result["id"]}
    if result.get("count", 1) != 1:
        new["result"]["count"] = result["count"]
    return new


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--upstream",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "upstream/CloudGlass",
    )
    parser.add_argument(
        "--out", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    upstream = args.upstream.resolve()
    out = args.out.resolve()
    if not (upstream / "gradle.properties").exists():
        raise SystemExit(f"no upstream checkout at {upstream}")

    assets = out / "assets/cloudglass"
    data = out / "data"
    (assets / "textures/block").mkdir(parents=True, exist_ok=True)
    textures = upstream / "src/main/resources/assets/cloudglass"
    generated = upstream / "src/generated/resources"

    # Lang: the generated English file plus the hand-written translations.
    write(
        assets / "lang/en_us.json",
        json.loads((generated / "assets/cloudglass/lang/en_us.json").read_text()),
    )
    for code in ("pt_br", "tr_tr"):
        write(
            assets / f"lang/{code}.json",
            json.loads((textures / f"lang/{code}.json").read_text()),
        )

    blocks = []
    dye_tags = []
    for name, map_color in COLOURS:
        block = f"{name}_cloud_glass"
        blocks.append(f"cloudglass:{block}")
        dye_tags.append(f"minecraft:{name}_dye")

        # Texture: the real upstream file, byte for byte.
        shutil.copyfile(
            textures / f"textures/block/{block}.png",
            assets / f"textures/block/{block}.png",
        )

        # Blockstate, block model and 26.3 item model definition. The 1.21
        # model said `render_type: translucent`; 26.3 puts `force_translucent`
        # on the sprite (as vanilla glass does).
        write(
            assets / f"blockstates/{block}.json",
            {"variants": {"": {"model": f"cloudglass:block/{block}"}}},
        )
        write(
            assets / f"models/block/{block}.json",
            {
                "parent": "minecraft:block/cube_all",
                "textures": {
                    "all": {
                        "force_translucent": True,
                        "sprite": f"cloudglass:block/{block}",
                    }
                },
            },
        )
        write(
            assets / f"items/{block}.json",
            {"model": {"type": "minecraft:model", "model": f"cloudglass:block/{block}"}},
        )

        # Block declaration: the dye's stained glass with no collision, and
        # upstream's properties spelled out (CloudRegistry.java:31-45).
        write(
            data / f"cloudglass/sunrise/block/{block}.json",
            {
                "template": TEMPLATE.format(colour=name),
                "collision_shapes": {"default": []},
                "properties": {
                    "hardness": 0.3,
                    "explosion_resistance": 0.3,
                    "map_color": map_color,
                    "requires_tool": False,
                    "sounds": "minecraft:glass",
                    "instrument": "HAT",
                    "occludes": False,
                },
            },
        )

        # Loot: drop self, survive explosions (CloudLootProvider.java:29-34).
        write(
            data / f"cloudglass/loot_table/blocks/{block}.json",
            {
                "type": "minecraft:block",
                "pools": [
                    {
                        "condition": {"type": "minecraft:survives_explosion"},
                        "entries": [{"type": "minecraft:item", "name": f"cloudglass:{block}"}],
                        "rolls": 1,
                    }
                ],
                "random_sequence": f"cloudglass:blocks/{block}",
            },
        )

        # Recipes: the upstream shaped recipe (four wool around one glass),
        # and the dye recipe (eight white cloud glass around one dye) for
        # every colour but white (CloudRecipeProvider.java:32-78).
        suffixes = [block]
        if name != "white":
            suffixes.append(f"{block}_from_dye")
        for suffix in suffixes:
            old = json.loads(
                (generated / f"data/cloudglass/recipe/{suffix}.json").read_text()
            )
            write(data / f"cloudglass/recipe/{suffix}.json", upgrade_recipe(old))

    # Convention tags. NeoForge supplied `c:dyes/*` and
    # `c:glass_blocks/colorless` in 1.21.1; 26.3 ships no `c` tags, so the
    # recipes' ingredients need them supplied here.
    for name, _ in COLOURS:
        write(
            data / f"c/tags/item/dyes/{name}.json",
            {"values": [f"minecraft:{name}_dye"]},
        )
    write(data / "c/tags/item/dyes.json", {"values": dye_tags})
    for side in ("block", "item"):
        write(
            data / f"c/tags/{side}/glass_blocks/colorless.json",
            {"values": ["minecraft:glass"]},
        )
        write(
            data / f"c/tags/{side}/glass_blocks/tinted.json",
            {"values": ["minecraft:tinted_glass"]},
        )
        write(
            data / f"c/tags/{side}/glass_blocks.json",
            {"values": ["#c:glass_blocks/colorless", "#c:glass_blocks/tinted"]},
        )

    # One creative tab for the content, as upstream's `cloudglass:tab`.
    write(
        data / "cloudglass/sunrise/creative_tab/cloudglass.json",
        {
            "title": "Cloud Glass",
            "icon": "cloudglass:light_blue_cloud_glass",
            "items": blocks,
        },
    )

    print(f"wrote {out}")


if __name__ == "__main__":
    main()
