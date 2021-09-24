import typing
from datetime import datetime, timedelta

import boto3
import click
import jwt
from botocore.exceptions import ClientError

JWT_ALGO = ("HS256",)


def get_secret(app_short_name, stage, region):
    """
    Fetch the token generation secret from AWS
    """
    client = boto3.client("secretsmanager", region_name=region)
    try:
        ret = client.get_secret_value(
            SecretId=f"/{app_short_name}/{stage}/token-secret",
        )
        return ret["SecretString"]
    except ClientError as e:
        error = e.response["Error"]
        raise click.ClickException(message=f"({error['Code']}) {error['Message']} {e.response}")


def create_timed_token(sub: str, iss: str, secret: str, duration: typing.Optional[int] = None, **kwargs):
    """
    Convenience method to create tokens of a particular duration
    You can also create non-expiring tokens by setting duration=None
    """
    if not secret or not sub or not iss:
        raise TypeError("secret, sub, and iss cannot be empty")

    kwargs.setdefault("algorithm", JWT_ALGO[0])

    payload = {"sub": sub, "iss": iss}
    if duration is not None:
        payload.update({"exp": _expiration(duration)})

    t = jwt.encode(payload, secret, **kwargs)

    # Make sure we created a usable token.
    # validate and create are slightly asymmetric in that you can allow multiple algorithms
    # during decode, but only one during encode, so swap these around
    validate_kwargs = kwargs.copy()
    validate_kwargs.setdefault("algorithms", [validate_kwargs.pop("algorithm")])
    validate_kwargs.setdefault("leeway", 1)
    assert validate_token(t, secret, **validate_kwargs)

    return t


def _expiration(duration: int):
    """
    Generate a datetime now + duration seconds
    """
    return datetime.utcnow() + timedelta(seconds=duration)


_NO_DEFAULT = object()


def validate_token(token: str, secret: str, default=_NO_DEFAULT, **kwargs):
    """
    Check a token signature and claims, and return the userid string (`sub` claim) or the supplied default
    If no default is passed in, this raises any exceptions that occur during token decode
    """
    kwargs.setdefault("algorithms", [JWT_ALGO[0]])
    try:
        payload = jwt.decode(token, secret, **kwargs)
        return payload

    except jwt.PyJWTError:
        if default is _NO_DEFAULT:
            raise

        return default