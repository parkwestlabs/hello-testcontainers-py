from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)


def create_session_factory(
    bind: AsyncEngine | AsyncConnection,
) -> async_sessionmaker[AsyncSession]:
    """アプリ（本番）とテストで共有するセッション設定を返します"""
    # expire_on_commit=False: commit 後も属性を読めるようにする。
    # async セッションでは期限切れ属性の遅延読み込みができないため必須
    return async_sessionmaker(bind=bind, class_=AsyncSession, expire_on_commit=False)
