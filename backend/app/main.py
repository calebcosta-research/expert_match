from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="ExpertMatch API")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/experts/", response_model=schemas.Expert)
def create_expert(expert: schemas.ExpertCreate, db: Session = Depends(get_db)):
    db_expert = models.Expert(**expert.dict())
    db.add(db_expert)
    db.commit()
    db.refresh(db_expert)
    return db_expert


@app.get("/experts/{expert_id}", response_model=schemas.Expert)
def read_expert(expert_id: int, db: Session = Depends(get_db)):
    db_expert = db.query(models.Expert).filter(models.Expert.id == expert_id).first()
    if not db_expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    return db_expert


@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@app.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project


@app.get("/projects/{project_id}/matches")
def match_experts(project_id: int, db: Session = Depends(get_db)):
    """Placeholder match endpoint. Returns all experts for now."""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    experts = db.query(models.Expert).all()
    # TODO: replace with real similarity search against OpenSearch
    return {"project": project, "experts": experts}
