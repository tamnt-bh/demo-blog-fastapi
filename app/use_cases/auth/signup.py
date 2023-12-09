from fastapi import Depends
from mongoengine import NotUniqueError

from app.domain.auth.entity import SignupRequest, TokenData, AuthInfoInResponse
from app.domain.user.entity import UserInCreate, User, UserInDB
from app.infra.database.models.user import UserModel
from app.infra.security.security_service import get_password_hash, create_access_token
from app.infra.user.user_repository import UserRepository
from app.shared import request_object, use_case, response_object


class SignupRequestObject(request_object.ValidRequestObject):
    def __init__(self, payload: UserInCreate):
        self.payload = payload

    @classmethod
    def builder(cls, payload: SignupRequest) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()

        if payload is None:
            invalid_req.add_error("payload", "Invalid payload")

        if not payload.email:
            invalid_req.add_error("payload.email", "Invalid email")

        if invalid_req.has_errors():
            return invalid_req

        new_payload = UserInCreate(**payload.model_dump())
        return SignupRequestObject(payload=new_payload)


class SignupUseCase(use_case.UseCase):
    def __init__(
            self,
            user_repository: UserRepository = Depends(UserRepository),
    ):
        self.user_repository = user_repository

    def process_request(self, req_object: SignupRequestObject):
        user_in: UserInCreate = req_object.payload
        obj_in: UserInCreate = UserInCreate(**user_in.model_dump(exclude=({"password"})),
                                            password=get_password_hash(user_in.password))

        try:
            user: UserModel = self.user_repository.create(user=obj_in)
            access_token = create_access_token(
                data=TokenData(email=user.email, id=str(user.id))
            )
            return AuthInfoInResponse(access_token=access_token,
                                      user=User(**UserInDB.model_validate(user).model_dump()))
        except NotUniqueError:
            return response_object.ResponseFailure.build_system_error("This email existed already")
        except Exception:
            return response_object.ResponseFailure.build_system_error("Something went error.")
