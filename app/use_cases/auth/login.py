from fastapi import Depends

from app.domain.auth.entity import LoginRequest, TokenData, AuthInfoInResponse
from app.domain.user.entity import User, UserInDB
from app.infra.database.models.user import UserModel
from app.infra.security.security_service import verify_password, create_access_token
from app.infra.user.user_repository import UserRepository
from app.shared import request_object, use_case, response_object


class LoginRequestObject(request_object.ValidRequestObject):
    def __init__(self, login_payload: LoginRequest):
        self.login_payload = login_payload

    @classmethod
    def builder(cls, login_payload: LoginRequest):
        invalid_req = request_object.InvalidRequestObject()
        if not login_payload:
            invalid_req.add_error("login_payload", "Invalid")

        if invalid_req.has_errors():
            return invalid_req

        return LoginRequestObject(login_payload=login_payload)


class LoginUseCase(use_case.UseCase):
    def __init__(
            self,
            user_repository: UserRepository = Depends(UserRepository),
    ):
        self.user_repository = user_repository

    def process_request(self, req_object: LoginRequestObject):
        user: UserModel = self.user_repository.get_by_email(req_object.login_payload.email)
        checker = False
        if user:
            checker = verify_password(req_object.login_payload.password, user.password)
        if not user or not checker:
            return response_object.ResponseFailure.build_parameters_error(message="Incorrect email or password")
        access_token = create_access_token(
            data=TokenData(email=user.email, id=str(user.id))
        )
        return AuthInfoInResponse(access_token=access_token,
                                  user=User(**UserInDB.model_validate(user).model_dump()))
