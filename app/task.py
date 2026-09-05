import os
import shutil
import logging
from datetime import datetime
from .config import Config
from .sources import download_and_extract
from .converter import convert_to_rtcm3

logger = logging.getLogger(__name__)

def process_source(source, work_dir):
    """处理单个数据源，下载并转换为 RTCM3"""
    rinex_file = download_and_extract(source, work_dir)
    logger.info(f"Downloaded RINEX from {source}: {rinex_file}")

    # 直接转换为 RTCM3（适用于所有源，包括 RINEX 4）
    convert_to_rtcm3(rinex_file, Config.OUTPUT_RTCM3)
    logger.info(f"Converted to RTCM3: {Config.OUTPUT_RTCM3}")
    return True

def run_download_task():
    """下载并转换广播星历"""
    logger.info("Starting download task...")
    work_dir = os.path.join(Config.DATA_DIR, 'work')
    os.makedirs(work_dir, exist_ok=True)

    # 清空工作目录
    for f in os.listdir(work_dir):
        os.remove(os.path.join(work_dir, f))

    success = False
    used_source = None
    for source in Config.SOURCE_PRIORITY:
        try:
            logger.info(f"Trying source: {source}")
            if process_source(source, work_dir):
                success = True
                used_source = source
                break
        except Exception as e:
            logger.error(f"Source {source} failed: {e}")
            if not Config.AUTO_DOWNGRADE:
                break
            # 否则继续尝试下一个源

    if not success:
        logger.error("All sources failed")

    update_status(success, used_source, datetime.utcnow().isoformat())
    shutil.rmtree(work_dir, ignore_errors=True)

def update_status(success, source, time):
    """将状态写入文件供 Web 界面读取"""
    status_file = os.path.join(Config.DATA_DIR, 'status.json')
    import json
    with open(status_file, 'w') as f:
        json.dump({
            'success': success,
            'source': source,
            'time': time,
            'output': Config.OUTPUT_RTCM3
        }, f)