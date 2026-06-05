from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import Column, String, Text, DateTime, Integer
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL =  "sqlite+aiosqlite:///./strokecare_tester.db"

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

class TestRun(Base):
    __tablename__ = "test_runs"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    possibility = Column(String(10), nullable=False)
    input_data  = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=False)
    user_prompt = Column(Text, nullable=False)
    output      = Column(Text, nullable=True)
    status      = Column(String(20), nullable=False, default="pending")
    # pass / fail_validation / fallback / error
    model_used  = Column(String(50), nullable=True)
    tokens_in   = Column(Integer, nullable=True)
    tokens_out  = Column(Integer, nullable=True)
    safety_result = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
