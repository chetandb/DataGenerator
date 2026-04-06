import random
import string
from datetime import datetime, timedelta
import pytest

# Cached datetime for consistency and performance
CURRENT_DATETIME = datetime.now()
DATE_LIMIT = CURRENT_DATETIME - timedelta(days=1000)

# Function to generate data
def generate_data(data_type, num_rows=10):
    if data_type == "int":
        return [random.randint(1, 100) for _ in range(num_rows)]
    elif data_type == "string":
        return [''.join(random.choices(string.ascii_letters, k=10)) for _ in range(num_rows)]
    elif data_type == "date":
        return [(CURRENT_DATETIME - timedelta(days=random.randint(1, 1000))).strftime("%Y-%m-%d") for _ in range(num_rows)]
    else:
        raise ValueError("Unsupported data type")

# Model for testing
class DataGenerationModel:
    def __init__(self, data_type, num_rows=10):
        self.data_type = data_type
        self.num_rows = num_rows
        self.data = generate_data(data_type, num_rows)

    def validate(self):
        if self.data_type == "int":
            return all(1 <= item <= 100 for item in self.data)
        elif self.data_type == "string":
            return all(len(item) == 10 for item in self.data)
        elif self.data_type == "date":
            return all(datetime.strptime(item, "%Y-%m-%d") >= DATE_LIMIT for item in self.data)
        else:
            raise ValueError("Unsupported data type")

# Pytest-based model tests
@pytest.mark.parametrize("data_type,num_rows", [
    ("int", 100),
    ("string", 50),
    ("date", 30),
])
def test_data_generation(data_type, num_rows):
    model = DataGenerationModel(data_type, num_rows)
    assert model.validate(), f"Validation failed for data type {data_type}"

# Example of running the test
if __name__ == "__main__":
    pytest.main([__file__])
