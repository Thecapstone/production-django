from rest_framework import status
from rest_framework.exceptions import APIException


class CustomError:
    class Forbidden(APIException):
        status_code = status.HTTP_403_FORBIDDEN
        default_detail = "forbidden"
        default_code = "forbidden"

    class ServiceUnavailable(APIException):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        default_detail = "Service unavailable."
        default_code = "service_unavailable"

    class BadRequest(APIException):
        status_code = status.HTTP_400_BAD_REQUEST
        default_detail = "bad request"
        default_code = "bad_request"

    class EmptyResponse(APIException):
        status_code = status.HTTP_200_OK
        default_detail = []
        default_code = status.HTTP_200_OK

    class NotFound(APIException):
        status_code = status.HTTP_404_NOT_FOUND
        default_detail = "Not Found"
        default_code = status.HTTP_404_NOT_FOUND

    class NotAcceptable(APIException):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        default_detail = "Not acceptable."
        default_code = "not_acceptable"

    class MethodNotAllowed(APIException):
        status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        default_detail = "Method not allowed."
        default_code = "method_not_allowed"

    class Redirect(APIException):
        status_code = status.HTTP_307_TEMPORARY_REDIRECT
        default_detail = "Temporary Redirect."
        default_code = "temporary_redirect"

    class UnAuthorized(APIException):
        status_code = status.HTTP_401_UNAUTHORIZED
        default_detail = "Authentication credentials were not provided."
        default_code = "unauthorized"

    @classmethod
    def raise_error(
        cls,
        message: str,
        exception: str = "BadRequest",
    ):
        e: APIException = getattr(cls, exception)
        raise e(message)
