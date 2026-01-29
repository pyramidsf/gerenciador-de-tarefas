"""
resumo do fluxo do backend
1. FastAPI recebe JSON
2. Verifica se o JSON bate com TabelaCreate 
3. Chama get.db() para abrir uma sessão 
4. Roda a função criar()
5. SQL Alchemy gera o SQL INSERT
6. Banco devolve o ID
7. A função retorna o objeto, que é validado pelo TarefaResponse e vira JSON de volta para o navegador. 

"""

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# modelo db, onde é criado as tabelas do banco de dados
class Tarefa(Base):
    __tablename__ = "tarefas"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    concluida = Column(Boolean, default=False)

# verifica se a tabela de tarefas existe ou não. cria se não existir 
Base.metadata.create_all(bind=engine)

# schemas pydantic. o fastapi vai usar essa tecnologia para verificar que os dados entrando e saindo estejam no formato certo 
class TarefaCreate(BaseModel):
    titulo: str
    concluida: bool = False

class TarefaResponse(TarefaCreate):
    id: int

    class Config:
        orm_mode = True 
        from_attributes = True

# injeçao de dependencia da db. garante que o banco seja abero e fechado no final da requisiçao 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# aqui ficam as rotas, a lógica da api

# rota para listar tarefa (GET)
@app.get("/tarefas/", response_model=list[TarefaResponse])
def listar(db: Session = Depends(get_db)):
    return db.query(Tarefa).all()

# rota para criar tarefa (POST)
@app.post("/tarefas/", response_model=TarefaResponse)
def criar(tarefa: TarefaCreate, db: Session = Depends(get_db)):
    db_item = Tarefa(**tarefa.dict())  
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# rota para deletar tarefa (DELETE)
@app.delete("/tarefas/{id}")
def deletar(id: int, db: Session = Depends(get_db)):
    item = db.query(Tarefa).filter(Tarefa.id == id).first()  
    if not item:
        raise HTTPException(status_code=404, detail="Tarefa não labelling")
    db.delete(item)
    db.commit()
    return {"ok": True}

# rota para atualizar tarefa (PUT)
@app.put("/tarefas/{id}", response_model=TarefaResponse)
def atualizar(id: int, tarefa: TarefaCreate, db: Session = Depends(get_db)):
    item = db.query(Tarefa).filter(Tarefa.id == id).first()  
    if not item:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    item.titulo = tarefa.titulo
    item.concluida = tarefa.concluida
    db.commit()
    db.refresh(item)
    return item