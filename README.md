# 文本合并工具

**快速将整个项目合并成单个文本文件，方便发送给 AI 助手（ChatGPT、Claude 等）进行代码分析、问题诊断、重构建议。**

**拖拽文件/文件夹 → 自动合并代码 → 一键复制 → 粘贴给 AI**

---

## 快速开始

1. **下载** `.py` 和 `.bat` 文件到任意文件夹
2. **拖拽**项目文件夹到 `mNc.bat` 上
3. **完成** - 内容已自动复制到剪贴板，直接粘贴给 ChatGPT/Claude

<img width="930" height="466" alt="使用演示" src="https://github.com/user-attachments/assets/09883392-7b97-4fb9-8641-5a0b840b435b" />

### 可选：右键菜单快捷方式

在资源管理器地址栏运行 `shell:sendto`，将 `mNc.bat` 快捷方式放入，即可通过"右键 → 发送到"调用。

---

## 为什么需要这个工具？

当你想让 AI 助手帮你：
- 🔍 **分析代码结构**："帮我看看这个项目的架构设计"
- 🐛 **诊断 Bug**："找出这段代码的问题"
- ♻️ **重构建议**："优化这个函数的性能"
- 📚 **生成文档**："为这个项目写个 README"
- 🎓 **学习代码**："解释这个开源项目的工作原理"

传统方式需要逐个复制粘贴文件，效率低下。本工具**一键完成**：自动收集、智能过滤、结构化输出。

---

## 功能特性

- ✅ **白名单模式**：仅处理代码和文本文件（`.py` `.js` `.java` `.md` 等）
- ✅ **智能过滤**：自动排除 `node_modules` `venv` `.git` 等构建目录
- ✅ **排除模式**：跳过 `.min.js` `.bundle.js` 等压缩文件（但仍显示在目录树中）
- ✅ **目录树**：自动生成项目结构图和文件统计
- ✅ **多线程**：并发处理，速度快
- ✅ **智能编码**：自动处理 UTF-8 和 GBK 编码

---

## 依赖安装

```bash
pip install pyperclip
```

---

## 自定义配置

在 Python 脚本顶部修改配置项：

### 核心配置

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

### 其他配置

```python
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 单文件大小限制（默认 20MB）
MAX_PATH_DISPLAY_LEN = 80               # 路径显示长度
```

---

## 输出示例

生成的文件包含：
- 📊 **项目统计**：文件数量、类型分布、生成时间
- 🌲 **目录树**：完整的项目结构图
- 📄 **文件内容**：所有代码文件，带路径标记和修改时间

示例输出：
```
================================================================================
PROJECT ANALYSIS SUMMARY
================================================================================

Base Path: C:\Projects\MyApp
Total Files Processed: 45
Total Files in Structure: 67
Generated: 2026-01-04 15:30:22

File Type Distribution (Processed):
----------------------------------------
  .js                  : 20 files
  .py                  : 15 files
  .md                  :  5 files
  ...

================================================================================
DIRECTORY STRUCTURE
================================================================================

MyApp
├── src
│   ├── main.js
│   ├── utils.js
│   └── app.min.js
├── README.md
└── package.json

================================================================================
FILE CONTENTS
================================================================================

// ============================================================
// FILE: C:\Projects\MyApp\src\main.js
// MODIFIED: 2026-01-04 14:25:10
// ============================================================

... 文件内容 ...
```

---

## 工作原理

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
5. **自动复制**：内容复制到剪贴板 + 生成桌面文件（时间戳命名）

---

## 使用技巧

### 发送给 AI 时的提示词示例

```
我有一个 [项目类型] 项目，代码如下。请帮我：
1. 分析整体架构和设计模式
2. 找出潜在的 bug 和性能问题
3. 提供优化建议

[粘贴合并后的代码]
```

### 针对特定问题

```
下面是我的项目代码，目前遇到 [具体问题描述]。
请帮我：
1. 定位问题原因
2. 提供解决方案
3. 给出修改后的代码

[粘贴合并后的代码]
```

---

## 常见问题

**Q: 为什么有些文件没有被包含？**  
A: 检查 `FORCE_TEXT_EXTENSIONS` 白名单和 `EXCLUDED_FILE_PATTERNS` 排除模式。

**Q: `.min.js` 文件会被处理吗？**  
A: 不会读取内容，但会显示在目录树中，让 AI 了解完整的项目结构。

---

## 许可

MIT License - 自由使用和修改

---

# Text Merge Tool (English Version)

**Quickly merge your entire project into a single text file for sending to AI assistants (ChatGPT, Claude, etc.) for code analysis, bug diagnosis, and refactoring suggestions.**

**Drag files/folders → Auto-merge code → One-click copy → Paste to AI**

---

## Quick Start

1. **Download** `.py` and `.bat` files to any folder
2. **Drag** your project folder onto `mNc.bat`
3. **Done** - Content is automatically copied to clipboard, paste directly to ChatGPT/Claude

<img width="930" height="466" alt="Demo" src="https://github.com/user-attachments/assets/09883392-7b97-4fb9-8641-5a0b840b435b" />

### Optional: Context Menu Shortcut

Run `shell:sendto` in File Explorer address bar, paste the `mNc.bat` shortcut to enable "Right-click → Send to".

---

## Why This Tool?

When you want AI assistants to help you:
- 🔍 **Analyze Code Structure**: "Review the architecture design of this project"
- 🐛 **Diagnose Bugs**: "Find issues in this code"
- ♻️ **Refactoring Advice**: "Optimize this function's performance"
- 📚 **Generate Documentation**: "Write a README for this project"
- 🎓 **Learn Code**: "Explain how this open-source project works"

Traditional way requires copying files one by one - inefficient. This tool does it **in one click**: auto-collect, smart-filter, structured output.

---

## Features

- ✅ **Whitelist Mode**: Only process code and text files (`.py` `.js` `.java` `.md` etc.)
- ✅ **Smart Filtering**: Auto-exclude `node_modules` `venv` `.git` build directories
- ✅ **Exclusion Patterns**: Skip `.min.js` `.bundle.js` minified files (still show in tree)
- ✅ **Directory Tree**: Auto-generate project structure and file statistics
- ✅ **Multi-threading**: Concurrent processing for speed
- ✅ **Smart Encoding**: Auto-handle UTF-8 and GBK encodings

---

## Dependencies

```bash
pip install pyperclip
```

---

## Configuration

Edit constants at the top of the Python script:

### Core Settings

```python
# Whitelist of allowed file types
FORCE_TEXT_EXTENSIONS = {
    '.py', '.js', '.java', '.md', '.txt', '.json', ...
}

# Excluded file patterns (show in tree but don't read content)
EXCLUDED_FILE_PATTERNS = [
    '*.min.js',      # Minified JS files
    '*.min.css',     # Minified CSS files
    '*.bundle.js',   # Bundle files
]

# Excluded directories (not scanned at all)
EXCLUDED_PATHS = [
    'node_modules', 'venv', '.git', '__pycache__', ...
]
```

### Other Settings

```python
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # Max file size (default 20MB)
MAX_PATH_DISPLAY_LEN = 80               # Path display length
```

---

## Output Example

Generated file contains:
- 📊 **Project Stats**: File count, type distribution, generation time
- 🌲 **Directory Tree**: Complete project structure
- 📄 **File Contents**: All code files with path markers and timestamps

Example output:
```
================================================================================
PROJECT ANALYSIS SUMMARY
================================================================================

Base Path: C:\Projects\MyApp
Total Files Processed: 45
Total Files in Structure: 67
Generated: 2026-01-04 15:30:22

File Type Distribution (Processed):
----------------------------------------
  .js                  : 20 files
  .py                  : 15 files
  .md                  :  5 files
  ...

================================================================================
DIRECTORY STRUCTURE
================================================================================

MyApp
├── src
│   ├── main.js
│   ├── utils.js
│   └── app.min.js
├── README.md
└── package.json

================================================================================
FILE CONTENTS
================================================================================

// ============================================================
// FILE: C:\Projects\MyApp\src\main.js
// MODIFIED: 2026-01-04 14:25:10
// ============================================================

... file content ...
```

---

## How It Works

1. **File Discovery**: Recursively scan dragged files/folders
2. **Smart Filtering**:
   - Skip excluded directories (e.g., `node_modules`)
   - Skip excluded pattern files (e.g., `.min.js`) - only show in tree
   - Skip non-whitelist files (e.g., `.jpg` `.exe`)
   - Skip oversized files (default >20MB)
3. **Concurrent Processing**: Multi-threaded reading and decoding
4. **Smart Output**:
   - Code files first, documentation files last
   - Use language-specific comment markers for file paths
5. **Auto Copy**: Copy to clipboard + generate desktop file (timestamped)

---

## Usage Tips

### Example Prompts for AI

```
I have a [project type] project with the following code. Please help me:
1. Analyze the overall architecture and design patterns
2. Identify potential bugs and performance issues
3. Provide optimization suggestions

[Paste merged code]
```

### For Specific Issues

```
Below is my project code. I'm encountering [specific issue description].
Please help me:
1. Locate the root cause
2. Provide solutions
3. Show the modified code

[Paste merged code]
```

---

## FAQ

**Q: Why are some files not included?**  
A: Check `FORCE_TEXT_EXTENSIONS` whitelist and `EXCLUDED_FILE_PATTERNS` exclusions.

**Q: Are `.min.js` files processed?**  
A: Content not read, but shown in directory tree so AI understands complete project structure.

---

## License

MIT License - Free to use and modify
