import os
from dotenv import load_dotenv, find_dotenv
import jwt
from typing import Optional


def load_env():
    env_path = find_dotenv(usecwd=True)
    if env_path:
        load_dotenv(env_path)


class JWTService:
    def __init__(self):
        load_env()
        self.secret = os.getenv('JWT_SECRET_KEY') or os.getenv('JWT_SECRET')
        if not self.secret:
            raise RuntimeError('JWT_SECRET_KEY or JWT_SECRET not set in environment')

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[os.getenv('JWT_ALGORITHM', 'HS256')])
            return payload
        except jwt.InvalidTokenError:
            return None
