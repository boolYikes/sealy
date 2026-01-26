from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/favicon.ico", include_in_schema=False)
def favicon():
  return FileResponse("sealy/static/favicon.ico")


@router.get("/health")
def health():
  return {"status": "ok"}
