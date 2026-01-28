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

# modelo db 
class Tarefa(Base):
    __tablename__ = "tarefas"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    concluida = Column(Boolean, default=False)

# cria tabelas 
Base.metadata.create_all(bind=engine)

# modelo do pydantic 
class TarefaCreate(BaseModel):
    titulo: str
    concluida: bool = False

class TarefaResponse(TarefaCreate):
    id: int

    class Config:
        orm_mode = True 
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.get("/tarefas/", response_model=list[TarefaResponse])
def listar(db: Session = Depends(get_db)):
    return db.query(Tarefa).all()

@app.post("/tarefas/", response_model=TarefaResponse)
def criar(tarefa: TarefaCreate, db: Session = Depends(get_db)):
    db_item = Tarefa(**tarefa.dict()) 
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/tarefas/{id}")
def deletar(id: int, db: Session = Depends(get_db)):
    item = db.query(Tarefa).filter(Tarefa.id == id).first()  
    if not item:
        raise HTTPException(status_code=404, detail="Tarefa não labelling")
    db.delete(item)
    db.commit()
    return {"ok": True}

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