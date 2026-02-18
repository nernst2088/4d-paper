import os
import json
import uuid
from datetime import datetime
from typing import List, Optional
import logging
from src.core.models.paper_model import DynamicPaper, PaperVersion, FourDDataReference
from src.agents.paper_generation.template_engine import TemplateEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PaperVersionManager")

class PaperVersionManager:
    """Manager for paper version control and storage"""
    
    def __init__(self, storage_path: str = "./storage/papers"):
        self.storage_path = storage_path
        self.template_engine = TemplateEngine()
        os.makedirs(storage_path, exist_ok=True)
    
    def _get_paper_path(self, paper_id: str) -> str:
        """Get path to paper metadata file"""
        return os.path.join(self.storage_path, f"{paper_id}.json")
    
    def _get_version_path(self, paper_id: str, version_number: int) -> str:
        """Get path to paper version content"""
        return os.path.join(self.storage_path, f"{paper_id}_v{version_number}")
    
    async def get_paper(self, paper_id: str) -> DynamicPaper:
        """
        Get paper by ID
        
        Args:
            paper_id: Paper ID
            
        Returns:
            DynamicPaper object
        """
        paper_path = self._get_paper_path(paper_id)
        if not os.path.exists(paper_path):
            raise FileNotFoundError(f"Paper {paper_id} not found")
        
        with open(paper_path, "r", encoding="utf-8") as f:
            paper_data = json.load(f)
        
        # Handle versions conversion
        if "versions" in paper_data:
            from src.core.models.paper_model import PaperVersion, FourDDataReference, SpaceCoordinate
            converted_versions = []
            for version_data in paper_data["versions"]:
                # Convert four_d_data_references
                if "four_d_data_references" in version_data:
                    converted_refs = []
                    for ref_data in version_data["four_d_data_references"]:
                        # Convert space_coordinate if present
                        if "space_coordinate" in ref_data and ref_data["space_coordinate"]:
                            ref_data["space_coordinate"] = SpaceCoordinate(**ref_data["space_coordinate"])
                        converted_refs.append(FourDDataReference(**ref_data))
                    version_data["four_d_data_references"] = converted_refs
                # Convert space_context if present
                if "space_context" in version_data and version_data["space_context"]:
                    version_data["space_context"] = SpaceCoordinate(**version_data["space_context"])
                # Convert create_time to datetime
                if "create_time" in version_data:
                    from datetime import datetime
                    version_data["create_time"] = datetime.fromisoformat(version_data["create_time"])
                converted_versions.append(PaperVersion(**version_data))
            paper_data["versions"] = converted_versions
        
        # Convert create_time to datetime
        if "create_time" in paper_data:
            from datetime import datetime
            paper_data["create_time"] = datetime.fromisoformat(paper_data["create_time"])
        
        return DynamicPaper(**paper_data)
    
    async def save_paper(self, paper: DynamicPaper):
        """
        Save paper metadata
        
        Args:
            paper: DynamicPaper object
        """
        paper_path = self._get_paper_path(paper.paper_id)
        
        # Convert Pydantic model to dict with proper serialization
        def serialize_pydantic(obj):
            if hasattr(obj, "dict"):
                return obj.dict()
            elif hasattr(obj, "__dict__"):
                return obj.__dict__
            else:
                return str(obj)
        
        paper_dict = paper.dict()
        
        with open(paper_path, "w", encoding="utf-8") as f:
            json.dump(paper_dict, f, indent=2, default=serialize_pydantic)
        
        logger.info(f"Paper saved: {paper.paper_id}")
    
    async def generate_version_content(
        self,
        paper: DynamicPaper,
        four_d_data_refs: List[FourDDataReference],
        version_number: int,
        update_reason: str
    ) -> str:
        """
        Generate paper version content
        
        Args:
            paper: DynamicPaper object
            four_d_data_refs: List of 4D data references
            version_number: Version number
            update_reason: Update reason
            
        Returns:
            Generated paper content (Markdown)
        """
        # Generate content using template engine
        content = self.template_engine.generate_paper_content(
            paper=paper,
            four_d_data_refs=four_d_data_refs,
            version_number=version_number,
            update_reason=update_reason
        )
        
        return content
    
    async def save_new_version(
        self,
        paper: DynamicPaper,
        version: PaperVersion,
        content: str
    ):
        """
        Save new paper version
        
        Args:
            paper: DynamicPaper object
            version: PaperVersion object
            content: Paper content
        """
        # Add new version to paper
        paper.add_new_version(version)
        
        # Save paper metadata
        await self.save_paper(paper)
        
        # Save version content (Markdown)
        version_path = self._get_version_path(paper.paper_id, version.version_number)
        md_path = f"{version_path}.md"
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Generate PDF version
        pdf_path = f"{version_path}.pdf"
        self.template_engine.generate_pdf(content, pdf_path)
        
        # Create timestamp and blockchain certification
        from src.agents.publication.timestamp_service import TimestampService
        from src.agents.publication.blockchain_cert import BlockchainCert
        
        timestamp_service = TimestampService()
        blockchain_cert = BlockchainCert()
        
        # Create timestamp
        timestamp = timestamp_service.create_timestamp(
            content=content,
            paper_id=paper.paper_id,
            version_number=version.version_number
        )
        
        # Create blockchain certification
        certification = blockchain_cert.certify_paper(
            paper_id=paper.paper_id,
            version_number=version.version_number,
            content_hash=version.paper_content_hash
        )
        
        # Save timestamp and certification info
        cert_path = f"{version_path}_cert.json"
        import json
        with open(cert_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": timestamp,
                "blockchain_certification": certification
            }, f, indent=2)
        
        logger.info(f"New version saved: {paper.paper_id} v{version.version_number} with timestamp and blockchain certification")
    
    async def get_version_content(self, paper_id: str, version_number: int) -> str:
        """
        Get paper version content
        
        Args:
            paper_id: Paper ID
            version_number: Version number
            
        Returns:
            Paper content (Markdown)
        """
        version_path = self._get_version_path(paper_id, version_number)
        md_path = f"{version_path}.md"
        
        if not os.path.exists(md_path):
            raise FileNotFoundError(f"Version {version_number} for paper {paper_id} not found")
        
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return content
    
    async def get_latest_version(self, paper_id: str) -> tuple[PaperVersion, str]:
        """
        Get latest paper version and content
        
        Args:
            paper_id: Paper ID
            
        Returns:
            Tuple of (PaperVersion, content)
        """
        paper = await self.get_paper(paper_id)
        if not paper.versions:
            raise ValueError(f"No versions found for paper {paper_id}")
        
        latest_version = paper.versions[-1]
        content = await self.get_version_content(paper_id, latest_version.version_number)
        
        return latest_version, content