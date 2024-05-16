from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from process import lambda_handler
from thread_process import thread_lambda_handler

app = FastAPI()

# uvicorn main:app --host 127.0.0.1 --port 8000

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

class ThreadEvent(BaseModel):
    guild_id: int
    thread_id: int
    title: str
    messages: str
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

@app.post("/thread")
def consume_thread_process(event: ThreadEvent):
    try:
        response = thread_lambda_handler(event)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))