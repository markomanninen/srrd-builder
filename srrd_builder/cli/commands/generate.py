"""
SRRD Generate Command - Generate research documents
"""

import json
from pathlib import Path

def handle_generate(args):
    """Handle 'srrd generate' command"""
    current_dir = Path.cwd()
    
    # Check if SRRD is initialized
    srrd_dir = current_dir / '.srrd'
    if not srrd_dir.exists():
        print("❌ SRRD not initialized in current directory")
        print("   Run 'srrd init' first")
        return 1
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📝 Generating {args.doc_type}: {args.title}")
    print(f"   Output: {output_dir}")
    
    if args.doc_type == 'proposal':
        return generate_proposal(args, output_dir, srrd_dir)
    elif args.doc_type == 'manuscript':
        return generate_manuscript(args, output_dir, srrd_dir)
    elif args.doc_type == 'latex':
        return generate_latex(args, output_dir, srrd_dir)
    else:
        print(f"❌ Unknown document type: {args.doc_type}")
        return 1

def generate_proposal(args, output_dir: Path, srrd_dir: Path):
    """Generate research proposal"""
    # Basic proposal template
    latex_content = f"""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}

\\title{{{args.title}}}
\\author{{Author Name}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\section{{Introduction}}
[Introduction section - describe the problem and motivation]

\\section{{Literature Review}}
[Review of relevant literature and existing work]

\\section{{Methodology}}
[Proposed research methodology and approach]

\\section{{Expected Outcomes}}
[Expected results and contributions]

\\section{{Timeline}}
[Project timeline and milestones]

\\section{{Budget}}
[Resource requirements and budget]

\\bibliographystyle{{plain}}
\\bibliography{{references}}

\\end{{document}}
"""
    
    # Write LaTeX file
    output_file = output_dir / 'proposal.tex'
    with open(output_file, 'w') as f:
        f.write(latex_content)
    
    print(f"✅ Proposal generated: {output_file}")
    print("   Edit the template and compile with: pdflatex proposal.tex")
    return 0

def generate_manuscript(args, output_dir: Path, srrd_dir: Path):
    """Generate manuscript template"""
    latex_content = f"""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}

\\title{{{args.title}}}
\\author{{Author Name}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
[Abstract - brief summary of the work]
\\end{{abstract}}

\\section{{Introduction}}
[Introduction - background and motivation]

\\section{{Methods}}
[Methodology and experimental approach]

\\section{{Results}}
[Results and findings]

\\section{{Discussion}}
[Discussion and interpretation]

\\section{{Conclusion}}
[Conclusions and future work]

\\bibliographystyle{{plain}}
\\bibliography{{references}}

\\end{{document}}
"""
    
    output_file = output_dir / 'manuscript.tex'
    with open(output_file, 'w') as f:
        f.write(latex_content)
    
    print(f"✅ Manuscript generated: {output_file}")
    return 0

def generate_latex(args, output_dir: Path, srrd_dir: Path):
    """Generate basic LaTeX document"""
    latex_content = f"""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}

\\title{{{args.title}}}
\\author{{Author}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\section{{Section 1}}
Content here.

\\end{{document}}
"""
    
    output_file = output_dir / 'document.tex'
    with open(output_file, 'w') as f:
        f.write(latex_content)
    
    print(f"✅ LaTeX document generated: {output_file}")
    return 0
