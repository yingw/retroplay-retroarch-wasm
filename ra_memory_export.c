// ra_memory_export.c
// 导出模拟器 RAM 指针给 JS 层，供外部 rcheevos 逻辑读取内存
//
// 背景：RetroArch WASM 未导出 retro_get_memory_data，JS 无法直接拿到模拟器 RAM。
// 这个文件提供 EMSCRIPTEN_KEEPALIVE 包装函数，编译时自动导出到 WASM。
//
// 用法（JS 侧）：
//   const ptr = Module._ra_get_ram_ptr()
//   const size = Module._ra_get_ram_size()
//   const ram = Module.HEAPU8.subarray(ptr, ptr + size)

#include <emscripten.h>

// libretro API：获取模拟器内存指针和大小
// retro_get_memory_data 是 core 实现的函数，RetroArch 前端调用
extern void *retro_get_memory_data(unsigned id);
extern unsigned retro_get_memory_size(unsigned id);

// RETRO_MEMORY_SYSTEM_RAM = 0
#define RETRO_MEMORY_SYSTEM_RAM 0

/// 获取模拟器系统 RAM 在 WASM 线性内存中的起始偏移
EMSCRIPTEN_KEEPALIVE
void* ra_get_ram_ptr(void) {
    return retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM);
}

/// 获取模拟器系统 RAM 的字节大小
EMSCRIPTEN_KEEPALIVE
unsigned ra_get_ram_size(void) {
    return retro_get_memory_size(RETRO_MEMORY_SYSTEM_RAM);
}
