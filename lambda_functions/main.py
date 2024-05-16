from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from process import lambda_handler
from thread_process import thread_lambda_handler

app = FastAPI()

# uvicorn main:app --host 127.0.0.1 --port 8000

class Event(BaseModel):
    guild_id: int
    thread_id: int
    title: str
    message: Union[str, None] = None
    messages: Union[str, None] = None
    message_id: Union[str, None] = None
    created_at: str
    owner_id: str

    @validator('message', 'messages', pre=True, always=True)
    def check_not_both(cls, v, values, field):
        if 'message' in values and 'messages' in values:
            raise ValueError("Both 'message' and 'messages' cannot be provided simultaneously.")
        return v

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/")
def consume_process(event: Event):
    try:
        if event.messages:
            response = thread_lambda_handler(event)
        else:
            response = lambda_handler(event)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))