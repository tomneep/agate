from typing import Union
from typing import Annotated
from fastapi import FastAPI, Header, HTTPException, status
import os;

app = FastAPI()


@app.get("/projects/{project_name}")
def get_project_authorization(project_name, Authorization: Annotated[Union[str, None], Header()] = None):
    if (Authorization != f"Token {os.environ['TOKEN']}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    elif project_name == "mscape":
        return {"message": "Authorized"}
    elif project_name == "project2":
        return {"message": "Authorized"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


@app.get("/projects")
def get_projects(Authorization: Annotated[Union[str, None], Header()] = None):
    if (Authorization != f"Token {os.environ['TOKEN']}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token"
        )

    return {"data": [
        {"project": "mscape", "scope": "analyst", "actions": ['get', 'list', 'filter', 'history']},
        {"project": "project2", "scope": "analyst", "actions": ['get', 'list', 'filter', 'history']},
    ]}


@app.get("/accounts/profile")
def get_profile(Authorization: Annotated[Union[str, None], Header()] = None):
    if (Authorization != f"Token {os.environ['TOKEN']}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token"
        )

    return {"data": {"username": "nabutcher.bham-mscape", "site": "bham"}}
