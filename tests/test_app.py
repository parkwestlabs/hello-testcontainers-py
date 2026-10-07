from httpx import AsyncClient
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from hello_testcontainers_py.models import User

# ==========================================
# 3. 実際のテストコード
# ==========================================


async def test_create_user_endpoint(client: AsyncClient):
    # HTTPXを使って、FastAPIアプリに非同期でリクエストを送る
    response = await client.post("/users", params={"name": "アリス"})

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "アリス"}


async def test_print_schema():
    """show CREATE TABLE schema SQL"""
    print(CreateTable(User.__table__).compile(dialect=postgresql.dialect()))  # pyright: ignore[reportArgumentType]
