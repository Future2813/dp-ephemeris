import os

class Config:
    DATA_DIR = os.getenv('DATA_DIR', '/data')
    LOG_DIR = os.getenv('LOG_DIR', '/logs')
    # 数据源优先级，逗号分隔，如 "wuhan_rnx4,ign,bkg"
    SOURCE_PRIORITY = os.getenv('SOURCE_PRIORITY', 'wuhan_rnx4,ign,bkg').split(',')
    AUTO_DOWNGRADE = os.getenv('AUTO_DOWNGRADE', 'true').lower() == 'true'
    DOWNLOAD_TIMEOUT = 60
    OUTPUT_RTCM3 = os.path.join(DATA_DIR, 'brdc.rtcm3')