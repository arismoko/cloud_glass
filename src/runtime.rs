//! Cloud Glass's pure model: the sixteen dye colours and the eye overlay's rules.
//!
//! Ported from Cloud Glass 1.1.0 (Mrbysco/CloudGlass, MIT) for Minecraft Java 1.21.1 NeoForge:
//! the block names and colours (`CloudRegistry.java:14-46`, `CloudGlassBlock.java:14-45`) and
//! the overlay (`ClientTick.java:17-43`). No game access here, so `cargo test` checks it alone.

/// The sixteen colours in upstream's registration order, each with vanilla's
/// `DyeColor.getTextureDiffuseColor` (`0xRRGGBB`): the beacon tint and the eye overlay's colour.
pub const DIFFUSE: [(&str, u32); 16] = [
    ("white", 0xF9FFFE),
    ("orange", 0xF9801D),
    ("magenta", 0xC74EBD),
    ("light_blue", 0x3AB3DA),
    ("yellow", 0xFED83D),
    ("lime", 0x80C71F),
    ("pink", 0xF38BAA),
    ("gray", 0x474F52),
    ("light_gray", 0x9D9D97),
    ("cyan", 0x169C9C),
    ("purple", 0x8932B8),
    ("blue", 0x3C44AA),
    ("brown", 0x835432),
    ("green", 0x5E7C16),
    ("red", 0xB02E26),
    ("black", 0x1D1D21),
];

/// The block of a colour: `orange` -> `cloudglass:orange_cloud_glass`.
#[must_use]
pub fn block_id(colour: &str) -> String {
    format!("cloudglass:{colour}_cloud_glass")
}

/// The overlay's alpha, upstream's `ALPHA` (`ClientTick.java:17`).
const OVERLAY_ALPHA: u32 = 0x80;

/// The ARGB the eye overlay fills the screen with while the eyes are inside `block`, or `None`
/// for a block that is not cloud glass: upstream's `(ALPHA << 24) | block.getTintRgb()`.
#[must_use]
pub fn overlay_argb(block: &str) -> Option<u32> {
    let colour = block
        .strip_prefix("cloudglass:")?
        .strip_suffix("_cloud_glass")?;
    DIFFUSE
        .iter()
        .find(|(name, _)| *name == colour)
        .map(|(_, rgb)| (OVERLAY_ALPHA << 24) | rgb)
}

/// The block a world position is inside (`BlockPos.containing`): each coordinate floored.
#[must_use]
pub fn block_at(position: [f64; 3]) -> [i32; 3] {
    position.map(|coordinate| coordinate.floor() as i32)
}

#[cfg(test)]
mod tests {
    use super::{DIFFUSE, block_at, overlay_argb};
    use std::path::Path;

    /// The vanilla `DyeColor` map colour ids, in registration order.
    const MAP_COLOR: [u8; 16] = [
        8, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
    ];

    fn read_json(path: &Path) -> String {
        std::fs::read_to_string(path)
            .unwrap_or_else(|e| panic!("cannot read {}: {e}", path.display()))
    }

    #[test]
    fn the_overlay_is_the_dye_colour_at_alpha_0x80() {
        assert_eq!(
            overlay_argb("cloudglass:orange_cloud_glass"),
            Some(0x80F9_801D)
        );
        assert_eq!(
            overlay_argb("cloudglass:white_cloud_glass"),
            Some(0x80F9_FFFE)
        );
        assert_eq!(
            overlay_argb("cloudglass:black_cloud_glass"),
            Some(0x801D_1D21)
        );
        assert_eq!(overlay_argb("minecraft:orange_stained_glass"), None);
        assert_eq!(overlay_argb("other:orange_cloud_glass"), None);
        assert_eq!(overlay_argb("cloudglass:teal_cloud_glass"), None);
    }

    #[test]
    fn the_eye_block_floors_each_coordinate() {
        assert_eq!(block_at([0.5, 81.62, 0.5]), [0, 81, 0]);
        assert_eq!(block_at([-0.5, 81.9, -0.001]), [-1, 81, -1]);
    }

    /// Each declaration copies its own dye's stained glass, walks through, and keeps the dye's
    /// map colour: what the code above assumes of the content.
    #[test]
    fn each_declaration_is_its_dyes_stained_glass_without_collision() {
        let dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("data/cloudglass/sunrise/block");
        for ((colour, _), map_color) in DIFFUSE.iter().zip(MAP_COLOR) {
            let path = dir.join(format!("{colour}_cloud_glass.json"));
            let text: String = read_json(&path).split_whitespace().collect();
            assert!(
                text.contains(&format!(
                    "\"template\":\"minecraft:{colour}_stained_glass\""
                )),
                "{colour}: wrong template"
            );
            assert!(
                text.contains("\"collision_shapes\":{\"default\":[]}"),
                "{colour}: collides"
            );
            assert!(
                text.contains(&format!("\"map_color\":{map_color},")),
                "{colour}: map colour"
            );
        }
        let declared = std::fs::read_dir(&dir).map(Iterator::count).unwrap_or(0);
        assert_eq!(declared, 16, "a stray or missing declaration");
    }

    /// One wool recipe per colour and one dye recipe per colour but white: 31 files, no stray one.
    #[test]
    fn the_carried_recipes_match_the_colours() {
        let dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("data/cloudglass/recipe");
        let mut carried: Vec<String> = std::fs::read_dir(&dir)
            .unwrap_or_else(|e| panic!("cannot read {}: {e}", dir.display()))
            .map(|entry| {
                entry
                    .expect("recipe entry")
                    .file_name()
                    .to_string_lossy()
                    .into_owned()
            })
            .collect();
        carried.sort();
        let mut expected = Vec::new();
        for (colour, _) in DIFFUSE {
            expected.push(format!("{colour}_cloud_glass.json"));
            if colour != "white" {
                expected.push(format!("{colour}_cloud_glass_from_dye.json"));
            }
        }
        expected.sort();
        assert_eq!(carried, expected);
    }
}
