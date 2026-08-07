import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# OpenAI Key (optional fallback)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Gemini Model
GEMINI_MODEL = "gemini-2.5-flash"

# Embedding Model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# FAISS Index Path
VECTOR_DB_PATH = "faiss_index"

# Chunk Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Number of retrieved chunks
TOP_K = 4