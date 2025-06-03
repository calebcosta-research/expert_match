from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from opensearchpy import OpenSearchException
from pathlib import Path
import shutil
from scholarly import scholarly

from . import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="ExpertMatch API")

UPLOAD_DIR = Path("uploaded_files")
UPLOAD_DIR.mkdir(exist_ok=True)


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


def build_expert_embedding(expert: models.Expert, publications: list[models.Publication]) -> list[float]:
    parts = [expert.name or "", expert.biography or "", expert.location or ""]
    parts += [pub.title for pub in publications]
    return compute_embedding(" ".join(parts))


@app.post("/experts/", response_model=schemas.Expert)
def create_expert(expert: schemas.ExpertCreate, db: Session = Depends(get_db)):
    db_expert = models.Expert(**expert.dict())
    db.add(db_expert)
    db.commit()
    db.refresh(db_expert)
    # index in OpenSearch
    client = database.get_opensearch_client()
    try:
        embedding = build_expert_embedding(db_expert, [])
        client.index(index="experts", id=db_expert.id, body={"id": db_expert.id, "embedding": embedding})
    except Exception:
        pass
    return db_expert


@app.get("/experts/{expert_id}", response_model=schemas.Expert)
def read_expert(expert_id: int, db: Session = Depends(get_db)):
    db_expert = db.query(models.Expert).filter(models.Expert.id == expert_id).first()
    if not db_expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    return db_expert


@app.post("/experts/{expert_id}/upload_cv", response_model=schemas.Expert)
def upload_cv(expert_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    expert = db.query(models.Expert).filter(models.Expert.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    path = UPLOAD_DIR / f"cv_{expert_id}.pdf"
    with path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    expert.cv_s3_key = str(path)
    db.commit()
    db.refresh(expert)
    return expert


@app.post("/experts/{expert_id}/upload_bio", response_model=schemas.Expert)
def upload_bio(expert_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    expert = db.query(models.Expert).filter(models.Expert.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    path = UPLOAD_DIR / f"bio_{expert_id}.txt"
    with path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    expert.biography_file_key = str(path)
    db.commit()
    db.refresh(expert)
    return expert


@app.post("/experts/{expert_id}/publications/fetch", response_model=list[schemas.Publication])
def fetch_publications(expert_id: int, db: Session = Depends(get_db)):
    expert = db.query(models.Expert).filter(models.Expert.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    if not expert.google_scholar_url:
        raise HTTPException(status_code=400, detail="Expert has no Google Scholar URL")

    scholar_id = expert.google_scholar_url.split("user=")[-1].split("&")[0]
    author = scholarly.search_author_id(scholar_id)
    author = scholarly.fill(author, sections=["publications"])
    publications = []
    for pub in author.get("publications", [])[:5]:
        filled = scholarly.fill(pub)
        title = filled.get("bib", {}).get("title", "")
        year = filled.get("bib", {}).get("pub_year")
        url = filled.get("pub_url")
        p = models.Publication(expert_id=expert_id, title=title, year=year, url=url)
        publications.append(p)
        db.add(p)
    db.commit()
    # update embedding with new publications
    client = database.get_opensearch_client()
    embedding = build_expert_embedding(expert, publications)
    try:
        client.index(index="experts", id=expert.id, body={"id": expert.id, "embedding": embedding})
    except Exception:
        pass
    return publications


@app.get("/experts/{expert_id}/publications", response_model=list[schemas.Publication])
def list_publications(expert_id: int, db: Session = Depends(get_db)):
    expert = db.query(models.Expert).filter(models.Expert.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    return expert.publications


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
