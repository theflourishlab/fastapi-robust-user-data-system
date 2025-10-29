from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import SQLModel, text
from src.config import Config
from src.users import models # Import the models module to ensure they are registered with SQLModel's metadata
from sqlalchemy.orm import sessionmaker



engine = create_async_engine(
    url=Config.DATABASE_URL,
    echo=False # Should be False in production
)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Create database tables
async def init_db():
    async with engine.begin() as conn:
        # Drop all tables first (useful for development to apply schema changes)
        # await conn.run_sync(SQLModel.metadata.drop_all) # This deletes all data on restart
        await conn.run_sync(SQLModel.metadata.create_all)
        # CREATE TRIGGER
        insert_trigger = (text(
            """
            CREATE TRIGGER IF NOT EXISTS log_user_create
            AFTER INSERT ON users
            BEGIN
                INSERT INTO user_activity_logs (user_id, action, performed_at, details)
                VALUES(
                    NEW.id,
                    'CREATE',
                    datetime('now'),
                    json_object(
                    'firstname', NEW.firstname,
                    'lastname', NEW.lastname,
                    'email', NEW.email
                    )
                );
            END;
            """
        ))
        delete_trigger = text(
            """
            CREATE TRIGGER IF NOT EXISTS log_user_delete 
            AFTER DELETE ON users
            BEGIN
                INSERT INTO user_activity_logs(user_id, action, performed_at, details)
                VALUES (
                    OLD.id,
                    'DELETE',
                    datetime('now'),
                     json_object(
                    'deleted_firstname', OLD.firstname,
                    'deleted_lastname', OLD.lastname,
                    'deleted_email', OLD.email)
                );
            END;
            """
        )

        update_trigger = text(
            """
            CREATE TRIGGER IF NOT EXISTS log_user_update
            AFTER UPDATE ON users
            BEGIN
                INSERT INTO user_activity_logs(user_id, action, performed_at, details)
                VALUES (
                    OLD.id,
                    'UPDATE',
                    datetime('now'),
                    json_object(
                    'old_firstname', OLD.firstname,
                    'new_firstname', NEW.firstname,                   
                    'old_lastname', OLD.lastname,
                    'new_lastname', NEW.lastname,
                    'old_email', OLD.email,
                    'new_email', NEW.email)
                );
            END;
            """
        )

        await conn.execute(insert_trigger)
        await conn.execute(delete_trigger)
        await conn.execute(update_trigger)


# Session Dependency
async def get_session() -> AsyncSession:
    """Dependency to get a new database session for each request."""
    async with AsyncSessionLocal() as session:
        yield session