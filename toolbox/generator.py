import math
import multiprocessing
from datetime import datetime
from multiprocessing import Process, Queue

import pandas as pd
import pyprimes as pp


class Decomposer(Process):
    def __init__(self, queue, value_list):
        Process.__init__(self)
        self.queue = queue
        self.value_list = value_list
    
    def get_ideal_factor(self, value: int, prime_factors: list[int]) -> float:
        return math.pow(value, 1/len(prime_factors))

    def get_mean_deviation(self, prime_factors: list[int], ideal_factor: float) -> float:
        if all(x == prime_factors[0] for x in prime_factors):
            return 0.0
        deviations_sum = 0
        for prime_factor in prime_factors:
            deviations_sum += abs(prime_factor - ideal_factor)
        mean_deviation = deviations_sum / len(prime_factors)

        return mean_deviation

    def run(self):
        updated_collection = []
        for value in self.value_list:
            new_record = {}
            new_record['value'] = value
            new_record['is_prime'] = pp.isprime(int(value))
            if new_record['value'] == 1:
                new_record['ideal_factor'] = 0
                new_record['prime_factors'] = []
                new_record['mean_deviation'] = 0
                new_record['antislope'] = 0
                new_record['division_family'] = 1
            else:
                new_record['prime_factors'] = []
                if new_record['is_prime']:
                    new_record['prime_factors'].append(new_record['value'])
                else:
                    new_record['prime_factors'] = pp.factors(new_record['value'])
                new_record['ideal_factor'] = self.get_ideal_factor(
                    new_record['value'], new_record['prime_factors'])
                new_record['mean_deviation'] = self.get_mean_deviation(
                    new_record['prime_factors'], new_record['ideal_factor'])
                if new_record['mean_deviation'] > 0:
                    new_record['antislope'] = new_record['value'] / new_record['mean_deviation']
                else:
                    new_record['antislope'] = 0
                new_record['division_family'] = math.prod(new_record['prime_factors'][:-1])
            updated_collection.append(new_record)
        self.queue.put(updated_collection)


def decompose(logger, values_list):
    logger.info('Decomposing')
    step_start = datetime.utcnow()
    decomposers = []
    composites_queue = Queue()
    cpu_count = multiprocessing.cpu_count()
    process_count = cpu_count

    # TEST
    # process_count = 1
    logger.debug(f'{process_count} decomposers employed')
    chunk_size = len(values_list) / max(1, (process_count - 1))
    for counter in range(process_count):
        start_index = int(counter * chunk_size)
        end_index = int(min((counter + 1) * chunk_size, len(values_list)))
        chunk = values_list[start_index: end_index]
        decomposers.append(Decomposer(queue=composites_queue, value_list=chunk))

    for decomposer in decomposers:
        decomposer.start()

    composites_collection = []
    decomposer_process_count = process_count
    while decomposer_process_count > 0:
        result = composites_queue.get()
        composites_collection.extend(result)
        decomposer_process_count -= 1
    step_end = datetime.utcnow()
    logger.debug(f'...done in {step_end-step_start}')

    collection_df = pd.DataFrame.from_dict(composites_collection)
    return collection_df
