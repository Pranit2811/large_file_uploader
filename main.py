from fastapi import FastAPI, File, UploadFile, Form, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from task import save_chunk
import csv
from io import StringIO
import json
from model.models import Company, get_db
from fastapi import FastAPI, Depends, Request
from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from helpers import *
from schema.schemas import UserDisplay
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext


from starlette.middleware.sessions import SessionMiddleware
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


templates = Jinja2Templates(directory="templates")


# Initialize FastAPI
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="some-random-string")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BATCH_SIZE = 1000 

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), chunk_number: int = Form(...), total_chunks: int = Form(...)):
    try:
        # Read the chunk data
        chunk_data = await file.read()
        file_stream = StringIO(chunk_data.decode('utf-8'))

        # Process the CSV data
        csv_reader = csv.DictReader(file_stream)
        batch = []  # Store rows in a batch

        for lines in csv_reader:
            batch.append(dict(lines))
            if len(batch) >= BATCH_SIZE:
                save_chunk.apply_async(args=[json.dumps(batch), total_chunks, chunk_number], queue='FILE_UPLOADER')
                batch = []  # Reset batch after sending

        # If there are any remaining rows in the batch, process them
        if batch:
            save_chunk.apply_async(args=[json.dumps(batch), total_chunks, chunk_number], queue='FILE_UPLOADER')

        return JSONResponse(content={"message": "Chunk uploaded successfully!"}, status_code=202)

    except UnicodeDecodeError:
        print(f"Chunk {chunk_number} could not be decoded as UTF-8. Ignoring this chunk.")

    except csv.Error as e:
        print(f"Error reading CSV: {e}")
        return JSONResponse(content={"message": "Error processing CSV."}, status_code=400)


@app.get("/upload_file", response_class=HTMLResponse)
async def get_upload_page(request: Request):
    return templates.TemplateResponse("file_upload.html", {"request": request})



@app.get("/suggest/{field}")
def suggest_field(field: str, q: str, session: Session = Depends(get_db)):
    """
    Endpoint to provide suggestions for different fields based on user input (q).
    """
    if field == "industry":

        results = session.query(Company.industry).filter(Company.industry.ilike(f"{q}%")).distinct().all()
    elif field == "year_founded":

        results = session.query(Company.year_founded).filter(Company.year_founded.ilike(f"{q}%")).distinct().all()
    elif field == "name":
        
        results = session.query(Company.name).filter(Company.name.ilike(f"{q}%")).distinct().all()
    elif field == "country":
        
        results = session.query(Company.country).filter(Company.country.ilike(f"{q}%")).distinct().all()
    else:
        results = []
    
    return {"suggestions": [result[0] for result in results]}


@app.get("/search", response_class=HTMLResponse)
def search_form(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

@app.post("/search_results", response_class=HTMLResponse)
def search_companies(
    request: Request,
    session: Session = Depends(get_db),
    year_founded: str = Form(None),
    name: str = Form(None),
    industry: str = Form(None),
    country: str =Form(None),
):

    query = session.query(Company)
    if year_founded:
        query = query.filter(Company.year_founded == year_founded)
    if name:
        query = query.filter(Company.name.ilike(f"%{name}%"))
    if industry:
        query = query.filter(Company.industry.ilike(f"%{industry}%"))
    if country:
        query = query.filter(Company.country.ilike(f"%{country}%"))
    
    result_count = query.count()
    companies = query.all()

    return templates.TemplateResponse("search.html", {
        "request": request,
        "companies": companies,
        "result_count": result_count 
    })

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(request: Request, 
                    response: Response,
                     db: Session = Depends(get_db),
                     username: str = Form(...), 
                     password: str = Form(...)):
    user = get_user_by_username(db, username)
    print("auth", user, pwd_context.verify(password, user.hashed_password))
    if user and pwd_context.verify(password, user.hashed_password):
        print("settin_co")
        request.session['user'] = user.username
        return RedirectResponse(url="/home", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/home")
async def home(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.get("/users", response_model=List[UserDisplay])
async def list_users(request: Request, db: Session = Depends(get_db)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")
    users = get_users(db)
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

@app.post("/users/add")
async def add_user(request: Request, db: Session = Depends(get_db),  username: str = Form(...), password: str = Form(...)):
    if get_user_by_username(db, username):
        return templates.TemplateResponse("users.html", {"request": request, "users": get_users(db), "error": "User already exists"})
    create_user(db, schemas.UserCreate(username=username, password=password))
    return RedirectResponse(url="/users", status_code=302)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



