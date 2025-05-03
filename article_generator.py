import os
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime

def sanitize_filename(title):
    """Convert title to a valid filename (lowercase, hyphens, no special chars)."""
    filename = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    filename = re.sub(r'\s+', '-', filename)
    return filename

def text_to_html(content):
    """Convert plain text to HTML, handling paragraphs and bullet points."""
    lines = content.strip().split('\n')
    html_content = []
    in_list = False

    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                html_content.append('</ul>')
                in_list = False
            continue

        # Check for bullet points (•, -, *)
        if line.startswith(('•', '-', '*')):
            if not in_list:
                html_content.append('<ul>')
                in_list = True
            # Remove bullet marker and leading/trailing whitespace
            item = line[1:].strip()
            if item:
                html_content.append(f'  <li>{item}</li>')
        else:
            if in_list:
                html_content.append('</ul>')
                in_list = False
            html_content.append(f'<p>{line}</p>')

    if in_list:
        html_content.append('</ul>')

    return '\n'.join(html_content)

def generate_blog_html(title, date, tags, content):
    """Generate HTML content using the blog post template."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=0.5" />
  <title>Beyond Equations - {title}</title>
  <link rel="stylesheet" href="../style.css" />
</head>
<body>
  <div class="wrapper">
    <aside class="sidebar">
      <h1>Beyond Equations</h1>
      <p class="tagline">Exploring Math, Code, and Creativity Beyond the Numbers</p>
      <nav>
        <ul>
          <li><a href="../index.html">Home</a></li>
        </ul>
      </nav>
      <!-- 1. Physics: Atom -->
      <div class="ascii-art-container">
       <pre class="ascii-art">
      .--.
     /    \
    : ,  . :
    : :  : :
     \    /
      `--'
      </pre>
     </div>
    </aside>

    <main class="main-content">
      <article class="blog-post">
        <h2 class="post-title">{title}</h2>
        <p class="post-meta">Posted on {date} | Tags: {tags}</p>
        <div class="post-content">
          {content}
        </div>
      </article>

      <footer>
        <p>© 2025 Lavian Dsouza • <a href="mailto:lavianvishal23@gmail.com">Contact</a></p>
      </footer>
    </main>
  </div>
</body>
</html>
"""

def generate_blog_post():
    """Generate the blog HTML file from GUI inputs."""
    title = title_entry.get().strip()
    date = date_entry.get().strip()
    tags = tags_entry.get().strip()
    content = content_text.get("1.0", tk.END).strip()

    # Validate inputs
    if not title:
        status_label.config(text="Error: Title is required.", foreground="red")
        return
    if not date:
        status_label.config(text="Error: Date is required.", foreground="red")
        return
    if not content:
        status_label.config(text="Error: Content is required.", foreground="red")
        return

    try:
        # Convert content to HTML
        html_content = text_to_html(content)

        # Sanitize title for filename
        filename = sanitize_filename(title) + '.html'
        posts_dir = 'posts'
        filepath = os.path.join(posts_dir, filename)

        # Create posts directory if it doesn't exist
        if not os.path.exists(posts_dir):
            os.makedirs(posts_dir)

        # Generate and save HTML file
        full_html = generate_blog_html(title, date, tags, html_content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_html)

        # Update status and show preview snippet
        status_label.config(text=f"Success: Blog post created at {filepath}", foreground="green")
        print(f"Blog post created: {filepath}")
        print("To add this to index.html, include a preview like:")
        print(f"""
    <article class="blog-preview">
      <h3 class="post-title">{title}</h3>
      <p class="post-meta">Posted on {date} | Tags: {tags}</p>
      <p class="post-excerpt">[Short summary, ~30-50 words]</p>
      <a href="posts/{filename}" class="read-more">Read More</a>
    </article>
    """)

    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", foreground="red")

# Create the Tkinter GUI
root = tk.Tk()
root.title("Beyond Equations Blog Post Generator")
root.geometry("600x700")
root.configure(bg="#0d0d0d")

# Styling
style = ttk.Style()
style.configure("TLabel", background="#0d0d0d", foreground="#e0e0e0", font=("Courier New", 10))
style.configure("TEntry", font=("Courier New", 10))
style.configure("TButton", font=("Courier New", 10))

# Title
ttk.Label(root, text="Blog Post Title:").pack(pady=5)
title_entry = ttk.Entry(root, width=60)
title_entry.pack()

# Date
ttk.Label(root, text="Post Date (e.g., May 04, 2025):").pack(pady=5)
date_entry = ttk.Entry(root, width=60)
date_entry.pack()

# Tags
ttk.Label(root, text="Tags (comma-separated, e.g., Mathematics, Python):").pack(pady=5)
tags_entry = ttk.Entry(root, width=60)
tags_entry.pack()

# Content
ttk.Label(root, text="Blog Content (paste from MS Word, use •, -, or * for bullets):").pack(pady=5)
content_text = scrolledtext.ScrolledText(root, width=60, height=20, font=("Courier New", 10), bg="#222222", fg="#e0e0e0", insertbackground="#e0e0e0")
content_text.pack(pady=5)

# Generate Button
generate_button = ttk.Button(root, text="Generate Blog Post", command=generate_blog_post)
generate_button.pack(pady=10)

# Status Label
status_label = tk.Label(root, text="", bg="#0d0d0d", fg="#e0e0e0", font=("Courier New", 10))
status_label.pack(pady=5)

# Run the application
root.mainloop()