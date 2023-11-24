# Importez les modules nécessaires
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Float, Integer, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List
import os

from pydantic import BaseModel, Field
from datetime import date

class BookCSV(BaseModel):
    bookID: int
    title: str
    authors: str
    average_rating: float
    isbn: str
    isbn13: str
    language_code: str
    num_pages: int
    ratings_count: int
    text_reviews_count: int
    publication_date: date  # Utiliser le type de données date de Python
    publisher: str


# Configuration de la base de données
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
BaseSQL = declarative_base()

# Modèle SQLAlchemy pour les livres dans la base de données
class BookDB(BaseSQL):
    __tablename__ = "books"
    bookID = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    authors = Column(String)
    average_rating = Column(Float)
    isbn = Column(String, index=True)
    isbn13 = Column(String, index=True)
    language_code = Column(String)
    num_pages = Column(Integer)
    ratings_count = Column(Integer)
    text_reviews_count = Column(Integer)
    publication_date = Column(Date)
    publisher = Column(String)


# FastAPI application
app = FastAPI(
    title="My title",
    description="My description",
    version="0.0.1",
)

# Middleware CORS pour autoriser les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fonction pour obtenir une instance de la base de données
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Créer la table de la base de données au démarrage
@app.on_event("startup")
async def startup_event():
    BaseSQL.metadata.create_all(bind=engine)

# Endpoint pour insérer des livres dans la base de données depuis le CSV
@app.post("/insert_books/")
async def insert_books(books: List[BookCSV], db: Session = Depends(get_db)):
    for book in books:
        db_book = BookDB(**book.dict())
        db.add(db_book)
    db.commit()
    return {"message": "Books inserted successfully"}

# Endpoint pour rechercher des livres en fonction du titre
@app.get("/search_books/")
async def search_books(
    title: str = Query(..., title="Search for books with this title"),
    db: Session = Depends(get_db)
):
# Modification suggérée
    books = db.query(BookDB).filter(BookDB.title.ilike(f"%{title}%")).all()

    if not books:
        raise HTTPException(status_code=404, detail="No books found with the given title")
    return books
