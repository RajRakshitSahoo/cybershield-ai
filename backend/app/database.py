"""
Database access layer.

Uses Motor (async MongoDB driver) when a real MongoDB instance is available.
Falls back to `mongomock` (an in-process, in-memory Mongo-compatible store)
when USE_MOCK_DB=true, so the whole application runs out of the box with
zero external infrastructure for demos/dev, while remaining a drop-in swap
to a real MongoDB deployment (e.g. via the provided docker-compose.yml) for
production.
"""
from app.config import settings

if settings.use_mock_db:
    import mongomock

    _client = mongomock.MongoClient()
    db = _client[settings.mongo_db_name]

    class _AsyncWrapper:
        """Thin wrapper so mock collections support the same await-based
        call sites as motor's async collections, keeping router code
        identical regardless of which backend is active."""

        def __init__(self, collection):
            self._c = collection

        async def find_one(self, *a, **kw):
            return self._c.find_one(*a, **kw)

        async def insert_one(self, *a, **kw):
            return self._c.insert_one(*a, **kw)

        async def update_one(self, *a, **kw):
            return self._c.update_one(*a, **kw)

        async def delete_one(self, *a, **kw):
            return self._c.delete_one(*a, **kw)

        async def count_documents(self, *a, **kw):
            return self._c.count_documents(*a, **kw)

        def find(self, *a, **kw):
            return self._c.find(*a, **kw)

        def aggregate(self, *a, **kw):
            return self._c.aggregate(*a, **kw)

    class MockDB:
        def __getitem__(self, name):
            return _AsyncWrapper(db[name])

    mongo_db = MockDB()

else:
    from motor.motor_asyncio import AsyncIOMotorClient

    _client = AsyncIOMotorClient(settings.mongo_uri)
    mongo_db = _client[settings.mongo_db_name]


def get_db():
    return mongo_db


async def to_list(cursor, length: int = 1000):
    """Normalizes cursor consumption across motor (async cursor, needs
    `await cursor.to_list(n)`) and mongomock (plain sync iterable)."""
    if hasattr(cursor, "to_list"):
        maybe = cursor.to_list(length)
        if hasattr(maybe, "__await__"):
            return await maybe
        return maybe
    return list(cursor)
