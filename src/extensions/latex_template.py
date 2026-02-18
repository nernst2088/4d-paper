import os
import jinja2
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LaTeXTemplate")

class LaTeXTemplate:
    """LaTeX template support for academic paper generation"""
    
    def __init__(self, templates_dir: str = "./templates/latex"):
        """
        Initialize LaTeX template manager
        
        Args:
            templates_dir: Directory containing LaTeX templates
        """
        self.templates_dir = templates_dir
        self._ensure_templates_dir()
        self._setup_jinja2()
        self._load_default_templates()
    
    def _ensure_templates_dir(self):
        """Ensure templates directory exists"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
            logger.info(f"Created templates directory: {self.templates_dir}")
    
    def _setup_jinja2(self):
        """Set up Jinja2 template environment"""
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            block_start_string='\\BLOCK{',
            block_end_string='}',
            variable_start_string='\\VAR{',
            variable_end_string='}',
            comment_start_string='\\#{',
            comment_end_string='}',
            line_statement_prefix='%%',
            line_comment_prefix='%#',
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False
        )
    
    def _load_default_templates(self):
        """Load default LaTeX templates"""
        # Create default template if not exists
        default_template = os.path.join(self.templates_dir, "default.tex")
        if not os.path.exists(default_template):
            self._create_default_template(default_template)
    
    def _create_default_template(self, template_path: str):
        """Create default LaTeX template"""
        default_content = r"""\documentclass[12pt, letterpaper]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{geometry}
\geometry{margin=1in}

\title{\VAR{title}}
\author{\VAR{authors}}
\date{\VAR{date}}

\begin{document}

\maketitle

\begin{abstract}
\VAR{abstract}
\end{abstract}

\section{Introduction}
\VAR{introduction}

\section{Methodology}
\VAR{methodology}

\section{Results}
\VAR{results}

\section{Discussion}
\VAR{discussion}

\section{Conclusion}
\VAR{conclusion}

\bibliography{references}
\bibliographystyle{plain}

\end{document}
"""
        
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(default_content)
        
        logger.info(f"Created default LaTeX template: {template_path}")
    
    def generate_latex(
        self,
        template_name: str,
        output_path: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate LaTeX document from template
        
        Args:
            template_name: Name of the template file (without .tex extension)
            output_path: Path to save the generated LaTeX file
            context: Dictionary with template variables
            
        Returns:
            Generation result
        """
        try:
            # Load template
            template = self.template_env.get_template(f"{template_name}.tex")
            
            # Render template
            latex_content = template.render(**context)
            
            # Save output
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(latex_content)
            
            result = {
                "success": True,
                "template": template_name,
                "output_path": output_path,
                "message": f"Successfully generated LaTeX document from template: {template_name}"
            }
            
            logger.info(f"LaTeX generation successful: {result['message']}")
            return result
            
        except Exception as e:
            logger.error(f"LaTeX generation failed: {str(e)}")
            return {
                "success": False,
                "template": template_name,
                "output_path": output_path,
                "error": str(e),
                "message": f"Failed to generate LaTeX document: {str(e)}"
            }
    
    def list_templates(self) -> list:
        """
        List available LaTeX templates
        
        Returns:
            List of template names
        """
        templates = []
        for file in os.listdir(self.templates_dir):
            if file.endswith(".tex"):
                templates.append(os.path.splitext(file)[0])
        return templates
    
    def add_template(self, template_name: str, template_content: str):
        """
        Add new LaTeX template
        
        Args:
            template_name: Name of the template (without .tex extension)
            template_content: LaTeX template content
        """
        template_path = os.path.join(self.templates_dir, f"{template_name}.tex")
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(template_content)
        logger.info(f"Added new LaTeX template: {template_name}")
    
    def get_template(self, template_name: str) -> Optional[str]:
        """
        Get template content
        
        Args:
            template_name: Name of the template (without .tex extension)
            
        Returns:
            Template content or None if not found
        """
        template_path = os.path.join(self.templates_dir, f"{template_name}.tex")
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        return None
