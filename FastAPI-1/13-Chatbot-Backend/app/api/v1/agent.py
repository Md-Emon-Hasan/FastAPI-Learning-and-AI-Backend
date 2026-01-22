from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.agent import AgentRunRequest, AgentResponse, AgentStatus
from app.db.models import User, AgentTaskDB
from app.tasks.background import run_agent_task
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/agent/run", response_model=AgentResponse)
async def run_agent(
    request: AgentRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run AI agent task
    - Supports: research, summarize, analyze
    - Can run in background
    - Tracks task status
    """
    try:
        # Create task record
        task_id = str(uuid.uuid4())
        
        task_db = AgentTaskDB(
            task_id=task_id,
            user_id=current_user.id,
            task_type=request.task.task_type,
            input_data=request.task.input_data,
            status="pending"
        )
        db.add(task_db)
        db.commit()
        
        if request.background:
            # Run in background
            background_tasks.add_task(
                run_agent_task,
                task_id,
                request.task.task_type,
                request.task.input_data,
                request.task.parameters
            )
            
            return AgentResponse(
                task_id=task_id,
                status=AgentStatus.PENDING,
                result=None
            )
        else:
            # Run synchronously
            from app.tasks.background import run_agent_task
            await run_agent_task(
                task_id,
                request.task.task_type,
                request.task.input_data,
                request.task.parameters
            )
            
            # Get result
            db.refresh(task_db)
            
            return AgentResponse(
                task_id=task_id,
                status=AgentStatus(task_db.status),
                result=task_db.result,
                error=task_db.error
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/status/{task_id}", response_model=AgentResponse)
async def get_agent_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get agent task status"""
    task = db.query(AgentTaskDB).filter(
        AgentTaskDB.task_id == task_id,
        AgentTaskDB.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return AgentResponse(
        task_id=task.task_id,
        status=AgentStatus(task.status),
        result=task.result,
        error=task.error
    )

@router.get("/agent/tasks")
async def list_agent_tasks(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all agent tasks for user"""
    tasks = db.query(AgentTaskDB).filter(
        AgentTaskDB.user_id == current_user.id
    ).order_by(AgentTaskDB.created_at.desc()).limit(limit).all()
    
    return {
        "tasks": [
            {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": task.status,
                "created_at": task.created_at,
                "completed_at": task.completed_at
            }
            for task in tasks
        ]
    }