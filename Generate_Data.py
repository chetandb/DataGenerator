import csv
import random
import string
import pandas as pd
import uuid
from datetime import datetime, timedelta
from constants import DOMAINS

# Function to generate random data based on data type
def generate_data(data_type, num_rows=10, current_time=None, seed=None, random_instance=None):
    # Validate num_rows
    if not isinstance(num_rows, int) or num_rows < 0:
        raise ValueError(f"num_rows must be a non-negative integer, got {num_rows}")
    
    # Explicit handling for num_rows == 0
    if num_rows == 0:
        return []
    
    if current_time is None:
        current_time = datetime.now()
    
    # Setup random instance for reproducibility
    if random_instance is not None:
        rng = random_instance
    elif seed is not None:
        rng = random.Random(seed)
    else:
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
        return [str(uuid.uuid4()) for _ in range(num_rows)]
    else:
        supported_types = ["int", "string", "float", "date", "bool", "email", "timestamp", "uuid"]
        raise ValueError(f"Unsupported data type '{data_type}'. Supported types: {', '.join(supported_types)}")

# Function to read CSV and generate data
def generate_test_data(csv_file, output_file='output.csv', num_rows=10, current_time=None, seed=None, random_instance=None):
    if current_time is None:
        current_time = datetime.now()
    
    columns = []
    data = {}

    # Reading the CSV file
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            column_name = row['column_name']
            data_type = row['data_type']
            columns.append(column_name)
            data[column_name] = generate_data(data_type, num_rows, current_time, seed, random_instance)

    # Creating a DataFrame and writing to a CSV file
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"Generated test data saved to {output_file}")

# Example usage
generate_test_data('columns.csv')
