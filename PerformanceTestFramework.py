import time
import random
import string
import uuid
from datetime import datetime, timedelta


# Function to generate random data based on data type
def generate_data(data_type, num_rows=10):
    if data_type == "int":
        return [random.randint(1, 100) for _ in range(num_rows)]
    elif data_type == "string":
        return [''.join(random.choices(string.ascii_letters, k=10)) for _ in range(num_rows)]
    elif data_type == "float":
        return [round(random.uniform(1000.00, 5000.00), 2) for _ in range(num_rows)]
    elif data_type == "date":
        return [(datetime.now() - timedelta(days=random.randint(1, 1000))).strftime("%Y-%m-%d") for _ in
                range(num_rows)]
    elif data_type == "bool":
        return [random.choice([True, False]) for _ in range(num_rows)]
    elif data_type == "email":
        domains = ["example.com", "test.com", "mail.com"]
        return [f"{''.join(random.choices(string.ascii_lowercase, k=5))}@{random.choice(domains)}" for _ in
                range(num_rows)]
    elif data_type == "timestamp":
        return [(datetime.now() - timedelta(seconds=random.randint(1, 1000000))).strftime("%Y-%m-%d %H:%M:%S") for _ in
                range(num_rows)]
    elif data_type == "uuid":
        return [str(uuid.uuid4()) for _ in range(num_rows)]
    else:
        return [None] * num_rows


# Performance testing class
class PerformanceTest:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def time_execution(self):
        start_time = time.time()
        self.func(*self.args, **self.kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"Time taken to execute {self.func.__name__}: {duration:.4f} seconds")
        return duration

    def run_all(self):
        print(f"Running performance test for {self.func.__name__}")
        duration = self.time_execution()
        return duration


# Example usage
if __name__ == "__main__":
    # Test the performance of generating 100,000 rows of integer data
    test = PerformanceTest(generate_data, 'int', num_rows=100000)
    test.run_all()

    # Test the performance of generating 50,000 rows of string data
    test = PerformanceTest(generate_data, 'string', num_rows=50000)
    test.run_all()

    # Test the performance of generating 10,000 rows of UUID data
    test = PerformanceTest(generate_data, 'uuid', num_rows=10000)
    test.run_all()
