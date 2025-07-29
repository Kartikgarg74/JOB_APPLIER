import os
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import event

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

DATABASE = {
    'drivername': 'postgresql+psycopg2',
    'host': os.getenv('SUPABASE_DB_HOST'),
    'port': os.getenv('SUPABASE_DB_PORT', '5432'),
    'username': os.getenv('SUPABASE_DB_USER'),
    'password': os.getenv('SUPABASE_DB_PASSWORD'),
    'database': os.getenv('SUPABASE_DB_NAME'),
}

SQLALCHEMY_DATABASE_URL = SUPABASE_DB_URL or str(URL.create(**DATABASE))

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class Base(DeclarativeBase): pass

# Helper for audit logging

def auto_log_audit(mapper, connection, target, action):
    user_id = getattr(target, 'user_id', None)
    table = target.__tablename__
    row_id = getattr(target, 'id', None)
    details = {c.name: getattr(target, c.name) for c in target.__table__.columns}
    from packages.database.models import AuditLog  # Import here to avoid circular import
    from datetime import datetime
    ins = AuditLog.__table__.insert().values(
        user_id=user_id,
        action=action,
        table_name=table,
        row_id=row_id,
        timestamp=datetime.utcnow(),

    )
    connection.execute(ins)

# Import models and set up event listeners after Base is defined
def setup_audit_listeners():
    from packages.database.models import User, Education, Experience, Project, Skill, JobPreference, InAppNotification
    models = [User, Education, Experience, Project, Skill, JobPreference, InAppNotification]
    for model in models:
        event.listen(model, 'after_insert', lambda m, c, t: auto_log_audit(m, c, t, 'insert'))
        event.listen(model, 'after_update', lambda m, c, t: auto_log_audit(m, c, t, 'update'))
        event.listen(model, 'after_delete', lambda m, c, t: auto_log_audit(m, c, t, 'delete'))

# Call this function after models are imported

def init_database():
    """Initialize database with audit listeners"""
    setup_audit_listeners()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
