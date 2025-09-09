# 自用文本一键合并&复制工具

一个命令行工具，用于快速合并一个或多个文件/文件夹的文本内容，并自动复制到系统剪-贴板。

## 核心用法

1.  将 `.py` 和 `.bat` 放到任意文件夹内。
2.  **直接将任意文件或文件夹拖拽到 `mNc.bat` 文件上即可执行。**
3.  (可选) 在资源管理器地址栏运行 `shell:sendto`，将 `mNc.bat` 文件的快捷方式粘贴进去，即可通过“右键 -> 发送到”的方式调用。

<img width="930" height="466" alt="image" src="https://github.com/user-attachments/assets/09883392-7b97-4fb9-8641-5a0b840b435b" />

## 主要特性

- **并发处理**: 使用多线程并发读取文件，处理大量文件时速度很快。
- **递归遍历**: 支持拖入文件夹，会自动递归遍历所有子文件。
- **智能识别**:
    - 自动处理 `UTF-8` 和 `GBK` 编码。
    - 通过头部采样和乱码检测，能有效区分文本文件和二进制文件（如图片、Office文档）。
    - 能识别出被修改了扩展名的文本文件。
- **安全过滤**: 自动跳过体积过大的文件，防止程序崩溃。
- **清晰报告**: 任务完成后，会统计成功、失败、跳过的文件数量和总耗时。

## 依赖

需要全局安装 `pyperclip` 库：
```bash
pip install pyperclip
```

## 配置

主要的配置项都在 Python 脚本 (`cNm_... .py`) 顶部的 **常量定义**区域，可根据需要自行修改，例如：

- `MAX_FILE_SIZE_BYTES`: 修改要跳过的大文件阈值。
- `MAX_PATH_DISPLAY_LEN`: 修改实时输出时路径的显示长度。
- `NON_PRINTABLE_THRESHOLD`: 调整乱码检测的灵敏度。

---

# Personal Text Merge & Copy Tool

A command-line tool to quickly merge text content from one or more files/folders and automatically copy it to the system clipboard.

## Core Usage

1.  Place the `.py` and `.bat` files in any folder.
2.  **Simply drag and drop any files or folders onto the `mNc.bat` file to execute.**
3.  (Optional) Run `shell:sendto` in the File Explorer address bar, then paste a shortcut of the `mNc.bat` file into the opened folder. This allows you to use the tool via the "Right-click -> Send to" context menu.

<img width="930" height="466" alt="image" src="https://github.com/user-attachments/assets/09883392-7b97-4fb9-8641-5a0b840b435b" />

## Key Features

- **Concurrent Processing**: Utilizes multi-threading to read files concurrently, significantly speeding up the process for a large number of files.
- **Recursive Traversal**: Supports dragging and dropping folders; it will automatically traverse all sub-files recursively.
- **Intelligent Recognition**:
    - Automatically handles `UTF-8` and `GBK` encodings.
    - Effectively distinguishes between text files and binary files (e.g., images, Office documents) through header sampling and garbage text detection.
    - Can identify text files with incorrect file extensions.
- **Safety Filter**: Automatically skips oversized files to prevent the program from crashing.
- **Clear Reporting**: After the task is completed, it provides a summary of successful, failed, and skipped files, along with the total time taken.

## Dependencies

Requires the global installation of the `pyperclip` library:
```bash
pip install pyperclip
```

## Configuration

The main configuration options are located in the **Constants Definition** section at the top of the Python script (`cNm_... .py`). You can modify them as needed, for example:

- `MAX_FILE_SIZE_BYTES`: Adjust the threshold for skipping large files.
- `MAX_PATH_DISPLAY_LEN`: Change the display length for file paths in the real-time output.
- `NON_PRINTABLE_THRESHOLD`: Fine-tune the sensitivity of the garbage text detection.
