import subprocess
import os

def convert_to_rtcm3(rinex_path, output_rtcm3):
    """使用 convbin 将 RINEX 导航文件（2/3/4）直接转换为 RTCM3"""
    cmd = [
        'convbin',
        '-r', rinex_path,
        '-v', '4.00',      # 指定 RINEX 版本（convbin 通常自动识别，此处可省略或保留）
        '-od',             # 输出观测数据（对导航文件无影响）
        '-os',             # 输出星历数据
        '-f', '2',         # 输出格式：2=RTCM3
        '-o', output_rtcm3
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"convbin failed: {result.stderr}")
    if not os.path.exists(output_rtcm3):
        raise RuntimeError("convbin did not produce output file")