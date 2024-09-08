from fastapi.routing import APIRouter
from fastapi import Depends
from api.web.auth_bearer import JWTBearer
from api.web.api import monitoring, comments


api_router = APIRouter(dependencies=[Depends(JWTBearer())])


api_router.include_router(monitoring.router)
api_router.include_router(comments.router, prefix="/comments")
