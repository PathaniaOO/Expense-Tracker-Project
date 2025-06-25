from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_NAME = "finance_db"
DB_USER = 'postgres'
DB_PASS = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def create_table():
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            type VARCHAR(10) CHECK (type IN ('income', 'expense')),
            category VARCHAR(50),
            amount NUMERIC(12, 2),
            description TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_date ON transactions(date);
        CREATE INDEX IF NOT EXISTS idx_type ON transactions(type);
    """
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
