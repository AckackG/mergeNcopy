# 文本合并工具 | Text Merge Tool

**拖拽文件/文件夹 → 自动合并文本 → 一键复制到剪贴板**

Drag files/folders → Auto-merge text → Copy to clipboard

---

## 快速开始 | Quick Start

1. **下载** `.py` 和 `.bat` 文件到任意文件夹
2. **拖拽**文件或文件夹到 `mNc.bat` 上
3. **完成** - 内容已自动复制到剪贴板并生成桌面文件

<img width="930" height="466" alt="使用演示" src="https://github.com/user-attachments/assets/09883392-7b97-4fb9-8641-5a0b840b435b" />

### 可选：右键菜单快捷方式 | Optional: Context Menu

在资源管理器地址栏运行 `shell:sendto`，将 `mNc.bat` 快捷方式放入，即可通过"右键 → 发送到"调用。

Run `shell:sendto` in File Explorer, paste the shortcut of `mNc.bat` to enable "Right-click → Send to".

---

## 功能特性 | Features

- ✅ **白名单模式**：仅处理代码和文本文件（`.py` `.js` `.java` `.md` 等）
- ✅ **智能过滤**：自动排除 `node_modules` `venv` `.git` 等构建目录
- ✅ **排除模式**：跳过 `.min.js` `.bundle.js` 等压缩文件（但仍显示在结构中）
- ✅ **目录树**：自动生成项目结构图和文件统计
- ✅ **多线程**：并发处理，快速高效
- ✅ **智能编码**：自动处理 UTF-8 和 GBK 编码

---

## 依赖安装 | Dependencies

```bash
pip install pyperclip
```

---

## 自定义配置 | Configuration

在 Python 脚本顶部修改以下配置项：

Edit these constants at the top of the Python script:

### 核心配置 | Core Settings

```python
# 允许读取的文件类型白名单
FORCE_TEXT_EXTENSIONS = {
    '.py', '.js', '.java', '.md', '.txt', '.json', ...
}

# 排除的文件模式（显示在树中但不读取内容）
EXCLUDED_FILE_PATTERNS = [
    '*.min.js',      # 压缩的 JS 文件
    '*.min.css',     # 压缩的 CSS 文件
    '*.bundle.js',   # 打包文件
]

# 排除的目录（完全不扫描）
EXCLUDED_PATHS = [
    'node_modules', 'venv', '.git', '__pycache__', ...
]
```

### 其他配置 | Other Settings

```python
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 单文件大小限制（默认 20MB）
MAX_PATH_DISPLAY_LEN = 80               # 路径显示长度
```

---

## 输出示例 | Output Example

生成的文件包含：

- 📊 项目统计信息（文件数量、类型分布）
- 🌲 目录树结构
- 📄 所有文本文件内容（带文件路径标记和修改时间）

The generated file contains:

- 📊 Project statistics (file count, type distribution)
- 🌲 Directory tree structure
- 📄 All text file contents (with file paths and timestamps)

---

## 工作原理 | How It Works

1. **文件发现**：递归扫描拖入的文件/文件夹
2. **智能过滤**：
   - 跳过排除目录（如 `node_modules`）
   - 跳过排除模式文件（如 `.min.js`）- 仅出现在树中
   - 跳过非白名单文件（如 `.jpg` `.exe`）
   - 跳过超大文件（默认 >20MB）
3. **并发处理**：多线程读取和解码文件
4. **智能输出**：
   - 代码文件优先，文档文件在后
   - 使用语言特定的注释符号标记文件路径
5. **自动复制**：内容复制到剪贴板 + 生成桌面文件

---

## 许可 | License

MIT License - 自由使用和修改 | Free to use and modify
