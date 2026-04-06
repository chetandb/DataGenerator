import csv
import random
import string
import pandas as pd
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

Use seed parameter for reproducible test data generation.
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
        return [(current_time - timedelta(days=rng.randint(1, 1000))).strftime("%Y-%m-%d") for _ in range(num_rows)]
    elif data_type == "bool":
        return [rng.choice([True, False]) for _ in range(num_rows)]
    elif data_type == "email":
        return [f"{''.join(rng.choices(string.ascii_lowercase, k=5))}@{rng.choice(DOMAINS)}" for _ in range(num_rows)]
    elif data_type == "timestamp":
        return [(current_time - timedelta(seconds=rng.randint(1, 1000000))).strftime("%Y-%m-%d %H:%M:%S") for _ in range(num_rows)]
    elif data_type == "uuid":
        # Use custom UUID generator if provided, otherwise use uuid.uuid4()
        gen = uuid_generator if uuid_generator is not None else uuid.uuid4
        return [str(gen()) for _ in range(num_rows)]
    else:
        supported_types = ["int", "string", "float", "date", "bool", "email", "timestamp", "uuid"]
        raise ValueError(f"Unsupported data type '{data_type}'. Supported types: {', '.join(supported_types)}")

# Function to read CSV and generate data
def generate_test_data(csv_file, output_file='output.csv', num_rows=10, current_time=None, seed=None, random_instance=None, uuid_generator=None):
    if current_time is None:
        current_time = datetime.now()
    
    columns = []
    data = {}

    # Reading the CSV file
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
            column_name = row['column_name']
            data_type = row['data_type']
            columns.append(column_name)
            
            try:
                data[column_name] = generate_data(data_type, num_rows, current_time, seed, random_instance, uuid_generator)
            except ValueError as e:
                # Provide descriptive error with CSV context
                error_msg = (
                    f"Error processing CSV file '{csv_file}' at row {row_num}:\n"
                    f"  Column: '{column_name}'\n"
                    f"  Data Type: '{data_type}'\n"
                    f"  Error: {str(e)}"
                )
                raise ValueError(error_msg) from e

    # Creating a DataFrame and writing to a CSV file
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"Generated test data saved to {output_file}")

# Example usage
generate_test_data('columns.csv')
