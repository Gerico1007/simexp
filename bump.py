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
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 bump.py <patch|minor|major> [mcp] [version]")
        print("")
        print("Examples:")
        print("  python3 bump.py patch              # Bump main package patch version")
        print("  python3 bump.py minor              # Bump main package minor version")
        print("  python3 bump.py major              # Bump main package major version")
        print("  python3 bump.py mcp patch          # Bump MCP package patch version")
        print("  python3 bump.py mcp minor          # Bump MCP package minor version")
        print("  python3 bump.py 0.5.1              # Set main package to specific version")
        print("  python3 bump.py mcp 0.2.0          # Set MCP package to specific version")
        sys.exit(1)

    # Determine package and bump type
    target_package = 'main'  # main or mcp
    bump_type = None
    custom_version = None

    if len(sys.argv) >= 2:
        if sys.argv[1] == 'mcp':
            target_package = 'mcp'
            if len(sys.argv) >= 3:
                if sys.argv[2] in ['patch', 'minor', 'major']:
                    bump_type = sys.argv[2]
                else:
                    custom_version = sys.argv[2]
        else:
            if sys.argv[1] in ['patch', 'minor', 'major']:
                bump_type = sys.argv[1]
            else:
                custom_version = sys.argv[1]

    # Validate arguments
    if bump_type is None and custom_version is None:
        print("Error: Must specify bump type (patch|minor|major) or version number")
        sys.exit(1)

    # Set file paths based on target package
    if target_package == 'main':
        version_file = 'setup.py'
        other_file = 'pyproject.toml'
    else:
        version_file = 'simexp-mcp/pyproject.toml'
        other_file = None

    # Get current version
    current_version_str = get_current_version(version_file)
    if not current_version_str:
        print(f"Error: Could not find version in {version_file}")
        sys.exit(1)

    # Calculate new version
    if custom_version:
        new_version = custom_version
        # Validate custom version format
        try:
            Version(new_version)
        except:
            print(f"Error: Invalid version format: {custom_version}")
            sys.exit(1)
    else:
        current_version = Version(current_version_str)
        major, minor, patch = current_version.major, current_version.minor, current_version.micro

        if bump_type == 'major':
            new_version = f'{major + 1}.0.0'
        elif bump_type == 'minor':
            new_version = f'{major}.{minor + 1}.0'
        elif bump_type == 'patch':
            new_version = f'{major}.{minor}.{patch + 1}'

    # Update files
    files_to_update = [version_file]
    if other_file:
        files_to_update.append(other_file)

    updated_files = []
    for file_path in files_to_update:
        if bump_version_file(file_path, new_version):
            updated_files.append(file_path)

    if updated_files:
        package_name = "simexp-mcp" if target_package == 'mcp' else "simexp"
        print(f"Version bumped to {new_version} in {package_name}")
        print(f"Files updated: {', '.join(updated_files)}")
    else:
        print("No files were updated.")
