import csv
import random
import string
import pandas as pd
from datetime import datetime, timedelta

# Function to generate random data based on data type
def generate_data(data_type, num_rows=100000):
    if data_type == "int":
        return [random.randint(1, 100) for _ in range(num_rows)]
    elif data_type == "string":
        return [''.join(random.choices(string.ascii_letters, k=5)) for _ in range(num_rows)]
    elif data_type == "float":
        return [round(random.uniform(1000.00, 5000.00), 2) for _ in range(num_rows)]
    elif data_type == "date":
        return [(datetime.now() - timedelta(days=random.randint(1, 1000))).strftime("%Y-%m-%d") for _ in range(num_rows)]
    else:
        return [None] * num_rows

# Function to read CSV and generate data
def generate_test_data(csv_file, output_file='output.csv', num_rows=100000):
    columns = []
    data = {}

    # Reading the CSV file
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            column_name = row['column_name']
            data_type = row['data_type']
            columns.append(column_name)
            data[column_name] = generate_data(data_type, num_rows)

    # Creating a DataFrame and writing to a CSV file
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"Generated test data saved to {output_file}")

# Example usage
generate_test_data('columns.csv')
