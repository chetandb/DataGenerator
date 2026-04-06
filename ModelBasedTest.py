import random
import string
from datetime import datetime, timedelta
import pytest

# Function to generate data
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
    elif data_type == "date":
        return [(current_time - timedelta(days=rng.randint(1, 1000))).strftime("%Y-%m-%d") for _ in range(num_rows)]
    else:
        supported_types = ["int", "string", "date"]
        raise ValueError(f"Unsupported data type '{data_type}'. Supported types: {', '.join(supported_types)}")

# Model for testing
class DataGenerationModel:
    def __init__(self, data_type, num_rows=10, current_time=None, seed=None, random_instance=None):
        self.data_type = data_type
        self.num_rows = num_rows
        self.current_time = current_time if current_time else datetime.now()
        self.seed = seed
        self.random_instance = random_instance
        self.data = generate_data(data_type, num_rows, self.current_time, seed, random_instance)

    def validate(self):
        date_limit = self.current_time - timedelta(days=1000)
        if self.data_type == "int":
            return all(1 <= item <= 100 for item in self.data)
        elif self.data_type == "string":
            return all(len(item) == 10 for item in self.data)
        elif self.data_type == "date":
            return all(datetime.strptime(item, "%Y-%m-%d") >= date_limit for item in self.data)
        else:
            raise ValueError("Unsupported data type")

# Pytest fixture for injecting a fixed datetime
@pytest.fixture
def fixed_datetime():
    """Provides a fixed datetime for deterministic testing"""
    return datetime(2024, 1, 1, 12, 0, 0)

# Pytest-based model tests
@pytest.mark.parametrize("data_type,num_rows", [
    ("int", 100),
    ("string", 50),
    ("date", 30),
])
def test_data_generation(data_type, num_rows):
    model = DataGenerationModel(data_type, num_rows)
    assert model.validate(), f"Validation failed for data type {data_type}"

# Tests with injected datetime for determinism
@pytest.mark.parametrize("data_type,num_rows", [
    ("int", 100),
    ("string", 50),
    ("date", 30),
])
def test_data_generation_deterministic(data_type, num_rows, fixed_datetime):
    """Test with injected datetime for reproducible results"""
    model = DataGenerationModel(data_type, num_rows, current_time=fixed_datetime)
    assert model.current_time == fixed_datetime, "Current time injection failed"
    assert model.validate(), f"Validation failed for data type {data_type}"

def test_date_generation_within_bounds(fixed_datetime):
    """Verify date generation respects the injected reference time"""
    model = DataGenerationModel("date", num_rows=50, current_time=fixed_datetime)
    for date_str in model.data:
        generated_date = datetime.strptime(date_str, "%Y-%m-%d")
        # Dates should be within 1000 days before the reference time
        assert generated_date >= fixed_datetime - timedelta(days=1000)
        assert generated_date <= fixed_datetime

def test_validation_uses_reference_time(fixed_datetime):
    """Ensure validation uses the stored reference time, not current time"""
    model = DataGenerationModel("date", num_rows=10, current_time=fixed_datetime)
    # Validation should pass because date_limit is computed from stored current_time
    assert model.validate()

def test_num_rows_edge_cases():
    """Test validation of num_rows parameter"""
    # Test zero rows - should return empty list
    result = generate_data("int", num_rows=0)
    assert result == [], "num_rows=0 should return empty list"
    
    # Test negative rows - should raise ValueError
    with pytest.raises(ValueError, match="num_rows must be a non-negative integer"):
        generate_data("int", num_rows=-1)
    
    # Test non-integer rows - should raise ValueError
    with pytest.raises(ValueError, match="num_rows must be a non-negative integer"):
        generate_data("int", num_rows=10.5)

def test_unsupported_data_type_error():
    """Test clear error for unsupported data types"""
    with pytest.raises(ValueError, match="Unsupported data type 'invalid_type'"):
        generate_data("invalid_type", num_rows=5)

def test_reproducibility_with_seed(fixed_datetime):
    """Test reproducible generation using seed parameter"""
    # Generate data twice with same seed
    data1 = generate_data("int", num_rows=10, seed=42)
    data2 = generate_data("int", num_rows=10, seed=42)
    assert data1 == data2, "Same seed should produce identical results"
    
    # Different seed should produce different data
    data3 = generate_data("int", num_rows=10, seed=123)
    assert data1 != data3, "Different seeds should produce different results"

def test_reproducibility_with_random_instance():
    """Test reproducible generation using random.Random instance"""
    import random
    
    # Create two random instances with same seed
    rng1 = random.Random(42)
    rng2 = random.Random(42)
    
    # Generate data with each instance
    data1 = generate_data("string", num_rows=5, random_instance=rng1)
    data2 = generate_data("string", num_rows=5, random_instance=rng2)
    
    assert data1 == data2, "Same random instance seed should produce identical results"

def test_model_with_seed(fixed_datetime):
    """Test DataGenerationModel respects seed parameter"""
    model1 = DataGenerationModel("date", num_rows=10, current_time=fixed_datetime, seed=42)
    model2 = DataGenerationModel("date", num_rows=10, current_time=fixed_datetime, seed=42)
    
    assert model1.data == model2.data, "Models with same seed and time should produce identical data"

# Example of running the test
if __name__ == "__main__":
    pytest.main([__file__])
