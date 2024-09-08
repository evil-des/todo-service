from fastapi import Depends
from api.db.models.comments import CommentModel
from api.web.api.comments.schema import Comment, CommentCreate, CommentUpdate
from api.db.dependencies import get_db_session
from api.services.todo_core.crud import TodoCoreCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.dao.comment_dao import CommentDAO
from fastcrud import FastCRUD, crud_router, EndpointCreator


class CommentsEndpoint(EndpointCreator):
    def _create_item(self):
        async def create_comment(comment: CommentCreate, comment_dao: CommentDAO = Depends()):
            result = await comment_dao.create_comment(comment.task_id, comment.content)
            return result

        return create_comment


router = crud_router(
    session=get_db_session,
    model=CommentModel,
    create_schema=CommentCreate,
    update_schema=CommentUpdate,
    endpoint_creator=CommentsEndpoint
)
