# retroplay-retroarch-wasm

RetroArch Emscripten builds for [RetroPlay](https://github.com/yingw/RetroPlay)，支持两种构建模式。

## 构建模式

### 1. Memory Export（当前方案）

导出 `_retro_get_memory_data` / `_retro_get_memory_size`，供 RetroPlay JS 层读取模拟器 RAM，再传给 Rust 侧 rcheevos 引擎。

```bash
gh workflow run build-memory-export.yml \
  --field retroarch_tag=v1.22.2 \
  --field cores=fceumm,mgba
```

产物使用：

```typescript
// 直接读取模拟器 RAM
const ptr = Module._retro_get_memory_data(2); // RETRO_MEMORY_SYSTEM_RAM
const size = Module._retro_get_memory_size(2);
const ram = Module.HEAPU8.slice(ptr, ptr + size);
```

### 2. Cheevos（RetroArch 内置成就）

RetroArch 前端内置 cheevos 模块（`HAVE_CHEEVOS=1`），不需要 Rust 侧 rcheevos。

```bash
gh workflow run build-retroarch-wasm-cheevos.yml \
  --field retroarch_tag=v1.22.2 \
  --field cores=fceumm,snes9x,mgba
```

产物使用：

```typescript
await Nostalgist.launch({
  core: { js: `${CDN}/fceumm_libretro.js`, wasm: `${CDN}/fceumm_libretro.wasm` },
  retroarchConfig: {
    cheevos_enable: true,
    cheevos_username: 'your_username',
    cheevos_password: 'your_password',
  },
  rom: romData,
});
```

## 支持的核心

| Core | 平台 | 构建系统 | 内存读取 |
|------|------|---------|---------|
| fceumm | FC / NES | Makefile | READ_CORE_MEMORY（1帧延迟） |
| snes9x | SFC / SNES | Makefile | _retro_get_memory_data ✅ |
| mgba | GBA | **CMake** | _retro_get_memory_data ✅ |
| genesis_plus_gx | MD / Genesis | Makefile | _retro_get_memory_data ✅ |
| gambatte | GB / GBC | Makefile | READ_CORE_MEMORY（1帧延迟） |

## 内存导出

`ra_memory_export.c` 提供 `EMSCRIPTEN_KEEPALIVE` 包装函数，自动导出到 WASM：

```c
void* ra_get_ram_ptr(void)   → retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM)
unsigned ra_get_ram_size(void) → retro_get_memory_size(RETRO_MEMORY_SYSTEM_RAM)
```

## GitHub Actions 手动触发

```bash
# Memory Export 版本（RetroPlay 当前方案）
gh workflow run build-memory-export.yml \
  --field retroarch_tag=v1.22.2 \
  --field cores=fceumm,mgba

# Cheevos 版本（RetroArch 内置成就）
gh workflow run build-retroarch-wasm-cheevos.yml \
  --field retroarch_tag=v1.22.2 \
  --field cores=fceumm,snes9x,mgba
```
