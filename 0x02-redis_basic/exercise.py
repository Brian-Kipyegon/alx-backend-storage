#!/usr/bin/env python3
"""Redis basic exercise module"""

import redis
import uuid
from typing import Union
from typing import Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator that counts how many times a method is called.

    Args:
        method: The method to wrap.

    Returns:
        A wrapped method that increments call count in Redis.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator that stores the history of inputs and outputs for a method.

    Args:
        method: The method to wrap.

    Returns:
        A wrapped method that stores input/output history in Redis.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Save the input as a string
        self._redis.rpush(input_key, str(args))

        # Call the original method
        result = method(self, *args, **kwargs)

        # Save the output
        self._redis.rpush(output_key, str(result))
        return result

    return wrapper


def replay(method: Callable) -> None:
    """
    Display the history of calls of a particular function.

    Args:
        method: The function whose history to display.
    """
    r = method.__self__._redis
    qualname = method.__qualname__

    inputs = r.lrange(f"{qualname}:inputs", 0, -1)
    outputs = r.lrange(f"{qualname}:outputs", 0, -1)
    count = r.get(qualname)
    count_int = int(count.decode("utf-8")) if count else 0

    print(f"{qualname} was called {count_int} times:")

    for i, (i_args, o_val) in enumerate(zip(inputs, outputs), 1):
        print(f"{qualname}(*{i_args.decode('utf-8')}) -> {o_val.decode('utf-8')}")


class Cache:
    """Cache class to interact with Redis."""

    def __init__(self):
        """Initialize the Redis connection and flush the database."""
        self._redis = redis.Redis(
            host="172.29.232.142", port=6379, decode_responses=True
        )
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the given data in Redis under a random key.

        Args:
            data: The data to store.

        Returns:
            The Redis key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
        self, key: str, fn: Optional[Callable] = None
    ) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally convert it using `fn`.

        Args:
            key: Redis key to retrieve.
            fn: Optional function to convert the returned data.

        Returns:
            The retrieved data, optionally converted.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a UTF-8 decoded string from Redis.

        Args:
            key: Redis key to retrieve.

        Returns:
            The decoded string if key exists, otherwise None.
        """
        return self.get(key, lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer value from Redis.

        Args:
            key: Redis key to retrieve.

        Returns:
            The integer value if key exists, otherwise None.
        """
        return self.get(key, int)
