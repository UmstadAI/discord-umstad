import json
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
    created_at: str
    owner: str


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/")
def consume_process(event: Event):
    print("WORKED")
    try:
        response = lambda_handler(event)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))