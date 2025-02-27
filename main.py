from fastapi import FastAPI
from fastapi.responses import RedirectResponse
# from app.api import items

app = FastAPI()


@app.get("/")
def get_docs():
    return RedirectResponse("/docs")
