from src.agents.data_management.data_ingestion import DataIngestionService
from src.core.models.data_model import DataIngestionRequest
from datetime import datetime, UTC
import tempfile
import os
import pandas as pd
import asyncio

# Create test data files
print("Creating test data files...")

# Test 1: Exact duplicate data
with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write("name,age,score\n")
    f.write("Alice,25,95\n")
    f.write("Bob,30,88\n")
    test_file_1 = f.name

# Test 2: Same data as test_file_1 (exact duplicate)
test_file_2 = test_file_1

# Test 3: Similar data (same structure, different values)
with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write("name,age,score\n")
    f.write("Charlie,28,92\n")
    f.write("David,32,85\n")
    test_file_3 = f.name

async def run_tests():
    # Create data ingestion service
    data_service = DataIngestionService()

    # Test 1: First upload (no duplicates yet)
    print("\nTest 1: First data upload")
    try:
        result = await data_service.ingest_four_d_data(
            data_path=test_file_1,
            user_id="test_user",
            paper_id="test_paper",
            timestamp=datetime.now(UTC)
        )
        print(f"Upload 1 status: Success")
        duplication_check = result.get("duplication_check")
        if duplication_check:
            print(f"Duplicate check: {duplication_check['has_duplicate']}")
            print(f"Similar check: {duplication_check['has_similar']}")
            print(f"Recommendation: {duplication_check['recommendation']}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Second upload (exact duplicate)
    print("\nTest 2: Exact duplicate data upload")
    try:
        result = await data_service.ingest_four_d_data(
            data_path=test_file_2,
            user_id="test_user",
            paper_id="test_paper",
            timestamp=datetime.now(UTC)
        )
        print(f"Upload 2 status: Success")
        duplication_check = result.get("duplication_check")
        if duplication_check:
            print(f"Duplicate check: {duplication_check['has_duplicate']}")
            print(f"Similar check: {duplication_check['has_similar']}")
            print(f"Recommendation: {duplication_check['recommendation']}")
            print(f"Similar data found: {len(duplication_check['similar_data'])} entries")
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: Similar data upload
    print("\nTest 3: Similar data upload")
    try:
        result = await data_service.ingest_four_d_data(
            data_path=test_file_3,
            user_id="test_user",
            paper_id="test_paper",
            timestamp=datetime.now(UTC)
        )
        print(f"Upload 3 status: Success")
        duplication_check = result.get("duplication_check")
        if duplication_check:
            print(f"Duplicate check: {duplication_check['has_duplicate']}")
            print(f"Similar check: {duplication_check['has_similar']}")
            print(f"Recommendation: {duplication_check['recommendation']}")
            print(f"Similar data found: {len(duplication_check['similar_data'])} entries")
    except Exception as e:
        print(f"Error: {e}")

# Run tests
asyncio.run(run_tests())

# Clean up
print("\nCleaning up test files...")
for file_path in [test_file_1, test_file_3]:
    if os.path.exists(file_path):
        os.unlink(file_path)

print("\nAll tests completed!")
