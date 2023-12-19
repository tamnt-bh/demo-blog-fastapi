from typing import Optional

from fastapi import APIRouter, Body, UploadFile, File, Depends, Query, HTTPException

from app.domain.post.entity import Post, PostInCreatePayload, PostInCreate, ManyPostResponse, PostInUpdate, SearchByPost
from app.domain.shared.enum import Sort
from app.domain.user.entity import UserInDB
from app.infra.database.models.user import UserModel
from app.infra.security.security_service import get_current_user
from app.shared.cloudianry import create_upload_file
from app.shared.decorator import response_decorator
from app.shared.validate_image import validate_image
from app.use_cases.post.create import CreatePostRequestObject, CreatePostUseCase
from app.use_cases.post.delete import DeletePostRequestObject, DeletePostUseCase
from app.use_cases.post.get import GetPostByIdUseCase, GetPostByIdObjectRequest
from app.use_cases.post.get_me import GetPostMeUseCase, GetPostMeObjectRequest
from app.use_cases.post.list import ListPostUseCase, ListPostRequestObject
from app.use_cases.post.update import UpdatePostObjectRequest, UpdatePostUseCase

router = APIRouter()


@router.get("", response_model=ManyPostResponse)
@response_decorator()
def get_all_post(
        page_index: int = Query(default=1, title="Page index"),
        page_size: int = Query(default=20, title="Page size"),
        search: str = Query(Optional[str], title="Search"),
        search_by: Optional[SearchByPost] = SearchByPost.TITLE,
        list_post_use_case: ListPostUseCase = Depends(ListPostUseCase),
        sort: Optional[Sort] = Sort.DESC,
        sort_by: Optional[str] = 'created_at'
):
    annotations = {}
    for base in reversed(Post.__mro__):
        annotations.update(getattr(base, '__annotations__', {}))
    if sort_by not in annotations:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by: {sort_by}")

    sort_query = {sort_by: 1 if sort is sort.ASCE else -1}
    req_object = ListPostRequestObject.builder(page_index=page_index, page_size=page_size, search=search,
                                               search_by=search_by, sort=sort_query)
    response = list_post_use_case.execute(request_object=req_object)
    return response


@router.post("", response_model=Post)
@response_decorator()
def create_post(
        payload: PostInCreatePayload = Body(...),
        thumbnail: UploadFile = File(None),
        current_user: UserModel = Depends(get_current_user),
        create_post_use_case: CreatePostUseCase = Depends(CreatePostUseCase)
):
    url: Optional[str] = None
    if thumbnail:
        validate_image(thumbnail)
        url = create_upload_file(thumbnail)

    new_payload = PostInCreate(**payload.model_dump(), author=current_user, thumbnail=url)
    req_object = CreatePostRequestObject.builder(payload=new_payload)
    response = create_post_use_case.execute(request_object=req_object)
    return response


@router.get("/me", response_model=ManyPostResponse)
@response_decorator()
def get_post_me(
        page_index: int = Query(default=1, title="Page index"),
        page_size: int = Query(default=20, title="Page size"),
        get_post_me_use_case: GetPostMeUseCase = Depends(GetPostMeUseCase),
        current_user: UserModel = Depends(get_current_user),
):
    req_object = GetPostMeObjectRequest.builder(author_id=current_user.id, page_size=page_size, page_index=page_index)
    response = get_post_me_use_case.execute(request_object=req_object)
    return response


@router.get("/{post_id}", response_model=Post)
@response_decorator()
def get_post_by_id(
        post_id: str,
        get_post_by_id_use_case: GetPostByIdUseCase = Depends(GetPostByIdUseCase)
):
    req_object = GetPostByIdObjectRequest.builder(post_id=post_id)
    response = get_post_by_id_use_case.execute(request_object=req_object)
    return response


@router.put("/{post_id}", response_model=Post)
@response_decorator()
def update_post(
        post_id: str,
        payload: PostInCreatePayload = Body(...),
        thumbnail: UploadFile = File(None),
        current_user: UserModel = Depends(get_current_user),
        update_post_use_case: UpdatePostUseCase = Depends(UpdatePostUseCase)
):
    url: Optional[str] = None
    if thumbnail:
        validate_image(thumbnail)
        url = create_upload_file(thumbnail)

    new_payload = PostInUpdate(**payload.model_dump(), thumbnail=url)
    req_object = UpdatePostObjectRequest.builder(payload=new_payload, post_id=post_id, author_id=current_user.id,
                                                 is_admin=UserInDB.model_validate(current_user).is_admin())
    response = update_post_use_case.execute(request_object=req_object)
    return response


@router.delete("/{post_id}")
@response_decorator()
def delete_post(
        post_id: str,
        current_user: UserModel = Depends(get_current_user),
        delete_post_use_case: DeletePostUseCase = Depends(DeletePostUseCase)
):
    req_object = DeletePostRequestObject.builder(post_id=post_id, author_id=current_user.id,
                                                 is_admin=UserInDB.model_validate(current_user).is_admin())
    response = delete_post_use_case.execute(request_object=req_object)
    return response
