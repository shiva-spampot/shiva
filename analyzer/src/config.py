import os

QUEUE_DIR = os.getenv("QUEUE_DIR", "/tmp/spam_queue/")
VT_API_KEY = os.getenv("VT_API_KEY", "")
ARCHIVE_DIR = os.getenv("/tmp/spam_queue/", "")
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://username:password@postgres/shiva-pot"
)
SSDEEP_SIMILARITY_THRESHOLD = int(os.getenv("SSDEEP_SIMILARITY_THRESHOLD", "95"))
