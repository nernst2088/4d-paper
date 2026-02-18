import asyncio
from src.agents.paper_generation.version_manager import PaperVersionManager
from src.core.models.paper_model import DynamicPaper

def test_paper_version():
    pm = PaperVersionManager()
    paper = DynamicPaper(
        paper_id="test_123",
        title="Test",
        research_purpose="Test",
        creator="user1"
    )
    asyncio.run(pm.save_paper(paper))
    loaded = asyncio.run(pm.get_paper("test_123"))
    assert loaded.paper_id == "test_123"