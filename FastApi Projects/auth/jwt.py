from jose import jwt
from datetime import datetime,timedelta

secret_key="yamuna123"
Algorithm="HS256"

def create_access_token(data:dict):
    expire= datetime.utcnow()+ timedelta(minutes=30)
    data.update({"exp":expire})
    return jwt.encode(data,secret_key,algorithm=Algorithm)