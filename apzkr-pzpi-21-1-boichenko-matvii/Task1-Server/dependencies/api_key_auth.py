import hashlib
import os

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

from config import settings
from common.error_messages import ErrorMessages


def generate_api_key(salt: str = None) -> str:
    """
    :param salt: string data to use as salt for hashing, by default 16 length bytes is generated
    :return: string key in the form of {hash}.{salt_hex}
    """
    if not salt:
        salt = os.urandom(16)
    else:
        salt = salt.encode()

    secret_key = settings.API_HASH_SECRET_KEY
    combined = salt + secret_key.encode()
    hash_output = hashlib.sha256(combined).hexdigest()
    return f"{hash_output}.{salt.hex()}"


def verify_string(str_to_verify: str, secret_key: str) -> bool:
    """
    :param str_to_verify: string to verify
    :param secret_key: string used as a secret to encrypt key_to_verify
    :return:
    """
    strs = str_to_verify.split(".")
    if len(strs) != 2:
        return False

    hash_, salt = strs
    decoded_salt = bytes.fromhex(salt)
    combined = decoded_salt + secret_key.encode()
    new_hash = hashlib.sha256(combined).hexdigest()
    return new_hash == hash_


# dependency uses regular
async def verify_api_key(request: Request) -> str:
    """
    Dependency uses regular declaration, must be used with Depends()
    """
    key_to_verify = request.headers.get("X-Api-Key", "")
    secret_key = settings.API_HASH_SECRET_KEY

    if not verify_string(key_to_verify, secret_key):
        raise HTTPException(status_code=401, detail=ErrorMessages.Auth.INVALID_API_KEY)

    return key_to_verify  # Or return True or any other relevant data


api_key_header = APIKeyHeader(name="X-Api-Key", auto_error=True,
                              description="Api key header for mqtt-handlers endpoints")


async def get_api_key(api_key_header: str = Security(api_key_header)):
    """
    Dependency uses FastApi Security declaration, must be used with Security()
    """
    secret_key = settings.API_HASH_SECRET_KEY

    if not verify_string(api_key_header, secret_key):
        raise HTTPException(status_code=401, detail=ErrorMessages.Auth.INVALID_API_KEY)

    return api_key_header
