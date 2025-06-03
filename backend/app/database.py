from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from opensearchpy import OpenSearch
import os

SQLALCHEMY_DATABASE_URL = "sqlite:///./expertmatch.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# OpenSearch connection
OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://localhost:9200")


def get_opensearch_client() -> OpenSearch:
    """Return an OpenSearch client using the configured host."""
    return OpenSearch(hosts=[OPENSEARCH_URL])

