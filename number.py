from decimal import Decimal

import lab


class Number():

    def __init__(self, value, division_family=1, calculate_division_family=False):
        self.value = value
        self.is_prime = lab.pp.isprime(value)
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
            self.division_family = division_family
            if self.is_prime:
                self.prime_factors.append(self.value)
                if calculate_division_family:
                    self.division_family = self.value
            else:
                self.prime_factors = lab.get_prime_factors(self.value)
                if calculate_division_family:
                    self.division_family = lab.get_division_family(self.value)
            self.prime_mean = lab.get_prime_mean(self.prime_factors)
            self.mean_deviation = lab.get_mean_deviation(self.prime_factors, self.prime_mean)
            if self.mean_deviation > 0:
                self.antislope = Decimal(self.value) / Decimal(self.mean_deviation)
                self.antislope_string = str(self.antislope)
            else:
                self.antislope = 0
                self.antislope_string = "0"
