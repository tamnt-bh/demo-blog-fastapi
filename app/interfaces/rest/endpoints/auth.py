from fastapi import APIRouter, Body, Depends

from app.domain.auth.entity import LoginRequest, AuthInfoInResponse, SignupRequest
from app.shared.decorator import response_decorator
from app.use_cases.auth.login import LoginRequestObject, LoginUseCase
from app.use_cases.auth.signup import SignupUseCase, SignupRequestObject

router = APIRouter()


@router.post("/login", response_model=AuthInfoInResponse)
@response_decorator()
def login(payload: LoginRequest = Body(...), login_use_case: LoginUseCase = Depends(LoginUseCase)):
    req_object = LoginRequestObject.builder(login_payload=payload)
    response = login_use_case.execute(req_object)
    return response


@router.post("/signup", response_model=AuthInfoInResponse)
@response_decorator()
def signup(payload: SignupRequest = Body(...), signup_use_case: SignupUseCase = Depends(SignupUseCase)):
    req_object = SignupRequestObject.builder(payload=payload)
    response = signup_use_case.execute(req_object)
    return response
