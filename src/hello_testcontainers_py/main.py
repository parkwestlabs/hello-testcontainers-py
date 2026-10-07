from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from hello_testcontainers_py.models import User

# ==========================================
# 1. テスト対象の FastAPI アプリ & モデル定義
# ==========================================

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# 依存注入（DI）用の関数。テスト時に fixture で上書き（オーバーライド）します
async def get_db() -> AsyncSession:
    # 実際の本番環境では async_sessionmaker 等から生成して yield する
    raise NotImplementedError()


@app.post("/users")
async def create_user(name: str, db: Annotated[AsyncSession, Depends(get_db)]):
    new_user = User(name=name)

    db.add(new_user)
    await db.commit()

    return {"id": new_user.id, "name": new_user.name}
