from ..shared.config import settings
from sqlalchemy import create_engine, text
import redis
import chromadb # ou milvus client selon le sujet
engine = create_engine(settings.db_url, echo=False)
def get_connection():
return engine.connect()
def get_redis_client():
return redis.StrictRedis(host=settings.REDIS_HOST,
port=settings.REDIS_PORT,
decode_responses=True)
def get_vector_db_client():
# Exemple ChromaDB
import chromadb
client = chromadb.Client(
host="localhost", # dans le container, le serveur écoute sur localhost
port=8000 # API HTTP
)
return client
# L’IA-Adapter (ex. Ollama) utilise settings.OLLAMA_HOST et settings.OLLAMA_MODEL
# Vous pouvez créer un wrapper dédié (voir la section 4 du document)