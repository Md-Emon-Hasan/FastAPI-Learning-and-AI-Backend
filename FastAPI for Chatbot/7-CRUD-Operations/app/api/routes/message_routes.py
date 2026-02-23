from fastapi import APIRouter
from fastapi import HTTPException
from app.schemas.message_schema import MessageCreate
from app.schemas.message_schema import MessageUpdate
from app.schemas.response_schema import APIResponse

router = APIRouter(prefix="/messages", tags=["messages"])

messages_db = []
current_id = 1

# create a message
@router.post("/", response_model=APIResponse)
def create_message(request: MessageCreate):
    global current_id
    message = {
        "id" : current_id,
        "user_id" : request.user_id,
        "content" : request.content
    }
    messages_db.append(message)
    current_id += 1
    
    return APIResponse(status="success", data=message)

# get message
@router.get("/", response_model=APIResponse)
def list_messages():
    return APIResponse(status="success", data=messages_db)

# get message by id
@router.get("/{message_id}", response_model=APIResponse)
def get_message(message_id: int):
    for message in messages_db:
        if message["id"] == message_id:
            return APIResponse(status="success", data=message)
    raise HTTPException(status_code=404, detail="Message not found")

# update message
@router.put("/{message_id}", response_model=APIResponse)
def update_message(message_id: int, request: MessageUpdate):
    for message in messages_db:
        if message['id'] == message_id:
            message['content'] = request.content
            return APIResponse(status="success", data=message)
    raise HTTPException(status_code=404, detail="Message not found")

# delete message
@router.delete("/{message_id}", response_model=APIResponse)
def delete_message(message_id: int):
    for message in messages_db:
        if message['id'] == message_id:
            messages_db.remove(message)
            return APIResponse(status="success", data={"message": "Message deleted"})
        raise HTTPException(status_code=404, detail="Message not found")