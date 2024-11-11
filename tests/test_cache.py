import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import time
from enma.infra.core.utils.cache import Cache

def test_cache_decorator():
    # Create an instance of the Cache class
    cache = Cache(max_age_seconds=10, max_size=5)

    class Fibonacci:
        @cache.cache
        def fibonacci(self, n):
            if n <= 1:
                return n
            else:
                return self.fibonacci(n-1) + self.fibonacci(n-2)

    fib = Fibonacci()
    # Call the fibonacci function multiple times with the same arguments
    result1 = fib.fibonacci(5)
    result2 = fib.fibonacci(5)
    result3 = fib.fibonacci(5)

    # Assert that the function is only executed once and the cached result is returned
    assert result1 == result2 == result3

    assert cache._CACHE.get(str([5])) == result1

    # Call the fibonacci function with a different argument
    result4 = fib.fibonacci(10)

    # Assert that a new execution is performed and the result is cached
    assert result4 == 55
    assert cache._CACHE.get(str([10])) == result4

def test_cache_expiration():
    # Create an instance of the Cache class with a short expiration time
    cache = Cache(max_age_seconds=2, max_size=5)

    @cache.cache
    def get_current_time():
        return time.time()

    # Call the function to cache its result
    result1 = get_current_time()

    # Wait for the cache entry to expire
    time.sleep(3)

    # Call the function again and expect a different result due to cache expiration
    result2 = get_current_time()

    assert result1 != result2, "Cache did not expire as expected."

def test_cache_with_various_argument_types():
    cache = Cache(max_age_seconds=2, max_size=5)

    class Sut:
        @cache.cache
        def concat_elements(self, *args):
            return ''.join(map(str, args))

    sut = Sut()
    # Test with string arguments
    assert sut.concat_elements("hello", "world") == "helloworld"
    assert sut.concat_elements("hello", "world") == "helloworld"  # Cached result

    # Test with a mix of types
    assert sut.concat_elements("number", 123, (1, 2, 3)) == "number123(1, 2, 3)"
    assert sut.concat_elements("number", 123, (1, 2, 3)) == "number123(1, 2, 3)"  # Cached result

def test_cache_function_no_arguments():
    call_count = 0
    cache = Cache(max_age_seconds=2, max_size=5, enabled='enabled')

    class Sut:
        @cache.cache
        def get_fixed_value(self):
            nonlocal call_count
            call_count += 1
            return 42
        
    sut = Sut()

    assert sut.get_fixed_value() == 42  # First call, cache miss
    assert sut.get_fixed_value() == 42  # Second call, should hit cache
    assert call_count == 1, "Function was called more than once, indicating a cache miss"
