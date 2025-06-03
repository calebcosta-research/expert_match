from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from opensearchpy import OpenSearchException

from . import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="ExpertMatch API")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def compute_embedding(text: str) -> list[float]:
    """Compute a very small dummy embedding for the given text."""
    if text is None:
        text = ""
    # Simple hash-based embedding placeholder
    return [float(abs(hash(text)) % 1000)]


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
    """Return experts ranked by similarity to the given project."""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    client = database.get_opensearch_client()
    embedding = compute_embedding((project.description or "") + (project.qualifications or ""))
    query = {
        "knn": {
            "field": "embedding",
            "query_vector": embedding,
            "k": 10,
            "num_candidates": 10,
        }
    }
    try:
        res = client.search(index="experts", body={"size": 10, "query": query})
        expert_ids = [hit["_source"]["id"] for hit in res.get("hits", {}).get("hits", [])]
    except OpenSearchException:
        raise HTTPException(status_code=503, detail="OpenSearch unavailable")

    if not expert_ids:
        return {"project": project, "experts": []}

    experts = db.query(models.Expert).filter(models.Expert.id.in_(expert_ids)).all()
    # maintain the order returned by OpenSearch
    experts_dict = {e.id: e for e in experts}
    ordered = [experts_dict[eid] for eid in expert_ids if eid in experts_dict]
    return {"project": project, "experts": ordered}
