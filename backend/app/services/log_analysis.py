import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from ..models.task import Task, TaskStatus, HealthStatus, RuleType

logger = logging.getLogger(__name__)

def analyze_log_lines(task: Task, lines: List[str]) -> Tuple[Optional[TaskStatus], Optional[HealthStatus], Optional[datetime]]:
    """
    Analyzes log lines to determine task status, health, and last log time.
    Returns:
        (new_status, new_health, last_log_time)
        Values are None if no change/detection.
    """
    if not lines:
        return None, None, None

    error_line_count = 0
    total_lines = len(lines)
    last_log_time_str = None
    last_log_time = None
    
    # 1. Parse lines for Error count and Time
    for line in lines:
        if "Error" in line:
            error_line_count += 1
        
        parts = line.strip().split()
        if len(parts) >= 2:
            try:
                dt_str = f"{parts[0]} {parts[1]}"
                # Validate format
                datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                last_log_time_str = dt_str
            except ValueError:
                pass

    new_status = None
    new_health = None

    # 2. Process Time
    if last_log_time_str:
        try:
            last_log_time = datetime.strptime(last_log_time_str, "%Y-%m-%d %H:%M:%S")
            
            # Check if stopped (> 1 hour old)
            if datetime.now() - last_log_time > timedelta(hours=1):
                new_status = TaskStatus.STOPPED
                new_health = HealthStatus.UNKNOWN 
            else:
                # If recent log, assume running if it was stopped
                if task.status != TaskStatus.RUNNING:
                    new_status = TaskStatus.RUNNING
        except Exception as e:
            logger.error(f"Error parsing time check for task {task.name}: {e}")

    # 3. Check Error Percentage (> 40%)
    if total_lines > 0 and (error_line_count / total_lines) > 0.4:
        new_health = HealthStatus.ERROR
    
    # 4. Check Custom Rules (if not already Error)
    # Note: Logic in scheduler checked specific output string content. 
    # Here we have lines. We can join them or check individually. 
    # Joining is safer for "content in output" semantics.
    full_output = "\n".join(lines)
    
    if new_health != HealthStatus.ERROR:
        for rule in task.health_rules:
            if rule.rule_type == RuleType.KEYWORD:
                if rule.rule_content in full_output:
                    new_health = HealthStatus.ERROR
                    break

    return new_status, new_health, last_log_time
