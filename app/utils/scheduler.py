import schedule
import time
import threading
from app.utils.logger import logger

# 需要安装的模块：schedule
# pip install schedule

class Scheduler:
    """
    定时任务管理
    """
    def __init__(self):
        self.jobs = {}
    
    def add_job(self, job_name, schedule_str, job_func, args=None):
        """
        添加一个定时任务
        Args:
          job_name: 定时任务名称，必须唯一
          schedule_str: 定时规则，例如 every().day.at("10:30")
          job_func: 需要执行的函数
          args: 函数需要的参数
        """
        if job_name in self.jobs:
          logger.warning(f"定时任务已存在，不能重复添加: job_name={job_name}")
          return
        schedule_job = schedule.every()
        exec(f'schedule_job.{schedule_str}') # 执行字符串化的调度
        schedule_job.do(self._safe_run, job_func, args)
        self.jobs[job_name] = schedule_job
        logger.info(f"添加定时任务成功: job_name={job_name}, schedule_str={schedule_str}")
    
    def _safe_run(self, func, args):
        """安全地执行定时任务"""
        try:
           if args:
             func(*args)
           else:
             func()
        except Exception as e:
          logger.error(f"定时任务执行失败, error={e}")
        
    def run_all(self):
        """启动所有任务，并且保持运行"""
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start_scheduler(self):
      """启动定时任务"""
      thread = threading.Thread(target=self.run_all)
      thread.daemon = True
      thread.start()
      logger.info("定时任务启动！")
   
    def remove_job(self, job_name):
      """移除定时任务"""
      if job_name in self.jobs:
          schedule.cancel_job(self.jobs[job_name])
          del self.jobs[job_name]
          logger.info(f"删除定时任务成功， job_name = {job_name}")
      else:
        logger.warning(f"未找到要删除的任务, job_name={job_name}")