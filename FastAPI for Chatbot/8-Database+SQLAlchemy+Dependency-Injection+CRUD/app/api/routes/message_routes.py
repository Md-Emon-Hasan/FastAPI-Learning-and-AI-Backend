from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.message_schema import MessageCreate
from app.schemas.message_schema import MessageUpdate
from app.schemas.message_schema import MessageOut
from app.schemas.response_schema import APIResponse
from app.services.message_service import MessageService
from app.services.message_service import get_message_service

router = APIRouter(prefix="/messages", tags=["Messages"])

# create
@router.post('/', response_model=APIResponse)
def create_message(
    req: MessageCreate,
    db: Session = Depends(get_db),
    service: MessageService = Depends(get_message_service)
):
    message = service.create_message(db, req)
    return APIResponse(status="success", data = MessageOut.model_validate(message))

# read all
@router.get('/', response_model=APIResponse)
def list_messages(
    db: Session = Depends(get_db),
    service: MessageService = Depends(get_message_service)
):
    messages = service.get_all_messages(db)
    data = [MessageOut.model_validate(m) for m in messages]
    return APIResponse(status="success", data=data)

# read by id
@router.get('/{message_id}', response_model=APIResponse)
def get_message_by_id(
    message_id: int,
    db: Session = Depends(get_db),
    service: MessageService = Depends(get_message_service)
):
    msg = service.get_message_by_id(db, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return APIResponse(status="success", data=MessageOut.model_validate(msg))

# update
@router.put('/{message_id}', response_model=APIResponse)
def update_message(
    message_id: int,
    req: MessageUpdate,
    db: Session = Depends(get_db),
    service: MessageService = Depends(get_message_service)
):
    msg = service.update_message(db, message_id, req)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return APIResponse(status="success", data=MessageOut.model_validate(msg))

# delete
@router.delete('/{message_id}', response_model=APIResponse)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    service: MessageService = Depends(get_message_service)
):
    success = service.delete_message(db, message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return APIResponse(status="success", data={"message": "Message deleted successfully"})