#!/usr/bin/env python3
"""Test web cache"""

from web import get_page, redis_client
import time

url = "http://slowwly.robertomurray.co.uk/delay/3000/url/http://example.com"

# First call - fetch from web
print("Fetching...")
html1 = get_page(url)
print(html1[:100])

# Second call (within 10s) - should use cache
print("\nFetching again quickly...")
html2 = get_page(url)
print(html2[:100])

# Check access count
count = redis_client.get(f"count:{url}")
print(f"\nURL accessed {int(count)} times.")

# Wait for cache to expire
print("\nWaiting 11 seconds for cache to expire...")
time.sleep(11)

# Fetch again - should fetch fresh content
print("Fetching after cache expiry...")
html3 = get_page(url)
print(html3[:100])

# Updated count
count = redis_client.get(f"count:{url}")
print(f"\nURL accessed {int(count)} times.")
