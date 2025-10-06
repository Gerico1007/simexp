from bs4 import BeautifulSoup
import re

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove unwanted tags like script and style
    for script in soup(['script', 'style']):
        script.decompose()

    # Locate the specific element using a CSS selector equivalent to the XPath
    target_div = soup.select_one("html > body > div > div:nth-of-type(1) > div > div")

    if target_div:
        markdown_content = ""

        # Process elements to retain markdown structure
        for element in target_div.descendants:
            if element.name == "h1":
                markdown_content += f"\n# {element.get_text().strip()}\n\n"
            elif element.name == "h2":
                markdown_content += f"\n## {element.get_text().strip()}\n\n\n"  # Add newline before and after
            elif element.name == "h3":
                markdown_content += f"\n### {element.get_text().strip()}\n\n\n"  # Add newline before and after
            elif element.name in ["ul", "ol"]:  # Handle unordered and ordered lists
                for li in element.find_all("li"):
                    markdown_content += f"- {li.get_text().strip()}\n"
                markdown_content += "\n"  # Add a newline after lists
            elif element.name == "blockquote":  # Handle blockquotes
                markdown_content += f"\n> {element.get_text().strip()}\n\n"
            elif element.name == "p":  # Handle paragraphs
                markdown_content += f"{element.get_text().strip()}\n\n"
            elif element.name == "code":  # Inline code
                markdown_content += f"`{element.get_text().strip()}`"
            else:
                continue

        # Normalize newlines and ensure proper spacing
        markdown_content = re.sub(r'\n+', '\n', markdown_content)  # Normalize excessive newlines
        markdown_content = re.sub(r'(^|\n)(#+)', r'\1\n\2', markdown_content)  # Ensure space before headers

        return markdown_content.strip()

    # Fallback if no specific content is found
    return "No content found."

def extract_title(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.title.string if soup.title else 'Untitled'
    return title.strip()

def process_content(html_content):
    title = extract_title(html_content)
    cleaned_content = clean_html(html_content)
    return title, cleaned_content