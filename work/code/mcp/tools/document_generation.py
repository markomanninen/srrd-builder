"""
Document Generation Tools for SRRD Builder MCP Server
Handles LaTeX generation, formatting, and document compilation
"""

from typing import Dict, Any, Optional, List
import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime

# Add parent directory to path to access storage modules
sys.path.append(str(Path(__file__).parent.parent))

from storage.project_manager import ProjectManager

# LaTeX template for scientific research documents
LATEX_TEMPLATE = r"""
\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{cite}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage{abstract}

\geometry{margin=1in}
\pagestyle{fancy}
\fancyhf{}
\rhead{\thepage}
\lhead{title_placeholder}

\title{title_placeholder}
\author{author_placeholder}
\date{date_placeholder}

\begin{document}

\maketitle

\begin{abstract}
{abstract}
\end{abstract}

\section{{Introduction}}
{introduction}

\section{{Methodology}}
{methodology}

\section{{Results}}
{results}

\section{{Discussion}}
{discussion}

\section{{Conclusion}}
{conclusion}

\begin{thebibliography}{{99}}
{bibliography}
\end{thebibliography}

\end{document}
"""

async def generate_latex_document_tool(**kwargs) -> str:
    """Generate LaTeX document from research content"""
    
    try:
        title = kwargs.get('title', 'Untitled Research Paper')
        author = kwargs.get('author', 'SRRD Builder')
        abstract = kwargs.get('abstract', '')
        introduction = kwargs.get('introduction', '')
        methodology = kwargs.get('methodology', '')
        results = kwargs.get('results', '')
        discussion = kwargs.get('discussion', '')
        conclusion = kwargs.get('conclusion', '')
        bibliography = kwargs.get('bibliography', '')
        project_path = kwargs.get('project_path', '')
        
        # Format the LaTeX document
        latex_content = LATEX_TEMPLATE.replace("title_placeholder", title)
        latex_content = latex_content.replace("author_placeholder", author)
        latex_content = latex_content.replace("date_placeholder", datetime.now().strftime("%B %d, %Y"))
        latex_content = latex_content.replace("{abstract}", abstract)
        latex_content = latex_content.replace("{introduction}", introduction)
        latex_content = latex_content.replace("{methodology}", methodology)
        latex_content = latex_content.replace("{results}", results)
        latex_content = latex_content.replace("{discussion}", discussion)
        latex_content = latex_content.replace("{conclusion}", conclusion)
        latex_content = latex_content.replace("{bibliography}", bibliography)
        
        # Save to project if path provided
        if project_path:
            project_manager = ProjectManager(project_path)
            doc_path = Path(project_path) / "documents" / f"{title.replace(' ', '_').lower()}.tex"
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            return f"LaTeX document generated successfully at: {doc_path}"
        else:
            return f"LaTeX document generated:\n{latex_content[:500]}..."
            
    except Exception as e:
        return f"Error generating LaTeX document: {str(e)}"

async def compile_latex_tool(**kwargs) -> str:
    """Compile LaTeX document to PDF or other formats"""
    
    try:
        tex_file_path = kwargs.get('tex_file_path')
        output_format = kwargs.get('output_format', 'pdf')
        
        if not tex_file_path:
            return "Error: Missing required parameter 'tex_file_path'"
        
        tex_path = Path(tex_file_path)
        if not tex_path.exists():
            return f"Error: LaTeX file not found at {tex_file_path}"
        
        # Change to the directory containing the .tex file
        work_dir = tex_path.parent
        tex_filename = tex_path.name
        
        if output_format.lower() == "pdf":
            # Check if pdflatex is available
            import shutil
            if not shutil.which("pdflatex"):
                return f"Error: pdflatex not found. Please install LaTeX distribution:\n• macOS: 'brew install --cask mactex'\n• Ubuntu: 'sudo apt-get install texlive-full'\n• Windows: Install MiKTeX from https://miktex.org/\n\nSee INSTALLATION.md for complete setup guide. The LaTeX source file is available at: {tex_file_path}"
            
            # Compile with pdflatex
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_filename],
                cwd=work_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                pdf_path = work_dir / tex_filename.replace('.tex', '.pdf')
                if pdf_path.exists():
                    return f"PDF compiled successfully: {pdf_path}"
                else:
                    return f"LaTeX compilation completed but PDF not found. Check LaTeX file syntax: {tex_file_path}"
            else:
                error_info = []
                if result.stdout:
                    error_info.append(f"Output: {result.stdout.strip()}")
                if result.stderr:
                    error_info.append(f"Error: {result.stderr.strip()}")
                
                if not error_info:
                    error_info = ["LaTeX compilation failed with no error output. The LaTeX file may contain syntax errors."]
                
                # Also check if the .tex file contains valid LaTeX
                try:
                    with open(tex_path, 'r') as f:
                        content = f.read().strip()
                    if not content.startswith('\\documentclass') and not content.startswith('\\begin{document}'):
                        error_info.append(f"Note: The file may not contain valid LaTeX syntax. LaTeX files should start with \\documentclass or \\begin{{document}}.")
                except:
                    pass
                
                return f"LaTeX compilation error: {' | '.join(error_info)}"
        else:
            return f"Unsupported output format: {output_format}"
            
    except Exception as e:
        return f"Error compiling LaTeX: {str(e)}"

async def format_research_content_tool(**kwargs) -> str:
    """Format research content according to academic standards"""
    
    try:
        content = kwargs.get('content', '')
        content_type = kwargs.get('content_type', 'section')
        formatting_style = kwargs.get('formatting_style', 'academic')
        
        if not content:
            return "Error: Missing required parameter 'content'"
        
        formatted_content = content.strip()
        
        if content_type == "section":
            # Add proper paragraph breaks and formatting
            lines = formatted_content.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    # Ensure proper sentence structure
                    if not line.endswith('.') and not line.endswith('!') and not line.endswith('?'):
                        line += '.'
                    formatted_lines.append(line)
            
            formatted_content = '\n\n'.join(formatted_lines)
        
        elif content_type == "equation":
            # Format mathematical equations
            if not formatted_content.startswith('\\begin{equation}'):
                formatted_content = f"\\begin{{equation}}\n{formatted_content}\n\\end{{equation}}"
        
        elif content_type == "citation":
            # Format citations
            if not formatted_content.startswith('\\cite'):
                formatted_content = f"\\cite{{{formatted_content}}}"
        
        return f"Formatted {content_type}:\n{formatted_content}"
        
    except Exception as e:
        return f"Error formatting content: {str(e)}"

async def generate_bibliography_tool(**kwargs) -> str:
    """Generate LaTeX bibliography from reference list"""
    
    try:
        references = kwargs.get('references', [])
        
        if not references:
            return "Error: Missing required parameter 'references'"
        
        bib_entries = []
        
        for i, ref in enumerate(references, 1):
            if ref.get('type') == 'article':
                entry = f"\\bibitem{{ref{i}}} {ref.get('authors', 'Unknown')}, \\textit{{{ref.get('title', 'Untitled')}}}, {ref.get('journal', 'Unknown Journal')}, {ref.get('year', 'Unknown Year')}."
            elif ref.get('type') == 'book':
                entry = f"\\bibitem{{ref{i}}} {ref.get('authors', 'Unknown')}, \\textit{{{ref.get('title', 'Untitled')}}}, {ref.get('publisher', 'Unknown Publisher')}, {ref.get('year', 'Unknown Year')}."
            else:
                entry = f"\\bibitem{{ref{i}}} {ref.get('authors', 'Unknown')}, \\textit{{{ref.get('title', 'Untitled')}}}, {ref.get('year', 'Unknown Year')}."
            
            bib_entries.append(entry)
        
        bibliography = '\n'.join(bib_entries)
        return f"Generated bibliography:\n{bibliography}"
        
    except Exception as e:
        return f"Error generating bibliography: {str(e)}"

async def extract_document_sections_tool(**kwargs) -> str:
    """Extract and identify sections from document content"""
    
    try:
        document_content = kwargs.get('document_content', '')
        
        if not document_content:
            return "Error: Missing required parameter 'document_content'"
        
        sections = {
            'title': '',
            'abstract': '',
            'introduction': '',
            'methodology': '',
            'results': '',
            'discussion': '',
            'conclusion': ''
        }
        
        # Simple section detection based on common headers
        lines = document_content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            lower_line = line.lower()
            
            if any(keyword in lower_line for keyword in ['title:', 'title']):
                current_section = 'title'
                sections[current_section] = line.replace('title:', '').replace('Title:', '').strip()
            elif any(keyword in lower_line for keyword in ['abstract:', 'abstract']):
                current_section = 'abstract'
            elif any(keyword in lower_line for keyword in ['introduction:', 'introduction']):
                current_section = 'introduction'
            elif any(keyword in lower_line for keyword in ['method', 'approach']):
                current_section = 'methodology'
            elif any(keyword in lower_line for keyword in ['result', 'finding']):
                current_section = 'results'
            elif any(keyword in lower_line for keyword in ['discussion:', 'discussion']):
                current_section = 'discussion'
            elif any(keyword in lower_line for keyword in ['conclusion:', 'conclusion']):
                current_section = 'conclusion'
            elif current_section and line:
                sections[current_section] += f"\n{line}"
        
        # Clean up sections
        for key in sections:
            sections[key] = sections[key].strip()
        
        return f"Extracted document sections: {json.dumps(sections, indent=2)}"
        
    except Exception as e:
        return f"Error extracting document sections: {str(e)}"

def register_document_tools(server):
    """Register document generation tools with the MCP server"""
    server.tools["generate_latex_document"] = generate_latex_document_tool
    server.tools["compile_latex"] = compile_latex_tool
    server.tools["format_research_content"] = format_research_content_tool
    server.tools["generate_bibliography"] = generate_bibliography_tool
    server.tools["extract_document_sections"] = extract_document_sections_tool
