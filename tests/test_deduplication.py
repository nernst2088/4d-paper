#!/usr/bin/env python3
"""
Test script for deduplication functionality
"""

import json
import time
from datetime import datetime
from src.agents.data_management.data_deduplication import DataDeduplication
from src.agents.data_management.deduplication_scheduler import DeduplicationScheduler


def test_data_deduplication():
    """Test data deduplication functionality"""
    print("\n=== Testing Data Deduplication ===")
    
    # Initialize deduplication service
    deduplication_service = DataDeduplication()
    
    # Test data
    test_data_1 = {
        "id": 1,
        "name": "Test Data",
        "value": 42
    }
    
    test_data_2 = {
        "id": 1,
        "name": "Test Data",
        "value": 42
    }  # Duplicate of test_data_1
    
    test_data_3 = {
        "id": 2,
        "name": "Different Data",
        "value": 99
    }  # Different data
    
    # Calculate hashes
    hash_1 = deduplication_service.calculate_data_hash(test_data_1)
    hash_2 = deduplication_service.calculate_data_hash(test_data_2)
    hash_3 = deduplication_service.calculate_data_hash(test_data_3)
    
    print(f"Hash 1: {hash_1[:10]}...")
    print(f"Hash 2: {hash_2[:10]}...")
    print(f"Hash 3: {hash_3[:10]}...")
    
    # Verify hashes
    assert hash_1 == hash_2, "Duplicate data should have the same hash"
    assert hash_1 != hash_3, "Different data should have different hashes"
    print("PASS: Hash calculation test passed")
    
    # Test duplication check
    result_1 = deduplication_service.check_duplication(
        data=test_data_1,
        data_type="test",
        paper_id="paper_1",
        user_id="user_1"
    )
    
    print(f"First duplication check result: {result_1['recommendation']}")
    
    # Test with duplicate data
    result_2 = deduplication_service.check_duplication(
        data=test_data_2,
        data_type="test",
        paper_id="paper_2",
        user_id="user_1"
    )
    
    print(f"Second duplication check result: {result_2['recommendation']}")
    assert result_2['has_duplicate'] == True, "Duplicate data should be detected"
    print("PASS: Duplication detection test passed")
    
    print("=== Data Deduplication Tests Completed Successfully ===")


def test_deduplication_scheduler():
    """Test deduplication scheduler functionality"""
    print("\n=== Testing Deduplication Scheduler ===")
    
    # Initialize scheduler
    scheduler = DeduplicationScheduler()
    print("✓ Scheduler initialized")
    
    # Test configuration
    scheduler.configure_schedule(interval="daily", time="12:00")
    print("✓ Scheduler configured")
    
    # Test manual deduplication
    print("Running manual deduplication...")
    result = scheduler.trigger_manual_deduplication()
    print(f"Manual deduplication completed:")
    print(f"  Total data: {result['total_data']}")
    print(f"  Checked data: {result['checked_data']}")
    print(f"  Duplicates found: {result['duplicate_found']}")
    print(f"  Similar found: {result['similar_found']}")
    print("PASS: Manual deduplication test passed")
    
    # Test scheduler start/stop
    print("Starting scheduler...")
    scheduler.start_scheduler()
    print("✓ Scheduler started")
    
    # Wait a moment
    time.sleep(1)
    
    print("Stopping scheduler...")
    scheduler.stop_scheduler()
    print("Scheduler stopped")
    
    print("=== Deduplication Scheduler Tests Completed Successfully ===")


if __name__ == "__main__":
    try:
        test_data_deduplication()
        test_deduplication_scheduler()
        print("\nAll tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
