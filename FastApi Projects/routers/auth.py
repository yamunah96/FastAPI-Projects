from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm



from dependencies import get_db
from models.users import User
from auth.security import hash_password,verify_password
from auth.jwt import create_access_token


router= APIRouter(prefix="/auth", tags=["Auth"])

# signup api

@router.post("/signup")
def signup(email:str,password:str,db:Session= Depends(get_db)):
    user= User(
        email=email, hashed_password=hash_password(password)
    )

    db.add(user)
    db.commit()
    return {"message":"user created"}

@router.post("/login")
def login(form: OAuth2PasswordRequestForm=Depends(), db:Session=Depends(get_db)):
    # find the user by email 
    user= db.query(User).filter(
        User.email == form.username
    ).first()

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401,details="invalid credits")
    
    token= create_access_token({
        "sub":user.email, "role":user.role
    })
    return {
        "acc_token":token,
        "token_type":"bearer"
    }