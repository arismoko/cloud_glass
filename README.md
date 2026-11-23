# Cloud Glass for Sunrise

Sixteen see-through, walk-through cloud glass blocks, one per dye colour.

A port of [Cloud Glass](https://github.com/Mrbysco/CloudGlass) by Mrbysco to [Sunrise](https://playsunrise.net) (Minecraft Java 26.3). The blocks are content; the beacon tint, the refusal of liquids and the screen tint are a small native part.

## What it does

- Sixteen cloud glass blocks, one per dye colour, with the glass sound, strength and translucent look of stained glass, but no collision: players, mobs and items pass through them, and they block no view and suffocate nobody.
- Standing with your eyes inside a cloud glass block tints the screen with its colour.
- A beacon beam passing through cloud glass takes its colour, as through stained glass.
- Water and lava neither flow into cloud glass nor wash it away, and a bucket can't fill it.
- Mobs don't spawn on it, and it doesn't conduct redstone.
- The original's recipes (four wool around a glass block makes four, and eight white cloud glass around a dye makes eight of that colour), self drops, creative tab and English, Portuguese and Turkish translations.

## Differences from the original

- None that a player can see.

## Building

With the Sunrise mod tool (`cargo sunrise-mod`, from the Sunrise SDK) and Rust:

```sh
cargo sunrise-mod build    # compiles against the pinned game, packs target/sunrise-mod/cloudglass.smod
cargo sunrise-mod run      # builds it and starts the game with it
cargo test
```

`tools/gen_content.py --upstream <CloudGlass checkout>` regenerates the content from the original's source.

## Licence

MIT, as the original. See [LICENSE](LICENSE) and [LICENSE-NOTICE.md](LICENSE-NOTICE.md).
