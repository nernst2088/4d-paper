from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import os
import tempfile
from src.extensions.format_converter import FormatConverter
from src.extensions.latex_template import LaTeXTemplate
from src.tools.utils import ToolsUtils

router = APIRouter()
format_converter = FormatConverter()
latex_template = LaTeXTemplate()
tools_utils = ToolsUtils()

@router.post("/convert")
async def convert_data(
    input_file: UploadFile = File(...),
    output_format: str = Form(...)
):
    """
    Convert data file to different format
    
    Args:
        input_file: Input file to convert
        output_format: Target output format
        
    Returns:
        Conversion result
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(input_file.filename)[1]) as temp_file:
            content = await input_file.read()
            temp_file.write(content)
            temp_input_path = temp_file.name
        
        # Determine output file path
        output_ext = {
            "csv": ".csv",
            "excel": ".xlsx",
            "json": ".json",
            "numpy": ".npy",
            "hdf5": ".h5",
            "text": ".txt",
            "markdown": ".md"
        }.get(output_format, ".txt")
        
        temp_output_path = f"{temp_input_path}_output{output_ext}"
        
        # Convert file
        result = format_converter.convert_data(
            input_path=temp_input_path,
            output_path=temp_output_path,
            output_format=output_format
        )
        
        # Clean up temporary files
        if os.path.exists(temp_input_path):
            os.unlink(temp_input_path)
        if os.path.exists(temp_output_path):
            os.unlink(temp_output_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/latex/generate")
async def generate_latex(
    template_name: str = Form(...),
    title: str = Form(...),
    authors: str = Form(...),
    abstract: str = Form(...),
    introduction: str = Form(...),
    methodology: str = Form(...),
    results: str = Form(...),
    discussion: str = Form(...),
    conclusion: str = Form(...)
):
    """
    Generate LaTeX document from template
    
    Args:
        template_name: Name of LaTeX template
        title: Paper title
        authors: Paper authors
        abstract: Paper abstract
        introduction: Introduction section
        methodology: Methodology section
        results: Results section
        discussion: Discussion section
        conclusion: Conclusion section
        
    Returns:
        Generation result
    """
    try:
        # Create context for template
        context = {
            "title": title,
            "authors": authors,
            "date": "\\today",
            "abstract": abstract,
            "introduction": introduction,
            "methodology": methodology,
            "results": results,
            "discussion": discussion,
            "conclusion": conclusion
        }
        
        # Generate output path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tex") as temp_file:
            temp_output_path = temp_file.name
        
        # Generate LaTeX
        result = latex_template.generate_latex(
            template_name=template_name,
            output_path=temp_output_path,
            context=context
        )
        
        # Clean up temporary file
        if os.path.exists(temp_output_path):
            os.unlink(temp_output_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latex/templates")
async def list_latex_templates():
    """
    List available LaTeX templates
    
    Returns:
        List of template names
    """
    try:
        templates = latex_template.list_templates()
        return {
            "templates": templates,
            "count": len(templates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/latex/compile")
async def compile_latex(
    latex_file: UploadFile = File(...)
):
    """
    Compile LaTeX file to PDF
    
    Args:
        latex_file: LaTeX file to compile
        
    Returns:
        Compilation result
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tex") as temp_file:
            content = await latex_file.read()
            temp_file.write(content)
            temp_latex_path = temp_file.name
        
        # Compile LaTeX
        result = tools_utils.compile_latex(temp_latex_path)
        
        # Clean up temporary files
        if os.path.exists(temp_latex_path):
            os.unlink(temp_latex_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run/script")
async def run_script(
    script_file: UploadFile = File(...),
    args: str = Form(default="")
):
    """
    Run Python script
    
    Args:
        script_file: Python script to run
        args: Additional arguments (space-separated)
        
    Returns:
        Execution result
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            content = await script_file.read()
            temp_file.write(content)
            temp_script_path = temp_file.name
        
        # Parse arguments
        script_args = args.split() if args else []
        
        # Run script
        result = tools_utils.run_python_script(temp_script_path, script_args)
        
        # Clean up temporary files
        if os.path.exists(temp_script_path):
            os.unlink(temp_script_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
