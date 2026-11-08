from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.schema import CreateTable

from hello_testcontainers_py.models import User

# ==========================================
# 3. 実際のテストコード
# ==========================================


async def test_create_user_endpoint(client: AsyncClient):
    # HTTPXを使って、FastAPIアプリに非同期でリクエストを送る
    response = await client.post("/users", params={"name": "アリス"})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "アリス"
    assert isinstance(body["id"], int)


async def test_db_is_isolated_between_tests(db_session: AsyncSession):
    # 前のテストで作成されたデータは rollback 済みで、常に空から始まる
    count = await db_session.scalar(select(func.count()).select_from(User))
    assert count == 0


async def test_print_schema():
    """show CREATE TABLE schema SQL"""
    print(CreateTable(User.__table__).compile(dialect=postgresql.dialect()))  # pyright: ignore[reportArgumentType]
