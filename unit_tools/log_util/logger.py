import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def get_logger(
    name: str = None,
    level: str = "INFO",
    log_dir: str = "logs",
    base_filename: str = "test",
    when: str = "midnight",
    interval: int = 1,
    backup_count: int = 7
):
    if name is None:
        name = __name__

    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{base_filename}.log")

    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] "
        "[%(process)d-%(threadName)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)
    console_handler.setLevel(logging.WARNING)

    # 文件 handler（每天切分）
    file_handler = TimedRotatingFileHandler(
        filename=log_path,
        when=when,
        interval=interval,
        backupCount=backup_count,
        encoding="utf-8",
        utc=False
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.INFO)

    # ⚠️ 关键：文件 handler 要挂到所有 logger 上
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 每次运行写入分隔符
    logger.info("\n\n" + "=" * 30 +
                f" NEW RUN START {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} " +
                "=" * 30 + "\n")

    return logger
