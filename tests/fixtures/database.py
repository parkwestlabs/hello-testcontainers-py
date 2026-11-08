from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer

from hello_testcontainers_py.db import create_session_factory, get_db
from hello_testcontainers_py.main import app
from hello_testcontainers_py.models import Base

# ==========================================
# 2. Testcontainers & Async の Fixture 設定
# ==========================================


@pytest.fixture(scope="session")
def postgres_container_url() -> Generator[str]:
    """PostgreSQLコンテナを起動し、接続URL文字列だけを返します"""
    with PostgresContainer("postgres:18-alpine", driver="asyncpg") as postgres:
        yield postgres.get_connection_url()


@pytest_asyncio.fixture()
async def async_db_engine(postgres_container_url: str) -> AsyncGenerator[AsyncEngine]:
    """テスト全体で1つのPostgreSQLコンテナを起動し、非同期Engineを返します"""
    engine = create_async_engine(postgres_container_url, echo=False)

    # 非同期でテーブルをすべて作成
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # クリーンアップ
    await engine.dispose()


@pytest_asyncio.fixture()
async def db_session(async_db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    """テスト1ケースごとに独立したセッションを提供します。テスト終了後に全変更を破棄します"""
    async with async_db_engine.connect() as conn:
        # 外側のトランザクションを開始。テスト終了時にここを rollback して全変更を取り消す
        outer = await conn.begin()

        # join_transaction_mode="create_savepoint": セッション内の commit() は
        # SAVEPOINT の解放だけを行い、外側のトランザクションは確定させない
        async with create_session_factory(conn)(
            join_transaction_mode="create_savepoint"
        ) as session:
            yield session

        await outer.rollback()


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """
    テストごとに独立した AsyncClient を提供します。
    この Fixture を呼ぶだけで、FastAPI の DB 依存関係も自動でテスト用に差し替わります。
    """

    # 1. FastAPI の get_db を、テスト用の db_session を返すように上書き
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # 2. クライアントの生成
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac  # 👈 これをテスト関数に渡す

    # 3. テスト終了後、依存関係の上書きをきれいにクリア
    app.dependency_overrides.clear()
