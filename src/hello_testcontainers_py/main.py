from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from hello_testcontainers_py.db import get_db
from hello_testcontainers_py.models import User

# ==========================================
# 1. テスト対象の FastAPI アプリ & モデル定義
# ==========================================

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/users")
async def create_user(name: str, db: Annotated[AsyncSession, Depends(get_db)]):
    new_user = User(name=name)

    db.add(new_user)
    await db.commit()

    return {"id": new_user.id, "name": new_user.name}
