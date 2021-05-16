import pyprimes as pp
from typing import List


class Number():

    def __init__(self, value):
        self.value = value
        self.is_prime = pp.isprime(value)
        self.prime_factors = []
        if self.is_prime:
            self.prime_factors.append(self.value)
        else:
            self.prime_factors = self.get_prime_factors()
        self.prime_mean = self.get_prime_mean()
        self.mean_deviation = self.get_mean_deviation()

    def get_prime_factors(self) -> List:
        prime_factors = []
        primes_below = list(pp.primes_below(int(self.value / 2)))
        number_body = self.value
        for prime in primes_below:
            if number_body == 1:
                break
            while number_body % prime == 0:
                prime_factors.append(prime)
                number_body = number_body / prime

        return prime_factors

    def get_prime_mean(self) -> float:
        prime_sum = 0
        for prime_factor in self.prime_factors:
            prime_sum += prime_factor
        prime_mean = prime_sum / len(self.prime_factors)

        return prime_mean

    def get_mean_deviation(self) -> float:
        deviations_sum = 0
        for prime_factor in self.prime_factors:
            deviations_sum += abs(prime_factor - self.prime_mean)
        mean_deviation = deviations_sum / len(self.prime_factors)
        
        return mean_deviation
