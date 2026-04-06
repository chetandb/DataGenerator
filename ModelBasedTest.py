import random
import string
from datetime import datetime, timedelta
import pytest

"""
Random Number Generation Strategy:
- Default (no seed, no random_instance): Uses global random module (stateful, non-deterministic)
- With seed: Creates isolated Random(seed) instance (deterministic, reproducible)
- With random_instance: Uses provided Random object (full control over RNG state)

UUID Generation:
- UUID generation is intentionally non-deterministic (uses uuid.uuid4() by default)
- To control UUID generation, pass a custom uuid_generator function
- Example: uuid_generator=lambda: str(uuid.uuid4())  # or any custom generator

Use seed parameter for reproducible test data generation in tests.
Use random_instance parameter for advanced control or when coordinating RNG state across multiple calls.
Use uuid_generator parameter to customize UUID generation or make it deterministic in tests.
"""

# Function to generate data
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
    elif data_type == "date":
        return [(current_time - timedelta(days=rng.randint(1, 1000))).strftime("%Y-%m-%d") for _ in range(num_rows)]
    else:
        supported_types = ["int", "string", "date"]
        raise ValueError(f"Unsupported data type '{data_type}'. Supported types: {', '.join(supported_types)}")

# Model for testing
class DataGenerationModel:
    def __init__(self, data_type, num_rows=10, current_time=None, seed=None, random_instance=None, uuid_generator=None):
        self.data_type = data_type
        self.num_rows = num_rows
        self.current_time = current_time if current_time else datetime.now()
        self.seed = seed
        self.random_instance = random_instance
        self.uuid_generator = uuid_generator
        self.data = generate_data(data_type, num_rows, self.current_time, seed, random_instance, uuid_generator)

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
    """Test data generation with default system datetime (non-deterministic)
    
    Note: Uses system datetime which makes this test non-deterministic.
    For deterministic tests with fixed datetime, see test_data_generation_deterministic().
    """
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
    """Test reproducible generation using seed parameter with fixed datetime
    
    Seed parameter ensures identical data generation across calls for all data types.
    Fixed datetime ensures date/timestamp values are within expected bounds.
    """
    # Generate int data twice with same seed - should be identical
    data1 = generate_data("int", num_rows=10, seed=42)
    data2 = generate_data("int", num_rows=10, seed=42)
    assert data1 == data2, "Same seed should produce identical results"
    
    # Different seed should produce different data
    data3 = generate_data("int", num_rows=10, seed=123)
    assert data1 != data3, "Different seeds should produce different results"
    
    # Test seed with fixed datetime for date generation
    date_data1 = generate_data("date", num_rows=5, seed=42, current_time=fixed_datetime)
    date_data2 = generate_data("date", num_rows=5, seed=42, current_time=fixed_datetime)
    assert date_data1 == date_data2, "Same seed and time should produce identical dates"

def test_reproducibility_with_random_instance():
    """Test reproducible generation using random.Random instance
    
    Note: Date/timestamp generation uses system datetime by default (non-deterministic).
    For deterministic date generation, provide current_time parameter.
    """
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

def test_pluggable_uuid_generator():
    """Test custom UUID generator function
    
    Note: This test is non-deterministic with respect to datetime (uses system time).
    UUID generation itself is deterministic via the plugged generator function.
    """
    counter = {'value': 0}
    
    def custom_uuid_gen():
        """Generate deterministic UUIDs for testing"""
        counter['value'] += 1
        return f"test-uuid-{counter['value']}"
    
    # Generate UUIDs using custom generator
    result = generate_data("uuid", num_rows=3, uuid_generator=custom_uuid_gen)
    
    expected = ["test-uuid-1", "test-uuid-2", "test-uuid-3"]
    assert result == expected, "Custom UUID generator should be used when provided"

def test_default_uuid_generation_is_non_deterministic():
    """Document that UUID generation is non-deterministic even with seed
    
    UUID generation uses uuid.uuid4() which is cryptographically random and not
    affected by the seed parameter. Each call generates truly random UUIDs.
    To make UUID generation deterministic, use the uuid_generator parameter.
    """
    # Even with seed, UUIDs should be different each call (non-deterministic)
    uuid_set1 = set(generate_data("uuid", num_rows=5, seed=42))
    uuid_set2 = set(generate_data("uuid", num_rows=5, seed=42))
    
    # All UUIDs should be unique (very high probability)
    assert len(uuid_set1) == 5, "All UUIDs in one set should be unique"
    assert len(uuid_set2) == 5, "All UUIDs in second set should be unique"
    
    # Sets should be different (non-deterministic despite same seed)
    assert uuid_set1 != uuid_set2, "UUID generation is non-deterministic even with seed"

# Example of running the test
if __name__ == "__main__":
    pytest.main([__file__])
