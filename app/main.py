from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

##################
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from fastapi import HTTPException, Depends
from sqlalchemy.orm import relationship


class Book(BaseModel):
    id: int
    title: str
    authors: str
    average_rating: float
    language_code: str
    num_pages: int
    rating_count: int
    text_review_count: int
    publication_date: str
    class Config:
        orm_mode = True

class UsersBook(BaseModel):
    book_id: int
    user_id: str

    class Config:
        orm_mode = True
    

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
    id = Column(Integer, primary_key=True)
    authors = Column(String, primary_key=False)
    title = Column(String, primary_key=False)
    average_rating = Column(Float, primary_key=False)
    language_code = Column(String, primary_key=False)
    num_pages = Column(Integer, primary_key=False)
    rating_count = Column(Integer, primary_key=False)
    text_review_count = Column(Integer, primary_key=False)
    publication_date = Column(String, primary_key=False)
    
    class Config:
        orm_mode = True

class User(BaseSQL):
    __tablename__ = "users"
    username = Column(String, unique=True, primary_key=True)
    password = Column(String, primary_key=False)

    class Config:
        orm_mode = True

class UsersBook(BaseSQL):
    __tablename__ = "users_books"

    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    user_id = Column(String, ForeignKey('users.username'), primary_key=True)

    book = relationship('Book', back_populates='users_books')
    user = relationship('User', back_populates='users_books')

##########################

def init_db():
    db = SessionLocal()
    with open("books.csv") as file:
        next(file)  # On saute la première ligne header
        for line in file:
            line_info = line.split(",")                
            if len(line_info)==12:            
                new_book = BooksDB(id=int(line_info[0]), title=line_info[1], authors=line_info[2],
                                average_rating=float(line_info[3]), language_code=line_info[6],
                                num_pages=int(line_info[7]), rating_count=int(line_info[8]),
                                text_review_count=int(line_info[9]), publication_date=line_info[10])
                db.add(new_book)
                db.commit()
    new_user = User(username="user@gmail.com", password="Test")
    db.add(new_user)
    db.commit()



app = FastAPI(
    title="My title",
    description="My description",
    version="0.0.1",
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.on_event("startup")
async def startup_event():
    BaseSQL.metadata.create_all(bind=engine)
    if not SessionLocal().query(BooksDB).first():
        init_db()

@app.post("/books/")
async def create_book(book: Book, db: Session = Depends(get_db)):
    record = db.query(BooksDB).filter(BooksDB.id == book.id).first()
    if record:
        raise HTTPException(status_code=409, detail="Already exists")
    db_book = BooksDB(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.post("/save_book/")
async def save_book(usersbook: UsersBook, db: Session = Depends(get_db)):
    record = db.query(UsersBook).filter(UsersBook.book_id == usersbook.book_id and UsersBook.user_id == usersbook.user_id).first()
    if record:
        raise HTTPException(status_code=409, detail="Already exists")
    db_usersbook = UsersBook(**usersbook.dict())
    db.add(db_usersbook)
    db.commit()
    db.refresh(db_usersbook)
    return db_usersbook

@app.get("/books/{id}")
async def get_book_by_id(id: int, db: Session = Depends(get_db)):
    record = db.query(BooksDB).filter(BooksDB.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Not Found") 
    return record

@app.get("/all_books")
async def get_all_books(db: Session = Depends(get_db)):
    return db.query(BooksDB).all()

@app.get("/books_avg_sup/{avg_rate}")
async def get_book_with_avg_sup(avg_rate: float, db: Session =  Depends(get_db)):
    records = db.query(BooksDB).filter(BooksDB.average_rating > avg_rate).all()
    return records

@app.delete("/delete/{id}", tags=["posts"])
async def delete_by_id(id: int, db: Session = Depends(get_db)):
    try:
        num_rows = db.query(BooksDB).filter_by(id=id).delete()
        if num_rows==0:
            raise HTTPException(status_code=404, detail="Record not found")
        db.commit()
    except HTTPException as e:
        raise
    except Exception as e:
        return{"error":e}
    return{"book": f"delete book {id}"}

@app.delete("/delete_all")
async def delete_all_books(db: Session = Depends(get_db)):
    try:
        num_rows = db.query(BooksDB).filter().delete()
        if num_rows==0:
            raise HTTPException(status_code=404, detail="Record not found")
        db.commit()
    except HTTPException as e:
        raise
    except Exception as e:
        return{"error":e}
    return{"book": f"delete all books"}
