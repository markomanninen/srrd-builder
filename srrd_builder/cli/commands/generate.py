"""
SRRD Generate Command - LaTeX compilation and build automation
Focuses on build processes, not content creation (that's for MCP)
"""

import subprocess
from pathlib import Path
import json
import shutil
from srrd_builder.config.installation_status import is_latex_installed

def handle_generate(args):
    """Handle 'srrd generate' command"""
    current_dir = Path.cwd()
    
    # Check if SRRD is initialized
    srrd_dir = find_srrd_root(current_dir)
    if not srrd_dir:
        print("❌ SRRD not initialized in current directory or parent directories")
        print("   Run 'srrd init' first")
        return 1
    
    if args.subcommand == 'pdf':
        return generate_pdf(args, srrd_dir.parent)
    elif args.subcommand == 'template':
        return generate_template(args, srrd_dir.parent)
    else:
        print(f"❌ Unknown generate subcommand: {args.subcommand}")
        return 1

def find_srrd_root(path: Path) -> Path:
    """Find .srrd directory in current or parent directories"""
    current = path.resolve()
    while current != current.parent:
        srrd_dir = current / '.srrd'
        if srrd_dir.exists():
            return srrd_dir
        current = current.parent
    return None

def generate_pdf(args, project_root: Path):
    """Compile LaTeX document to PDF"""
    # Check if LaTeX is installed according to configuration
    if not is_latex_installed():
        print("❌ LaTeX is not installed according to system configuration")
        print("   Please run 'setup.sh --with-latex' to install LaTeX")
        print("   Or install LaTeX manually:")
        print("     macOS: brew install --cask mactex")
        print("     Ubuntu: sudo apt-get install texlive-latex-extra")
        return 1
    
    tex_file = args.input
    if not tex_file:
        print("❌ No input file specified")
        print("   Usage: srrd generate pdf input.tex [--output dir/]")
        return 1
    
    tex_path = Path(tex_file).resolve()  # Convert to absolute path
    if not tex_path.exists():
        print(f"❌ File not found: {tex_file}")
        return 1
    
    if not tex_path.suffix == '.tex':
        print(f"❌ Input must be a .tex file, got: {tex_path.suffix}")
        return 1
    
    print(f"📄 Compiling LaTeX: {tex_path}")
    
    # Compile with pdflatex
    try:
        # First pass - use filename only since we're setting cwd to parent
        result = subprocess.run([
            'pdflatex', 
            '-interaction=nonstopmode',
            '-output-directory', '.',
            tex_path.name  # Use just the filename
        ], capture_output=True, text=True, cwd=tex_path.parent)
        
        if result.returncode != 0:
            print("❌ LaTeX compilation failed (first pass)")
            print("LaTeX output:")
            print(result.stdout[-1000:])  # Last 1000 chars
            return 1
        
        # Check if bibliography exists and run bibtex if needed
        bib_file = tex_path.with_suffix('.bib')
        aux_file = tex_path.with_suffix('.aux')
        
        if bib_file.exists() and aux_file.exists():
            print("📚 Processing bibliography...")
            bibtex_result = subprocess.run([
                'bibtex', str(aux_file.stem)
            ], capture_output=True, text=True, cwd=tex_path.parent)
            
            if bibtex_result.returncode == 0:
                # Second pass for bibliography
                subprocess.run([
                    'pdflatex', 
                    '-interaction=nonstopmode',
                    '-output-directory', '.',
                    tex_path.name
                ], capture_output=True, text=True, cwd=tex_path.parent)
                
                # Third pass for cross-references
                subprocess.run([
                    'pdflatex', 
                    '-interaction=nonstopmode',
                    '-output-directory', '.',
                    tex_path.name
                ], capture_output=True, text=True, cwd=tex_path.parent)
        
        pdf_file = tex_path.with_suffix('.pdf')
        if pdf_file.exists():
            # Move to output directory if specified
            if args.output:
                output_dir = Path(args.output)
                output_dir.mkdir(parents=True, exist_ok=True)
                final_pdf = output_dir / pdf_file.name
                shutil.move(str(pdf_file), str(final_pdf))
                print(f"✅ PDF generated: {final_pdf}")
            else:
                print(f"✅ PDF generated: {pdf_file}")
            
            return 0
        else:
            print("❌ PDF was not generated")
            return 1
            
    except FileNotFoundError:
        print("❌ pdflatex not found. Please install LaTeX:")
        print("   macOS: brew install --cask mactex")
        print("   Ubuntu: sudo apt-get install texlive-latex-extra")
        return 1
    except Exception as e:
        print(f"❌ Compilation error: {e}")
        return 1

def generate_template(args, project_root: Path):
    """Generate basic LaTeX template (no AI content)"""
    template_type = args.template_type
    title = args.title
    output = args.output or "documents/"
    
    if not title:
        print("❌ Title is required")
        print("   Usage: srrd generate template proposal --title 'My Research'")
        return 1
    
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📝 Generating {template_type} template: {title}")
    
    if template_type == 'proposal':
        return create_proposal_template(title, output_dir)
    elif template_type == 'paper':
        return create_paper_template(title, output_dir)
    elif template_type == 'thesis':
        return create_thesis_template(title, output_dir)
    else:
        print(f"❌ Unknown template type: {template_type}")
        print("   Available: proposal, paper, thesis")
        return 1

def create_proposal_template(title: str, output_dir: Path):
    """Create research proposal template"""
    filename = title.lower().replace(' ', '_').replace('-', '_') + '.tex'
    output_file = output_dir / filename
    
    template_content = f"""\\documentclass[11pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath,amsfonts,amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{natbib}}
\\usepackage{{hyperref}}
\\usepackage{{geometry}}
\\geometry{{margin=1in}}

\\title{{{title}}}
\\author{{[Author Name]\\\\[0.5em] [Institution]\\\\[0.5em] [Email]}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\section{{Research Objectives}}
% Clearly state your research goals and what you aim to achieve
% Use bullet points or numbered lists for clarity

\\section{{Background and Significance}}
% Provide context for your research
% Explain why this research is important
% Review relevant literature

\\section{{Research Questions}}
% List your primary and secondary research questions
% Ensure they are specific and answerable

\\section{{Methodology}}
% Describe your research approach
% Explain data collection methods
% Outline analysis procedures

\\section{{Timeline and Milestones}}
% Provide a realistic timeline
% Include major milestones and deliverables

\\section{{Resources and Budget}}
% List required resources
% Provide budget breakdown if applicable

\\section{{Expected Outcomes}}
% Describe anticipated results
% Explain potential impact and applications

\\section{{Risk Assessment}}
% Identify potential risks and challenges
% Propose mitigation strategies

\\bibliographystyle{{apa}}
\\bibliography{{references}}

\\end{{document}}
"""
    
    with open(output_file, 'w') as f:
        f.write(template_content)
    
    # Create accompanying bibliography file
    bib_file = output_file.with_suffix('.bib')
    bib_content = """% Bibliography for research proposal
% Add your references here in BibTeX format
% Example:
%
% @article{example2023,
%   title={Example Research Paper},
%   author={Author, A. and Coauthor, B.},
%   journal={Journal of Example Research},
%   volume={12},
%   number={3},
%   pages={45--67},
%   year={2023},
%   publisher={Example Publisher}
% }
"""
    
    with open(bib_file, 'w') as f:
        f.write(bib_content)
    
    print(f"✅ LaTeX template generated: {output_file}")
    print(f"✅ Bibliography file created: {bib_file}")
    print("\n💡 Next steps:")
    print(f"   1. Edit the template: {output_file}")
    print(f"   2. Add references to: {bib_file}")
    print(f"   3. Compile: srrd generate pdf {output_file}")
    return 0

def create_paper_template(title: str, output_dir: Path):
    """Create paper template"""
    filename = title.lower().replace(' ', '_').replace('-', '_') + '.tex'
    output_file = output_dir / filename
    
    template_content = f"""\\documentclass[twocolumn]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath,amsfonts,amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{natbib}}
\\usepackage{{booktabs}}
\\usepackage{{hyperref}}

\\title{{{title}}}
\\author{{[Author Name]$^{{1}}$, [Coauthor Name]$^{{2}}$\\\\
$^{{1}}$[Institution 1]\\\\
$^{{2}}$[Institution 2]}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
% Write a concise abstract (150-250 words)
% Include: background, methods, results, conclusions
\\end{{abstract}}

\\section{{Introduction}}
% Provide background and context
% State the research problem
% Outline the study objectives

\\section{{Methods}}
% Describe your methodology
% Include sufficient detail for reproducibility
% Reference established protocols

\\section{{Results}}
% Present your findings
% Use figures and tables appropriately
% Be objective and factual

\\section{{Discussion}}
% Interpret your results
% Compare with existing literature
% Discuss limitations
% Suggest future research

\\section{{Conclusion}}
% Summarize key findings
% Restate significance
% Provide final thoughts

\\section*{{Acknowledgments}}
% Acknowledge funding sources
% Thank contributors and advisors

\\bibliographystyle{{nature}}
\\bibliography{{references}}

\\end{{document}}
"""
    
    with open(output_file, 'w') as f:
        f.write(template_content)
    
    # Create bibliography file
    bib_file = output_file.with_suffix('.bib')
    with open(bib_file, 'w') as f:
        f.write("% Add your manuscript references here\n")
    
    print(f"✅ LaTeX template generated: {output_file}")
    print(f"✅ Bibliography file created: {bib_file}")
    return 0

def create_thesis_template(title: str, output_dir: Path):
    """Create thesis template"""
    filename = title.lower().replace(' ', '_').replace('-', '_') + '.tex'
    output_file = output_dir / filename
    
    template_content = f"""\\documentclass[12pt,a4paper]{{report}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath,amsfonts,amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{natbib}}
\\usepackage{{hyperref}}
\\usepackage{{geometry}}
\\geometry{{margin=1in}}
\\usepackage{{setspace}}
\\doublespacing

\\title{{{title}}}
\\author{{[Your Name]}}
\\date{{[Submission Date]}}

\\begin{{document}}

\\maketitle

\\tableofcontents
\\newpage

\\begin{{abstract}}
% Write your thesis abstract here
\\end{{abstract}}

\\chapter{{Introduction}}
% Introduction to your research topic
% Problem statement
% Research objectives

\\chapter{{Literature Review}}
% Comprehensive review of existing literature
% Theoretical framework
% Research gaps

\\chapter{{Methodology}}
% Research design
% Data collection methods
% Analysis procedures

\\chapter{{Results}}
% Present your findings
% Use appropriate figures and tables

\\chapter{{Discussion}}
% Interpret results
% Compare with literature
% Discuss implications

\\chapter{{Conclusion}}
% Summarize findings
% Contributions to knowledge
% Future research directions

\\bibliographystyle{{apa}}
\\bibliography{{references}}

\\end{{document}}
"""
    
    with open(output_file, 'w') as f:
        f.write(template_content)
    
    print(f"✅ LaTeX template generated: {output_file}")
    return 0

def generate_bibliography(args, project_root: Path):
    """Generate bibliography from .bib files"""
    print("📚 Bibliography generation not yet implemented")
    print("   Use MCP server tools for advanced bibliography management")
    return 0
