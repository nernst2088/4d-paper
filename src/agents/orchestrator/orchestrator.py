import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from src.agents.data_management.data_ingestion import DataIngestionService
from src.agents.data_management.deduplication_scheduler import DeduplicationScheduler
from src.agents.paper_generation.version_manager import PaperVersionManager
from src.agents.notification.user_notifier import UserNotifier
from src.agents.discussion.discussion_manager import DiscussionManager
from src.agents.stats.stats_manager import StatsManager
from src.core.models.paper_model import DynamicPaper, PaperVersion, FourDDataReference
from src.core.security.hash_utils import calculate_data_hash
from src.storage.timeseries_db import TimeSeriesDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrchestratorAgent")

class OrchestratorAgent:
    """Core orchestrator agent that coordinates all other agents and monitors for updates"""
    
    def __init__(self):
        # Initialize dependent agents
        self.data_ingestion_service = DataIngestionService()
        self.deduplication_scheduler = DeduplicationScheduler()
        self.paper_version_manager = PaperVersionManager()
        self.user_notifier = UserNotifier()
        self.discussion_manager = DiscussionManager()
        self.stats_manager = StatsManager()
        self.time_series_db = TimeSeriesDB()
        # Async task queue
        self.task_queue = asyncio.Queue()
        # Monitoring state
        self.monitoring_running = False
        # Scheduler state
        self.scheduler_task = None

    async def start_monitoring(self):
        """Start monitoring for new data/uploads/updates"""
        self.monitoring_running = True
        logger.info("Orchestrator Agent: Starting monitoring for new data and updates")
        
        # Start deduplication scheduler
        self.deduplication_scheduler.start_scheduler()
        self.scheduler_task = asyncio.create_task(self._run_scheduler())
        logger.info("Orchestrator Agent: Deduplication scheduler started")
        
        while self.monitoring_running:
            try:
                # Get next task from queue
                task = await self.task_queue.get()
                await self.handle_task(task)
                self.task_queue.task_done()
            except Exception as e:
                logger.error(f"Orchestrator Agent: Task processing failed - {str(e)}")
                # Only send notification if task has user_id
                if "user_id" in task:
                    await self.user_notifier.send_error_notification(
                        user_id=task.get("user_id"),
                        message=f"Task processing failed: {str(e)}"
                    )
            # Check queue every second (configurable)
            await asyncio.sleep(1)
    
    async def _run_scheduler(self):
        """Run the deduplication scheduler in a background task"""
        try:
            self.deduplication_scheduler.run_scheduler()
        except Exception as e:
            logger.error(f"Orchestrator Agent: Deduplication scheduler error - {str(e)}")

    def stop_monitoring(self):
        """Stop monitoring for updates"""
        self.monitoring_running = False
        
        # Stop deduplication scheduler
        if self.scheduler_task:
            self.deduplication_scheduler.stop_scheduler()
            self.scheduler_task.cancel()
            self.scheduler_task = None
            logger.info("Orchestrator Agent: Deduplication scheduler stopped")
        
        logger.info("Orchestrator Agent: Stopped monitoring")

    def submit_task(self, task: Dict[str, Any]):
        """Submit new task to processing queue (external API entry point)"""
        task_id = task.get("task_id", f"task_{datetime.utcnow().timestamp()}")
        task["task_id"] = task_id
        task["submit_time"] = datetime.utcnow()
        self.task_queue.put_nowait(task)
        logger.info(f"Orchestrator Agent: Received new task - {task_id}")

    async def handle_task(self, task: Dict[str, Any]):
        """Process core task flow: data upload → paper update → user notification"""
        task_type = task.get("task_type")
        user_id = task.get("user_id")
        paper_id = task.get("paper_id")
        data_path = task.get("data_path")
        update_reason = task.get("update_reason", "New or updated research data")
        space_context = task.get("space_context")  # Optional spatial coordinates

        # Handle different task types
        if task_type == "deduplication":
            await self._handle_deduplication_task(task)
            return
        else:
            # Default task type: data upload
            await self._handle_data_upload_task(task)
    
    async def _handle_deduplication_task(self, task: Dict[str, Any]):
        """Handle manual deduplication task"""
        user_id = task.get("user_id")
        data_ids = task.get("data_ids")  # Optional list of data IDs to check
        
        # Step 1: Notify user task has started
        await self.user_notifier.send_progress_notification(
            user_id=user_id,
            message=f"Starting deduplication task {task['task_id']}..."
        )
        
        try:
            # Step 2: Run deduplication
            deduplication_result = self.deduplication_scheduler.trigger_manual_deduplication(data_ids)
            
            # Step 3: Notify user of completion
            await self.user_notifier.send_success_notification(
                user_id=user_id,
                message=f"Deduplication task {task['task_id']} completed! "
                        f"Checked {deduplication_result['checked_data']} data entries, "
                        f"found {deduplication_result['duplicate_found']} duplicates, "
                        f"and {deduplication_result['similar_found']} similar entries."
            )
            logger.info(f"Orchestrator Agent: Deduplication task {task['task_id']} completed")
            
        except Exception as e:
            logger.error(f"Orchestrator Agent: Deduplication task {task['task_id']} failed - {str(e)}")
            await self.user_notifier.send_error_notification(
                user_id=user_id,
                message=f"Deduplication task {task['task_id']} failed: {str(e)}. Please contact support."
            )
    
    async def _handle_data_upload_task(self, task: Dict[str, Any]):
        """Handle data upload task"""
        user_id = task.get("user_id")
        paper_id = task.get("paper_id")
        data_path = task.get("data_path")
        update_reason = task.get("update_reason", "New or updated research data")
        space_context = task.get("space_context")  # Optional spatial coordinates

        # Step 1: Notify user task has started
        await self.user_notifier.send_progress_notification(
            user_id=user_id,
            message=f"Starting task {task['task_id']}: {update_reason}"
        )

        try:
            # Step 2: Process 4D data via Data Management Agent
            await self.user_notifier.send_progress_notification(
                user_id=user_id, message="Processing 4D data..."
            )
            data_ingestion_result = await self.data_ingestion_service.ingest_four_d_data(
                data_path=data_path,
                user_id=user_id,
                paper_id=paper_id,
                timestamp=datetime.utcnow(),
                space_coordinate=space_context
            )
            data_hash = calculate_data_hash(str(data_ingestion_result["data_content"]))
            four_d_data_ref = FourDDataReference(
                data_id=data_ingestion_result["data_id"],
                timestamp=datetime.utcnow(),
                space_coordinate=space_context,
                data_hash=data_hash,
                data_type=data_ingestion_result["data_type"],
                description=update_reason
            )

            # Step 3: Generate new paper version via Paper Generation Agent
            await self.user_notifier.send_progress_notification(
                user_id=user_id, message="Generating new paper version..."
            )
            paper: DynamicPaper = await self.paper_version_manager.get_paper(paper_id)
            new_version_number = paper.latest_version + 1
            
            # Generate version content with 4D data integration
            new_version_content = await self.paper_version_manager.generate_version_content(
                paper=paper,
                four_d_data_refs=[four_d_data_ref],
                version_number=new_version_number,
                update_reason=update_reason
            )
            
            # Generate content hash for tamper protection
            content_hash = paper.generate_paper_hash(new_version_content)
            
            # Create new version object
            new_version = PaperVersion(
                version_id=f"version_{paper_id}_{new_version_number}",
                version_number=new_version_number,
                update_reason=update_reason,
                four_d_data_references=[four_d_data_ref],
                paper_content_hash=content_hash,
                author_team=[user_id],
                space_context=space_context
            )
            
            # Save new version to storage
            await self.paper_version_manager.save_new_version(paper, new_version, new_version_content)

            # Step 4: Store in time-series database for long-term tracking
            await self.time_series_db.insert_paper_version(
                paper_id=paper_id,
                version=new_version,
                timestamp=datetime.utcnow()
            )

            # Step 5: Notify user of successful completion
            await self.user_notifier.send_success_notification(
                user_id=user_id,
                message=f"Task {task['task_id']} completed! Paper updated to version {new_version_number}. "
                        f"4D data ID: {four_d_data_ref.data_id}. All temporal/spatial data is traceable."
            )
            logger.info(f"Orchestrator Agent: Task {task['task_id']} completed - Paper {paper_id} updated to v{new_version_number}")

        except Exception as e:
            logger.error(f"Orchestrator Agent: Task {task['task_id']} failed - {str(e)}")
            await self.user_notifier.send_error_notification(
                user_id=user_id,
                message=f"Task {task['task_id']} failed: {str(e)}. Please check your data or contact support."
            )

            raise e