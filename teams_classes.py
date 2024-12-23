from pydantic import BaseModel, conint, constr, Field
from typing import Optional
import random

class NewUser(BaseModel):
    username: constr(min_length=1)
    name: constr(min_length=1)
    description: Optional[str] = ""
    location: Optional[str] = None

class User(BaseModel):
    user_id: constr(min_length=1)
    username: constr(min_length=1) #This one unique
    name: constr(min_length=1)
    description: Optional[str] = ""
    location: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.user_id,
            "tweet_count": random.randint(10, 100),#modification might not be ligiable
            "z_score": random.uniform(-1, 1),
            "username": self.username,
            "name": self.name,
            "description": self.description,
            "location": self.location
        }
        

class NewPost(BaseModel):
    text: constr(min_length=1)
    author_id: constr(min_length=1)
    created_at: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.000Z$') # Time format like this 2024-03-27T00:06:30.000Z

    def to_dict(self, dataset_lang):
        return {
            "id": "",
            "text": self.text,
            "author_id": self.author_id,
            "created_at": self.created_at,
            "lang": dataset_lang,
        }

class DetectionMark(BaseModel):
    user_id: constr(min_length=1)
    confidence: conint(ge=0, le=100)
    bot: bool

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "confidence": self.confidence,
            "bot": self.bot
        }