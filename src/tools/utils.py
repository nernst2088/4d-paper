import os
import subprocess
import tempfile
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ToolsUtils")

class ToolsUtils:
    """Utility tools for various operations"""
    
    def __init__(self):
        """Initialize tools utilities"""
        pass
    
    def compile_latex(self, latex_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Compile LaTeX document to PDF
        
        Args:
            latex_path: Path to LaTeX file
            output_dir: Output directory for PDF (defaults to same directory as LaTeX file)
            
        Returns:
            Compilation result
        """
        if not os.path.exists(latex_path):
            raise FileNotFoundError(f"LaTeX file not found: {latex_path}")
        
        if output_dir is None:
            output_dir = os.path.dirname(latex_path)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Get filename without extension
        base_name = os.path.splitext(os.path.basename(latex_path))[0]
        pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
        
        logger.info(f"Compiling LaTeX to PDF: {latex_path} -> {pdf_path}")
        
        # Try different LaTeX compilers
        compilers = ["pdflatex", "xelatex", "lualatex"]
        success = False
        error_message = ""
        
        for compiler in compilers:
            try:
                # Run LaTeX compiler
                result = subprocess.run(
                    [compiler, "-output-directory", output_dir, latex_path],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    success = True
                    logger.info(f"Successfully compiled with {compiler}")
                    break
                else:
                    error_message = f"{compiler} failed: {result.stderr}"
                    logger.warning(error_message)
                    
            except FileNotFoundError:
                # Compiler not found, try next one
                continue
            except Exception as e:
                error_message = f"Error compiling: {str(e)}"
                logger.error(error_message)
                continue
        
        if success:
            return {
                "success": True,
                "latex_path": latex_path,
                "pdf_path": pdf_path,
                "message": f"Successfully compiled LaTeX to PDF"
            }
        else:
            return {
                "success": False,
                "latex_path": latex_path,
                "error": error_message or "No LaTeX compiler found",
                "message": "Failed to compile LaTeX to PDF"
            }
    
    def run_python_script(self, script_path: str, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Run Python script
        
        Args:
            script_path: Path to Python script
            args: Additional arguments to pass to script
            
        Returns:
            Execution result
        """
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        if args is None:
            args = []
        
        logger.info(f"Running Python script: {script_path} with args: {args}")
        
        try:
            # Run script
            result = subprocess.run(
                ["python", script_path] + args,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "script_path": script_path,
                    "stdout": result.stdout,
                    "message": "Successfully executed Python script"
                }
            else:
                return {
                    "success": False,
                    "script_path": script_path,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "message": f"Python script failed with return code {result.returncode}"
                }
                
        except Exception as e:
            logger.error(f"Error running script: {str(e)}")
            return {
                "success": False,
                "script_path": script_path,
                "error": str(e),
                "message": f"Failed to run Python script: {str(e)}"
            }
    
    def create_temp_file(self, content: str, suffix: str = ".txt") -> str:
        """
        Create temporary file with given content
        
        Args:
            content: File content
            suffix: File suffix
            
        Returns:
            Path to temporary file
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as f:
            f.write(content)
            temp_path = f.name
        
        logger.info(f"Created temporary file: {temp_path}")
        return temp_path
    
    def cleanup_temp_files(self, files: list):
        """
        Clean up temporary files
        
        Args:
            files: List of file paths to delete
        """
        for file_path in files:
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                    logger.info(f"Cleaned up temporary file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up file {file_path}: {str(e)}")
