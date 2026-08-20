import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
STAFF_PATH = os.path.join(DATA_DIR, "staff.json")
JOBS_PATH = os.path.join(DATA_DIR, "jobs.json")
GENERATED_DIR = os.path.join(BASE_DIR, "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)

# Allow the frontend origin(s) that may call this API. Update with your real
# Medics Online domain when you deploy; "*" is convenient for local demo only.
CORS_ALLOW_ORIGINS = os.environ.get("CORS_ALLOW_ORIGINS", "*").split(",")
