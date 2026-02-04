from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config import DATABASE_URL

#движок
engine = create_async_engine(DATABASE_URL, echo=True)

#фабрика сессий
async_session = async_sessionmaker(engine, expire_on_commit=False)


#базовый класс
class Base(AsyncAttrs, DeclarativeBase):
    pass


#описание таблицы пользователей
class User(Base):
    __tablename__ = 'users'

    #ID
    id: Mapped[int] = mapped_column(primary_key=True)
    #имя пользователя
    username: Mapped[str | None] = mapped_column()
    #группа
    group_number: Mapped[str | None] = mapped_column(default=None)


#создание таблиц
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
