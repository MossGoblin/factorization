import numpy as np
from py import process
import pyprimes as pp
from typing import List
from number import Number





def generate_continuous_number_list(lowerbound: int, upperbound: int, include_primes: bool):
    lowerbound = lowerbound
    upperbound = upperbound
    if lowerbound < 2:
        lowerbound = 2
    number_list = []
    for value in range(lowerbound, upperbound + 1):
        if pp.isprime(value) and not include_primes:
            continue
        number = Number(value=value)
        number_list.append(number)
    return number_list

def generate_number_families(families: List, include_all_identities: bool, family_count):
    processed_numbers = []
    for family in families:
        family_product = np.prod(family)
        identity_factors = []
        if include_all_identities:
            identity_factors_lower_bound = family[-1]
        else:
            identity_factors_lower_bound = 2
        # identity_factors.append(first_identity_factor)
        identity_factors.extend(get_primes_between(identity_factors_lower_bound, family_count-1))
        for identity_factor in identity_factors:
            number_value = int(family_product) * identity_factor
            try:
                number = Number(number_value)
            except Exception as e:
                print(number_value)
                raise e
            processed_numbers.append(number)
    return processed_numbers

def get_primes_between(previous: int, total_count: int):
    primes = []
    prime_generator = pp.primes_above(previous)
    for count in range(total_count):
        primes.append(next(prime_generator))
    return primes