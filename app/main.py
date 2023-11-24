from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import pandas as pd

##################

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
BaseSQL = declarative_base()

class Book(BaseModel):
    name: str
    price: float

class CsvBook(BaseSQL):
    __tablename__ = "books"
    bookID = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    authors = Column(String)
    average_rating = Column(Float)
    isbn = Column(String)
    isbn13 = Column(String)
    language_code = Column(String)
    num_pages = Column(Integer)
    ratings_count = Column(Integer)
    text_reviews_count = Column(Integer)
    publication_date = Column(String)
    publisher = Column(String)

    class Config:
        orm_mode = True

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.on_event("startup")
async def startup_event():
    BaseSQL.metadata.create_all(bind=engine)
    BaseCSV.metadata.create_all(bind=engine)

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
    if not record:
        raise HTTPException(status_code=404, detail="Not Found") 
    return record

@app.get("/all_books")
async def get_all_books(db: Session = Depends(get_db)):
    return db.query(BooksDB).all()

@app.delete("/delete/{name}", tags=["posts"])
async def delete_by_name(name: str, db: Session = Depends(get_db)):
    try:
        num_rows = db.query(BooksDB).filter_by(name=name).delete()
        if num_rows == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        db.commit()
    except HTTPException as e:
        raise
    except Exception as e:
        return {"error": e}
    return {"book": f"delete book {name}"}

@app.delete("/delete_all")
async def delete_all_books(db: Session = Depends(get_db)):
    try:
        num_rows = db.query(BooksDB).filter().delete()
        if num_rows == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        db.commit()
    except HTTPException as e:
        raise
    except Exception as e:
        return {"error": e}
    return {"book": f"delete all books"}

@app.get("/search_books")
async def search_books(query: str, db: Session = Depends(get_db)):
    results = db.query(CsvBook).filter(CsvBook.title.ilike(f"%{query}%")).all()
    if not results:
        raise HTTPException(status_code=404, detail="No matching books found")
    return results
