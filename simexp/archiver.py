import os
from datetime import datetime

def save_as_markdown(title, content, base_path, daily_folder, source_name):
    """
    Save content as markdown file in the specified daily folder

    Args:
        title: Content title (currently unused, could be added to file)
        content: The content to save
        base_path: Base path from config (for reference)
        daily_folder: Full path to the daily folder (YYYYMMDD)
        source_name: Source filename (without extension)

    Returns:
        tuple: (success: bool, file_path: str)
    """
    try:
        # Ensure daily folder exists
        os.makedirs(daily_folder, exist_ok=True)

        # Define the filename based on the source name
        current_date = datetime.now().strftime('%Y%m%d')
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

        return (True, file_path)
    except Exception as e:
        return (False, str(e))