from sqlalchemy.orm import Session
from app.db.models import Message
from app.schemas.message_schema import MessageCreate
from app.schemas.message_schema import MessageUpdate

class MessageService:
    
    def create_message(self, db: Session, data: MessageCreate):
        message = Message(user_id=data.user_id, content=data.content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    def get_all_messages(self, db: Session):
        return db.query(Message).all()
    
    def get_message_by_id(self, db: Session, message_id: int):
        return db.query(Message).filter(Message.id == message_id).first()
    
    def update_message(self, db: Session, message_id: int, data: MessageUpdate):
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return None
        message.content = data.content
        db.commit()
        db.refresh(message)
        return message
    
    def delete_message(self, db:Session, message_id: int):
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return False
        db.delete(message)
        db.commit()
        return True
    
# Dependency Injection
def get_message_service():
    return MessageService()