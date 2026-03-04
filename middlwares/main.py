import time

from fastapi import FastAPI, Request,Depends,Form,HTTPException,Body
from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

@app.get("/fer")
def root():
    return {"message":"hello world"}

@app.post("/login")
def create_post(payload:dict=Body(...)):
    print(payload)
    return {"message":"post created"}

# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     start_time = time.perf_counter()  # start
#     response = await call_next(request)  # route
#     process_time = time.perf_counter() - start_time # middle processing
#     response.headers["X-Process-Time"] = str(process_time)  # headers 
#     return response

# cors, headers, json format


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https/my-fornted.com","http://localhost:5000"],
#     allow_credentials=True,
#     allow_methods=["GET","POST","PUT"],
#     allow_headers=['****'],
   
# )
# app.add_middleware(
#  GZipMiddleware,minimum_size=1000
# )

# app.add_middleware(
#     HTTPSRedirectMiddleware
# )

# response from the server 3mb--- gzip middlware - comparess the data 300kb -1000kb 

# @app.middleware("http")
# async def timer_middleware(request:Request,call_next):
#     if request.url.path.startswith("/hello"):
#         start_time= time.time()
#         response= await call_next(request)

#         duration= time.time() -start_time
#         print(f"Request: {request.url.path} proceed in time of {duration:.5f} s")
#         # response.headers["X-Custom-Status"] = "Processed"
#         return response
    
#     # For all other routes, just proceed normally
#     return await call_next(request)

# @app.get("/hello")
# async def hello2():
#     # for i in range(100000):
#     #     pass
#     return {"message":"hello world!!"}

# @app.get("/other")
# async def other():
#     return {"message": "this one won't be timed"}


# def get_database():
#     db={"users":"yamuna"}
#     print("hello" +db)

# @app.get("/user")
# def create_user(db= Depends(get_database)):
#     return "its excuted " +db['users']


'''
client--- api (/token(user email,password) ---- server /profile - profile screen) 

'''
o_scheme= OAuth2PasswordBearer(tokenurl="login")
@app.post("/login")
def login (username :str=Form(...),password:str=Form(...)):
    if username=="yamuna" and password =="1234":
        return {"acces_token":"valid_token"}
    raise HTTPException(status_code=400,detail="login error")
def decode_token(token:str):
    if token == "valid_token":
        return {"name":"yamuna"}
    raise HTTPException(status_code=400,detail="Invalid auth")

def get_cuurent_user(token:str=Depends(o_scheme)):
    return decode_token(token)