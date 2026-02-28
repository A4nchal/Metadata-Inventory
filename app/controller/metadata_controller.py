from fastapi import APIRouter, BackgroundTasks, status
from pydantic import HttpUrl
from app.dto.request import Request
from app.service.metadata_service import MetadataService

router = APIRouter(prefix="/metadata", tags=["Metadata"])

service = MetadataService()

@router.post("/", status_code=status.HTTP_200_OK, summary="Create metadata record")
async def create_metadata(request: Request):
    return await service.create_metadata(str(request.url))

@router.get("/",    
        responses={
            200: {"description": "Metadata found"},
            202: {"description": "Metadata collection initiated"},
            502: {"description": "Upstream service unreachable"},
            504: {"description": "Upstream timeout"},
    })
async def get_metadata(url: HttpUrl, background_tasks: BackgroundTasks):
    return await service.get_metadata(str(url), background_tasks)