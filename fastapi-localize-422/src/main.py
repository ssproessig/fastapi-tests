from typing import List, Optional
from uuid import UUID, uuid4

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

from localization import localized_validation_exception_handler

app = FastAPI(docs_url=None, redoc_url=None)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return localized_validation_exception_handler(request, exc)


class FooCreate(BaseModel):
    name: str = Field(
        max_length=10
    )
    tags: Optional[List[str]] = []


class FooGet(FooCreate):
    id: UUID


@app.get(
    "/foos",
    response_model=List[FooGet],
    response_model_exclude_unset=True
)
async def get_foos() -> List[FooGet]:
    return list(FOOS.values())


@app.post(
    "/foos",
    response_model=FooGet
)
async def post_foo(foo: FooCreate) -> FooGet:
    new_foo = FooGet(**foo.dict(), id=uuid4())
    FOOS[new_foo.id] = new_foo
    return new_foo


FOOS = {}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
