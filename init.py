from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
import uvicorn
import base_models, models, constants
from chatbot_1 import *

app = FastAPI()
flag = False
user_sessions = {}


# Set up the database engine and session
engine = create_engine(constants.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Signup endpoint
@app.post("/signup")
def signup(user: base_models.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.name == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = models.User(name=user.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.user_id}

# Login endpoint
@app.post("/login", response_model=base_models.User)
def login(user: base_models.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.name == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username")
    return {"message": "Login successful", "user_id": db_user.user_id}


@app.post("/Restaurant-Recommender-Chatbot")
async def Communicate(user_input: str , user_id:int):

    if user_id not in user_sessions:
        
        user_sessions[user_id] = GenAI(constants.API_KEY)   
    print("User:" ,user_input)
    ai_model = user_sessions[user_id]
    response = ai_model.chatbot(user_id, user_input)

    return {"response": response}



if __name__ == "__main__":
    
    uvicorn.run("init:app", host = "127.0.0.1", port = 8000, reload = True)