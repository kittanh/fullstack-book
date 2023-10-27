from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

##################
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from sqlalchemy import Column, String, Integer
from fastapi import HTTPException, Depends


class Book(BaseModel):
    name: str
    price: float
    class Config:
        orm_mode = True

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")


SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db/{POSTGRES_DB}"
print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

BaseSQL = declarative_base()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class BooksDB(BaseSQL):
    __tablename__ = "books"
    name = Column(String, primary_key=True)
    price = Column(Integer)
    
    class Config:
        orm_mode = True

##########################




app = FastAPI(
    title="My title",
    description="My description",
    version="0.0.1",
)



@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/TEST")
def read_test():
    return{"test":POSTGRES_USER}

@app.on_event("startup")
async def startup_event():
    BaseSQL.metadata.create_all(bind=engine)

@app.post("/books/")
async def create_book(book: Book, db: Session = Depends(get_db)):
    record = db.query(BooksDB).filter(BooksDB.name == book.name).first()
    if record:
        raise HTTPException(status_code=409, detail="Already exists")
    db_book = BooksDB(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/{name}")
async def get_book_by_name(name: str, db: Session = Depends(get_db)):
    record = db.query(BooksDB).filter(BooksDB.name == name).first()
    print(name)
    if not record:
        raise HTTPException(status_code=404, detail="Not Found") 
    return record

@app.get("/all_books")
async def get_all_books(db: Session = Depends(get_db)):
    return db.query(BooksDB).all()

# @app.delete("/{name}")
# async def delete_by_name(name: str, db: Session = Depends(get_db)):
#     db_book = get_book_by_name(name)
#     db.delete(db_book)
#     db.commit()
#     return(db_book)

# @app.delete("/all")
# async def delete_all_books(db: Session = Depends(get_db)):
#     records = db.query(BooksDB).filter()
#     for record in records:
#         db.delete(record)
#     db.commit()
#     return records