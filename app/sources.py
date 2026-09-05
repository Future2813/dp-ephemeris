import os
import ftplib
import requests
import gzip
import shutil
from datetime import datetime, timezone
from urllib.parse import urlparse

def get_year_doy():
    now = datetime.now(timezone.utc)
    year = now.strftime('%Y')
    doy = now.strftime('%j')
    return year, doy

def build_urls(source_name):
    year, doy = get_year_doy()
    if source_name == 'wuhan_rnx4':
        return f"ftp://igs.gnsswhu.cn/pub/gps/data/daily/{year}/brdc/BRD400DLR_S_{year}{doy}0000_01D_MN.rnx.gz"
    elif source_name == 'ign':
        return f"ftp://igs.ign.fr/pub/igs/data/{year}/{doy}/BRDC00IGN_R_{year}{doy}0000_01D_MN.rnx.gz"
    elif source_name == 'bkg':
        return f"https://igs.bkg.bund.de/root_ftp/IGS/BRDC/{year}/{doy}/BRDM00DLR_S_{year}{doy}0000_01D_MN.rnx.gz"
    else:
        raise ValueError(f"Unknown source: {source_name}")

def download_file(url, dest_path):
    """下载文件，支持 FTP 和 HTTP/HTTPS"""
    parsed = urlparse(url)
    if parsed.scheme == 'ftp':
        host = parsed.hostname
        path = parsed.path
        filename = os.path.basename(path)
        dirname = os.path.dirname(path)
        with ftplib.FTP(host, timeout=60) as ftp:
            ftp.login()  # 匿名登录
            ftp.cwd(dirname)
            with open(dest_path, 'wb') as f:
                ftp.retrbinary(f'RETR {filename}', f.write)
    elif parsed.scheme in ('http', 'https'):
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    else:
        raise ValueError(f"Unsupported scheme: {parsed.scheme}")

def gunzip_file(gz_path, output_path):
    with gzip.open(gz_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def download_and_extract(source_name, work_dir):
    """下载并解压 RINEX 文件，返回解压后的路径"""
    url = build_urls(source_name)
    gz_path = os.path.join(work_dir, f"{source_name}.rnx.gz")
    rinex_path = os.path.join(work_dir, f"{source_name}.rnx")
    try:
        download_file(url, gz_path)
        gunzip_file(gz_path, rinex_path)
        return rinex_path
    except Exception as e:
        raise RuntimeError(f"Failed to download from {source_name}: {e}")
    finally:
        if os.path.exists(gz_path):
            os.remove(gz_path)