//! Cloud Glass — the one `impl Hooks` at the crate root.
//!
//! The sixteen blocks are content in `data/` and `assets/`: each declares its dye's stained
//! glass as the template with an empty collision table, so it keeps glass's look, sound and
//! properties and can be walked through. The code here is what content can't say:
//!
//! - a block part per colour, which tints a beacon beam with its dye (upstream's
//!   `BeaconBeamBlock`) and refuses liquids (upstream's `LiquidBlockContainer`), so water
//!   neither flows into nor washes away a block it could otherwise pass;
//! - a HUD layer that tints the screen while the player's eyes are inside a block.
//!
//! [`runtime`] is the port's pure model: the dye colours and the overlay's rules.

pub mod runtime;

use mod_api::{
    self, BeaconColorMultiplierEvent, BlockPart, CanPlaceLiquidEvent, ClientHost, DrawContext,
    GuiLayerPlacement, Hooks, Host, LevelSide, RegisterGuiLayersEvent, Registrar,
    RegistrationContext,
};

/// One colour's block: its beacon tint and its refusal of liquids.
struct CloudGlass {
    /// The dye's diffuse colour, `0xRRGGBB`.
    diffuse: u32,
}

#[mod_api::sunrise_part]
impl BlockPart for CloudGlass {
    /// `BeaconBeamBlock.getColor`: the beam takes the dye's colour.
    fn beacon_color_multiplier(&self, _: &dyn Host, event: &mut BeaconColorMultiplierEvent<'_>) {
        *event.color = Some(0xFF00_0000 | self.diffuse);
    }

    /// `CloudGlassBlock.canPlaceLiquid`: no liquid, from a bucket or from a flow.
    fn can_place_liquid(&self, _: LevelSide, _: &mut CanPlaceLiquidEvent) -> Option<bool> {
        Some(false)
    }
}

/// Upstream's `ClientTick` layer, above vanilla's camera overlays: fill the screen with the dye's
/// colour at alpha `0x80` while the block containing the player's eyes is cloud glass.
fn draw_eye_tint(host: &dyn ClientHost, draw: &mut dyn DrawContext) {
    let Some(player) = host.local_player() else {
        return;
    };
    let Some(eye) = player.entity().eye_position(host) else {
        return;
    };
    let Some(level) = player.level(host) else {
        return;
    };
    let Some(block) = level.block(host, runtime::block_at(eye)) else {
        return;
    };
    let Some(argb) = block.id(host).and_then(runtime::overlay_argb) else {
        return;
    };
    let [width, height] = draw.size();
    draw.fill([0.0, 0.0, width, height], argb);
}

#[derive(Default)]
struct Mod;

#[mod_api::sunrise_mod]
impl Hooks for Mod {
    /// The part on each of the sixteen blocks.
    fn register(&self, r: &mut dyn Registrar, _: &RegistrationContext) {
        for (colour, diffuse) in runtime::DIFFUSE {
            let block = r.block_key(&runtime::block_id(colour));
            r.block_part(block, CloudGlass { diffuse });
        }
    }

    /// The eye tint, registered as upstream does it: above the camera overlays, which in the
    /// layer order is right below the crosshair.
    fn register_gui_layers(&self, _: &RegistrationContext, event: &mut RegisterGuiLayersEvent<'_>) {
        event.layers.register(
            "cloudglass:eye_tint".to_owned(),
            GuiLayerPlacement::Below("minecraft:crosshair".to_owned()),
            Box::new(draw_eye_tint),
        );
    }
}
