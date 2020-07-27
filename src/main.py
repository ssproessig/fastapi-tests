from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

import uvicorn
from fastapi import FastAPI, Security, Request
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.auth import parse_bearer_token


app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


class User(BaseModel):
    id: Optional[UUID]
    name: str
    joined: datetime


class Message(BaseModel):
    message: str


USERS = {}


@app.get("/")
async def read_root():
    return RedirectResponse("/docs")


@app.get("/me")
async def me(_=Security(parse_bearer_token)):
    return {"message": "you are logged in!"}


@app.get("/users", response_model=List[User])
async def read_users(_=Security(parse_bearer_token, scopes=["fastapi-tests:users:read"])):
    return list(USERS.values())


@app.get("/users/{user_id}", response_model=User, responses={404: {"model": Message, "description": "User not found"}})
async def read_user(user_id: str, _=Security(parse_bearer_token, scopes=["fastapi-tests:users:read"])):
    if user_id not in USERS:
        return JSONResponse(status_code=404, content={"message": "User not found"})

    return USERS[user_id]


@app.post("/users/", status_code=201)
async def post_user(user: User, _=Security(parse_bearer_token, scopes=["fastapi-tests:users:write"])):
    user.id = uuid4()
    USERS[user.id] = user
    return user


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)