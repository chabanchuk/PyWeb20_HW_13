import logging
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError


from src.database.db import get_db
from src.routes import todos, auth

logging.basicConfig(level=logging.ERROR)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://example.com",
    "https://example.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory='src/static'), name="static")
app.include_router(auth.router, prefix="/api")
app.include_router(todos.router, prefix="/api")


# Головна сторінка
@app.get("/")
def index():
    return {"message": "Application"}

# Маршрут для перевірки стану застосунку
@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except SQLAlchemyError as e:
        logging.error(f"Error executing database query: {e}")
        raise HTTPException(status_code=500, detail="Error connecting to the database")

# Запуск додатку як Python скрипта
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)