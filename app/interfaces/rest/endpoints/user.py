from typing import Optional

from fastapi import APIRouter, Body, Depends, UploadFile, File, Query, status

from app.domain.user.entity import UserInCreate, UserInCreatePayload, User, ManyUserResponse, UserInDB, \
    UserInUpdatePayload, UserInUpdate
from app.infra.database.models.user import UserModel
from app.infra.security.security_service import get_current_user, get_current_admin
from app.shared.cloudianry import create_upload_file
from app.shared.decorator import response_decorator
from app.shared.validate_image import validate_image
from app.use_cases.user.create import CreateUserUseCase, CreateUserRequestObject
from app.use_cases.user.delete import DeleteUserRequestObject, DeleteUserUseCase
from app.use_cases.user.get import GetUserRequestObject, GetUserUseCase
from app.use_cases.user.list import ListUserRequestObject, ListUserUseCase
from app.use_cases.user.update import UpdateUserRequestObject, UpdateUserUseCase

router = APIRouter()


@router.post(
    "",
    response_model=User,
    dependencies=[Depends(get_current_admin)],
)
@response_decorator()
def create_user(
        payload: UserInCreatePayload = Body(..., title="UserInCreate payload"),
        avatar: UploadFile = File(None),
        create_user_use_case: CreateUserUseCase = Depends(CreateUserUseCase),
):
    url: Optional[str] = None
    if avatar is not None:
        validate_image(avatar)
        url = create_upload_file(avatar)

    new_payload = UserInCreate(**payload.model_dump(), avatar=url)
    req_object = CreateUserRequestObject.builder(payload=new_payload)
    response = create_user_use_case.execute(request_object=req_object)
    return response


@router.get(
    "",
    response_model=ManyUserResponse,
    dependencies=[Depends(get_current_user)]
)
@response_decorator()
def get_all_user(
        page_index: int = Query(default=1, title="Page index"),
        page_size: int = Query(default=20, title="Page size"),
        list_user_use_case: ListUserUseCase = Depends(ListUserUseCase),
):
    req_object = ListUserRequestObject.builder(page_index=page_index, page_size=page_size)
    response = list_user_use_case.execute(request_object=req_object)
    return response


@router.get(
    "/me",
    response_model=User,
)
@response_decorator()
def get_me(
        user_me: UserModel = Depends(get_current_user)
):
    return User(**UserInDB.model_validate(user_me).model_dump())


@router.get(
    "/{user_id}",
    response_model=User,
    dependencies=[Depends(get_current_user)]
)
@response_decorator()
def get_user_by_id(
        user_id: str,
        get_user_use_case: GetUserUseCase = Depends(GetUserUseCase),
):
    req_object = GetUserRequestObject.builder(user_id=user_id)
    response = get_user_use_case.execute(request_object=req_object)
    return response


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_admin)]
)
@response_decorator()
def delete_user_by_id(
        user_id: str,
        delete_user_use_case: DeleteUserUseCase = Depends(DeleteUserUseCase),
):
    req_object = DeleteUserRequestObject.builder(user_id=user_id)
    response = delete_user_use_case.execute(request_object=req_object)
    return response


@router.put(
    "/me",
    response_model=User,
)
@response_decorator()
def update_me(
        user_me: UserModel = Depends(get_current_user),
        payload: UserInUpdatePayload = Body(...),
        avatar: UploadFile = File(None),
        update_user_use_case: UpdateUserUseCase = Depends(UpdateUserUseCase),
):
    url: Optional[str] = None
    if avatar is not None:
        validate_image(avatar)
        url = create_upload_file(avatar)
    new_payload = UserInUpdate(**payload.model_dump(), avatar=url)
    req_object = UpdateUserRequestObject.builder(id=user_me.id, payload=new_payload)
    response = update_user_use_case.execute(request_object=req_object)
    return response


@router.put(
    "/{user_id}",
    response_model=User,
    dependencies=[Depends(get_current_admin)]
)
@response_decorator()
def update_user_by_id(
        user_id: str,
        payload: UserInUpdatePayload = Body(..., title="UserInUpdate payload"),
        avatar: UploadFile = File(None),
        update_user_use_case: UpdateUserUseCase = Depends(UpdateUserUseCase),
):
    url: Optional[str] = None
    if avatar is not None:
        validate_image(avatar)
        url = create_upload_file(avatar)
    new_payload = UserInUpdate(**payload.model_dump(), avatar=url)
    req_object = UpdateUserRequestObject.builder(id=user_id, payload=new_payload)
    response = update_user_use_case.execute(request_object=req_object)
    return response
