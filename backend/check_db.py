import asyncio
from sqlalchemy import text
from app.db.session import async_engine

async def check():
    async with async_engine.connect() as conn:
        res = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;"))
        tables = [r[0] for r in res.fetchall()]
        print("Existing tables count:", len(tables))
        print("Tables:", tables)
        try:
            ver = await conn.execute(text("SELECT version_num FROM alembic_version;"))
            print("alembic_version:", [r[0] for r in ver.fetchall()])
        except Exception as e:
            print("alembic_version error:", e)

if __name__ == "__main__":
    asyncio.run(check())
