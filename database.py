from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Float, String, Integer, DateTime
from datetime import datetime

# Cria a classe Base do SQLAlchemy (na versão 2.x)
Base = declarative_base()

class DadosHistoricosAcoes(Base):
    """Define a tabela no banco de dados."""
    __tablename__ = "dados_historicos_acoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fechamento = Column(Float, nullable=False)             # Valor de fechamento
    fechamento_ajustado = Column(Float, nullable=False)    # Valor de fechamento ajustado
    ticker = Column(String(50), nullable=False)            # Código da ação (ex.: PETR4, VALE3)
    moeda = Column(String(10), nullable=False, default="BRL") # Moeda, padrão BRL
    data = Column(DateTime, nullable=False)                # Data da cotação
    timestamp = Column(DateTime, default=datetime.now)     # Data de criação do registro