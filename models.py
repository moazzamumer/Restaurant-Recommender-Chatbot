from sqlalchemy import create_engine, Column, Integer, Text, DateTime,ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import constants

# Set up the database engine and session
engine = create_engine(constants.DATABASE_URL,  connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    chat_id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(Text)
    text = Column(Text)
    timestamp = Column(DateTime)
    user_id = Column(Integer, ForeignKey('Users.user_id'))


class User(Base):
    __tablename__ = 'Users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(Text)

# Create the table
Base.metadata.create_all(bind=engine)