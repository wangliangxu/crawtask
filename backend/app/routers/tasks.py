from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
import shlex

from ..database import get_db
from ..models.task import Task, TaskStatus, HealthRule
from ..models.node import Node
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse, HealthRuleCreate
from ..services.ssh_service import ssh_manager

router = APIRouter(
    prefix="/api/tasks",
    tags=["tasks"],
)

# --- CRUD ---

@router.post("/", response_model=List[TaskResponse])
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    created_tasks = []
    
    # Validate all nodes exist first? Or just skip invalid ones? 
    # Let's validate first to be safe, or just loop and check.
    # The requirement says "create task on multiple nodes".
    
    # Fetch all requested nodes
    nodes = db.query(Node).filter(Node.id.in_(task.node_ids)).all()
    found_node_ids = {n.id for n in nodes}
    
    if len(found_node_ids) != len(set(task.node_ids)):
        # Calculate missing IDs for better error message
        missing = set(task.node_ids) - found_node_ids
        raise HTTPException(status_code=404, detail=f"Nodes with ids {missing} not found")

    for node in nodes:
        db_task = Task(
            name=task.name,
            node_id=node.id,
            log_file_path=task.log_file_path,
            start_command=task.start_command,
            stop_command=task.stop_command,
            check_interval=task.check_interval,
        )
        db.add(db_task)
        db.commit() # Commit to get ID
        db.refresh(db_task)

        # Add Health Rules
        for rule in task.health_rules:
            db_rule = HealthRule(
                task_id=db_task.id,
                rule_type=rule.rule_type,
                rule_content=rule.rule_content
            )
            db.add(db_rule)
        
        db.commit()
        db.refresh(db_task)
        created_tasks.append(db_task)
        
    return created_tasks

@router.get("/", response_model=List[TaskResponse])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    db.delete(task)
    db.commit()
    return {"ok": True}

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update basic fields
    update_data = task_update.dict(exclude_unset=True)
    health_rules_data = update_data.pop("health_rules", None)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    # Update health rules if provided
    if health_rules_data is not None:
        # Clear existing rules
        db.query(HealthRule).filter(HealthRule.task_id == task_id).delete()
        
        # Add new rules
        for rule in health_rules_data:
            db_rule = HealthRule(
                task_id=task_id,
                rule_type=rule['rule_type'],
                rule_content=rule['rule_content']
            )
            db.add(db_rule)

    db.commit()
    db.refresh(db_task)
    return db_task

# --- Actions ---

from pydantic import BaseModel

class ActionRequest(BaseModel):
    action: str # "start" or "stop" or "restart"

@router.post("/{task_id}/action")
async def execute_task_action(task_id: int, request: ActionRequest, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.node:
         raise HTTPException(status_code=400, detail="Task has no associated node")

    command = ""
    if request.action == "start":
        # Wrap in nohup for background execution
        # Ensure log path exists or default to /dev/null
        log_path = task.log_file_path if task.log_file_path else "/dev/null"
        # We use sh -c to ensure redirection works as expected
        # Use shlex.quote to safely quote the command string for inclusion in sh -c '...'
        quoted_command = shlex.quote(task.start_command)
        command = f"nohup sh -c {quoted_command} >> {log_path} 2>&1 &"
    elif request.action == "stop":
        command = task.stop_command
    elif request.action == "restart":
        # For restart, we stop then start.
        log_path = task.log_file_path if task.log_file_path else "/dev/null"
        quoted_command = shlex.quote(task.start_command)
        start_cmd = f"nohup sh -c {quoted_command} >> {log_path} 2>&1 &"
        command = f"{task.stop_command} && {start_cmd}"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    if not command and request.action != "start" and request.action != "restart":
         # Start/Restart are constructed above, but if somehow empty...
         # actually task.start_command could be empty in DB.
         if request.action == "start" and not task.start_command:
              raise HTTPException(status_code=400, detail=f"No command configured for action {request.action}")
         if request.action == "restart" and (not task.start_command or not task.stop_command):
               raise HTTPException(status_code=400, detail=f"Commands missing for action {request.action}")

    if request.action == "stop" and not command:
        raise HTTPException(status_code=400, detail=f"No command configured for action {request.action}")

    # Fetch Center Node (Gateway)
    gateway_node = db.query(Node).filter(Node.is_center == 1).first()

    try:
        output = await ssh_manager.execute_command(task.node, command, gateway_node=gateway_node)
        
        # Update status optimistically
        if request.action == "start":
            task.status = TaskStatus.RUNNING
        elif request.action == "stop":
            task.status = TaskStatus.STOPPED
        db.commit()

        return {"status": "success", "output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- WebSocket ---

@router.websocket("/{task_id}/log_stream")
async def websocket_endpoint(websocket: WebSocket, task_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        await websocket.close(code=4004)
        return

    try:
        if not task.node:
            await websocket.send_text("Error: Task has no node")
            await websocket.close()
            return

        # Fetch Center Node (Gateway)
        gateway_node = db.query(Node).filter(Node.is_center == 1).first()

        from ..services.log_analysis import analyze_log_lines
        log_buffer = []

        async for line in ssh_manager.stream_log(task.node, task.log_file_path, gateway_node=gateway_node):
            await websocket.send_text(line)
            
            # Add to buffer
            log_buffer.append(line)
            
            # Analyze every 20 lines (or could use time)
            if len(log_buffer) >= 20:
                # Analyze task status using buffered logs
                try:
                    new_status, new_health, last_log_time = analyze_log_lines(task, log_buffer)
                    
                    changed = False
                    if new_status and task.status != new_status:
                        task.status = new_status
                        changed = True
                    if new_health and task.health_status != new_health:
                        task.health_status = new_health
                        changed = True
                    if last_log_time:
                         task.last_log_time = last_log_time
                         changed = True
                    
                    if changed:
                        db.commit()
                except Exception as e:
                    # Don't break stream on analysis error
                    print(f"Error analyzing stream logs: {e}")
                
                # Keep last 10 lines for context in next batch? or clear?
                # If we clear, we might miss cross-chunk patterns, but our logic is line-based or simple percentage.
                # Percentage needs enough sample size. 20 lines is small.
                # Let's keep a rolling window of 50.
                if len(log_buffer) > 50:
                    log_buffer = log_buffer[-50:]

    except WebSocketDisconnect:
        # Client disconnected
        pass
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
        await websocket.close()
