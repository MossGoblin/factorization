import lab


class Number():

    def __init__(self, value):
        self.value = value
        self.is_prime = lab.pp.isprime(value)
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
                self.prime_factors = lab.get_prime_factors(self.value)
            self.ideal_factor = lab.get_ideal_factor(self.value, self.prime_factors)
            self.mean_deviation = lab.get_mean_deviation(
                self.prime_factors, self.ideal_factor)
            if self.mean_deviation > 0:
                self.anti_slope = self.value / self.mean_deviation
            else:
                self.anti_slope = 0