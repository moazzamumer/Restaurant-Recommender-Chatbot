from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
import uvicorn
import base_models, models, constants
from chatbot import *

app = FastAPI()
flag = False
user_sessions = {}


# Set up the database engine and session
engine = create_engine(constants.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Signup endpoint
@app.post("/login")
def create_user(user: base_models.UserLogin, db: Session = Depends(get_db)):
    new_user = models.User(username=user.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully",  "user_id": new_user.user_id}


@app.post("/Restaurant-Recommender-Chatbot")
async def Communicate(user_input: str , user_id: int, db: Session = Depends(get_db)):

    # Check if user_id exists in the database
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User does not exist")

    if user_id not in user_sessions:
        user_sessions[user_id] = GenAI()
    
    ai_model = user_sessions[user_id]
    response = ai_model.chatbot(user_id, user_input)

    return {"response": response}



if __name__ == "__main__":
    
    uvicorn.run("init:app", host = "127.0.0.1", port = 8000, reload = True)