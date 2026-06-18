from fastapi import HTTPException
from starlette import status


def success(message: str, data=None):
    return {"message": message, "data": data}


def bad_request(message: str):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def not_found(message: str):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
