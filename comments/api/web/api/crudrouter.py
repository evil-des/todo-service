import fastapi_crudrouter
from pydantic import create_model
from typing import Type, Any
from fastapi_crudrouter.core._types import PYDANTIC_SCHEMA, T


# Fix for CRUDRouter if using Pydantic V2
# https://github.com/awtkns/fastapi-crudrouter/issues/189

def get_pk_type_patch(schema: Type[PYDANTIC_SCHEMA], pk_field: str) -> Any:
    try:
        return schema.__fields__[pk_field].annotation
    except KeyError:
        return int


def schema_factory_patch(
    schema_cls: Type[T], pk_field_name: str = "id", name: str = "Create"
) -> Type[T]:
    fields = {
        name: (f.annotation, ...)
        for name, f in schema_cls.__fields__.items()
        if name != pk_field_name
    }

    name = schema_cls.__name__ + name
    schema: Type[T] = create_model(__model_name=name, **fields)  # type: ignore
    return schema


fastapi_crudrouter.core._utils.get_pk_type = get_pk_type_patch
fastapi_crudrouter.core._utils.schema_factory = schema_factory_patch
fastapi_crudrouter.core._base.schema_factory = schema_factory_patch
