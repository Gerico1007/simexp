import os
from datetime import datetime

def save_as_markdown(title, content, source_name):
    # Base folder path for storing daily files
    base_path = os.path.join(os.path.dirname(__file__), '..', 'output')
    
    # Create a folder for the current date
    current_date = datetime.now().strftime('%Y%m%d')
    daily_folder = os.path.join(base_path, current_date)
    os.makedirs(daily_folder, exist_ok=True)
    
    # Define the filename based on the source name
    filename = f"{current_date}_{source_name}.md"
    file_path = os.path.join(daily_folder, filename)
    
    # Format the content with title and paragraphs
    formatted_content = f""
    paragraphs = content.split('\n\n')  # Split content into paragraphs based on double newlines
    for paragraph in paragraphs:
        formatted_content += f"{paragraph}\n\n"  # Add each paragraph followed by two newlines
    
    # Save the content to the Markdown file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(formatted_content)