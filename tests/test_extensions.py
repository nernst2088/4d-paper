from src.extensions.format_converter import FormatConverter
from src.extensions.latex_template import LaTeXTemplate
from src.tools.utils import ToolsUtils
import tempfile
import os

# Test FormatConverter
print("Testing FormatConverter...")
converter = FormatConverter()

# Create test CSV file
with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write("name,age,score\n")
    f.write("Alice,25,95\n")
    f.write("Bob,30,88\n")
    test_csv = f.name

# Test CSV to JSON conversion
json_output = f"{test_csv}_output.json"
try:
    result = converter.convert_data(
        input_path=test_csv,
        output_path=json_output,
        output_format="json"
    )
    print(f"CSV to JSON conversion: {result['success']} - {result['message']}")
    if os.path.exists(json_output):
        print(f"Output file created: {json_output}")
        os.unlink(json_output)
except Exception as e:
    print(f"Conversion error: {e}")

# Clean up
if os.path.exists(test_csv):
    os.unlink(test_csv)

# Test LaTeXTemplate
print("\nTesting LaTeXTemplate...")
latex_template = LaTeXTemplate()

# List available templates
templates = latex_template.list_templates()
print(f"Available templates: {templates}")

# Test LaTeX generation
test_context = {
    "title": "Test Paper",
    "authors": "John Doe, Jane Smith",
    "date": "2026-02-18",
    "abstract": "This is a test abstract.",
    "introduction": "This is the introduction.",
    "methodology": "This is the methodology.",
    "results": "These are the results.",
    "discussion": "This is the discussion.",
    "conclusion": "This is the conclusion."
}

with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
    latex_output = f.name

try:
    result = latex_template.generate_latex(
        template_name="default",
        output_path=latex_output,
        context=test_context
    )
    print(f"LaTeX generation: {result['success']} - {result['message']}")
    if os.path.exists(latex_output):
        print(f"LaTeX file created: {latex_output}")
        os.unlink(latex_output)
except Exception as e:
    print(f"LaTeX generation error: {e}")

# Test ToolsUtils
print("\nTesting ToolsUtils...")
tools = ToolsUtils()

# Test temporary file creation
temp_content = "This is a test file."
temp_file = tools.create_temp_file(temp_content, suffix='.txt')
print(f"Temporary file created: {temp_file}")

# Clean up
if os.path.exists(temp_file):
    tools.cleanup_temp_files([temp_file])
    print("Temporary file cleaned up.")

print("\nAll tests completed!")
