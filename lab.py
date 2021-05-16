import pyprimes as pp
from typing import List


def get_prime_factors(value) -> List:
    # [...] retork
    prime_factors = []
    primes_below = list(pp.primes_below(value))
    number_body = value
    for prime in primes_below:
        if number_body == 1:
            break
        while number_body % prime == 0:
            prime_factors.append(prime)
            number_body = number_body / prime
    return prime_factors