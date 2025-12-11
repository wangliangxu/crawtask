from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta
import asyncio

from ..database import SessionLocal
from ..models.node import Node
from ..models.task import Task, TaskStatus, HealthStatus, RuleType
from .ssh_service import ssh_manager
from ..models.system import SystemSetting

import json
from pathlib import Path

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

def get_interval_from_db():
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter(SystemSetting.key == "inspection_interval").first()
        if setting and setting.value:
            return int(setting.value)
    except Exception as e:
        logger.error(f"Failed to fetch interval from DB: {e}")
    finally:
        db.close()
    return 600

async def check_task_health_job():
    """
    Periodic job to check health of all active tasks.
    """
    db: Session = SessionLocal()
    try:
        tasks = db.query(Task).filter(Task.is_enabled == True).all() 
        gateway_node = db.query(Node).filter(Node.is_center == 1).first()
        for task in tasks:
            await verify_single_task(db, task, gateway_node)
    finally:
        db.close()

async def verify_single_task(db: Session, task: Task, gateway_node: Node = None):
    """
    Verifies a single task's health by tailing logs and checking rules.
    """
    if not task.node:
        return

    try:
        # Get last 50 lines
        command = f"tail -n 50 {task.log_file_path}"
        output = await ssh_manager.execute_command(task.node, command, gateway_node=gateway_node)
        
        # Analyze
        lines = output.strip().splitlines()
        
        # Use shared analysis service
        from .log_analysis import analyze_log_lines
        new_status, new_health, last_log_time = analyze_log_lines(task, lines)

        if last_log_time:
            task.last_log_time = last_log_time
            logger.info(f"Task {task.name} last log time: {last_log_time}")

        if new_status:
            task.status = new_status
            if new_status == TaskStatus.STOPPED:
                 logger.warning(f"Task {task.name} detected as STOPPED based on log time.")

        # Update health if detected, otherwise default to HEALTHY (if not previously ERROR/WARNING?)
        # The previous logic defaulted to HEALTHY at start.
        if new_health:
            task.health_status = new_health
        else:
            # If no error detected, assumes healthy? 
            # Previous logic: new_health = HealthStatus.HEALTHY initially.
            # Then if Error -> ERROR.
            # So if analysis returns None, it means no ERROR found.
            # But we must preserve the logic that if NO error found, it IS healthy.
            if not new_health and task.status == TaskStatus.RUNNING:
                 task.health_status = HealthStatus.HEALTHY

        task.last_check_time = datetime.now()
        db.commit()

    except Exception as e:
        logger.error(f"Health check failed for task {task.name}: {e}")
        task.health_status = HealthStatus.UNKNOWN
        db.commit()

def update_job_interval(seconds: int):
    scheduler.reschedule_job('health_check_job', trigger='interval', seconds=seconds)
    logger.info(f"Updated health check job interval to {seconds} seconds")

def start_scheduler():
    interval = get_interval_from_db()
    scheduler.add_job(check_task_health_job, 'interval', seconds=interval, id='health_check_job')
    logger.info(f"Scheduler started with interval {interval}s")
    scheduler.start()
