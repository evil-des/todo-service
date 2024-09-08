from fastapi import Depends

from api.web.api.crudrouter import fastapi_crudrouter

from api.db.models.comments import CommentModel
from api.web.api.comments.schema import Comment, CommentCreate
from api.db.dependencies import get_db_session
from api.services.todo_core.crud import TodoCoreCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.dao.comment_dao import CommentDAO


router = fastapi_crudrouter.SQLAlchemyCRUDRouter(
    schema=Comment,
    create_schema=CommentCreate,
    db_model=CommentModel,
    db=get_db_session,
)


@router.post("")
async def create_comment(comment: CommentCreate, comment_dao: CommentDAO = Depends()):
    result = await comment_dao.create_comment(comment.task_id, comment.content)
    return result
