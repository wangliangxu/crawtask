from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..schemas.system import SystemSettings
from ..services.scheduler import update_job_interval
from ..database import get_db
from ..models.system import SystemSetting

router = APIRouter(
    prefix="/api/system",
    tags=["system"],
)

@router.get("/settings", response_model=SystemSettings)
def get_settings(db: Session = Depends(get_db)):
    # Fetch from DB
    setting = db.query(SystemSetting).filter(SystemSetting.key == "inspection_interval").first()
    
    interval = 600
    if setting and setting.value:
        try:
            interval = int(setting.value)
        except ValueError:
            pass
            
    return SystemSettings(inspection_interval=interval)

@router.post("/settings", response_model=SystemSettings)
def update_settings(settings: SystemSettings, db: Session = Depends(get_db)):
    # Upsert into DB
    db_setting = db.query(SystemSetting).filter(SystemSetting.key == "inspection_interval").first()
    if not db_setting:
        db_setting = SystemSetting(key="inspection_interval", value=str(settings.inspection_interval))
        db.add(db_setting)
    else:
        db_setting.value = str(settings.inspection_interval)
    
    db.commit()
    db.refresh(db_setting)
    
    # Update scheduler
    try:
        update_job_interval(settings.inspection_interval)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update scheduler: {str(e)}")
        
    return settings
