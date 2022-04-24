from databases import Database
from orm import ModelRegistry


db = Database("sqlite:///../db.db")
objects = ModelRegistry(database=db)
