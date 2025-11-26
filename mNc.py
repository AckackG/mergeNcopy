import sys
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Dict
from collections import defaultdict

# 尝试导入 pyperclip，如果失败则设置标记
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

# --- 常量定义 ---

# [显示配置]
# 实时输出时，用于显示文件路径的最大字符长度。超过此长度的路径中间会显示为...
MAX_PATH_DISPLAY_LEN = 80

# [文件过滤]
# 定义单个文件的最大体积（20MB）。超过此大小的文件将被直接跳过，不进行任何读取或分析。
# 目的是为了防止因意外拖入超大文件（如视频、数据库）导致程序内存溢出或长时间无响应。
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024

# [强制文本读取 / 白名单配置]
# 强制以文本方式读取的文件后缀名列表 (白名单模式)
# 只有在此列表中的后缀名才会被读取
# "*" 表示无后缀的文件
FORCE_TEXT_EXTENSIONS = {
    # --- 排除的后缀 (原 TEMP_FILE_PATTERNS 内容) ---
    # .pyc, .pyo, .pyd, __pycache__, .DS_Store, Thumbs.db
    # .o, .obj, .class, .log, .tmp, .temp, .swp, .swo, ~
    # .lock, package-lock.json, yarn.lock, poetry.lock, Pipfile.lock
    
    # --- 通用文本 ---
    '.txt', '.md', '.markdown', '.rst', '.tex',
    
    # --- 常见编程语言 ---
    # Python
    '.py', '.pyw', '.pyi',
    # JavaScript/Web
    '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.vue',
    '.html', '.htm', '.css', '.scss', '.sass', '.less',
    # Java/JVM
    '.java', '.kt', '.kotlin', '.scala', '.groovy', '.gradle',
    # C/C++
    '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.make', '.cmake',
    # C#/.NET
    '.cs', '.csproj', '.sln', '.vb', '.fs', '.config',
    # Go/Rust/Swift
    '.go', '.rs', '.swift',
    # Shell/Scripting
    '.sh', '.bash', '.zsh', '.bat', '.cmd', '.ps1', '.lua', '.pl', '.pm', '.rb', '.php',
    
    # --- 数据与配置 ---
    '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.conf', '.properties',
    '.sql', '.env', '.gitignore', '.dockerignore', 'Dockerfile',
    
    # --- 其它保留 ---
    # '*' # 保留匹配无后缀文件的能力
}

# [排除路径配置]
# 需要排除的目录路径列表（支持多级路径）
EXCLUDED_PATHS = [
    # Python 相关
    'venv', 'env', '.venv', '.env',
    'venv/Lib', 'venv/lib', 'env/Lib', 'env/lib', '.venv/Lib', '.venv/lib',
    'venv/Scripts', 'env/Scripts', '.venv/Scripts',
    '__pycache__',
    '.pytest_cache',
    '.tox',
    'dist', 'build',
    '*.egg-info',
    '.mypy_cache',
    '.ruff_cache',
    '.eggs',
    'site-packages',
    
    # JavaScript/Node 相关
    'node_modules',
    'node_modules/.bin',
    'node_modules/.cache',
    '.npm',
    '.yarn',
    '.pnp',
    'bower_components',
    'dist', 'build',
    '.next',
    '.nuxt',
    'coverage',
    # 'out',
    '.output',
    
    # Java 相关
    # 'target',
    # 'bin',
    '.gradle',
    '.m2',
    
    # .NET 相关
    # 'bin',
    # 'obj',
    # 'packages',
    '.vs',
    
    # Ruby 相关
    '.bundle',
    'vendor/bundle',
    'vendor/cache',
    
    # Go 相关
    'vendor/bundle',
    'vendor/cache',
    
    # Rust 相关
    'target/debug',
    'target/release',
    
    # 版本控制
    '.git',
    '.svn',
    '.hg',
    
    # IDE 配置
    '.idea',
    '.vscode',
    '.vs',
    '*.code-workspace',
    '.eclipse',
    '.settings',
    
    # 其他
    '.cache',
    'tmp', 'temp',
    'logs',
    '__MACOSX',
]

# [文本读取配置]
# 文本解码尝试的编码列表（按优先级排序）
TEXT_ENCODINGS = [
    ('utf-8-sig', 'ignore'),
    ('gb18030', 'ignore'),
]

# [语言特定注释符号]
# 用于在合并文件头部标记文件路径时使用相应语言的注释符号
COMMENT_MARKERS = {
    # Python
    '.py': '#',
    '.pyw': '#',
    '.pyi': '#',
    
    # JavaScript/TypeScript
    '.js': '//',
    '.jsx': '//',
    '.ts': '//',
    '.tsx': '//',
    '.mjs': '//',
    '.cjs': '//',
    
    # Java/C/C++/C#
    '.java': '//',
    '.c': '//',
    '.cpp': '//',
    '.cc': '//',
    '.cxx': '//',
    '.h': '//',
    '.hpp': '//',
    '.cs': '//',
    '.go': '//',
    '.rs': '//',
    '.swift': '//',
    '.kt': '//',
    '.scala': '//',
    
    # Shell scripts
    '.sh': '#',
    '.bash': '#',
    '.zsh': '#',
    
    # Batch/PowerShell
    '.bat': 'REM',
    '.cmd': 'REM',
    '.ps1': '#',
    
    # SQL
    '.sql': '--',
    
    # HTML/XML
    '.html': '<!--',
    '.htm': '<!--',
    '.xml': '<!--',
    
    # CSS
    '.css': '/*',
    '.scss': '//',
    '.sass': '//',
    '.less': '//',
    
    # Ruby
    '.rb': '#',
    
    # PHP
    '.php': '//',
    
    # Lua
    '.lua': '--',
    
    # R
    '.r': '#',
    '.R': '#',
    
    # Perl
    '.pl': '#',
    '.pm': '#',
    
    # YAML/TOML
    '.yaml': '#',
    '.yml': '#',
    '.toml': '#',
    
    # Configuration files
    '.ini': '#',
    '.conf': '#',
    '.config': '#',
    
    # Markdown
    '.md': '<!--',
    '.markdown': '<!--',
}

# --- 结构化结果定义 ---
class Status(Enum):
    TEXT_SUCCESS = auto()
    NON_TEXT = auto()
    SKIPPED_LARGE = auto()
    SKIPPED_NOT_WHITELISTED = auto() # 替换了 SKIPPED_TEMP
    SKIPPED_EXCLUDED_PATH = auto()
    FAILED = auto()

@dataclass
class ProcessResult:
    path: str
    status: Status
    content: Optional[str] = None
    error_message: Optional[str] = None

# --- 核心逻辑函数 ---

def should_exclude_path(file_path: str) -> bool:
    """检查文件路径是否应该被排除"""
    normalized_path = file_path.replace('\\', '/')
    path_parts = normalized_path.split('/')
    
    for excluded in EXCLUDED_PATHS:
        if '*' in excluded:
            import fnmatch
            if any(fnmatch.fnmatch(part, excluded) for part in path_parts):
                return True
        else:
            excluded_parts = excluded.split('/')
            for i in range(len(path_parts) - len(excluded_parts) + 1):
                if path_parts[i:i+len(excluded_parts)] == excluded_parts:
                    return True
    
    return False

def should_exclude_directory(dir_path: str) -> bool:
    """检查目录是否应该被排除（用于os.walk的目录过滤）"""
    return should_exclude_path(dir_path)

def is_allowed_extension(file_path: str) -> bool:
    """检查文件是否在允许的白名单列表中"""
    _, ext = os.path.splitext(file_path)
    
    # 检查是否有扩展名
    if not ext:
        # 检查是否包含特殊文件名（如 Dockerfile）在白名单中
        filename = os.path.basename(file_path)
        if filename in FORCE_TEXT_EXTENSIONS:
            return True
        return '*' in FORCE_TEXT_EXTENSIONS
    
    return ext.lower() in FORCE_TEXT_EXTENSIONS

def get_comment_marker(file_path: str) -> str:
    """根据文件扩展名获取相应的注释符号"""
    _, ext = os.path.splitext(file_path)
    ext_lower = ext.lower()
    
    marker = COMMENT_MARKERS.get(ext_lower, '#')
    
    # 对于需要闭合的注释符号，只返回开始符号
    if marker in ['<!--', '/*']:
        return marker
    
    return marker

def format_file_header(file_path: str) -> str:
    """格式化文件头部，使用语言特定的注释符号，并包含修改时间"""
    comment = get_comment_marker(file_path)
    separator = '=' * 60
    
    # 获取文件修改时间
    try:
        mtime = os.path.getmtime(file_path)
        modified_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        modified_time = "Unknown"
    
    if comment == '<!--':
        return f"<!-- {separator}\n     FILE: {file_path}\n     MODIFIED: {modified_time}\n     {separator} -->\n"
    elif comment == '/*':
        return f"/* {separator}\n   FILE: {file_path}\n   MODIFIED: {modified_time}\n   {separator} */\n"
    else:
        return f"{comment} {separator}\n{comment} FILE: {file_path}\n{comment} MODIFIED: {modified_time}\n{comment} {separator}\n"

def analyze_file(file_path: str) -> ProcessResult:
    """分析单个文件，返回一个包含所有信息的 ProcessResult 对象。"""
    try:
        # 1. 检查排除路径
        if should_exclude_path(file_path):
            return ProcessResult(path=file_path, status=Status.SKIPPED_EXCLUDED_PATH)
        
        # 2. 检查白名单 (白名单模式)
        if not is_allowed_extension(file_path):
            return ProcessResult(path=file_path, status=Status.SKIPPED_NOT_WHITELISTED)
        
        # 3. 检查文件大小
        if os.path.getsize(file_path) > MAX_FILE_SIZE_BYTES:
            return ProcessResult(path=file_path, status=Status.SKIPPED_LARGE)

        content = None
        decode_success = False
        
        # 尝试多种编码读取文件
        for encoding, errors in TEXT_ENCODINGS:
            try:
                with open(file_path, "r", encoding=encoding, errors=errors) as f:
                    content = f.read()
                    decode_success = True
                    break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        # 如果解码失败，由于是白名单模式，通常不再强行尝试，除非确实需要
        # 但为了稳健性，如果解码完全失败（例如二进制），即使在白名单也可能无法读取
        if not decode_success:
            # 尝试最后一次强制 utf-8 替换错误
            try:
                with open(file_path, "r", encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    decode_success = True
            except Exception:
                pass
        
        if not decode_success:
            return ProcessResult(path=file_path, status=Status.NON_TEXT)

        return ProcessResult(path=file_path, status=Status.TEXT_SUCCESS, content=content)

    except (PermissionError, FileNotFoundError) as e:
        return ProcessResult(path=file_path, status=Status.FAILED, error_message=str(e))
    except Exception as e:
        return ProcessResult(path=file_path, status=Status.NON_TEXT, error_message=str(e))

def truncate_path(path: str, max_len: int) -> str:
    """如果路径超过最大长度，则在中间用...缩短它。"""
    if len(path) <= max_len:
        return path
    
    total_chars_to_keep = max_len - 3
    head_len = total_chars_to_keep // 2
    tail_len = total_chars_to_keep - head_len
    
    head = path[:head_len]
    tail = path[-tail_len:]
    
    return f"{head}...{tail}"

def get_desktop_path() -> str:
    """获取桌面路径"""
    if sys.platform == 'win32':
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
            desktop_path = winreg.QueryValueEx(key, 'Desktop')[0]
            winreg.CloseKey(key)
            return desktop_path
        except Exception:
            return os.path.join(os.path.expanduser('~'), 'Desktop')
    else:
        return os.path.join(os.path.expanduser('~'), 'Desktop')

def build_tree_structure(file_paths: List[str], base_path: str = None) -> str:
    """构建目录树结构字符串"""
    if not file_paths:
        return ""
    
    # 确定基础路径
    if base_path is None:
        if len(file_paths) == 1:
            base_path = os.path.dirname(file_paths[0])
        else:
            base_path = os.path.commonpath(file_paths)
    
    # 构建树形结构
    tree_dict = {}
    for file_path in file_paths:
        try:
            rel_path = os.path.relpath(file_path, base_path)
        except ValueError:
            rel_path = file_path
        
        parts = rel_path.split(os.sep)
        current = tree_dict
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
    
    # 递归生成树形字符串
    def generate_tree(node: dict, prefix: str = "", is_last: bool = True) -> List[str]:
        lines = []
        items = sorted(node.items(), key=lambda x: (bool(x[1]), x[0]))  # 文件在前，目录在后
        
        for i, (name, children) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            connector = "└── " if is_last_item else "├── "
            lines.append(f"{prefix}{connector}{name}")
            
            if children:
                extension = "    " if is_last_item else "│   "
                lines.extend(generate_tree(children, prefix + extension, is_last_item))
        
        return lines
    
    tree_lines = [os.path.basename(base_path) or base_path]
    tree_lines.extend(generate_tree(tree_dict))
    
    return "\n".join(tree_lines)

def analyze_file_statistics(file_paths: List[str]) -> Dict[str, int]:
    """分析文件扩展名统计"""
    extension_count = defaultdict(int)
    
    for file_path in file_paths:
        _, ext = os.path.splitext(file_path)
        if ext:
            extension_count[ext.lower()] += 1
        else:
            extension_count['[无扩展名]'] += 1
    
    # 按数量排序
    sorted_stats = dict(sorted(extension_count.items(), key=lambda x: x[1], reverse=True))
    return sorted_stats

def is_documentation_file(file_path: str) -> bool:
    """判断是否为文档类文件（README、MD等）"""
    file_name = os.path.basename(file_path).lower()
    _, ext = os.path.splitext(file_path)
    
    # README 文件
    if file_name.startswith('readme'):
        return True
    
    # Markdown 文件
    if ext.lower() in ['.md', '.markdown']:
        return True
    
    return False

def sort_files_by_priority(results: List['ProcessResult']) -> List['ProcessResult']:
    """按优先级排序文件：代码文件在前，文档文件在后"""
    code_files = []
    doc_files = []
    
    for result in results:
        if is_documentation_file(result.path):
            doc_files.append(result)
        else:
            code_files.append(result)
    
    # 分别按路径排序，保持稳定性
    code_files.sort(key=lambda x: x.path)
    doc_files.sort(key=lambda x: x.path)
    
    return code_files + doc_files

# --- 主程序 ---

def main():
    if len(sys.argv) < 2:
        print("用法: 请将一个或多个文件/文件夹拖拽到 .bat 文件上。")
        time.sleep(3)
        return

    print("--- 正在发现文件... ---")
    paths_to_process = []
    processed_paths = set()
    for path_arg in sys.argv[1:]:
        abs_path = os.path.abspath(path_arg)
        if abs_path in processed_paths:
            continue
        
        if os.path.isfile(abs_path):
            processed_paths.add(abs_path)
            paths_to_process.append(abs_path)
        elif os.path.isdir(abs_path):
            for root, dirs, files in os.walk(abs_path):
                # 过滤掉应该排除的目录，避免进入遍历
                dirs[:] = [d for d in dirs if not should_exclude_directory(os.path.join(root, d))]
                
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    if file_path not in processed_paths:
                        processed_paths.add(file_path)
                        paths_to_process.append(file_path)

    if not paths_to_process:
        print("未找到任何文件进行处理。")
        return

    start_time = time.monotonic()
    
    results: List[ProcessResult] = []
    with ThreadPoolExecutor() as executor:
        future_to_path = {executor.submit(analyze_file, path): path for path in paths_to_process}
        
        print(f"\n--- 开始处理 {len(paths_to_process)} 个文件 ---\n")
        for future in as_completed(future_to_path):
            res = future.result()
            
            # 对于排除路径的文件，不输出到控制台
            if res.status == Status.SKIPPED_EXCLUDED_PATH:
                results.append(res)
                continue
            
            status_map = {
                Status.TEXT_SUCCESS: "✔  成功 (文本)",
                Status.NON_TEXT: "🖼  跳过 (非文本)",
                Status.SKIPPED_LARGE: "🟡 跳过 (文件过大)",
                Status.SKIPPED_NOT_WHITELISTED: "⚪ 跳过 (未在白名单)",
                Status.FAILED: f"❌ 失败 ({res.error_message})"
            }
            status_str = status_map.get(res.status, "未知状态")
            
            # 如果是白名单跳过，可以选择不打印以减少噪音，但为了明确反馈，这里还是打印
            display_path = truncate_path(res.path, MAX_PATH_DISPLAY_LEN)
            print(f"{display_path} ===> {status_str}")
            
            results.append(res)

    end_time = time.monotonic()
    total_duration = end_time - start_time

    # --- 结果聚合与报告 ---
    text_results = []
    failed_files = []
    skipped_large_files = []
    skipped_not_whitelisted = []
    skipped_excluded_files = []
    non_text_files_count = 0

    for res in results:
        if res.status == Status.TEXT_SUCCESS:
            text_results.append(res)
        elif res.status == Status.FAILED:
            failed_files.append((res.path, res.error_message))
        elif res.status == Status.SKIPPED_LARGE:
            skipped_large_files.append(res.path)
        elif res.status == Status.SKIPPED_NOT_WHITELISTED:
            skipped_not_whitelisted.append(res.path)
        elif res.status == Status.SKIPPED_EXCLUDED_PATH:
            skipped_excluded_files.append(res.path)
        else:
            non_text_files_count += 1
    
    if text_results:
        # 按优先级排序：代码文件在前，文档在后
        sorted_results = sort_files_by_priority(text_results)
        
        # 生成项目统计信息
        all_paths = [res.path for res in sorted_results]
        
        # 确定基础路径
        if len(all_paths) == 1:
            base_path = os.path.dirname(all_paths[0])
        else:
            base_path = os.path.commonpath(all_paths)
        
        tree_structure = build_tree_structure(all_paths, base_path)
        file_stats = analyze_file_statistics(all_paths)
        
        # 构建统计信息头部
        stats_header = "=" * 80 + "\n"
        stats_header += "PROJECT ANALYSIS SUMMARY\n"
        stats_header += "=" * 80 + "\n\n"
        stats_header += f"Base Path: {base_path}\n"
        stats_header += f"Total Files: {len(all_paths)}\n"
        stats_header += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        stats_header += "File Type Distribution:\n"
        stats_header += "-" * 40 + "\n"
        for ext, count in file_stats.items():
            stats_header += f"  {ext:20s} : {count:4d} files\n"
        
        stats_header += "\n" + "=" * 80 + "\n"
        stats_header += "DIRECTORY STRUCTURE\n"
        stats_header += "=" * 80 + "\n\n"
        stats_header += tree_structure + "\n\n"
        stats_header += "=" * 80 + "\n"
        stats_header += "FILE CONTENTS\n"
        stats_header += "=" * 80 + "\n\n"
        
        # 合并文件内容
        merged_texts = [f"{format_file_header(res.path)}{res.content}\n{'-'*60}\n" 
                       for res in sorted_results]
        final_text = stats_header + "\n".join(merged_texts)
        clean_text = final_text.replace('\x00', '')
        
        # 统计字符数
        total_chars = len(clean_text)
        
        # 生成桌面文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        desktop_path = get_desktop_path()
        output_file = os.path.join(desktop_path, f"{timestamp}.txt")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(clean_text)
            print(f"\n✅ 已生成文件: {output_file}")
        except Exception as e:
            print(f"\n❌ 文件生成失败: {e}")
        
        # 复制到剪贴板（如果可用）
        if PYPERCLIP_AVAILABLE:
            try:
                pyperclip.copy(clean_text)
                print("✅ 已复制到剪贴板")
            except Exception as e:
                print(f"⚠️  剪贴板复制失败: {e}")
        else:
            print("ℹ️  未安装 pyperclip 模块，跳过剪贴板复制")
    else:
        print("\nℹ️ 未处理任何有效文本内容。")

    print("\n----- 处理报告 -----")
    print(f"✔️  成功处理文本文件: {len(text_results)} 个")
    print(f"📝 总字符数: {total_chars:,} 字符" if text_results else "")
    print(f"🔩 跳过的非文本文件: {non_text_files_count} 个")
    print(f"⏭️  因过大而跳过的文件: {len(skipped_large_files)} 个")
    print(f"⚪  未在白名单的文件: {len(skipped_not_whitelisted)} 个")
    print(f"⏭️  排除路径中的文件: {len(skipped_excluded_files)} 个")
    print(f"❌ 失败的文件或路径: {len(failed_files)} 个")
    print(f"⏱️  总耗时: {total_duration:.2f} 秒")

    if skipped_large_files:
        print("\n跳过的大文件列表:")
        for path in skipped_large_files:
            print(f"  - {path}")

    if failed_files:
        print("\n失败的路径列表:")
        for path, reason in failed_files:
            print(f"  - {path}\n    原因: {reason}")
    
    print("--------------------")

    timeout = 30 if failed_files else 5
    print(f"\n程序将在 {timeout} 秒后自动关闭...")
    time.sleep(timeout)

if __name__ == "__main__":
    main()
