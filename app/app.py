import os
import json
import logging
from flask import Flask, render_template, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .config import Config
from .task import run_download_task

app = Flask(__name__)
scheduler = BackgroundScheduler()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    status = {}
    status_file = os.path.join(Config.DATA_DIR, 'status.json')
    if os.path.exists(status_file):
        with open(status_file) as f:
            status = json.load(f)
    return render_template('index.html', status=status, config=Config)

@app.route('/trigger', methods=['POST'])
def trigger():
    """手动触发下载任务"""
    run_download_task()
    return redirect(url_for('index'))

def start_scheduler():
    # 每小时执行一次
    scheduler.add_job(run_download_task, IntervalTrigger(hours=1), id='download_job')
    scheduler.start()
    logger.info("Scheduler started")

if __name__ == '__main__':
    # 启动时先执行一次任务（可选，取消注释即可）
    # run_download_task()
    start_scheduler()
    app.run(host='0.0.0.0', port=5000, debug=False)