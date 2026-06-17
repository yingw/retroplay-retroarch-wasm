#!/usr/bin/env python3
"""patch_command.py — 在 RetroArch command.c 中添加 retro_get_memory_data fallback

用法: python3 patch_command.py <path/to/command.c>

原理: READ_CORE_MEMORY 命令依赖 memory descriptor 系统。
当 core 没有注册 memory descriptor 时，fallback 到 retro_get_memory_data API。

原始代码（无大括号的 if）：
    if (!sys_info || sys_info->mmaps.num_descriptors == 0)
        strlcpy(s, " -1 no memory map defined\\n", len);
    else
    {

替换为（加 fallback 大括号块）：
    if (!sys_info || sys_info->mmaps.num_descriptors == 0)
    {
        /* RetroPlay: fallback to retro_get_memory_data */
        void *fallback_data = retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM);
        ...
        strlcpy(s, " -1 no memory map defined\\n", len);
    }
    else
    {
"""

import sys

def patch_command_c(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # 找到 "no memory map defined" 那行
    target_idx = None
    for i, line in enumerate(lines):
        if 'no memory map defined' in line:
            target_idx = i
            break

    if target_idx is None:
        print(f"ERROR: 'no memory map defined' not found in {filepath}")
        sys.exit(1)

    # 向上找 if 语句
    if_idx = target_idx - 1
    while if_idx >= 0 and 'num_descriptors == 0' not in lines[if_idx]:
        if_idx -= 1

    if if_idx < 0:
        print(f"ERROR: Could not find if statement before line {target_idx}")
        sys.exit(1)

    # 找 else { 行（在 strlcpy 之后）
    else_idx = target_idx + 1
    while else_idx < len(lines) and 'else' not in lines[else_idx]:
        else_idx += 1

    if else_idx >= len(lines) or '{' not in lines[else_idx]:
        # else 可能在下一行
        if else_idx + 1 < len(lines) and '{' in lines[else_idx + 1]:
            else_idx += 1

    print(f"Found if at line {if_idx + 1}: {lines[if_idx].rstrip()}")
    print(f"Found strlcpy at line {target_idx + 1}: {lines[target_idx].rstrip()}")
    print(f"Found else at line {else_idx + 1}: {lines[else_idx].rstrip()}")

    # 构建替换代码
    fallback_code = [
        lines[if_idx],  # if (!sys_info || ...)
        '   {\n',
        '      /* RetroPlay: fallback to retro_get_memory_data for cores without memory maps */\n',
        '      void *fallback_data = retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM);\n',
        '      unsigned fallback_size = retro_get_memory_size(RETRO_MEMORY_SYSTEM_RAM);\n',
        '      if (fallback_data && fallback_size > 0)\n',
        '      {\n',
        '         *max_bytes = (size_t)fallback_size;\n',
        '         return (uint8_t*)fallback_data;\n',
        '      }\n',
        '      strlcpy(s, " -1 no memory map defined\\n", len);\n',
        '   }\n',
        '   else\n',
    ]

    # 替换：从 if 行到 else 行（不含 else 的 { 行）
    # 保留 else { 行
    new_lines = lines[:if_idx] + fallback_code + lines[else_idx:]

    with open(filepath, 'w') as f:
        f.writelines(new_lines)

    print(f"✅ Patched {filepath}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <command.c>")
        sys.exit(1)
    patch_command_c(sys.argv[1])
