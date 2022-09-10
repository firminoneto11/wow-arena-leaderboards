from databases import Database
from orm import ModelRegistry


db = Database("sqlite:///db.db")
db_engine = ModelRegistry(database=db)
