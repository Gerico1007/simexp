import re
import sys
from packaging.version import Version

def get_current_version(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        # Try double quotes first, then single quotes
        match = re.search(r'version\s*=\s*"([^"]*)"', content) or re.search(r"version\s*=\s*'([^']*)'", content)
        if match:
            return match.group(1)
    return None

def bump_version_file(file_path, new_version):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Replace version whether it's in double or single quotes
        content = re.sub(r'version\s*=\s*"[^"]*"', f'version = "{new_version}"', content)
        content = re.sub(r"version\s*=\s*'[^']*'", f'version = "{new_version}"', content)
        
        with open(file_path, 'w') as file:
            file.write(content)
        return True
    except FileNotFoundError:
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ['patch', 'minor', 'major']:
        print("Usage: python bump.py <patch|minor|major>")
        sys.exit(1)

    bump_type = sys.argv[1]

    # Get current version from setup.py as the source of truth
    current_version_str = get_current_version('setup.py')
    if not current_version_str:
        print("Error: Could not find version in setup.py")
        sys.exit(1)

    current_version = Version(current_version_str)
    major, minor, patch = current_version.major, current_version.minor, current_version.micro

    if bump_type == 'major':
        new_version = f'{major + 1}.0.0'
    elif bump_type == 'minor':
        new_version = f'{major}.{minor + 1}.0'
    elif bump_type == 'patch':
        new_version = f'{major}.{minor}.{patch + 1}'

    files_to_update = [
        'setup.py',
        'pyproject.toml'
    ]

    updated_files = []
    for file_path in files_to_update:
        if bump_version_file(file_path, new_version):
            updated_files.append(file_path)

    if updated_files:
        print(f"Version bumped to {new_version} in {', '.join(updated_files)}")
    else:
        print("No files were updated.")
