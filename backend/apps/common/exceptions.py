from rest_framework.exceptions import APIException
from rest_framework import status

class ApplicationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An application error occurred.'
    default_code = 'application_error'

    def __init__(self, detail=None, code=None, status_code=None):
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail
            
        if code is not None:
            self.code = code
        else:
            self.code = self.default_code
            
        if status_code is not None:
            self.status_code = status_code
            
class InvalidStateError(ApplicationError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'The action cannot be performed in the current state.'
    default_code = 'invalid_state'

class ResourceNotFoundError(ApplicationError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'The requested resource was not found.'
    default_code = 'not_found'
