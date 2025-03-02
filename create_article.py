import os
from datetime import datetime

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

def get_user_input():
    """Get article details from user input, allowing multi-line content."""
    print("Available categories:", ", ".join(CATEGORIES))
    category = input("Enter the category for your article: ").lower().strip()
    while category not in CATEGORIES:
        print("Invalid category. Please choose from:", ", ".join(CATEGORIES))
        category = input("Enter the category: ").lower().strip()

    title = input("Enter the article title: ").strip()
    
    print("Enter the article content (one line at a time). Press Enter twice to finish:")
    content_lines = []
    while True:
        line = input("> ").strip()
        if line == "":  # Empty line signals end of input
            break
        content_lines.append(line)
    content = "\n".join(content_lines)  # Join lines with newlines
    
    filename = input("Enter the filename (e.g., 'my-article', no extension): ").strip().lower().replace(" ", "-")

    return category, title, content, filename

def create_article_file(category, title, content, filename):
    """Generate a new article HTML file with multi-line content."""
    article_dir = os.path.join(BASE_DIR, "articles", category)
    os.makedirs(article_dir, exist_ok=True)
    article_path = os.path.join(article_dir, f"{filename}.html")

    # Split content into paragraphs for HTML
    paragraphs = "\n                ".join(f"<p>{line}</p>" for line in content.split("\n") if line.strip())

    # Article template matching your style
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
                    <li><a href="#mathematics">Mathematics</a></li>
                    <li><a href="#physics">Physics</a></li>
                    <li><a href="#programming-ai">Programming & AI</a></li>
                    <li><a href="#sql-database">SQL & Database</a></li>
                    <li><a href="#game-mechanics">Game Mechanics</a></li>
                    <li><a href="#sci-fi-fantasy">Sci-Fi & Fantasy</a></li>
                    <li><a href="#ethical-hacking">Ethical Hacking</a></li>
                    <li><a href="#miscellaneous">Miscellaneous</a></li>
                    <li><a href="../../gallery.html">Gallery</a></li>
                    <li><a href="../../about.html">About</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <div class="container">
        <main class="main-content">
            <article class="article" data-category="{category}">
                <h2>{title}</h2>
                <div class="article-meta">Published: {datetime.now().strftime('%B %d, %Y')} | Category: {category.capitalize()}</div>
                {paragraphs}
                <p><a href="../../index.html">Back to Home</a></p>
            </article>
        </main>

        <aside class="sidebar">
            <h3>Recent Articles</h3>
            <ul>
                <li><a href="collatz.html">Collatz Conjecture</a></li>
                <li><a href="../programming-ai/math-ai.html">Math-First AI</a></li>
            </ul>
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

def update_index_html(index_content, category, title, content, filename):
    """Update index.html with the new article reference."""
    # Take first 100 chars of first line for preview
    preview = content.split("\n")[0][:100] + "..." if content else "No content provided..."
    article_entry = f'''            <article class="article" data-category="{category}">
                <h2><a href="articles/{category}/{filename}.html">{title}</a></h2>
                <div class="article-meta">Published: {datetime.now().strftime('%B %d, %Y')} | Category: {category.capitalize()}</div>
                <p>{preview}</p>
            </article>
'''
    # Find the position to insert the new article (before the first existing article)
    insert_pos = index_content.find('<article class="article"')
    if insert_pos == -1:
        insert_pos = index_content.find('</main>')  # Fallback to end of main
    updated_content = index_content[:insert_pos] + article_entry + index_content[insert_pos:]
    
    # Update sidebar recent articles (add new entry at the top)
    sidebar_pos = updated_content.find('<h3>Recent Articles</h3>')
    list_pos = updated_content.find('<ul>', sidebar_pos)
    updated_content = (
        updated_content[:list_pos + 4] +
        f'\n                <li><a href="articles/{category}/{filename}.html">{title}</a></li>' +
        updated_content[list_pos + 4:]
    )
    
    return updated_content

def main():
    # File paths
    index_path = os.path.join(BASE_DIR, "index.html")
    css_path = os.path.join(BASE_DIR, "styles.css")
    about_path = os.path.join(BASE_DIR, "about.html")

    # Read existing files (just to confirm they exist)
    try:
        index_content = read_file(index_path)
        read_file(css_path)  # Not modifying, just checking
        read_file(about_path)  # Not modifying, just checking
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure index.html, styles.css, and about.html exist in {BASE_DIR}")
        return

    # Get user input for new article
    category, title, content, filename = get_user_input()

    # Create new article file
    article_path = create_article_file(category, title, content, filename)
    print(f"Created new article: {article_path}")

    # Update index.html
    updated_index_content = update_index_html(index_content, category, title, content, filename)
    write_file(index_path, updated_index_content)
    print(f"Updated index.html with reference to {title}")

if __name__ == "__main__":
    main()