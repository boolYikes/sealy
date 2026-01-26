from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sealy.api.routes import router

app = FastAPI()

app.mount(
  "/static",
  StaticFiles(directory="sealy/static"),
  name="static",
)

app.include_router(router)
