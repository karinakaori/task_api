from datetime import datetime, timezone
from sqlalchemy import Column, Date, DateTime, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# URL do banco SQLite local. O arquivo tasks.db será criado na raiz do projeto.
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"

# Cria o motor de conexão com SQLite.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Fábrica de sessões que serão usadas pelo FastAPI para cada requisição.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Gera uma sessão de banco de dados para uso em dependências do FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TaskDB(Base):
    """Modelo de dados que representa a tabela de tarefas no banco."""
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String(16), nullable=False, default="todo")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    due_date = Column(Date, nullable=True)
