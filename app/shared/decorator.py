import functools

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.interfaces.rest.error_handler import ApplicationLevelException
from app.shared.response_object import ResponseSuccess, ResponseFailure


def response_decorator():
    """Handle data response for resource

    Keyword Arguments:

    Returns:
        [type] -- [description]
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            response = f(*args, **kwargs)

            if isinstance(response, ResponseSuccess):
                # handle response success object
                val = response.value
                return JSONResponse(content=jsonable_encoder(val, by_alias=True))
                # return response.value
            elif isinstance(response, ResponseFailure):
                # handle response failure error
                if response.type == ResponseFailure.RESOURCE_ERROR:
                    # Client / resource error
                    raise ApplicationLevelException(msg=response.message)
                if response.type == ResponseFailure.PARAMETERS_ERROR:
                    raise HTTPException(
                        status_code=400,
                        detail=response.message,
                    )
                elif response.type == ResponseFailure.RESOURCE_NOT_FOUND:
                    # Item not found
                    raise HTTPException(
                        status_code=404,
                        detail=response.message,
                    )
                elif response.type == ResponseFailure.AUTH_ERROR:
                    # Authentication error status code
                    raise HTTPException(
                        status_code=401,
                        detail=response.message,
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                else:
                    # System error http status code
                    raise HTTPException(status_code=500, detail=response.message)
            else:
                return JSONResponse(content=jsonable_encoder(response))

        return wrapper

    return decorator
