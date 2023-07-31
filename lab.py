import math
import pyprimes as pp
from typing import List


def get_prime_factors(value) -> List:
    prime_factors = []
    primes_below = list(pp.primes_below(math.floor(value/2)))
    number_body = value
    for prime in primes_below:
        if number_body == 1:
            break
        while number_body % prime == 0:
            prime_factors.append(prime)
            number_body = number_body / prime
    return prime_factors


def get_division_family(value) -> int:
    division_family = 1
    primes_below = list(pp.primes_below(math.floor(value/2)))
    primes_below.sort(reverse=True)
    for prime in primes_below:
        if value % prime == 0:
            division_family = value / prime
            break
    return division_family


def get_prime_mean(prime_factors: List[int]) -> float:
    prime_sum = 0
    for prime_factor in prime_factors:
        prime_sum += prime_factor
    prime_mean = prime_sum / len(prime_factors)
    return prime_mean


def get_mean_deviation(prime_factors: List[int], prime_mean: float) -> float:
    deviations_sum = 0
    for prime_factor in prime_factors:
        deviations_sum += abs(prime_factor - prime_mean)
    mean_deviation = deviations_sum / len(prime_factors)

    return mean_deviation
