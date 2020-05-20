from pymongo import MongoClient
import config

mongo_client = MongoClient(config.MONGO_DATABASE_URI)


# class User(db.Model):
#     id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid.uuid4()))
#     username = db.Column(db.String())
#     email = db.Column(db.String(), unique=True)
