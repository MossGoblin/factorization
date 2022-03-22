import math
import pyprimes as pp
from typing import List


def get_prime_factors(value) -> List:
    prime_factors = []
    primes_below = list(pp.primes_below(int(value / 2)))
    number_body = value
    for prime in primes_below:
        if number_body == 1:
            break
        while number_body % prime == 0:
            prime_factors.append(prime)
            number_body = number_body / prime
    return prime_factors


def get_ideal_factor(value: int, prime_factors: List[int]) -> float:
    return math.pow(value, 1/len(prime_factors))


def get_mean_deviation(prime_factors: List[int], ideal_factor: float) -> float:
    deviations_sum = 0
    for prime_factor in prime_factors:
        deviations_sum += abs(prime_factor - ideal_factor)
    mean_deviation = deviations_sum / len(prime_factors)

    return mean_deviation
