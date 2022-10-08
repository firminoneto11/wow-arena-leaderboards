from decouple import config as get_env_var
from databases import Database
from orm import ModelRegistry


DATABASE_URL: str = get_env_var("DATABASE_URL")

db = Database(DATABASE_URL)
engine = ModelRegistry(database=db)
