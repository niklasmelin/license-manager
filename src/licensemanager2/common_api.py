"""
Boilerplate responses
"""
from pydantic import BaseModel


class OK(BaseModel):
    """
    A response that there was no error, when no other data is required
    """

    status: str = "ok"
    message: str = ""


class NotOK(OK):
    """
    A response that there was no error, when no other data is required
    """

    status: str = "notok"
    message: str = ""
