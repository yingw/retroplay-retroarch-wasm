# retroplay-retroarch-wasm

RetroArch Emscripten builds with RetroAchievements (cheevos) support, for use with [RetroPlay](https://github.com/yingw/RetroPlay).

Built with `HAVE_CHEEVOS=1 HAVE_NETWORKING=1`.

## Usage

```typescript
const CDN = 'https://cdn.jsdelivr.net/gh/yingw/retroplay-retroarch-wasm@release-v1.0.0/output/retroarch';

await Nostalgist.launch({
  core: {
    js: `${CDN}/fceumm_libretro.js`,
    wasm: `${CDN}/fceumm_libretro.wasm`,
  },
  retroarchConfig: {
    cheevos_enable: true,
    cheevos_username: 'your_username',
    cheevos_password: 'your_password',
  },
  rom: romData,
});
```

## Supported Cores

| Core | Platform |
|------|----------|
| fceumm | FC / NES |
| snes9x | SFC / SNES |
| mgba | GBA |
| genesis_plus_gx | MD / Genesis |
| gambatte | GB / GBC |

## Build

Trigger manually via GitHub Actions:

```
gh workflow run "Build RetroArch WASM with Cheevos" \
  --field retroarch_tag=v1.22.2 \
  --field cores=fceumm,snes9x,mgba
```
