from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from hello_testcontainers_py.db import get_db, get_engine
from hello_testcontainers_py.models import Base, User

# ==========================================
# 1. テスト対象の FastAPI アプリ & モデル定義
# ==========================================


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    # 起動時にテーブルを作成する（既にあれば何もしない）。
    # 本番で運用する場合は Alembic などのマイグレーションを使ってください
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/users")
async def create_user(name: str, db: Annotated[AsyncSession, Depends(get_db)]):
    new_user = User(name=name)

    db.add(new_user)
    await db.commit()

    return {"id": new_user.id, "name": new_user.name}
