from redis import asyncio as aioredis
from src.config import Config

JTI_EXPIRY = 3600

token_blocklist = aioredis.Redis(
    host = Config.REDIS_HOST,
    port= Config.REDIS_PORT,
    db=0,
    decode_responses=True # Ensures keys and values are returned as strings
)

# Function to add a token to our blocklist 
async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(
        name=jti,
        value="",
        ex=JTI_EXPIRY
    )

# Function to check if a token is in our blocklist
async def token_in_blocklist(jti: str) -> bool:
    # The new library returns strings (due to decode_responses=True) or None
    redis_result = await token_blocklist.get(jti)

    return redis_result is not None 