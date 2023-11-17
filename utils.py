import math
from typing import List
import pyprimes as pp
import numpy as np


class Number():

    def __init__(self, value):
        self.value = value
        self.is_prime = pp.isprime(self.value)
        if self.value == 1:
            self.ideal_factor = 0
            self.prime_factors = []
            self.mean_deviation = 0
            self.anti_slope = 0
        else:
            self.prime_factors = []
            if self.is_prime:
                self.prime_factors.append(self.value)
            else:
                self.prime_factors = pp.factors(self.value)
            self.ideal_factor = self.get_ideal_factor(
                self.value, self.prime_factors)
            self.mean_deviation = self.get_mean_deviation(
                self.prime_factors, self.ideal_factor)
            if self.mean_deviation > 0:
                self.anti_slope = self.value / self.mean_deviation
            else:
                self.anti_slope = 0

    def __str__(self):
        str = f'value: {self.value} :: '
        str = str + \
            f':: factors: [{self.prime_factors[:-1]}] {self.prime_factors[-1]}'
        str = str + f' > ideal factor: {self.ideal_factor}'
        str = str + f' > mean deviation: {self.mean_deviation}'
        str = str + f' > antislope: {self.anti_slope}'
        return str

    def __repr__(self):
        repr = f'{self.value} ({self.prime_factors[:-1]} {self.prime_factors[-1]})'
        return repr

    def get_ideal_factor(self, value: int, prime_factors: List[int]) -> float:
        return math.pow(value, 1/len(prime_factors))

    def get_mean_deviation(self, prime_factors: List[int], ideal_factor: float) -> float:
        deviations_sum = 0
        for prime_factor in prime_factors:
            deviations_sum += abs(prime_factor - ideal_factor)
        mean_deviation = deviations_sum / len(prime_factors)

        return mean_deviation


class ToolBox():
    def __init__(self, logger, config) -> None:
        self.logger = logger
        self.cfg = config


    def generate_number_list(self):
        self.logger.info('Generating numbers')
        if self.cfg.set.mode == 'family':
            self.logger.debug('Processing families')
            number_list = self.generate_number_families()
        elif self.cfg.set.mode == 'range':
            self.logger.debug('Processing range')
            number_list = self.generate_continuous_number_list()
        else:
            self.logger.debug('Processing file')
        print('NYI')
        return number_list

    def generate_continuous_number_list(self):
        lowerbound = self.cfg.set.range_min
        upperbound = self.cfg.set.range_max
        if lowerbound < 2:
            lowerbound = 2
        number_list = []
        for value in range(lowerbound, upperbound + 1):
            if pp.isprime(value) and not self.cfg.set.include_primes:
                continue
            number_list.append(value)
        return number_list

    def generate_number_families(self):
        processed_numbers = []
        for family in self.cfg.set.families:
            # order family
            family = sorted(family)
            family_product = np.prod(family)
            if self.cfg.set.identity_factor_mode == 'count':
                if self.cfg.set.identity_factor_minimum_mode == 'family':
                    largest_family_factor = family[-1]
                    larger_primes = pp.primes_above(largest_family_factor)
                    first_identity_factor = next(larger_primes)
                elif self.cfg.set.identity_factor_minimum_mode == 'origin':
                    first_identity_factor = 2
                else:
                    first_identity_factor = self.cfg.set.identity_factor_minimum_value
                number_of_composites = self.cfg.set.identity_factor_count
            else:
                first_identity_factor = self.cfg.set.identity_factor_range_min
                number_of_composites = pp.prime_count(self.cfg.set.identity_factor_range_max) - pp.prime_count(self.cfg.set.identity_factor_range_min)
            # iterate identity factors
            processed_numbers.append(family_product * first_identity_factor)
            prime_generator = pp.primes_above(first_identity_factor)
            for count in range(number_of_composites):
                processed_numbers.append(family_product * next(prime_generator))

        return processed_numbers

    def get_primes_between(self, previous: int, total_count: int):
        primes = []
        prime_generator = pp.primes_above(previous)
        for count in range(total_count):
            primes.append(next(prime_generator))
        return primes