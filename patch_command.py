#!/usr/bin/env python3
"""patch_command.py — 在 RetroArch command.c 中添加 retro_get_memory_data fallback

用法: python3 patch_command.py <path/to/command.c>

原理: READ_CORE_MEMORY 命令依赖 memory descriptor 系统。
当 core 没有注册 memory descriptor 时，fallback 到 retro_get_memory_data API。
"""

import sys
import re

def patch_command_c(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # 找到 command_memory_get_pointer 函数中的 "no memory map defined" 处理
    # 原始代码：
    #   if (!sys_info || sys_info->mmaps.num_descriptors == 0)
    #       strlcpy(s, " -1 no memory map defined\n", len);
    #
    # 替换为：
    #   if (!sys_info || sys_info->mmaps.num_descriptors == 0) {
    #       /* RetroPlay: fallback to retro_get_memory_data */
    #       void *fallback_data = retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM);
    #       unsigned fallback_size = retro_get_memory_size(RETRO_MEMORY_SYSTEM_RAM);
    #       if (fallback_data && fallback_size > 0) {
    #           *max_bytes = (size_t)fallback_size;
    #           return (uint8_t*)fallback_data;
    #       }
    #       strlcpy(s, " -1 no memory map defined\n", len);
    #   }

    old_pattern = (
        r'if \(!sys_info \|\| sys_info->mmaps\.num_descriptors == 0\)\s*\n'
        r'\s+strlcpy\(s, " -1 no memory map defined\\n", len\);'
    )

    new_code = '''if (!sys_info || sys_info->mmaps.num_descriptors == 0) {
      /* RetroPlay: fallback to retro_get_memory_data for cores without memory maps */
      void *fallback_data = retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM);
      unsigned fallback_size = retro_get_memory_size(RETRO_MEMORY_SYSTEM_RAM);
      if (fallback_data && fallback_size > 0) {
          *max_bytes = (size_t)fallback_size;
          return (uint8_t*)fallback_data;
      }
      strlcpy(s, " -1 no memory map defined\\n", len);
  }'''

    new_content, count = re.subn(old_pattern, new_code, content)

    if count == 0:
        print(f"ERROR: Pattern not found in {filepath}")
        print("Looking for: if (!sys_info || sys_info->mmaps.num_descriptors == 0)")
        # 尝试查找附近的内容
        if "no memory map defined" in content:
            idx = content.index("no memory map defined")
            print(f"Found 'no memory map defined' at offset {idx}")
            print(f"Context: ...{content[max(0,idx-100):idx+50]}...")
        sys.exit(1)

    with open(filepath, 'w') as f:
        f.write(new_content)

    print(f"✅ Patched {filepath} ({count} replacement)")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <command.c>")
        sys.exit(1)
    patch_command_c(sys.argv[1])
