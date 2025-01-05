import schedule
import time
import uuid
import threading
from app.utils.logger import logger

# 需要安装的模块：schedule
# pip install schedule

_scheduler = None
class Scheduler:
    """
    定时任务管理
    """
    def __init__(self):
        self.jobs = {}
        self.scheduler_thread = None
    
    def add_job(self, job_name, interval, job_func, args=None):
        """
        添加一个定时任务
        Args:
          job_name: 定时任务名称，必须唯一
          interval: 时间间隔，单位为秒
          job_func: 需要执行的函数
          args: 函数需要的参数
        """
        if job_name in self.jobs:
          logger.warning(f"定时任务已存在，不能重复添加: job_name={job_name}")
          return
        schedule_job = schedule.every(interval).seconds
        
        schedule_job.do(self._safe_run, job_func, args)
        self.jobs[job_name] = schedule_job
        logger.info(f"添加定时任务成功: job_name={job_name}, interval={interval}")
    
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
        """启动所有任务，并且保持运行，使用while True 循环"""
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def start_scheduler(self):
        """启动定时任务"""
        if not self.scheduler_thread or not self.scheduler_thread.is_alive():
          self.scheduler_thread = threading.Thread(target=self.run_all)
          self.scheduler_thread.daemon = True
          self.scheduler_thread.start()
          logger.info("定时任务启动！")
        else:
          logger.warning("定时任务已经启动，无需重复启动")

    def remove_job(self, job_name):
      """移除定时任务"""
      if job_name in self.jobs:
          schedule.cancel_job(self.jobs[job_name])
          del self.jobs[job_name]
          logger.info(f"删除定时任务成功， job_name = {job_name}")
      else:
          logger.warning(f"未找到要删除的任务, job_name={job_name}")

    def add_delayed_job(self, delay, job_func, args=None):
        """
        添加一个延迟执行的任务
        Args:
          delay:  延迟的时间(s)
          job_func: 需要执行的函数
          args: 函数的参数
        """
        def run_job():
            self._safe_run(job_func, args)
            self.remove_job(job_name)  # 执行完删除任务
            
        job_name = str(uuid.uuid4())
        schedule_job = schedule.every(delay).seconds.do(run_job)
        self.jobs[job_name] = schedule_job
        logger.info(f"添加延迟执行任务成功， job_name= {job_name}")


def create_scheduler():
    """创建定时任务实例，并赋值给全局变量_scheduler"""
    global _scheduler
    if not _scheduler:
      _scheduler = Scheduler()
    return _scheduler

def get_scheduler():
    """获取 scheduler 实例"""
    global _scheduler
    if not _scheduler:
      _scheduler = create_scheduler()
    return _scheduler