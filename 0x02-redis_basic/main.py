#!/usr/bin/env python3
"""Main file"""

from exercise import Cache, replay

cache = Cache()

cache.store(1)
cache.store(2)
cache.store(42)

replay(cache.store)
