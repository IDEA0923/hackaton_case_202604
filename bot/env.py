import os
TOKEN = os.getenv("TOKEN")
OPENROUTER_API_KEY = os.getenv("TOKEN_AI")
admins = [int(os.getenv("admin_id"))]

db_file = "database.db"