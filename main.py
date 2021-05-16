from configparser import ConfigParser
from number import Number


config = ConfigParser()

config.read('config.ini')

lowerbound = int(config.get('setup', 'lowerbound'))
upperbound = int(config.get('setup', 'upperbound'))


# DBG test
# import lab
# pf = lab.get_prime_factors(24)


def run(lowerbound=2, upperbound=10):
    # [ ] iterate between bounds and cache numbers
    number_list = []
    for value in range(lowerbound, upperbound):
        number = Number(value=value)
        number_list.append(number)

    pass

if __name__ == "__main__":
    run(lowerbound=lowerbound, upperbound=upperbound)
