import math
from decimal import Decimal
from typing import List

import pyprimes as pp


class Number():

    def __init__(self, value, division_family, calculate_division_family=False):
        self.value = int(value)
        self.is_prime = pp.isprime(value)
        if self.value == 1:
            self.prime_mean = 0
            self.prime_factors = []
            self.division_family = 1
            self.prime_mean = 0
            self.mean_deviation = 0
            self.antislope = 0
            self.antislope_string = "0"
        else:
            self.prime_factors = []
            if calculate_division_family:
                self.division_family = self._get_division_family(self.value)
            else:
                self.division_family = division_family
            if self.is_prime:
                self.prime_factors.append(self.value)
                self.division_family = self.value
            else:
                self.prime_factors = self._get_prime_factors(self.value)
            self.prime_mean = self._get_prime_mean(self.prime_factors)
            self.mean_deviation = self._get_mean_deviation(self.prime_factors, self.prime_mean)
            if self.mean_deviation > 0:
                self.antislope = Decimal(self.value) / Decimal(self.mean_deviation)
                self.antislope_string = str(self.antislope)
            else:
                self.antislope = 0
                self.antislope_string = "0"


    def _get_division_family(self, value) -> int:
        division_family = self.get_division_family(value)
        return division_family

    def _get_mean_deviation(self, prime_factors: List[int], prime_mean: float) -> float:
        mean_deviation = self.get_mean_deviation(prime_factors, prime_mean)
        return mean_deviation

    def _get_prime_mean(self, prime_factors: List[int]) -> float:
        prime_mean = self.get_prime_mean(prime_factors)
        return prime_mean

    def _get_prime_factors(self, value) -> List:
        prime_factors = self.get_prime_factors(value)
        return prime_factors

    @staticmethod
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

    @staticmethod
    def get_prime_mean(prime_factors: List[int]) -> float:
        prime_sum = 0
        for prime_factor in prime_factors:
            prime_sum += prime_factor
        prime_mean = prime_sum / len(prime_factors)

        return prime_mean
    
    @staticmethod
    def get_mean_deviation(prime_factors: List[int], prime_mean: float) -> float:
        deviations_sum = 0
        for prime_factor in prime_factors:
            deviations_sum += abs(prime_factor - prime_mean)
        mean_deviation = deviations_sum / len(prime_factors)

        return mean_deviation

    @staticmethod
    def get_division_family(value) -> int:
        division_family = 1
        primes_below = list(pp.primes_below(math.floor(value/2)))
        primes_below.sort(reverse=True)
        for prime in primes_below:
            if value % prime == 0:
                division_family = value / prime
                break

        return division_family
