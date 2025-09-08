#!/usr/bin/env python3
"""
Simple notebook publishing script for BIRN workshop.
Processes notebooks with metadata and solution-tagged cells.
"""

import json
from pathlib import Path
import zipfile
from glob import glob
import yaml
import re
import shutil
import subprocess
import sys
try:
    import markdown
except ImportError:
    print("Warning: 'markdown' package not installed. Install with: pip install markdown")
    markdown = None

def get_notebook_metadata(notebook):
    """Extract workshop metadata from notebook."""
    return notebook.get('metadata', {}).get('workshop', {})

def extract_markdown_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    
    if match:
        yaml_content = match.group(1)
        markdown_content = match.group(2)
        try:
            frontmatter = yaml.safe_load(yaml_content)
            return frontmatter, markdown_content
        except:
            print(f"Warning: Invalid YAML frontmatter")
            return {}, content
    return {}, content

def generate_toc_from_markdown(markdown_content, has_useful_links=False):
    """Generate a table of contents from second-level headers (##) in markdown content."""
    # Find all second-level headers
    header_pattern = r'^## (.+)$'
    headers = re.findall(header_pattern, markdown_content, re.MULTILINE)
    
    # Add Useful Links to the beginning if it exists
    if has_useful_links:
        headers = ["Useful Links"] + headers
    
    if not headers:
        return ""
    
    # Build TOC
    toc_lines = ["## Table of Contents\n"]
    for header in headers:
        # Create anchor link - remove special characters and convert spaces to hyphens
        anchor = re.sub(r'[^\w\s-]', '', header).strip().lower().replace(' ', '-')
        toc_lines.append(f"- [{header}](#{anchor})")
    
    return "\n".join(toc_lines) + "\n"

def markdown_to_html(content, title=""):
    """Convert markdown to HTML with basic styling."""
    if markdown:
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite', 'toc'])
    else:
        # Fallback: just wrap in pre tags if markdown not available
        html_content = f"<pre>{content}</pre>"
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <style>
        body {{
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 16px;
            padding-bottom: 5em;
        }}
        h1, h3, h4 {{ margin-top: 2em; }}
        h2 {{
            position: sticky;
            top: 0;
            background: white;
            padding-top: 2em;
            padding-bottom: 0.5em;
            z-index: 100;
            border-bottom: 2px solid #eee;
        }}
        /* Give the first h2 (Table of Contents) less top margin */
        h2:first-of-type {{
            margin-top: 1em;
            padding-top: 1em;
        }}
        h3 a {{
            text-decoration: none;
        }}
        h3 a:hover {{
            text-decoration: underline;
        }}
        p {{
            margin: 1em 0;
        }}
        code {{ 
            background: #f4f4f4; 
            padding: 2px 4px; 
            border-radius: 3px;
            font-family: Consolas, Monaco, monospace;
        }}
        pre {{ 
            background: #f4f4f4; 
            padding: 1em; 
            border-radius: 5px; 
            overflow-x: auto;
        }}
        pre code {{ background: none; padding: 0; }}
        a {{ color: #0066cc; }}
        img {{
            display: block;
            max-width: 80%;
            height: auto;
            margin: 1em auto;
            border: solid 1px #999;
        }}
        blockquote {{
            border-left: solid lightblue 20px;
            margin-left: 4em;
            padding-left: 1em;
            color: #999;
        }}
        video {{
            display: block;
            max-width: 80%;
            height: auto;
            margin: 1em auto;
            border: solid 1px #999;
        }}
        .download-box {{
            background: #e8f4f8;
            padding: 1em;
            border-radius: 5px;
            margin: 1em 0;
        }}
        ul {{
            list-style-type: disc;
            padding-left: 2em;
            margin: 0.5em 0;
        }}
        li {{
            margin: 0.3em 0;
        }}
        .section-header {{
            margin-top: 2em;
            margin-bottom: 1em;
            padding-bottom: 0.5em;
            border-bottom: 2px solid #eee;
        }}
        .resource-buttons {{
            margin: 1em 0;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5em;
        }}
        .resource-button {{
            display: inline-block;
            padding: 0.4em 0.8em;
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 4px;
            text-decoration: none;
            color: #333;
            font-size: 0.9em;
            transition: all 0.2s;
        }}
        .resource-button:hover {{
            background: #e0e0e0;
            border-color: #ccc;
        }}
        .resource-button.primary {{
            background: #e3f2fd;
            color: #1565c0;
            border-color: #90caf9;
        }}
        .resource-button.primary:hover {{
            background: #bbdefb;
            border-color: #64b5f6;
        }}
        .resource-button.completed {{
            background: #e8f5e9;
            color: #2e7d32;
            border-color: #a5d6a7;
        }}
        .resource-button.completed:hover {{
            background: #c8e6c9;
            border-color: #81c784;
        }}
        .data-download {{
            margin: 0.5em 0;
            font-size: 0.9em;
        }}
        .download-links {{
            margin: 0.5em 0;
            line-height: 1.8;
        }}
        .download-links a {{
            color: #1976d2;
            text-decoration: none;
        }}
        .download-links a:hover {{
            text-decoration: underline;
        }}
        p:last {{
            margin-bottom: 0;
            margin-top: 5em;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

def load_config():
    """Load workshop configuration from YAML file."""
    config_path = Path('workshop-config.yaml')
    if not config_path.exists():
        print("Warning: workshop-config.yaml not found, using defaults")
        return {
            'github_repo': 'jsoma/natural-pdf-workshop',
            'github_branch': 'main',
            'title': 'Workshop',
            'description': '',
            'output_dir': 'docs'
        }
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_setup_cell(zip_name, config, install_packages="pandas natural_pdf tqdm", links=None):
    """Create setup cell that works in Colab, Jupyter, etc."""
    github_repo = config['github_repo']
    github_branch = config.get('github_branch', 'main')
    output_dir = config.get('output_dir', 'docs')
    
    source_lines = [
        "# First we need to download some things!\n",
        "# Run this cell to get the necessary data and software\n"
        "import os\n",
        "import urllib.request\n",
        "import zipfile\n",
        "\n",
    ]
    
    # Handle package installation
    if install_packages:
        source_lines.append("# Install required packages\n")
        if isinstance(install_packages, str):
            # If it's a string, split it into a list
            packages = install_packages.split()
        elif isinstance(install_packages, list):
            packages = install_packages
        else:
            packages = []
            
        # Install each package separately
        for package in packages:
            if package.strip():  # Only if package name is not empty
                source_lines.append(f"!pip install --upgrade --quiet {package.strip()}\n")
        source_lines.append("\n")
    
    source_lines.extend([
        "# Download and extract data files\n",
        f"url = 'https://github.com/{github_repo}/raw/{github_branch}/{output_dir}/{zip_name}'\n",
        "print(f'Downloading data from {url}...')\n",
        f"urllib.request.urlretrieve(url, '{zip_name}')\n",
        "\n",
        f"print('Extracting {zip_name}...')\n",
        f"with zipfile.ZipFile('{zip_name}', 'r') as zip_ref:\n",
        "    zip_ref.extractall('.')\n",
        "\n",
        f"os.remove('{zip_name}')\n",
        "print('✓ Data files extracted!')"
    ])
    
    # Add links section if provided
    if links:
        source_lines.extend([
            "\n",
            "# Useful links:\n"
        ])
        for link in links:
            name = link.get('name', 'Link')
            url = link.get('url', '#')
            desc = link.get('description', '')
            if desc:
                source_lines.append(f"# - {name}: {url} ({desc})\n")
            else:
                source_lines.append(f"# - {name}: {url}\n")
    
    return {
        "cell_type": "code",
        "metadata": {},
        "source": source_lines,
        "execution_count": None,
        "outputs": []
    }

def process_notebook(notebook_path, output_dir, config, section_slides=None):
    """Process a single notebook and return info for index."""
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    metadata = get_notebook_metadata(notebook)
    if not metadata:
        print(f"Skipping {notebook_path} - no workshop metadata")
        return None
    
    # If no item-specific slides, use section slides
    if not metadata.get('slides') and section_slides:
        metadata['slides'] = section_slides
    
    base_name = notebook_path.stem
    notebook_dir = notebook_path.parent
    
    # Create complete version (ANSWERS)
    complete_nb = notebook.copy()
    
    # Set kernel to python3 for both versions
    if 'metadata' not in complete_nb:
        complete_nb['metadata'] = {}
    if 'kernelspec' not in complete_nb['metadata']:
        complete_nb['metadata']['kernelspec'] = {}
    complete_nb['metadata']['kernelspec']['name'] = 'python3'
    complete_nb['metadata']['kernelspec']['display_name'] = 'Python 3'
    complete_nb['metadata']['kernelspec']['language'] = 'python'
    
    # Create exercise version
    exercise_nb = json.loads(json.dumps(complete_nb))  # Deep copy
    
    # Process cells for exercise version - replace solution-tagged cells
    for i, cell in enumerate(exercise_nb['cells']):
        if cell.get('metadata', {}).get('tags') and 'solution' in cell['metadata']['tags']:
            # Replace with empty cell
            exercise_nb['cells'][i] = {
                "cell_type": "code",
                "metadata": {},
                "source": [],
                "execution_count": None,
                "outputs": []
            }
    
    # Add setup cell if data files are specified
    if metadata.get('data_files'):
        zip_name = f"{base_name}-data.zip"
        install_packages = metadata.get('install', 'pandas natural_pdf tqdm')
        links = metadata.get('links', None)
        setup_cell = create_setup_cell(zip_name, config, install_packages, links)
        
        # Find first non-metadata cell position
        insert_pos = 0
        for i, cell in enumerate(complete_nb['cells']):
            if cell['cell_type'] == 'markdown':
                insert_pos = i + 1
                break
        
        complete_nb['cells'].insert(insert_pos, setup_cell)
        exercise_nb['cells'].insert(insert_pos, setup_cell)
        
        # Create data zip with paths relative to notebook directory
        create_data_zip(metadata['data_files'], output_dir / zip_name, notebook_dir)
    
    # Write output files
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy any referenced files (PDFs, images) to output
    find_and_copy_referenced_files(notebook, notebook_dir, output_dir)
    
    # Handle slides if specified (item-specific or section-level)
    slide_file = metadata.get('slides')
    if slide_file:
        # Add simple markdown cell with slide link at the very top
        slide_link_cell = {
            "cell_type": "markdown",
            "metadata": {},
            "source": [f"**Slides:** [{slide_file}](./{slide_file})"]
        }
        # Insert at position 0 (very first cell)
        complete_nb['cells'].insert(0, slide_link_cell)
        exercise_nb['cells'].insert(0, slide_link_cell)
        
        # Copy slide file to output
        source_pdf = notebook_dir / slide_file
        if not source_pdf.exists():
            # Try as absolute path from project root
            source_pdf = Path(slide_file)
        if source_pdf.exists():
            dest_pdf = output_dir / slide_file
            if not dest_pdf.exists():
                dest_pdf.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_pdf, dest_pdf)
                print(f"  → Copied slide file: {slide_file}")
        else:
            print(f"\n❌ ERROR: Slide file not found: {slide_file}")
            print(f"   Looked in: {notebook_dir / slide_file}")
            print(f"   Also tried: {Path(slide_file)}")
            sys.exit(1)
    
    # Exercise version keeps original name
    with open(output_dir / f"{base_name}.ipynb", 'w') as f:
        json.dump(exercise_nb, f, indent=1)
    print(f"✓ Created {output_dir / base_name}.ipynb")
    
    # Complete version gets -ANSWERS suffix
    with open(output_dir / f"{base_name}-ANSWERS.ipynb", 'w') as f:
        json.dump(complete_nb, f, indent=1)
    print(f"✓ Created {output_dir / base_name}-ANSWERS.ipynb")
    
    # Return info for index
    return {
        'name': base_name,
        'title': metadata.get('title', base_name),
        'description': metadata.get('description', ''),
        'exercise_file': f"{base_name}.ipynb",
        'answers_file': f"{base_name}-ANSWERS.ipynb",
        'data_file': f"{base_name}-data.zip" if metadata.get('data_files') else None,
        'section': notebook_dir.name,
        'order': metadata.get('order', None),
        'links': metadata.get('links', None),
        'slides': metadata.get('slides', None)
    }

def create_data_zip(data_patterns, zip_path, base_dir):
    """Create a zip file with files matching the patterns, relative to base_dir."""
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        added_files = set()
        
        for pattern in data_patterns:
            # Resolve pattern relative to notebook directory
            full_pattern = str(base_dir / pattern)
            matches = glob(full_pattern, recursive=True)
            
            if not matches:
                print(f"  Warning: No files match pattern '{pattern}' in {base_dir}")
            
            for file_path in matches:
                file_path = Path(file_path)
                # Calculate the archive name relative to the notebook's directory
                try:
                    arcname = file_path.relative_to(base_dir)
                except ValueError:
                    # If file is outside notebook dir, use full relative path
                    arcname = file_path
                
                if str(file_path) not in added_files:
                    zipf.write(file_path, str(arcname))
                    added_files.add(str(file_path))
        
        print(f"✓ Created {zip_path.name} with {len(added_files)} files")

def find_and_copy_referenced_files(notebook, notebook_dir, output_dir):
    """Find files referenced in markdown cells and copy them to output."""
    copied_files = []
    
    # Regex patterns for finding file references
    patterns = [
        r'\[.*?\]\(([^)]+\.(?:pdf|png|jpg|jpeg|gif|svg))\)',  # Markdown links
        r'<img.*?src=["\']([^"\']+\.(?:png|jpg|jpeg|gif|svg))["\']',  # HTML img tags
        r'!\[.*?\]\(([^)]+\.(?:png|jpg|jpeg|gif|svg))\)',  # Markdown images
    ]
    
    for cell in notebook.get('cells', []):
        if cell['cell_type'] == 'markdown':
            content = ''.join(cell.get('source', []))
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Skip URLs
                    if match.startswith('http://') or match.startswith('https://'):
                        continue
                    
                    # Resolve the file path relative to the notebook
                    source_file = notebook_dir / match
                    if source_file.exists():
                        # Copy to output directory
                        dest_file = output_dir / match
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        if not dest_file.exists():
                            shutil.copy2(source_file, dest_file)
                            copied_files.append(match)
                            print(f"  → Copied referenced file: {match}")
    
    return copied_files

def copy_markdown_referenced_files(content, markdown_dir, output_dir):
    """Find files referenced in markdown content and copy them to output."""
    copied_files = []
    
    # Regex patterns for finding file references
    patterns = [
        r'\[.*?\]\(([^)]+\.(?:pdf|png|jpg|jpeg|gif|svg|mp4|webm|mov))\)',  # Markdown links
        r'<img.*?src=["\']([^"\']+\.(?:png|jpg|jpeg|gif|svg))["\']',  # HTML img tags
        r'!\[.*?\]\(([^)]+\.(?:png|jpg|jpeg|gif|svg))\)',  # Markdown images
        r'<source.*?src=["\']([^"\']+\.(?:mp4|webm|mov))["\']',  # HTML video sources
        r'<video.*?src=["\']([^"\']+\.(?:mp4|webm|mov))["\']',  # HTML video src
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            # Skip URLs
            if match.startswith('http://') or match.startswith('https://'):
                continue
            
            # Resolve the file path relative to the markdown file
            source_file = markdown_dir / match
            if source_file.exists():
                # Copy to output directory
                dest_file = output_dir / match
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                if not dest_file.exists():
                    shutil.copy2(source_file, dest_file)
                    copied_files.append(match)
                    print(f"  → Copied referenced file: {match}")
            else:
                print(f"  ⚠ Referenced file not found: {match}")
    
    return copied_files

def create_slide_thumbnail(pdf_path, output_dir, width=800):
    """Create a thumbnail of the first page of a PDF."""
    pdf_name = pdf_path.stem
    thumb_name = f"{pdf_name}-thumb.png"
    thumb_path = output_dir / thumb_name
    
    if thumb_path.exists():
        return thumb_name
    
    try:
        # Try using ImageMagick's convert command
        cmd = [
            'convert',
            '-density', '150',
            f'{pdf_path}[0]',  # First page only
            '-resize', f'{width}x',
            '-quality', '85',
            str(thumb_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  → Created slide thumbnail: {thumb_name}")
            return thumb_name
    except:
        pass
    
    # If ImageMagick fails, try pdftoppm
    try:
        cmd = [
            'pdftoppm',
            '-f', '1',
            '-l', '1',
            '-png',
            '-r', '150',
            '-singlefile',
            str(pdf_path),
            str(output_dir / pdf_name)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            # pdftoppm creates a file with .png extension
            if (output_dir / f"{pdf_name}.png").exists():
                shutil.move(output_dir / f"{pdf_name}.png", thumb_path)
                print(f"  → Created slide thumbnail: {thumb_name}")
                return thumb_name
    except:
        pass
    
    print(f"  ⚠ Could not create thumbnail for {pdf_path.name} (install ImageMagick or poppler-utils)")
    return None

def generate_slide_embed(slide_file, notebook_dir, output_dir, item_type='notebook'):
    """Generate HTML for slide embedding with lazy loading."""
    # Copy the slide PDF to output
    source_pdf = notebook_dir / slide_file
    if not source_pdf.exists():
        # Try as absolute path from project root
        source_pdf = Path(slide_file)
        if not source_pdf.exists():
            print(f"\n❌ ERROR: Slide file not found: {slide_file}")
            print(f"   Looked in: {notebook_dir / slide_file}")
            print(f"   Also tried: {Path(slide_file)}")
            sys.exit(1)
    
    dest_pdf = output_dir / slide_file
    if not dest_pdf.exists():
        dest_pdf.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_pdf, dest_pdf)
        print(f"  → Copied slide file: {slide_file}")
    
    # Create thumbnail
    thumb_name = create_slide_thumbnail(source_pdf, output_dir)
    
    # Generate unique ID for this slide embed
    slide_id = f"slides-{source_pdf.stem}".replace(' ', '-').replace('.', '-')
    
    # Build the HTML
    if thumb_name:
        preview_html = f'<img src="./{thumb_name}" alt="First slide" style="max-width: 100%; cursor: pointer;">'
    else:
        preview_html = '<div style="background: #f0f0f0; padding: 3em; text-align: center; cursor: pointer;">📊 Click to load slides</div>'
    
    html = f'''
<div id="{slide_id}" class="slide-embed" style="margin: 2em 0;">
    <div class="slide-preview" onclick="loadSlides('{slide_id}', './{slide_file}')">
        {preview_html}
        <p style="text-align: center; margin-top: 0.5em;">
            <button style="padding: 0.5em 1em; background: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer;">
                📊 View Slides
            </button>
            <a href="./{slide_file}" download style="margin-left: 1em;">📥 Download PDF</a>
        </p>
    </div>
    <div class="slide-container" style="display: none;">
        <embed src="./{slide_file}" type="application/pdf" style="width: 100%; height: 600px; border: 1px solid #ddd;">
    </div>
</div>

<script>
function loadSlides(id, src) {{
    const container = document.querySelector(`#${{id}} .slide-container`);
    const preview = document.querySelector(`#${{id}} .slide-preview`);
    container.style.display = 'block';
    preview.style.display = 'none';
}}
</script>
'''
    
    return html

def process_markdown(markdown_path, output_dir, config, section_slides=None):
    """Process a markdown file with frontmatter and return info for index."""
    with open(markdown_path, 'r') as f:
        content = f.read()
    
    frontmatter, markdown_content = extract_markdown_frontmatter(content)
    if not frontmatter:
        print(f"Skipping {markdown_path} - no frontmatter")
        return None
    
    # If no item-specific slides, use section slides
    if not frontmatter.get('slides') and section_slides:
        frontmatter['slides'] = section_slides
    
    base_name = markdown_path.stem
    markdown_dir = markdown_path.parent
    title = frontmatter.get('title', base_name)
    
    # Copy referenced files (images, videos, etc) from markdown content
    copy_markdown_referenced_files(markdown_content, markdown_dir, output_dir)
    
    # Create data zip if data files are specified
    if frontmatter.get('data_files'):
        zip_name = f"{base_name}-data.zip"
        create_data_zip(frontmatter['data_files'], output_dir / zip_name, markdown_dir)
    
    # Build the full content with title
    full_content = f"# {title}\n\n"
    
    # Generate and add table of contents at the top (after title)
    has_useful_links = bool(frontmatter.get('links'))
    toc = generate_toc_from_markdown(markdown_content, has_useful_links)
    if toc:
        full_content += toc + "\n"
    
    # Add download link if data files exist
    if frontmatter.get('data_files'):
        zip_name = f"{base_name}-data.zip"
        full_content += f'<div class="download-box">\n<strong>Download files:</strong> <a href="./{zip_name}">📦 {zip_name}</a>\n</div>\n\n'
    
    # Add slides if specified
    if frontmatter.get('slides'):
        slide_html = generate_slide_embed(frontmatter['slides'], markdown_dir, output_dir, 'markdown')
        full_content += slide_html + '\n\n'
    
    # Add links section if present
    if frontmatter.get('links'):
        full_content += "## Useful Links\n\n"
        for link in frontmatter['links']:
            name = link.get('name', 'Link')
            url = link.get('url', '#')
            desc = link.get('description', '')
            if desc:
                full_content += f"- [{name}]({url}) - {desc}\n"
            else:
                full_content += f"- [{name}]({url})\n"
        full_content += "\n"
    
    full_content += markdown_content
    
    # Convert to HTML and save
    html_content = markdown_to_html(full_content, title)
    output_html = output_dir / f"{base_name}.html"
    with open(output_html, 'w') as f:
        f.write(html_content)
    
    print(f"✓ Created {output_html}")
    
    # Return info for index
    return {
        'name': base_name,
        'title': title,
        'description': frontmatter.get('description', ''),
        'html_file': f"{base_name}.html",
        'data_file': f"{base_name}-data.zip" if frontmatter.get('data_files') else None,
        'section': markdown_dir.name,
        'type': 'markdown',
        'order': frontmatter.get('order', None),
        'links': frontmatter.get('links', None),
        'slides': frontmatter.get('slides', None)
    }

def create_index(notebooks, config, output_dir):
    """Create index.html with links to all notebooks."""
    github_repo = config['github_repo']
    github_branch = config.get('github_branch', 'main')
    output_dir_name = config.get('output_dir', 'docs')
    
    # Group notebooks by section
    sections = {}
    section_configs = {}
    
    # Get section configurations from config
    for section_cfg in config.get('sections', []):
        if isinstance(section_cfg, dict):
            section_configs[section_cfg.get('title', section_cfg.get('folder'))] = section_cfg
    
    for nb in notebooks:
        section = nb['section']
        if section not in sections:
            sections[section] = []
        sections[section].append(nb)
    
    # Build notebooks markdown
    notebooks_md = []
    
    # Process sections in the order they appear in config
    section_order = []
    for section_cfg in config.get('sections', []):
        if isinstance(section_cfg, dict):
            title = section_cfg.get('title', section_cfg.get('folder'))
            if title in sections:
                section_order.append(title)
    
    # Add any sections not in config at the end
    for section in sorted(sections.keys()):
        if section not in section_order:
            section_order.append(section)
    
    for section in section_order:
        section_items = sections.get(section, [])
        notebooks_md.append(f'\n## {section}\n')
        
        # Add section slides if available
        section_cfg = section_configs.get(section, {})
        if section_cfg.get('slides'):
            # Get the first item's folder to determine the section directory
            section_dir = Path(section_items[0]['section_folder']) if section_items else Path('.')
            slide_html = generate_slide_embed(section_cfg['slides'], section_dir.parent, Path(config.get('output_dir', 'docs')), 'index')
            notebooks_md.append('\n' + slide_html + '\n')
        
        # Sort items: first by those with order (ascending), then by filename (descending)
        def sort_key(item):
            if item['order'] is not None:
                return (0, item['order'], '')  # Items with order come first
            else:
                return (1, 0, item['name'])  # Then items without order
        
        sorted_items = sorted(section_items, key=sort_key)
        # For items without order, we want descending by name
        items_with_order = [item for item in sorted_items if item['order'] is not None]
        items_without_order = sorted([item for item in sorted_items if item['order'] is None], 
                                   key=lambda x: x['name'], reverse=True)
        sorted_items = items_with_order + items_without_order
        
        for item in sorted_items:
            # Make title a link
            if item.get('type') == 'markdown':
                notebooks_md.append(f"### [{item['title']}](./{item['html_file']})\n")
            else:
                colab_url = f"https://colab.research.google.com/github/{github_repo}/blob/{github_branch}/{output_dir_name}/{item['exercise_file']}"
                notebooks_md.append(f"### [{item['title']}]({colab_url})\n")
            
            if item['description']:
                notebooks_md.append(f"{item['description']}\n")
            
            if item.get('type') == 'markdown':
                # Handle markdown files
                notebooks_md.append('<div>\n')
                # notebooks_md.append(f'📄 View: <a href="./{item["html_file"]}">content</a><br>\n')
                if item['data_file']:
                    notebooks_md.append(f'📦 Data: <a href="./{item["data_file"]}">{item["data_file"]}</a><br>\n')
                notebooks_md.append('</div>\n')
            else:
                # Handle notebooks
                colab_url = f"https://colab.research.google.com/github/{github_repo}/blob/{github_branch}/{output_dir_name}/{item['exercise_file']}"
                answers_colab_url = f"https://colab.research.google.com/github/{github_repo}/blob/{github_branch}/{output_dir_name}/{item['answers_file']}"
                
                notebooks_md.append('<div class="resource-buttons">\n')
                notebooks_md.append(f'<a href="{colab_url}" class="resource-button primary">🚀 Live coding worksheet</a>\n')
                notebooks_md.append(f'<a href="{answers_colab_url}" class="resource-button completed">✓ Completed version</a>\n')
                notebooks_md.append('</div>\n')
                
                notebooks_md.append('<div class="download-links">\n')
                notebooks_md.append(f'📓 Download: <a href="./{item["exercise_file"]}">worksheet</a> | ')
                notebooks_md.append(f'<a href="./{item["answers_file"]}">completed</a><br>\n')
                if item['data_file']:
                    notebooks_md.append(f'📦 Data: <a href="./{item["data_file"]}">{item["data_file"]}</a>\n')
                notebooks_md.append('</div>\n')
            
            # Add slides mention if present (only item-specific slides, not section slides)
            if item.get('slides') and not item.get('section_slides'):
                slide_filename = Path(item["slides"]).name
                notebooks_md.append(f'<div style="margin: 0.5em 0; color: #666;">📑 Slides: <a href="./{item["slides"]}">{slide_filename}</a></div>\n')
            
            # Add links if present
            if item.get('links'):
                notebooks_md.append('\n**Links:**\n\n')
                notebooks_md.append("<ul>")
                for link in item['links']:
                    name = link.get('name', 'Link')
                    url = link.get('url', '#')
                    desc = link.get('description', '')
                    if desc:
                        notebooks_md.append(f'<li><a href="{url}">{name}</a> {desc}</li>\n')
                    else:
                        notebooks_md.append(f'<li><a href="{url}">{name}</a></li>\n')
            notebooks_md.append("</ul>")
            notebooks_md.append("\n\n")
            notebooks_md.append("")  # Empty line between items
    
    # Use template from config or default
    template = config.get('index_template', '''# {{ title }}

{{ description }}

{{ notebooks }}
''')
    
    # Replace template variables
    index_content = template
    index_content = index_content.replace('{{ title }}', config.get('title', 'Workshop'))
    index_content = index_content.replace('{{ description }}', config.get('description', ''))
    index_content = index_content.replace('{{ notebooks }}', '\n'.join(notebooks_md))
    index_content = index_content.replace('{{ author }}', config.get('author', ''))
    index_content = index_content.replace('{{ organization }}', config.get('organization', ''))
    
    # Convert to HTML and write
    html_content = markdown_to_html(index_content, config.get('title', 'Workshop'))
    with open(output_dir / 'index.html', 'w') as f:
        f.write(html_content)
    
    print(f"✓ Created {output_dir / 'index.html'}")

def main():
    """Process all notebooks and create data packages."""
    config = load_config()
    output_dir = Path(config.get('output_dir', 'docs'))
    
    # Clean up old publish directory
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)
        print(f"✓ Cleaned up old {output_dir}/ directory")
    
    output_dir.mkdir(exist_ok=True)
    
    # Look for notebooks and markdown files in configured sections
    sections = config.get('sections', [])
    if not sections:
        print("Warning: No sections defined in workshop-config.yaml")
        return
    
    processed_items = []
    
    for section in sections:
        if isinstance(section, dict):
            folder = section.get('folder')
            title = section.get('title', folder)
            section_slides = section.get('slides')
        else:
            # Handle if sections is a list of strings
            folder = section
            title = section
            section_slides = None
            
        if not folder or not Path(folder).exists():
            print(f"Warning: Section folder '{folder}' not found")
            continue
            
        # Process notebooks
        for notebook_path in Path(folder).glob('*.ipynb'):
            # Skip checkpoints
            if '.ipynb_checkpoints' in str(notebook_path):
                continue
            
            print(f"\nProcessing {notebook_path}")
            notebook_info = process_notebook(notebook_path, output_dir, config, section_slides)
            if notebook_info:
                # Override section with configured title
                notebook_info['section'] = title
                notebook_info['section_folder'] = folder
                # Add section slides if not overridden
                if section_slides and not notebook_info.get('slides'):
                    notebook_info['section_slides'] = section_slides
                processed_items.append(notebook_info)
        
        # Process markdown files
        for markdown_path in Path(folder).glob('*.md'):
            print(f"\nProcessing {markdown_path}")
            markdown_info = process_markdown(markdown_path, output_dir, config, section_slides)
            if markdown_info:
                # Override section with configured title
                markdown_info['section'] = title
                markdown_info['section_folder'] = folder
                # Add section slides if not overridden
                if section_slides and not markdown_info.get('slides'):
                    markdown_info['section_slides'] = section_slides
                processed_items.append(markdown_info)
    
    # Create index.html
    if processed_items:
        print("\nCreating index.html...")
        create_index(processed_items, config, output_dir)
    
    print(f"\n✓ Published {len(processed_items)} items to {output_dir}/")

if __name__ == '__main__':
    main()