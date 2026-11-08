import pytest
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


@pytest.mark.parametrize("name", ["", "a" * 51])
async def test_create_user_rejects_invalid_name_length(client: AsyncClient, name: str):
    response = await client.post("/users", params={"name": name})

    assert response.status_code == 422


async def test_db_is_isolated_between_tests(db_session: AsyncSession):
    # 前のテストで作成されたデータは rollback 済みで、常に空から始まる
    count = await db_session.scalar(select(func.count()).select_from(User))
    assert count == 0


def test_user_create_table_sql():
    """User モデルから生成される CREATE TABLE 文を検証します"""
    sql = str(CreateTable(User.__table__).compile(dialect=postgresql.dialect()))  # pyright: ignore[reportArgumentType]

    # 改行やインデントの違いを無視して比較する
    expected = (
        "CREATE TABLE users ( "
        "id SERIAL NOT NULL, name VARCHAR NOT NULL, PRIMARY KEY (id) )"
    )
    assert " ".join(sql.split()) == expected
