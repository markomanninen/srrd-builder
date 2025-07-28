"""
Document Generation Tools for SRRD Builder MCP Server
Handles LaTeX generation, formatting, and document compilation
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

from storage.project_manager import ProjectManager
from storage.vector_manager import VectorManager

# Import vector database tools
from .vector_database import retrieve_bibliography_references_tool

# Fix import path issues by adding utils directory to sys.path
current_dir = Path(__file__).parent.parent
utils_dir = current_dir / "utils"
if str(utils_dir) not in sys.path:
    sys.path.insert(0, str(utils_dir))

from context_decorator import context_aware
from current_project import get_current_project as get_project_path

import srrd_builder.config.installation_status

LATEX_TEMPLATE = r"""\documentclass[12pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{amsmath,amsfonts,amssymb}}
\usepackage{{graphicx}}
\usepackage{{hyperref}}
\usepackage{{cite}}
\usepackage{{geometry}}
\usepackage{{fancyhdr}}

\geometry{{margin=1in}}
\pagestyle{{fancy}}
\fancyhf{{}}
\rhead{{\thepage}}
\lhead{{{title}}}

\title{{{title}}}
\author{{{author}}}
\date{{{date}}}

\begin{{document}}

\maketitle

\begin{{abstract}}
{abstract}
\end{{abstract}}

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

\begin{{thebibliography}}{{99}}
{bibliography}
\end{{thebibliography}}

\end{{document}}
"""


class LaTeXTemplateManager:
    """Manages multiple LaTeX templates for different document types and journals"""

    def __init__(self):
        self.templates = {
            "basic_article": {
                "name": "Basic Academic Article",
                "description": "Standard academic article format",
                "template": LATEX_TEMPLATE,
            },
            "nature": {
                "name": "Nature Journal Format",
                "description": "Template following Nature journal guidelines",
                "template": r"""\documentclass[twocolumn]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{amsmath,amsfonts,amssymb}}
\usepackage{{graphicx}}
\usepackage{{natbib}}
\usepackage{{booktabs}}
\usepackage{{hyperref}}
\usepackage{{geometry}}

\geometry{{margin=0.75in}}

\title{{{title}}}
\author{{{author}}}
\date{{{date}}}

\begin{{document}}

\maketitle

\begin{{abstract}}
{abstract}
\end{{abstract}}

\section{{Introduction}}
{introduction}

\section{{Methods}}
{methodology}

\section{{Results}}
{results}

\section{{Discussion}}
{discussion}

\section*{{Acknowledgments}}
We thank the contributors and reviewers for their valuable feedback.

\bibliographystyle{{nature}}
\bibliography{{references}}

\end{{document}}
""",
            },
            "ieee": {
                "name": "IEEE Conference Format",
                "description": "Template for IEEE conference proceedings",
                "template": r"""\documentclass[conference]{{IEEEtran}}
\usepackage[utf8]{{inputenc}}
\usepackage{{amsmath,amsfonts,amssymb}}
\usepackage{{graphicx}}
\usepackage{{cite}}
\usepackage{{hyperref}}

\title{{{title}}}
\author{{\IEEEauthorblockN{{{author}}}
\IEEEauthorblockA{{Institution\\
Email: author@institution.edu}}}}

\begin{{document}}

\maketitle

\begin{{abstract}}
{abstract}
\end{{abstract}}

\begin{{IEEEkeywords}}
keyword1, keyword2, keyword3
\end{{IEEEkeywords}}

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

\begin{{thebibliography}}{{99}}
{bibliography}
\end{{thebibliography}}

\end{{document}}
""",
            },
            "proposal": {
                "name": "Research Proposal",
                "description": "Template for research proposals",
                "template": r"""\documentclass[11pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{amsmath,amsfonts,amssymb}}
\usepackage{{graphicx}}
\usepackage{{natbib}}
\usepackage{{hyperref}}
\usepackage{{geometry}}
\usepackage{{titlesec}}

\geometry{{margin=1in}}

\title{{{title}}}
\author{{{author}}}
\date{{{date}}}

\begin{{document}}

\maketitle

\begin{{abstract}}
{abstract}
\end{{abstract}}

\section{{Research Objectives}}
{introduction}

\section{{Literature Review}}
Please provide a comprehensive literature review here.

\section{{Methodology}}
{methodology}

\section{{Expected Results}}
{results}

\section{{Timeline}}
Please provide a detailed project timeline.

\section{{Budget}}
Please provide budget considerations.

\section{{Significance}}
{discussion}

\bibliographystyle{{apa}}
\bibliography{{references}}

\end{{document}}
""",
            },
            "thesis": {
                "name": "Thesis/Dissertation",
                "description": "Template for thesis and dissertation documents",
                "template": r"""\documentclass[12pt,a4paper]{{report}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{amsmath,amsfonts,amssymb}}
\usepackage{{graphicx}}
\usepackage{{natbib}}
\usepackage{{hyperref}}
\usepackage{{geometry}}
\usepackage{{fancyhdr}}
\usepackage{{setspace}}

\geometry{{margin=1in}}
\doublespacing
\pagestyle{{fancy}}
\fancyhf{{}}
\rhead{{\thepage}}
\lhead{{\leftmark}}

\title{{{title}}}
\author{{{author}}}
\date{{{date}}}

\begin{{document}}

\frontmatter
\maketitle

\begin{{abstract}}
{abstract}
\end{{abstract}}

\tableofcontents
\listoffigures
\listoftables

\mainmatter

\chapter{{Introduction}}
{introduction}

\chapter{{Literature Review}}
Please provide a comprehensive literature review.

\chapter{{Methodology}}
{methodology}

\chapter{{Results}}
{results}

\chapter{{Discussion}}
{discussion}

\chapter{{Conclusion}}
{conclusion}

\chapter{{Future Work}}
Please provide directions for future research.

\bibliographystyle{{apa}}
\bibliography{{references}}

\appendix
\chapter{{Additional Materials}}
Additional materials and appendices can be added here.

\end{{document}}
""",
            },
        }

    def get_template(self, template_type: str = "basic_article") -> dict:
        """Get a specific template by type"""
        return self.templates.get(template_type, self.templates["basic_article"])

    def list_templates(self) -> dict:
        """List all available templates"""
        return {
            key: {"name": template["name"], "description": template["description"]}
            for key, template in self.templates.items()
        }

    def add_custom_template(
        self, template_id: str, name: str, description: str, template_content: str
    ):
        """Add a custom template"""
        self.templates[template_id] = {
            "name": name,
            "description": description,
            "template": template_content,
        }


template_manager = LaTeXTemplateManager()


@context_aware(require_context=True)
async def generate_latex_document_tool(**kwargs) -> str:
    """Generate LaTeX document from research content"""
    project_manager = None
    try:
        title = kwargs.get("title", "Untitled Research Paper")
        author = kwargs.get("author", "SRRD Builder")
        abstract = kwargs.get("abstract", "")
        introduction = kwargs.get("introduction", "")
        methodology = kwargs.get("methodology", "")
        results = kwargs.get("results", "")
        discussion = kwargs.get("discussion", "")
        conclusion = kwargs.get("conclusion", "")
        bibliography = kwargs.get("bibliography", "")
        project_path = get_project_path()

        latex_content = LATEX_TEMPLATE.format(
            title=title,
            author=author,
            date=datetime.now().strftime("%B %d, %Y"),
            abstract=abstract,
            introduction=introduction,
            methodology=methodology,
            results=results,
            discussion=discussion,
            conclusion=conclusion,
            bibliography=bibliography,
        )

        if project_path:
            project_manager = ProjectManager(project_path)
            doc_path = (
                Path(project_path)
                / "documents"
                / f"{title.replace(' ', '_').lower()}.tex"
            )
            doc_path.parent.mkdir(parents=True, exist_ok=True)

            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(latex_content)

            return f"LaTeX document generated successfully at: {doc_path}"
        else:
            return f"LaTeX document generated:\n{latex_content[:500]}..."

    except Exception as e:
        return f"Error generating LaTeX document: {str(e)}"
    finally:
        if project_manager:
            await project_manager.close()


@context_aware(require_context=True)
async def compile_latex_tool(**kwargs) -> str:
    """Compile LaTeX document to PDF or other formats"""
    if not srrd_builder.config.installation_status.is_latex_installed():
        return "LaTeX is not installed. Please run setup with --with-latex."
    try:
        tex_file_path = kwargs.get("tex_file_path")
        output_format = kwargs.get("output_format", "pdf")

        if not tex_file_path:
            return "Error: Missing required parameter 'tex_file_path'"

        tex_path = Path(tex_file_path)
        if not tex_path.exists():
            return f"Error: LaTeX file not found at {tex_file_path}"

        work_dir = tex_path.parent
        tex_filename = tex_path.name

        if output_format.lower() == "pdf":
            import shutil

            if not shutil.which("pdflatex"):
                return f"Error: pdflatex not found. Please install LaTeX distribution:\n- macOS: 'brew install --cask mactex'\n- Ubuntu: 'sudo apt-get install texlive-full'\n- Windows: Install MiKTeX from https://miktex.org/\n\nSee INSTALLATION.md for complete setup guide. The LaTeX source file is available at: {tex_file_path}"

            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_filename],
                cwd=work_dir,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                pdf_path = work_dir / tex_filename.replace(".tex", ".pdf")
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
                    error_info = [
                        "LaTeX compilation failed with no error output. The LaTeX file may contain syntax errors."
                    ]

                try:
                    with open(tex_path, "r") as f:
                        content = f.read().strip()
                    if not content.startswith(
                        "\\documentclass"
                    ) and not content.startswith("\\begin{document}"):
                        error_info.append(
                            f"Note: The file may not contain valid LaTeX syntax. LaTeX files should start with \\documentclass or \\begin{{document}}."
                        )
                except:
                    pass

                return f"LaTeX compilation error: {' | '.join(error_info)}"
        else:
            return f"Unsupported output format: {output_format}"

    except Exception as e:
        return f"Error compiling LaTeX: {str(e)}"


@context_aware(require_context=False)
async def format_research_content_tool(**kwargs) -> str:
    """Format research content according to academic standards"""
    try:
        content = kwargs.get("content", "")
        content_type = kwargs.get("content_type", "section")
        formatting_style = kwargs.get("formatting_style", "academic")

        if not content:
            return "Error: Missing required parameter 'content'"

        formatted_content = content.strip()

        if content_type == "section":
            lines = formatted_content.split("\n")
            formatted_lines = []

            for line in lines:
                line = line.strip()
                if line:
                    if len(formatted_lines) == 0 and line[0].islower():
                        line = line[0].upper() + line[1:]
                    formatted_lines.append(line)
                else:
                    formatted_lines.append("")

            formatted_content = "\n\n".join([line for line in formatted_lines if line])

        elif content_type == "equation":
            if not formatted_content.startswith("\\begin{equation}"):
                formatted_content = (
                    f"\\begin{{equation}}\n{formatted_content}\n\\end{{equation}}"
                )

        elif content_type == "citation":
            if not formatted_content.startswith("\\cite"):
                formatted_content = f"\\cite{{{formatted_content}}}"

        return f"Formatted content:\n{formatted_content}"

    except Exception as e:
        return f"Error formatting content: {str(e)}"


@context_aware(require_context=False)
async def generate_bibliography_tool(**kwargs) -> str:
    """Generate LaTeX bibliography from reference list"""
    try:
        references = kwargs.get("references", [])

        if not references:
            return "Error: Missing required parameter 'references'"

        bib_entries = []

        for i, ref in enumerate(references, 1):
            if isinstance(ref, dict):
                title = ref.get("title", "Unknown Title")
                authors = ref.get("authors", "Unknown Author")
                year = ref.get("year", "Unknown Year")
                journal = ref.get("journal", "")

                if journal:
                    bib_entry = f"\\bibitem{{ref{i}}} {authors}. {title}. \\textit{{{journal}}}, {year}."
                else:
                    bib_entry = f"\\bibitem{{ref{i}}} {authors}. {title}. {year}."

                bib_entries.append(bib_entry)
            else:
                bib_entries.append(f"\\bibitem{{ref{i}}} {ref}")

        bibliography = "\n\n".join(bib_entries)

        return f"Generated bibliography:\n{bibliography}"

    except Exception as e:
        return f"Error generating bibliography: {str(e)}"


@context_aware(require_context=False)
async def extract_document_sections_tool(**kwargs) -> str:
    """Extract and identify sections from document content for modular LaTeX management"""
    project_manager = None
    try:
        document_content = kwargs.get("document_content", "")
        create_separate_files = kwargs.get("create_separate_files", False)

        if not document_content:
            return "Error: Missing required parameter 'document_content'"

        project_path = get_project_path()
        if create_separate_files and not project_path:
            return "Error: A project context is required when create_separate_files is True."

        section_patterns = [
            r"\\section\{([^}]+)\}",
            r"\\subsection\{([^}]+)\}",
            r"\\subsubsection\{([^}]+)\}",
            r"(?i)(?:^|\n)\s*(abstract|introduction|methodology|methods|results|discussion|conclusion|references|bibliography|acknowledgments?)\s*(?:\n|:|\.|$)",
            r"(?i)(?:^|\n)\s*(\d+\.?\s*[A-Z][^.\n]*(?:introduction|methodology|methods|results|discussion|conclusion))\s*(?:\n|$)",
        ]

        sections = {}
        current_section = "preamble"
        current_content = []
        document_started = False

        lines = document_content.split("\n")

        for line in lines:
            if "\\begin{document}" in line:
                if current_section == "preamble":
                    sections["preamble"] = "\n".join(current_content).strip()
                    current_content = []
                document_started = True
                continue
            elif "\\end{document}" in line:
                if current_content and current_section != "preamble":
                    sections[current_section] = "\n".join(current_content).strip()
                break

            if document_started and (
                "\\maketitle" in line or "\\begin{document}" in line
            ):
                continue

            section_found = False
            if document_started:
                for pattern in section_patterns:
                    import re

                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        if current_content and current_section != "preamble":
                            sections[current_section] = "\n".join(
                                current_content
                            ).strip()

                        section_name = match.group(1).lower().replace(" ", "_")
                        current_section = section_name
                        current_content = [line]
                        section_found = True
                        break

            if not section_found:
                current_content.append(line)

        if current_content and current_section != "preamble":
            sections[current_section] = "\n".join(current_content).strip()

        if create_separate_files and project_path:
            project_manager = ProjectManager(project_path)
            sections_dir = Path(project_path) / "sections"
            sections_dir.mkdir(exist_ok=True)
            main_tex_includes = []

            for section_name, content in sections.items():
                if section_name != "preamble" and content.strip():
                    clean_content = content.strip()
                    section_file = sections_dir / f"{section_name}.tex"
                    with open(section_file, "w", encoding="utf-8") as f:
                        f.write(clean_content)
                    main_tex_includes.append(f"\\input{{../sections/{section_name}}}")

            if main_tex_includes:
                main_doc_path = Path(project_path) / "documents" / "main.tex"
                main_doc_path.parent.mkdir(parents=True, exist_ok=True)
                preamble = sections.get("preamble", "").strip()
                main_document = f"""{preamble}
\\begin{{document}}
\\maketitle
{chr(10).join(main_tex_includes)}
\\end{{document}}
"""
                with open(main_doc_path, "w", encoding="utf-8") as f:
                    f.write(main_document)
                return f"Document sections extracted and modularized:\n- Main document: {main_doc_path}\n- Sections directory: {sections_dir}\n- Created {len(main_tex_includes)} separate section files"

        result = "Extracted document sections:\n\n"
        for section_name, content in sections.items():
            preview = content[:100] + "..." if len(content) > 100 else content
            result += f"**{section_name.upper()}:**\n{preview}\n\n"

        return result

    except Exception as e:
        return f"Error extracting document sections: {str(e)}"
    finally:
        if project_manager:
            await project_manager.close()


@context_aware(require_context=True)
async def generate_document_with_database_bibliography_tool(**kwargs) -> str:
    """Generate LaTeX document with bibliography retrieved from vector database"""
    project_manager = None
    try:
        title = kwargs.get("title", "Untitled Research Paper")
        author = kwargs.get("author", "SRRD Builder")
        abstract = kwargs.get("abstract", "")
        introduction = kwargs.get("introduction", "")
        methodology = kwargs.get("methodology", "")
        results = kwargs.get("results", "")
        discussion = kwargs.get("discussion", "")
        conclusion = kwargs.get("conclusion", "")
        project_path = get_project_path()
        bibliography_query = kwargs.get("bibliography_query", "")

        bibliography = ""
        if bibliography_query:
            bib_result = await retrieve_bibliography_references_tool(
                query=bibliography_query, project_path=project_path, max_results=10
            )
            if "Retrieved" in bib_result and "references:" in bib_result:
                bib_lines = bib_result.split("\n")
                bib_entries = [
                    line.strip()
                    for line in bib_lines
                    if line.strip().startswith("\\bibitem")
                ]
                bibliography = "\n".join(bib_entries)

        latex_content = LATEX_TEMPLATE.format(
            title=title,
            author=author,
            date=datetime.now().strftime("%B %d, %Y"),
            abstract=abstract,
            introduction=introduction,
            methodology=methodology,
            results=results,
            discussion=discussion,
            conclusion=conclusion,
            bibliography=bibliography,
        )

        if project_path:
            project_manager = ProjectManager(project_path)
            doc_path = (
                Path(project_path)
                / "documents"
                / f"{title.replace(' ', '_').lower()}_with_db_bib.tex"
            )
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(latex_content)
            return f"LaTeX document with database bibliography generated successfully at: {doc_path}"
        else:
            return f"LaTeX document with database bibliography generated:\n{latex_content[:500]}..."

    except Exception as e:
        return f"Error generating document with database bibliography: {str(e)}"
    finally:
        if project_manager:
            await project_manager.close()


@context_aware(require_context=False)
async def list_latex_templates_tool(**kwargs) -> str:
    """List all available LaTeX templates"""
    try:
        templates = template_manager.list_templates()
        result = "Available LaTeX Templates:\n\n"

        for template_id, info in templates.items():
            result += f"- **{template_id}**: {info['name']}\n"
            result += f"  {info['description']}\n\n"

        return result
    except Exception as e:
        return f"Error listing templates: {str(e)}"


@context_aware(require_context=True)
async def generate_latex_with_template_tool(**kwargs) -> str:
    """Generate LaTeX document using a specific template"""
    project_manager = None
    try:
        title = kwargs.get("title", "Untitled Research Document")
        author = kwargs.get("author", "SRRD Builder")
        abstract = kwargs.get("abstract", "")
        introduction = kwargs.get("introduction", "")
        methodology = kwargs.get("methodology", "")
        results = kwargs.get("results", "")
        discussion = kwargs.get("discussion", "")
        conclusion = kwargs.get("conclusion", "")
        bibliography = kwargs.get("bibliography", "")
        project_path = get_project_path()
        template_type = kwargs.get("template_type", "basic_article")

        template_info = template_manager.get_template(template_type)
        latex_template = template_info["template"]

        latex_content = latex_template.format(
            title=title,
            author=author,
            date=datetime.now().strftime("%B %d, %Y"),
            abstract=abstract,
            introduction=introduction,
            methodology=methodology,
            results=results,
            discussion=discussion,
            conclusion=conclusion,
            bibliography=bibliography,
        )

        if project_path:
            project_manager = ProjectManager(project_path)
            doc_path = (
                Path(project_path)
                / "documents"
                / f"{title.replace(' ', '_').lower()}_{template_type}.tex"
            )
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(latex_content)
            return f"LaTeX document generated using '{template_info['name']}' template at: {doc_path}"
        else:
            return f"LaTeX document generated using '{template_info['name']}' template:\n{latex_content[:500]}..."

    except Exception as e:
        return f"Error generating LaTeX document with template: {str(e)}"
    finally:
        if project_manager:
            await project_manager.close()


import os


def register_document_tools(server):
    """Register document generation tools with the MCP server"""

    if srrd_builder.config.installation_status.is_latex_installed():
        server.register_tool(
            name="generate_latex_document",
            description="Generate LaTeX research document",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title"},
                    "author": {"type": "string", "description": "Author name"},
                    "abstract": {"type": "string", "description": "Abstract content"},
                    "introduction": {
                        "type": "string",
                        "description": "Introduction section",
                    },
                    "methodology": {
                        "type": "string",
                        "description": "Methodology section",
                    },
                    "results": {"type": "string", "description": "Results section"},
                    "discussion": {
                        "type": "string",
                        "description": "Discussion section",
                    },
                    "conclusion": {
                        "type": "string",
                        "description": "Conclusion section",
                    },
                    "bibliography": {
                        "type": "string",
                        "description": "Bibliography content",
                    },
                },
                "required": ["title"],
            },
            handler=generate_latex_document_tool,
        )
        server.register_tool(
            name="compile_latex",
            description="Compile LaTeX document to PDF",
            parameters={
                "type": "object",
                "properties": {
                    "tex_file_path": {"type": "string", "description": "Path to .tex file"},
                    "output_format": {
                        "type": "string",
                        "description": "Output format (pdf)",
                        "default": "pdf",
                    },
                },
                "required": ["tex_file_path"],
            },
            handler=compile_latex_tool,
        )

        server.register_tool(
            name="generate_bibliography",
            description="Generate LaTeX bibliography from reference list",
            parameters={
                "type": "object",
                "properties": {
                    "references": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of references",
                    }
                },
                "required": ["references"],
            },
            handler=generate_bibliography_tool,
        )

        server.register_tool(
            name="extract_document_sections",
            description="Extract and identify sections from document content for modular LaTeX management",
            parameters={
                "type": "object",
                "properties": {
                    "document_content": {
                        "type": "string",
                        "description": "Document content to analyze",
                    },
                    "create_separate_files": {
                        "type": "boolean",
                        "description": "Create separate .tex files for each section",
                        "default": False,
                    },
                },
                "required": ["document_content"],
            },
            handler=extract_document_sections_tool,
        )

        server.register_tool(
            name="generate_document_with_database_bibliography",
            description="Generate LaTeX document with bibliography retrieved from vector database",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title"},
                    "author": {"type": "string", "description": "Author name"},
                    "abstract": {"type": "string", "description": "Abstract content"},
                    "introduction": {
                        "type": "string",
                        "description": "Introduction section",
                    },
                    "methodology": {"type": "string", "description": "Methodology section"},
                    "results": {"type": "string", "description": "Results section"},
                    "discussion": {"type": "string", "description": "Discussion section"},
                    "conclusion": {"type": "string", "description": "Conclusion section"},
                    "bibliography_query": {
                        "type": "string",
                        "description": "Query to retrieve relevant bibliography from database",
                    },
                },
                "required": ["title", "bibliography_query"],
            },
            handler=generate_document_with_database_bibliography_tool,
        )

        server.register_tool(
            name="list_latex_templates",
            description="List all available LaTeX templates",
            parameters={"type": "object", "properties": {}, "required": []},
            handler=list_latex_templates_tool,
        )

        server.register_tool(
            name="generate_latex_with_template",
            description="Generate LaTeX document using a specific template",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title"},
                    "author": {"type": "string", "description": "Author name"},
                    "abstract": {"type": "string", "description": "Abstract content"},
                    "introduction": {
                        "type": "string",
                        "description": "Introduction section",
                    },
                    "methodology": {"type": "string", "description": "Methodology section"},
                    "results": {"type": "string", "description": "Results section"},
                    "discussion": {"type": "string", "description": "Discussion section"},
                    "conclusion": {"type": "string", "description": "Conclusion section"},
                    "bibliography": {
                        "type": "string",
                        "description": "Bibliography content",
                    },
                    "template_type": {
                        "type": "string",
                        "description": "Type of template to use",
                        "default": "basic_article",
                    },
                },
                "required": ["title"],
            },
            handler=generate_latex_with_template_tool,
        )

    # Non-LaTeX specific tools that are always available
    server.register_tool(
        name="format_research_content",
        description="Format research content according to academic standards",
        parameters={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content to format"},
                "content_type": {
                    "type": "string",
                    "description": "Type of content (section, equation, citation)",
                    "default": "section",
                },
                "formatting_style": {
                    "type": "string",
                    "description": "Formatting style (academic)",
                    "default": "academic",
                },
            },
            "required": ["content"],
        },
        handler=format_research_content_tool,
    )


__all__ = [
    "generate_latex_document_tool",
    "compile_latex_tool",
    "format_research_content_tool",
    "generate_bibliography_tool",
    "extract_document_sections_tool",
    "generate_document_with_database_bibliography_tool",
    "register_document_tools",
]
