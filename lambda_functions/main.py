from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from process import lambda_handler

app = FastAPI()


class Event(BaseModel):
    guild_id: int
    thread_id: int
    title: str
    message: str
    message_id: str
    created_at: str
    owner_id: str

    def get(self, key, default=None):
        return getattr(self, key, default)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/")
def consume_process(event: Event):
    try:
        response = lambda_handler(event)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
