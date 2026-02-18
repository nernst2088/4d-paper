from fastapi import APIRouter, HTTPException, UploadFile, File
from datetime import datetime
from src.agents.data_management.data_ingestion import DataIngestionService
from src.core.models.data_model import DataIngestionRequest

router = APIRouter()
data_service = DataIngestionService()

@router.post("/ingest")
async def ingest_data(request: DataIngestionRequest):
    """
    Ingest 4D research data
    """
    try:
        result = await data_service.ingest_four_d_data(
            data_path=request.data_path,
            user_id=request.user_id,
            paper_id=request.paper_id,
            timestamp=datetime.utcnow(),
            space_coordinate=request.space_coordinate
        )
        return {
            "status": "success",
            "data": result,
            "duplication_check": result.get("duplication_check")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    user_id: str = "",
    paper_id: str = "",
    data_type: str = "tabular",
    description: str = ""
):
    """
    Upload and ingest 4D data file
    """
    try:
        # Create tmp directory if not exists
        import os
        os.makedirs("./tmp", exist_ok=True)
        
        # Save uploaded file
        save_path = f"./tmp/{file.filename}"
        with open(save_path, "wb") as f:
            f.write(await file.read())
        
        # Ingest the data
        result = await data_service.ingest_four_d_data(
            data_path=save_path,
            user_id=user_id,
            paper_id=paper_id,
            timestamp=datetime.utcnow(),
            space_coordinate=None
        )
        
        return {
            "status": "success",
            "message": f"File {file.filename} uploaded and ingested successfully",
            "data": result,
            "duplication_check": result.get("duplication_check")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{data_id}")
async def get_data(data_id: str, user_id: str):
    """
    Get 4D data by ID
    """
    try:
        from src.agents.data_management.four_d_data_handler import FourDDataHandler
        from src.core.security.encryption import derive_encryption_key
        
        handler = FourDDataHandler()
        # Use default key (in production, use user-specific key)
        key, _ = derive_encryption_key("default-encryption-key-change-in-production")
        
        data = handler.load_four_d_data(
            data_id=data_id,
            encryption_key=key
        )
        
        return {
            "status": "success",
            "data": data
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Data {data_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deduplicate")
async def trigger_deduplication(user_id: str, data_ids: list = None):
    """
    Trigger manual data deduplication
    
    Args:
        user_id: User ID
        data_ids: Optional list of data IDs to check (None for all data)
        
    Returns:
        Task submission result
    """
    try:
        from src.agents.orchestrator.orchestrator import OrchestratorAgent
        
        orchestrator = OrchestratorAgent()
        task = {
            "task_type": "deduplication",
            "user_id": user_id,
            "data_ids": data_ids
        }
        
        orchestrator.submit_task(task)
        
        return {
            "status": "success",
            "message": "Deduplication task submitted successfully",
            "task_id": task.get("task_id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deduplication/action")
async def handle_deduplication_action(
    user_id: str,
    notification_id: str,
    action_id: str,
    duplicate_data_id: str = None,
    original_data_id: str = None
):
    """
    Handle user action on deduplication alert
    
    Args:
        user_id: User ID
        notification_id: Notification ID
        action_id: Action ID (ignore, replace, merge, review)
        duplicate_data_id: ID of the duplicate data (if applicable)
        original_data_id: ID of the original data (if applicable)
        
    Returns:
        Action result
    """
    try:
        from src.agents.notification.user_notifier import UserNotifier
        from src.agents.data_management.data_deduplication import DataDeduplication
        
        notifier = UserNotifier()
        deduplication_service = DataDeduplication()
        
        # Process action based on action_id
        if action_id == "ignore":
            # Simply mark notification as read
            message = "Duplication alert ignored"
        elif action_id == "replace":
            # Replace duplicate with existing data
            if not original_data_id:
                raise ValueError("Original data ID is required for replace action")
            message = f"Duplicate data replaced with original data: {original_data_id}"
        elif action_id == "merge":
            # Merge duplicate data with existing
            if not original_data_id:
                raise ValueError("Original data ID is required for merge action")
            message = f"Data merged with original data: {original_data_id}"
        elif action_id == "review":
            # Mark for manual review
            message = "Data marked for manual review"
        else:
            raise ValueError(f"Invalid action ID: {action_id}")
        
        # Log action
        import logging
        logger = logging.getLogger("DataRoutes")
        logger.info(f"User {user_id} performed action {action_id} on deduplication alert")
        
        return {
            "status": "success",
            "message": message,
            "action": action_id,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))