"""
Provide utilities that communicate with the backend.
"""
import pathlib
import typing

import httpx
import jwt
from pydantic import BaseModel, ValidationError

from lm_agent.config import settings
from lm_agent.exceptions import LicenseManagerAuthTokenError, LicenseManagerBackendConnectionError
from lm_agent.logs import logger


def _get_cache_dir() -> pathlib.Path:
    """
    Get the path to the cache dir. Will always be a sub-directory of the current user's home.
    """
    return pathlib.Path.home() / f".cache/license-manager"


def _get_token_path() -> pathlib.Path:
    """
    Get the path to the access token.
    """
    return _get_cache_dir() / "access_token"


def _load_token_from_cache() -> typing.Union[str, None]:
    """
    Looks for and returns a token from a cache file (if it exists).

    Returns None if::
    * The token does not exist
    * Can't read the token
    * The token is expired (or will expire within 10 seconds)
    """
    token_path = _get_token_path()
    if not token_path.exists():
        return None

    try:
        token = token_path.read_text()
    except Exception as err:
        logger.warning(f"Couldn't load token from cache file {token_path}. Will acquire a new one: {err}")
        return None

    try:
        jwt.decode(token, options=dict(verify_signature=False, verify_exp=True), leeway=-10)
    except jwt.ExpiredSignatureError:
        logger.warning("Cached token is expired. Will acquire a new one.")
        return None

    return token


def _write_token_to_cache(token: str):
    """
    Writes the token to the cache.
    """
    cache_dir = _get_cache_dir()
    if not cache_dir.exists():
        logger.debug("Attempting to create missing cache directory")
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as err:
            logger.warning(
                f"Couldn't create missing cache directory {cache_dir}. Token won't be saved: {err}"
            )
            return

    token_path = _get_token_path()
    try:
        token_path.touch(mode=0o600, exist_ok=True)
        token_path.write_text(token)
    except Exception as err:
        logger.warning(f"Couldn't save token to {token_path}: {err}")


def acquire_token() -> str:
    """
    Retrieves a token from Auth0 based on the app settings.
    """
    logger.debug("Attempting to use cached token")
    token = _load_token_from_cache()

    if token is None:
        logger.debug("Attempting to acquire token from Auth0")
        auth0_body = dict(
            audience=settings.AUTH0_AUDIENCE,
            client_id=settings.AUTH0_CLIENT_ID,
            client_secret=settings.AUTH0_CLIENT_SECRET,
            grant_type="client_credentials",
        )
        auth0_url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
        logger.debug(f"Posting Auth0 request to {auth0_url}")
        response = httpx.post(auth0_url, data=auth0_body)
        LicenseManagerAuthTokenError.require_condition(
            response.status_code == 200, f"Failed to get auth token from Auth0: {response.text}"
        )
        with LicenseManagerAuthTokenError.handle_errors("Malformed response payload from Auth0"):
            token = response.json()["access_token"]
        _write_token_to_cache(token)

    logger.debug("Successfully acquired auth token from Auth0")
    return token


class AsyncBackendClient(httpx.AsyncClient):
    """
    Extends the httpx.AsyncClient class with automatic token acquisition for requests.
    The token is acquired lazily on the first httpx request issued.

    This client should be used for most agent actions.
    """

    _token: typing.Optional[str]

    def __init__(self):
        self._token = None
        super().__init__(base_url=settings.BACKEND_BASE_URL, auth=self._inject_token)

    def _inject_token(self, request: httpx.Request) -> httpx.Request:
        if self._token is None:
            self._token = acquire_token()
        request.headers["authorization"] = f"Bearer {self._token}"
        return request


backend_client = AsyncBackendClient()


class SyncBackendClient(httpx.Client):
    """
    Extends the synchronous httpx.Client class with automatic token acquisition for requests.
    The token is acquired lazily on the first httpx request issued.

    This client should be used only for the CLI tools.
    """

    _token: typing.Optional[str]

    def __init__(self):
        self._token = None
        super().__init__(base_url=settings.BACKEND_BASE_URL, auth=self._inject_token)

    def _inject_token(self, request: httpx.Request) -> httpx.Request:
        if self._token is None:
            self._token = acquire_token()
        request.headers["authorization"] = f"Bearer {self._token}"
        return request


async def check_backend_health():
    """Hit the API's health-check endpoint to make sure the API is available."""
    resp = await backend_client.get("/lm/health")
    if resp.status_code != 204:
        logger.error("license-manager-backend health-check failed.")
        raise LicenseManagerBackendConnectionError("Could not connect to the backend health-check endpoint")


class BackendConfigurationRow(BaseModel):
    """
    NOTE: This is a copy of the schema from the backend.
          If the schema changes upstream in a non-reverse-compatible way, this schema should cause errors
          in deserialization.
    """

    class Config:
        extra = "ignore"

    id: typing.Optional[int] = None
    product: str
    features: dict
    license_servers: typing.List[str]
    license_server_type: str
    grace_time: int


class BackendBookingRow(BaseModel):
    """
    NOTE: This is a copy of the schema from the backend.
          If the schema changes upstream in a non-reverse-compatible
          way, this schema should cause errors in deserialization.
    """

    class Config:
        extra = "ignore"

    job_id: str
    product_feature: str
    booked: int
    config_id: int
    lead_host: str
    user_name: str
    cluster_name: str


async def get_bookings_from_backend(
    cluster_name: typing.Optional[str] = None,
) -> typing.List[BackendBookingRow]:
    bookings: typing.List = []
    try:
        if cluster_name:
            resp = await backend_client.get(f"/lm/api/v1/booking/all?cluster_name={cluster_name}")
        else:
            resp = await backend_client.get("/lm/api/v1/booking/all")
    except httpx.ConnectError as e:
        logger.error(f"Connection failed to backend: {e}")
        return bookings
    for booking in resp.json():
        try:
            bookings.append(BackendBookingRow.parse_obj(booking))
        except ValidationError as err:
            logger.error(f"Wrong format for booking: {str(err)}")
    return bookings


async def get_config_id_from_backend(product_feature: str) -> int:
    """Given the product_feature return return the config id."""
    path = "/lm/api/v1/config/"
    resp = await backend_client.get(path, params={"product_feature": product_feature})
    return resp.json()


async def get_config_from_backend() -> typing.List[BackendConfigurationRow]:
    """Get all config rows from the backend."""
    path = "/lm/api/v1/config/all"

    try:
        resp = await backend_client.get(path)
    except httpx.ConnectError as e:
        logger.error(f"Connection failed to backend: {backend_client.base_url}{path}: {e}")
        return []

    configs = []
    for (i, config_row) in enumerate(resp.json()):
        try:
            configs.append(BackendConfigurationRow.parse_obj(config_row))
        except ValidationError as err:
            logger.error(f"Could not validate config entry at row {i}: {str(err)}")
    return configs
