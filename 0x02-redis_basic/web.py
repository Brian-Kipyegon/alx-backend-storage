#!/usr/bin/env python3
"""
Web caching and tracker module using Redis
"""

import redis
import requests
from typing import Callable
from functools import wraps


# Connect to Redis
redis_client = redis.Redis(host="172.29.232.142", port=6379, decode_responses=False)


def count_url_access(fn: Callable) -> Callable:
    """
    Decorator to count URL access in Redis.
    Increments "count:{url}" key.
    """

    @wraps(fn)
    def wrapper(url: str) -> str:
        redis_client.incr(f"count:{url}")
        return fn(url)

    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """
    Get and cache a web page. Cached content lasts 10 seconds.
    If the content is cached, return it directly.
    Otherwise, fetch from the web and cache it.

    Args:
        url (str): The URL to fetch

    Returns:
        str: The HTML content of the page
    """
    cached_key = f"cached:{url}"
    cached_data = redis_client.get(cached_key)

    if cached_data:
        return cached_data.decode("utf-8")

    response = requests.get(url)
    html = response.text

    redis_client.setex(cached_key, 10, html)
    return html
