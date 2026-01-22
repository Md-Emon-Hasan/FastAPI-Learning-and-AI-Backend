# from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship
# from datetime import datetime

# Base = declarative_base()

# class User(Base):
#     __tablename__ = "users"
    
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True, nullable=False)
#     hashed_password = Column(String, nullable=False)
#     full_name = Column(String)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
    
#     # Relationships
#     conversations = relationship("Conversation", back_populates="user")
#     api_keys = relationship("APIKey", back_populates="user")

# class Conversation(Base):
#     __tablename__ = "conversations"
    
#     id = Column(Integer, primary_key=True, index=True)
#     conversation_id = Column(String, unique=True, index=True, nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     title = Column(String)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships
#     user = relationship("User", back_populates="conversations")
#     messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

# class Message(Base):
#     __tablename__ = "messages"
    
#     id = Column(Integer, primary_key=True, index=True)
#     conversation_id = Column(Integer, ForeignKey("conversations.id"))
#     role = Column(String, nullable=False)  # user or assistant
#     content = Column(Text, nullable=False)
#     tokens_used = Column(Integer)
#     timestamp = Column(DateTime, default=datetime.utcnow)
#     metadata = Column(JSON)  # Store extra info
    
#     # Relationships
#     conversation = relationship("Conversation", back_populates="messages")

# class APIKey(Base):
#     __tablename__ = "api_keys"
    
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     key_hash = Column(String, unique=True, index=True)
#     name = Column(String)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     last_used = Column(DateTime)
    
#     user = relationship("User", back_populates="api_keys")

# class AgentTaskDB(Base):
#     __tablename__ = "agent_tasks"
    
#     id = Column(Integer, primary_key=True, index=True)
#     task_id = Column(String, unique=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     task_type = Column(String)
#     input_data = Column(Text)
#     status = Column(String, default="pending")
#     result = Column(Text)
#     error = Column(Text)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     completed_at = Column(DateTime)


from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String, nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON)  # Changed from 'metadata' to 'meta_data' (metadata is reserved in SQLAlchemy)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key_hash = Column(String, unique=True, index=True)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    
    user = relationship("User", back_populates="api_keys")

class AgentTaskDB(Base):
    __tablename__ = "agent_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_type = Column(String)
    input_data = Column(Text)
    status = Column(String, default="pending")
    result = Column(Text)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)