from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.config import SQLALCHEMY_DATABASE_URL

# Synchronous engine creation
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Synchronous session local creation
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(drop_and_create=False):
    if drop_and_create:
        # Create an engine for the root connection (without the database name)
        root_engine = create_engine(SQLALCHEMY_DATABASE_URL.rsplit('/', 1)[0])

        # Create a session with the root connection
        RootSession = sessionmaker(bind=root_engine)
        root_session = RootSession()

        try:
            # Drop the existing database
            root_session.execute(text("DROP DATABASE IF EXISTS budongsan"))
            
            # Create a new database
            root_session.execute(text("CREATE DATABASE budongsan"))
            
            # Commit the changes
            root_session.commit()
        finally:
            # Close the session
            root_session.close()

        # Dispose of the root engine
        root_engine.dispose()

    # Create an engine for the newly created database
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Dispose of the engine
    engine.dispose()