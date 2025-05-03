import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
import html

def get_excerpt(content_div, max_words=50):
    """Extract the first max_words from the content, stripping HTML tags."""
    text = content_div.get_text(separator=' ', strip=True)
    words = text.split()
    excerpt = ' '.join(words[:max_words])
    if len(words) > max_words:
        excerpt += '...'
    return html.escape(excerpt)

def try_parse_date(date_str):
    """Try parsing date in multiple formats."""
    formats = [
        '%B %d, %Y',  # May 03, 2025
        '%m/%d/%Y',   # 05/03/2025
        '%Y-%m-%d',   # 2025-05-03
        '%B %d %Y'    # May 03 2025
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None

def parse_post(file_path):
    """Parse an HTML blog post to extract title, date, tags, and excerpt."""
    print(f"\nParsing file: {file_path}")
    try:
        # Check file size and readability
        file_size = os.path.getsize(file_path)
        print(f"File size: {file_size} bytes")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"File content length: {len(content)} characters")

        soup = BeautifulSoup(content, 'html.parser')

        # Extract title
        title_tag = soup.find('h2', class_='post-title')
        if not title_tag:
            print("Error: Missing <h2 class=\"post-title\"> tag.")
            return None
        title = title_tag.get_text(strip=True)
        print(f"Found title: {title}")

        # Extract date and tags from post-meta
        meta_tag = soup.find('p', class_='post-meta')
        if not meta_tag:
            print("Error: Missing <p class=\"post-meta\"> tag.")
            return None
        meta_text = meta_tag.get_text(strip=True)
        print(f"Raw post-meta: '{meta_text}'")
        
        date_match = re.match(r'Posted on (.+?) \| Tags: (.+)', meta_text)
        if not date_match:
            print(f"Error: Invalid post-meta format. Expected 'Posted on [Date] | Tags: [Tags]', got '{meta_text}'.")
            return None
        date_str = date_match.group(1).strip()
        tags = date_match.group(2).strip()
        print(f"Extracted date: '{date_str}'")
        print(f"Extracted tags: '{tags}'")

        # Parse date
        post_date = try_parse_date(date_str)
        if not post_date:
            print(f"Error: Could not parse date '{date_str}'. Tried formats: Month Day, Year; MM/DD/YYYY; YYYY-MM-DD; Month Day Year")
            return None
        print(f"Parsed date: {post_date}")

        # Extract excerpt
        content_div = soup.find('div', class_='post-content')
        if not content_div:
            print("Error: Missing <div class=\"post-content\"> tag.")
            return None
        excerpt = get_excerpt(content_div)
        print(f"Generated excerpt: {excerpt}")

        filename = os.path.basename(file_path)

        return {
            'title': title,
            'date_str': date_str,
            'tags': tags,
            'excerpt': excerpt,
            'filename': filename,
            'date': post_date
        }
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return None

def generate_preview_snippet(post):
    """Generate an <article class="blog-preview"> snippet."""
    return f"""      <article class="blog-preview">
        <h3 class="post-title">{post['title']}</h3>
        <p class="post-meta">Posted on {post['date_str']} | Tags: {post['tags']}</p>
        <p class="post-excerpt">{post['excerpt']}</p>
        <a href="posts/{post['filename']}" class="read-more">Read More</a>
      </article>
"""

def main():
    posts_dir = 'posts'
    previews = []

    # Get absolute path for clarity
    posts_dir_abs = os.path.abspath(posts_dir)
    print(f"Scanning directory: {posts_dir_abs}")

    # Check if posts directory exists
    if not os.path.exists(posts_dir):
        print("Error: The 'posts' directory does not exist.")
        return

    # List all files in posts/
    try:
        files = os.listdir(posts_dir)
        print(f"Directory contents: {files}")
        html_files = [f for f in files if f.lower().endswith('.html')]
        if not html_files:
            print("No .html files found in the 'posts' directory.")
            return
        print(f"Found {len(html_files)} .html file(s): {html_files}")
    except Exception as e:
        print(f"Error accessing 'posts' directory: {str(e)}")
        return

    # Parse each HTML file
    for filename in html_files:
        file_path = os.path.join(posts_dir, filename)
        post_data = parse_post(file_path)
        if post_data:
            previews.append(post_data)
        else:
            print(f"Skipping {file_path}: Not a valid blog post.")

    if not previews:
        print("\nNo valid blog posts found in the 'posts' directory.")
        return

    # Sort previews by date (newest first)
    previews.sort(key=lambda x: x['date'], reverse=True)

    # Generate preview snippets
    preview_snippets = [generate_preview_snippet(post) for post in previews]
    preview_html = '\n\n'.join(preview_snippets)

    # Print snippets
    print("\nGenerated blog preview snippets for index.html:")
    print("Copy the following into the <main> section of index.html under <h2>Blog Posts</h2> and before <footer>:")
    print("\n" + preview_html)
    print("\nEnsure proper indentation (2 spaces before each <article> to align with existing HTML).")

if __name__ == "__main__":
    main()