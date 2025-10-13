import yaml
import os
import pyperclip

# Config file in user's home directory (consistent with simex.py)
# Issue #15: Fixed path inconsistency - was pointing to package directory
CONFIG_FILE = os.path.expanduser('~/.simexp/simexp.yaml')
MAX_SOURCES = 3

def load_config():
    if not os.path.exists(CONFIG_FILE):
        # Create config directory if it doesn't exist
        config_dir = os.path.dirname(CONFIG_FILE)
        os.makedirs(config_dir, exist_ok=True)
        # Create default config
        save_config({'BASE_PATH': os.path.expanduser('~/'), 'SOURCES': []})
    with open(CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)
        if config is None:
            config = {}
        if 'BASE_PATH' not in config:
            config['BASE_PATH'] = os.path.expanduser('~/')
            save_config(config)
        return config

def save_config(config):
    # Ensure config directory exists
    config_dir = os.path.dirname(CONFIG_FILE)
    os.makedirs(config_dir, exist_ok=True)
    with open(CONFIG_FILE, 'w') as file:
        yaml.safe_dump(config, file)

def is_clipboard_content_valid():
    clipboard_content = pyperclip.paste().strip()
    return clipboard_content.startswith('http://') or clipboard_content.startswith('https://')

def update_sources_from_clipboard():
    # Get the current clipboard content
    clipboard_content = pyperclip.paste().strip()
    
    # Check if the clipboard content is a valid URL
    if is_clipboard_content_valid():
        config = load_config()
        
        # Create a new source entry
        new_source = {
            'url': clipboard_content,
            'filename': os.path.basename(clipboard_content).split('.')[0] + '.md'
        }
        
        # Update the configuration with the new source
        if 'CLIPBOARD_SOURCES' not in config:
            config['CLIPBOARD_SOURCES'] = []
        
        config['CLIPBOARD_SOURCES'].append(new_source)
        
        # Ensure we do not exceed the maximum number of sources
        if len(config['CLIPBOARD_SOURCES']) > MAX_SOURCES:
            config['CLIPBOARD_SOURCES'] = config['CLIPBOARD_SOURCES'][-MAX_SOURCES:]
        
        save_config(config)
    else:
        print("Invalid clipboard content. No changes made to the configuration.")

if __name__ == "__main__":
    update_sources_from_clipboard()