# FILE: F:\program5\copyNmerge\cNm_path_optimized.py
import sys
import os
import time
import pyperclip
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

# --- 常量定义 ---

# [显示配置]
# 实时输出时，用于显示文件路径的最大字符长度。超过此长度的路径中间会显示为...
MAX_PATH_DISPLAY_LEN = 80

# [文件过滤]
# 定义单个文件的最大体积（20MB）。超过此大小的文件将被直接跳过，不进行任何读取或分析。
# 目的是为了防止因意外拖入超大文件（如视频、数据库）导致程序内存溢出或长时间无响应。
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024

# [智能识别逻辑]
# 对于具有可疑扩展名（如.docx, .pdf）的文件，即使成功解码为文本，
# 如果其内容长度小于此值（30个字符），我们仍然认为它是一次错误的解码，并将其归类为非文本文件。
# 目的是过滤掉那些二进制文件头部恰好能被解码成一小段无意义文本的情况。
MIN_SUSPICIOUS_TEXT_LEN = 30

# 乱码检测阈值。在文件头部的样本中，如果不可打印字符（除换行、制表符外）的比例超过5%，
# 则该文件被判定为二进制/乱码文件。这个值可以根据需要微调，值越低越严格。
NON_PRINTABLE_THRESHOLD = 0.05

# 进行乱码检测时，从文件头部读取的样本大小（8KB）。
# 我们仅检查这部分内容来判断文件类型，而不是读取整个文件，这极大地提高了处理大文件时的性能。
GARBAGE_CHECK_SAMPLE_SIZE = 8192

# 只有当读取到的文本样本长度超过此值（100个字符）时，才启动乱码检测。
# 这是为了防止对本身内容就很少的短文本文件（如只有一个单词的txt）进行误判。
GARBAGE_CHECK_MIN_LEN = 100

# --- ---- ---

SUSPICIOUS_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.jpg', 
    '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.mp3', 
    '.wav', '.mp4', '.mkv', '.avi', '.mov', '.flv', '.zip', '.rar', 
    '.7z', '.tar', '.gz', '.exe', '.dll', '.so', '.bin', '.iso', '.dat', '.db'
}

# --- 结构化结果定义 ---
class Status(Enum):
    TEXT_SUCCESS = auto()
    NON_TEXT = auto()
    SKIPPED_LARGE = auto()
    SKIPPED_SUSPICIOUS_SHORT = auto()
    FAILED = auto()

@dataclass
class ProcessResult:
    path: str
    status: Status
    content: Optional[str] = None
    error_message: Optional[str] = None

# --- 核心逻辑函数 ---

def is_likely_garbage_text(text_sample: str) -> bool:
    """通过计算不可打印字符的比例来判断文本样本是否为二进制乱码。"""
    if len(text_sample) < GARBAGE_CHECK_MIN_LEN:
        return False
    
    non_printable_count = sum(1 for char in text_sample if not char.isprintable() and char not in '\n\r\t')
    ratio = non_printable_count / len(text_sample)
    return ratio > NON_PRINTABLE_THRESHOLD

def analyze_file(file_path: str) -> ProcessResult:
    """分析单个文件，返回一个包含所有信息的 ProcessResult 对象。"""
    try:
        if os.path.getsize(file_path) > MAX_FILE_SIZE_BYTES:
            return ProcessResult(path=file_path, status=Status.SKIPPED_LARGE)

        content = None
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                sample = f.read(GARBAGE_CHECK_SAMPLE_SIZE)
                if is_likely_garbage_text(sample):
                    return ProcessResult(path=file_path, status=Status.NON_TEXT)
                content = sample + f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="gb18030", errors="ignore") as f:
                sample = f.read(GARBAGE_CHECK_SAMPLE_SIZE)
                if is_likely_garbage_text(sample):
                    return ProcessResult(path=file_path, status=Status.NON_TEXT)
                content = sample + f.read()
        
        _, extension = os.path.splitext(file_path)
        is_suspicious = extension.lower() in SUSPICIOUS_EXTENSIONS
        if is_suspicious and len(content) < MIN_SUSPICIOUS_TEXT_LEN:
            return ProcessResult(path=file_path, status=Status.SKIPPED_SUSPICIOUS_SHORT)

        return ProcessResult(path=file_path, status=Status.TEXT_SUCCESS, content=content)

    except (PermissionError, FileNotFoundError) as e:
        return ProcessResult(path=file_path, status=Status.FAILED, error_message=str(e))
    except Exception as e:
        return ProcessResult(path=file_path, status=Status.NON_TEXT, error_message=str(e))

# --- 新增：路径格式化辅助函数 ---
def truncate_path(path: str, max_len: int) -> str:
    """如果路径超过最大长度，则在中间用...缩短它。"""
    if len(path) <= max_len:
        return path
    
    # 为 "..." 留出3个字符
    total_chars_to_keep = max_len - 3
    head_len = total_chars_to_keep // 2
    tail_len = total_chars_to_keep - head_len
    
    head = path[:head_len]
    tail = path[-tail_len:]
    
    return f"{head}...{tail}"

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
            for root, _, files in os.walk(abs_path):
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
            
            status_map = {
                Status.TEXT_SUCCESS: "✔  成功 (文本)",
                Status.NON_TEXT: "🖼  成功 (二进制)",
                Status.SKIPPED_LARGE: "🟡  跳过 (文件过大)",
                Status.SKIPPED_SUSPICIOUS_SHORT: "🟡  跳过 (可疑且内容过短)",
                Status.FAILED: f"❌ 失败 ({res.error_message})"
            }
            status_str = status_map.get(res.status, "未知状态")
            
            # --- 此处是唯一的修改点 ---
            # 使用新函数格式化路径用于显示
            display_path = truncate_path(res.path, MAX_PATH_DISPLAY_LEN)
            print(f"{display_path} ===> {status_str}")
            
            results.append(res)

    end_time = time.monotonic()
    total_duration = end_time - start_time

    # --- 结果聚合与报告 ---
    text_results = []
    failed_files = []
    skipped_large_files = []
    non_text_files_count = 0

    for res in results:
        if res.status == Status.TEXT_SUCCESS:
            text_results.append(res)
        elif res.status == Status.FAILED:
            failed_files.append((res.path, res.error_message))
        elif res.status == Status.SKIPPED_LARGE:
            skipped_large_files.append(res.path)
        else:
            non_text_files_count += 1
    
    if text_results:
        merged_texts = [f"===== FILE: {res.path} =====\n{res.content}\n{'-'*60}\n" for res in text_results]
        final_text = "\n".join(merged_texts)
        pyperclip.copy(final_text.replace('\x00', ''))
        print("\n✅ 已复制到剪贴板")
    else:
        print("\nℹ️ 未处理任何有效文本内容，剪贴板未改动。")

    print("\n----- 处理报告 -----")
    print(f"✔️ 成功处理文本文件: {len(text_results)} 个")
    print(f"🔩 处理为非文本文件: {non_text_files_count} 个")
    print(f"⏭️ 因过大而跳过的文件: {len(skipped_large_files)} 个")
    print(f"❌ 失败的文件或路径: {len(failed_files)} 个")
    print(f"⏱️ 总耗时: {total_duration:.2f} 秒")

    if skipped_large_files:
        print("\n跳过的文件列表:")
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
