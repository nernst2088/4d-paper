#!/usr/bin/env python3
"""
Test script to verify all imports are working correctly
"""

from src.agents.data_management.data_deduplication import DataDeduplication
from src.agents.data_management.deduplication_scheduler import DeduplicationScheduler
from src.agents.orchestrator.orchestrator import OrchestratorAgent

print("All imports successful!")
print("DataDeduplication class imported:", DataDeduplication is not None)
print("DeduplicationScheduler class imported:", DeduplicationScheduler is not None)
print("OrchestratorAgent class imported:", OrchestratorAgent is not None)
