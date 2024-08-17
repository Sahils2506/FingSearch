import json
from pymongo import MongoClient
from pymongo import TEXT
class Query:
    def __init__(self,title,url,description) -> None:
        self.title = title
        self.url = url
        self.description = description
    
    def __str__(self) -> str:
        obj = {
            'url' : self.url,
            'title' : self.title,
            'description' : self.description,
        }
        return json.dumps(obj)

    def save(self,client):
        obj = {
            'url' : self.url,
            'title' : self.title,
            'description' : self.description,
        }
        db = client.gluggle
        collection = db.queries
        collection.insert_one(obj)
        collection.create_index([
            ('url', TEXT),
            ('title', TEXT),
            ('description', TEXT),
            ], name='search_results', default_language='english')
        client.close()
        