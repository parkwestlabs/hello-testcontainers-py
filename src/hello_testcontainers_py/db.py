import os
from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@lru_cache
def get_engine() -> AsyncEngine:
    """DATABASE_URL 環境変数から Engine を作成します（初回呼び出し時のみ作成）"""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return create_async_engine(database_url)


def create_session_factory(
    bind: AsyncEngine | AsyncConnection,
) -> async_sessionmaker[AsyncSession]:
    """アプリ（本番）とテストで共有するセッション設定を返します"""
    # expire_on_commit=False: commit 後も属性を読めるようにする。
    # async セッションでは期限切れ属性の遅延読み込みができないため必須
    return async_sessionmaker(bind=bind, class_=AsyncSession, expire_on_commit=False)


# 依存注入（DI）用の関数。テスト時は fixture で上書き（オーバーライド）します
async def get_db() -> AsyncGenerator[AsyncSession]:
    session_factory = create_session_factory(get_engine())
    async with session_factory() as session:
        yield session
