import logging
import uuid
from datetime import datetime, timedelta, timezone


import jwt
from passlib.context import CryptContext

from src.config import Config

passwd_context = CryptContext(schemes=["bcrypt"])


ACCESS_TOKEN_EXPIRY_SECONDS = 3600  # 1 hour
REFRESH_TOKEN_EXPIRY_DAYS = 7  # 7 days


def generate_passwd_hash(password: str) -> str:
    hash = passwd_context.hash(password)

    return hash


def verify_password(password: str, hash: str) -> bool:
    return passwd_context.verify(password, hash)


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    payload = {}
    token_type = "refresh" if refresh else "access"

    payload["user"] = user_data
    default_expiry = timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS) if refresh else timedelta(seconds=ACCESS_TOKEN_EXPIRY_SECONDS)
    payload["exp"] = datetime.now(timezone.utc) + (expiry if expiry is not None else default_expiry)
    payload["jti"] = str(uuid.uuid4())

    payload["type"] = token_type

    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )

        return token_data

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None