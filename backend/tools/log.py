from datetime import datetime



def write_log(content: str, log_path):
    """按格式写入本地日志文件： 时间：内容"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp}: {content}\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)