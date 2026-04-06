import time
import random
import string
import uuid
from datetime import datetime, timedelta
from datagenerator.constants import DOMAINS

"""
Random Number Generation Strategy:
- Default (no seed, no random_instance): Uses global random module (stateful, non-deterministic)
- With seed: Creates isolated Random(seed) instance (deterministic, reproducible)
- With random_instance: Uses provided Random object (full control over RNG state)

UUID Generation:
- UUID generation is intentionally non-deterministic (uses uuid.uuid4() by default)
- To control UUID generation, pass a custom uuid_generator function
- Example: uuid_generator=lambda: str(uuid.uuid4())  # or any custom generator

Use seed parameter for reproducible performance test data generation.
Use random_instance parameter for advanced control or when coordinating RNG state across multiple calls.
Use uuid_generator parameter to customize UUID generation or make it deterministic in tests.
"""

# Function to generate random data based on data type
def generate_data(data_type, num_rows=10, current_time=None, seed=None, random_instance=None, uuid_generator=None):
    # Validate num_rows
    if not isinstance(num_rows, int) or num_rows < 0:
        raise ValueError(f"num_rows must be a non-negative integer, got {num_rows}")
    
    # Explicit handling for num_rows == 0
    if num_rows == 0:
        return []
    
    if current_time is None:
        current_time = datetime.now()
    
    # Setup random instance for reproducibility
    # Priority: random_instance > seed > default random module
    if random_instance is not None:
        # Use provided custom Random instance
        rng = random_instance
    elif seed is not None:
        # Create a new Random instance with specified seed for deterministic output
        rng = random.Random(seed)
    else:
        # Use global random module (stateful, non-deterministic across calls)
        # This uses Python's standard random module which maintains global state
        rng = random
    
    if data_type == "int":
        return [rng.randint(1, 100) for _ in range(num_rows)]
    elif data_type == "string":
        return [''.join(rng.choices(string.ascii_letters, k=10)) for _ in range(num_rows)]
    elif data_type == "float":
        return [round(rng.uniform(1000.00, 5000.00), 2) for _ in range(num_rows)]
    elif data_type == "date":
        return [(current_time - timedelta(days=rng.randint(1, 1000))).strftime("%Y-%m-%d") for _ in
                range(num_rows)]
    elif data_type == "bool":
        return [rng.choice([True, False]) for _ in range(num_rows)]
    elif data_type == "email":
        return [f"{''.join(rng.choices(string.ascii_lowercase, k=5))}@{rng.choice(DOMAINS)}" for _ in
                range(num_rows)]
    elif data_type == "timestamp":
        return [(current_time - timedelta(seconds=rng.randint(1, 1000000))).strftime("%Y-%m-%d %H:%M:%S") for _ in
                range(num_rows)]
    elif data_type == "uuid":
        # Use custom UUID generator if provided, otherwise use uuid.uuid4()
        gen = uuid_generator if uuid_generator is not None else uuid.uuid4
        return [str(gen()) for _ in range(num_rows)]
    else:
        supported_types = ["int", "string", "float", "date", "bool", "email", "timestamp", "uuid"]
        raise ValueError(f"Unsupported data type '{data_type}'. Supported types: {', '.join(supported_types)}")


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
