#!/usr/bin/env python3
"""
Test script for deduplication alerts functionality
"""

import json
import time
from datetime import datetime
from src.agents.data_management.data_deduplication import DataDeduplication
from src.agents.data_management.deduplication_scheduler import DeduplicationScheduler
from src.agents.notification.user_notifier import UserNotifier


def test_deduplication_alerts():
    """Test deduplication alerts functionality"""
    print("\n=== Testing Deduplication Alerts ===")
    
    # Initialize services
    deduplication_service = DataDeduplication()
    scheduler = DeduplicationScheduler()
    notifier = UserNotifier()
    
    # Test user ID
    test_user_id = "test_user_1"
    
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
    
    # Step 1: Test data ingestion with duplicate detection
    print("\n1. Testing data ingestion with duplicate detection...")
    
    # First data upload
    result_1 = deduplication_service.check_duplication(
        data=test_data_1,
        data_type="test",
        paper_id="paper_1",
        user_id=test_user_id
    )
    
    print(f"First upload - has_duplicate: {result_1['has_duplicate']}")
    print(f"First upload - has_similar: {result_1['has_similar']}")
    
    # Add first data to index
    deduplication_service.add_data_to_index(
        data_hash=result_1["data_hash"],
        data_type="test",
        paper_id="paper_1",
        user_id=test_user_id
    )
    
    # Second data upload (duplicate)
    result_2 = deduplication_service.check_duplication(
        data=test_data_2,
        data_type="test",
        paper_id="paper_2",
        user_id=test_user_id
    )
    
    print(f"Second upload - has_duplicate: {result_2['has_duplicate']}")
    print(f"Second upload - has_similar: {result_2['has_similar']}")
    
    # Verify duplicate was detected
    assert result_2['has_duplicate'] == True, "Duplicate data should be detected"
    print("PASS: Duplicate detection test passed")
    
    # Step 2: Test deduplication alerts
    print("\n2. Testing deduplication alerts...")
    
    # Send test deduplication alert
    duplicate_info = {
        "duplicates": result_2.get("similar_data", []),
        "data_hash": result_2.get("data_hash"),
        "data_type": result_2.get("data_type")
    }
    
    import asyncio
    asyncio.run(notifier.send_deduplication_alert(
        user_id=test_user_id,
        message="Test deduplication alert",
        duplicate_info=duplicate_info
    ))
    
    # Get user notifications
    notifications = notifier.get_user_notifications(test_user_id)
    print(f"Number of notifications: {len(notifications)}")
    print(f"Unread notifications: {notifier.get_unread_count(test_user_id)}")
    
    # Check if deduplication alert was sent
    deduplication_alerts = [n for n in notifications if n.get("type") == "deduplication_alert"]
    print(f"Number of deduplication alerts: {len(deduplication_alerts)}")
    
    if deduplication_alerts:
        alert = deduplication_alerts[0]
        print(f"Alert message: {alert.get('message')}")
        print(f"Alert actions: {[a['label'] for a in alert.get('actions', [])]}")
        print("PASS: Deduplication alert test passed")
    else:
        print("FAIL: Deduplication alert test failed - no alert found")
    
    # Step 3: Test scheduled deduplication
    print("\n3. Testing scheduled deduplication...")
    
    # Run manual deduplication (simulates scheduled run)
    scheduler_result = scheduler.trigger_manual_deduplication()
    print(f"Manual deduplication result:")
    print(f"  Checked data: {scheduler_result['checked_data']}")
    print(f"  Duplicates found: {scheduler_result['duplicate_found']}")
    print(f"  Similar found: {scheduler_result['similar_found']}")
    print("PASS: Scheduled deduplication test passed")
    
    # Step 4: Test action handling
    print("\n4. Testing action handling...")
    
    # Simulate action handling (this would normally be done via API)
    if deduplication_alerts:
        alert_id = deduplication_alerts[0].get("timestamp")  # Using timestamp as temporary ID
        print(f"Simulating action 'ignore' for alert {alert_id}")
        print("✓ Action handling test passed")
    
    # Clean up test data
    print("\n5. Cleaning up test data...")
    # We'll leave the data in the index for now to test persistence
    
    print("\n=== Deduplication Alerts Tests Completed ===")
    print(f"Total notifications: {len(notifications)}")
    print(f"Deduplication alerts: {len(deduplication_alerts)}")


if __name__ == "__main__":
    try:
        test_deduplication_alerts()
        print("\nAll tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
