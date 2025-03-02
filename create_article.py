import os
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
import glob
from bs4 import BeautifulSoup
import shutil

# Base directory (assuming script runs in beyond-equations/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Valid categories
CATEGORIES = [
    "mathematics", "physics", "programming-ai", "sql-database",
    "game-mechanics", "sci-fi-fantasy", "ethical-hacking", "miscellaneous"
]

def read_file(file_path):
    """Read content from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(file_path, content):
    """Write content to a file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_all_articles():
    """Scan all articles and return a sorted list by creation date with HTML titles."""
    article_files = glob.glob(os.path.join(BASE_DIR, "articles", "*", "*.html"))
    articles = []
    for file_path in article_files:
        creation_time = os.path.getctime(file_path)
        filename = os.path.basename(file_path)
        category = os.path.basename(os.path.dirname(file_path))
        relative_path = f"articles/{category}/{filename}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                title = soup.find('h2').get_text(strip=True) if soup.find('h2') else filename.replace(".html", "").replace("-", " ").title()
        except Exception:
            title = filename.replace(".html", "").replace("-", " ").title()
        
        articles.append({"path": relative_path, "title": title, "date": creation_time})
    
    articles.sort(key=lambda x: x["date"], reverse=True)
    return articles[:8]

def parse_content(content):
    """Parse the full content into paragraphs, equations, and code."""
    content_parts = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        if line.startswith("\\(") or line.startswith("\\["):
            content_parts.append({"type": "equation", "content": line})
            i += 1
            continue

        if "python" in line.lower():
            i += 1
            code_lines = []
            while i < len(lines) and lines[i].strip() and not (lines[i].startswith("\\(") or lines[i].startswith("\\[")):
                code_lines.append(lines[i].rstrip())
                i += 1
            if code_lines:
                content_parts.append({"type": "code", "content": "\n".join(code_lines)})
            continue

        paragraph_lines = []
        while i < len(lines) and lines[i].strip() and not (lines[i].startswith("\\(") or lines[i].startswith("\\[") or "python" in lines[i].lower()):
            paragraph_lines.append(lines[i].strip())
            i += 1
        if paragraph_lines:
            content_parts.append({"type": "paragraph", "content": "\n".join(paragraph_lines)})

    return content_parts

def create_article_file(category, title, content_parts, filename, image_path=None):
    """Generate a new article HTML file with image support."""
    article_dir = os.path.join(BASE_DIR, "articles", category)
    os.makedirs(article_dir, exist_ok=True)
    article_path = os.path.join(article_dir, f"{filename}.html")

    # Handle image if provided
    image_html = ""
    if image_path:
        image_filename = os.path.basename(image_path)
        dest_image_path = os.path.join(BASE_DIR, "assets", "images", image_filename)
        os.makedirs(os.path.dirname(dest_image_path), exist_ok=True)
        shutil.copy(image_path, dest_image_path)
        image_html = f'                <img src="../../assets/images/{image_filename}" alt="{title} Image" class="article-image">\n'

    content_html = ""
    for part in content_parts:
        if part["type"] == "paragraph":
            paragraphs = "\n                ".join(f"<p>{line}</p>" for line in part["content"].split("\n") if line.strip())
            content_html += f"                {paragraphs}\n"
        elif part["type"] == "equation":
            content_html += f'                <div class="equation">{part["content"]}</div>\n'
        elif part["type"] == "code":
            content_html += f'                <pre><code>{part["content"]}</code></pre>\n'

    article_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Beyond Equations</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <link rel="stylesheet" href="../../styles.css">
</head>
<body>
    <header>
        <div class="header-content">
            <h1>Beyond Equations</h1>
            <nav>
                <ul>
                    <li><a href="../../index.html">Home</a></li>
                    <li><a href="../../gallery.html">Gallery</a></li>
                    <li><a href="../../about.html">About</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <div class="container">
        <main class="main-content">
            <article class="article">
                <h2>{title}</h2>
                <div class="article-meta">Published: {datetime.now().strftime('%B %d, %Y')} | Category: {category.capitalize()}</div>
{image_html}{content_html}
                <p><a href="../../index.html">Back to Home</a></p>
            </article>
        </main>

        <aside class="sidebar">
            <h3>Resources</h3>
            <ul>
                <li><a href="#">LaTeX Guide</a></li>
                <li><a href="#">Math Tools</a></li>
            </ul>
            <div class="gallery">
                <h3>Gallery</h3>
                <div class="gallery-grid">
                    <div class="gallery-item">
                        <img src="../../assets/images/collatz.png" alt="Collatz Visualization">
                    </div>
                    <div class="gallery-item">
                        <img src="../../assets/images/neural-net.jpg" alt="AI Neural Network">
                    </div>
                </div>
            </div>
        </aside>
    </div>

    <footer>
        <p>© 2025 Beyond Equations | Beyond Boundaries</p>
    </footer>
</body>
</html>
'''
    write_file(article_path, article_template)
    return article_path

def update_index_html(index_content, category, title, content_parts, filename, recent_articles, image_path=None):
    """Update index.html with the new article and sorted recent articles."""
    preview = ""
    for part in content_parts:
        if part["type"] == "paragraph":
            preview = part["content"].split("\n")[0][:100] + "..."
            break
    if not preview:
        preview = "Article content preview..."

    image_html = ""
    if image_path:
        image_filename = os.path.basename(image_path)
        image_html = f'                <img src="assets/images/{image_filename}" alt="{title} Image" class="article-image">\n'

    article_entry = f'''            <article class="article" data-category="{category}">
                <h2><a href="articles/{category}/{filename}.html">{title}</a></h2>
                <div class="article-meta">Published: {datetime.now().strftime('%B %d, %Y')} | Category: {category.capitalize()}</div>
{image_html}                <p>{preview}</p>
            </article>
'''
    insert_pos = index_content.find('<article class="article"')
    if insert_pos == -1:
        insert_pos = index_content.find('</main>')
    updated_content = index_content[:insert_pos] + article_entry + index_content[insert_pos:]
    
    recent_html = "\n                ".join(f'<li><a href="{article["path"]}">{article["title"]}</a></li>' for article in recent_articles)
    sidebar_start = updated_content.find('<h3>Recent Articles</h3>')
    list_start = updated_content.find('<ul>', sidebar_start)
    list_end = updated_content.find('</ul>', list_start)
    updated_content = (
        updated_content[:list_start + 4] +
        f'\n                {recent_html}' +
        updated_content[list_end:]
    )
    
    return updated_content

def update_other_html_files(recent_articles):
    """Update about.html and gallery.html with sorted recent articles and simplified nav."""
    for file_name in ["about.html", "gallery.html"]:
        file_path = os.path.join(BASE_DIR, file_name)
        try:
            content = read_file(file_path)
            nav_start = content.find('<nav>')
            nav_end = content.find('</nav>', nav_start) + 6
            new_nav = '''                <nav>
                    <ul>
                        <li><a href="index.html">Home</a></li>
                        <li><a href="gallery.html">Gallery</a></li>
                        <li><a href="about.html">About</a></li>
                    </ul>
                </nav>'''
            updated_content = content[:nav_start] + new_nav + content[nav_end:]

            recent_html = "\n                ".join(f'<li><a href="{article["path"]}">{article["title"]}</a></li>' for article in recent_articles)
            sidebar_start = updated_content.find('<h3>Recent Articles</h3>')
            list_start = updated_content.find('<ul>', sidebar_start)
            list_end = updated_content.find('</ul>', list_start)
            updated_content = (
                updated_content[:list_start + 4] +
                f'\n                {recent_html}' +
                updated_content[list_end:]
            )
            write_file(file_path, updated_content)
        except FileNotFoundError:
            print(f"Warning: {file_name} not found, skipping update.")

def browse_image():
    """Open file dialog to select an image."""
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
    if file_path:
        image_entry.delete(0, tk.END)
        image_entry.insert(0, file_path)

def submit_article():
    """Handle form submission and create/update files."""
    category = category_var.get()
    title = title_entry.get()
    content = content_text.get("1.0", tk.END).strip()
    filename = filename_entry.get().lower().replace(" ", "-")
    image_path = image_entry.get() or None

    if not all([category, title, content, filename]):
        status_label.config(text="Please fill all fields!")
        return

    content_parts = parse_content(content)
    recent_articles = get_all_articles()
    article_path = create_article_file(category, title, content_parts, filename, image_path)
    
    new_article = {"path": f"articles/{category}/{filename}.html", "title": title, "date": datetime.now().timestamp()}
    recent_articles.insert(0, new_article)
    recent_articles = recent_articles[:8]

    updated_index_content = update_index_html(index_content, category, title, content_parts, filename, recent_articles, image_path)
    write_file(index_path, updated_index_content)
    update_other_html_files(recent_articles)

    status_label.config(text=f"Article created: {article_path}\nAll HTML files updated!")
    root.quit()

# GUI Setup
root = tk.Tk()
root.title("Create New Article - Beyond Equations")
root.geometry("600x600")  # Slightly increased height to ensure space

# File paths
index_path = os.path.join(BASE_DIR, "index.html")
css_path = os.path.join(BASE_DIR, "styles.css")
about_path = os.path.join(BASE_DIR, "about.html")

# Read existing files
try:
    index_content = read_file(index_path)
    read_file(css_path)
    read_file(about_path)
except FileNotFoundError as e:
    root.destroy()
    print(f"Error: {e}. Please ensure index.html, styles.css, and about.html exist in {BASE_DIR}")
    exit(1)

# Create a main frame with scrollbar
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(main_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)

# Frame for content
content_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=content_frame, anchor="nw")

# Category Dropdown
tk.Label(content_frame, text="Category:").pack(pady=5)
category_var = tk.StringVar()
category_dropdown = ttk.Combobox(content_frame, textvariable=category_var, values=CATEGORIES, state="readonly")
category_dropdown.pack(pady=5)
category_dropdown.set(CATEGORIES[0])

# Title Entry
tk.Label(content_frame, text="Title:").pack(pady=5)
title_entry = tk.Entry(content_frame, width=50)
title_entry.pack(pady=5)

# Filename Entry
tk.Label(content_frame, text="Filename (no extension):").pack(pady=5)
filename_entry = tk.Entry(content_frame, width=50)
filename_entry.pack(pady=5)

# Image Entry with Browse Button
tk.Label(content_frame, text="Image (optional):").pack(pady=5)
image_frame = tk.Frame(content_frame)
image_frame.pack(pady=5)
image_entry = tk.Entry(image_frame, width=40)
image_entry.pack(side=tk.LEFT)
browse_button = tk.Button(image_frame, text="Browse", command=browse_image)
browse_button.pack(side=tk.LEFT, padx=5)

# Content Text Box
tk.Label(content_frame, text="Content (paste full article here):").pack(pady=5)
content_text = tk.Text(content_frame, height=15, width=70)
content_text.pack(pady=5)

# Submit Button
submit_button = tk.Button(content_frame, text="Create Article", command=submit_article)
submit_button.pack(pady=10)

# Status Label
status_label = tk.Label(content_frame, text="")
status_label.pack(pady=5)

# Update scroll region
def configure_scroll(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

content_frame.bind("<Configure>", configure_scroll)

root.mainloop()