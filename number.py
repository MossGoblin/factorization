import lab


class Number():

    def __init__(self, value):
        self.value = value
        self.is_prime = lab.pp.isprime(value)
        self.prime_factors = []
        if self.is_prime:
            self.prime_factors.append(self.value)
        else:
            self.prime_factors = lab.get_prime_factors(self.value)
        self.prime_mean = lab.get_prime_mean(self.prime_factors)
        self.mean_deviation = lab.get_mean_deviation(
            self.prime_factors, self.prime_mean)
