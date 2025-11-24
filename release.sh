#!/bin/bash

# SimExp Main Package Release Script
# Handles version bumping, git operations, and PyPI upload

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PACKAGE_NAME="simexp"
MAIN_BRANCH="main"

# Functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_clean_working_tree() {
    if ! git diff-index --quiet HEAD --; then
        print_error "Working directory has uncommitted changes. Please commit or stash first."
        exit 1
    fi
}

check_on_main_branch() {
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [[ "$CURRENT_BRANCH" != "$MAIN_BRANCH" ]]; then
        print_warning "Not on $MAIN_BRANCH branch (currently on $CURRENT_BRANCH)"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

get_current_version() {
    python -c "import re; content = open('setup.py').read(); match = re.search(r'version\s*=\s*[\"\']([\d.]+)[\"\']', content); print(match.group(1) if match else '')"
}

# Main workflow
main() {
    print_header "SimExp Release Process"
    echo ""

    # Pre-flight checks
    print_header "Pre-flight Checks"
    check_clean_working_tree
    print_success "Working directory clean"

    check_on_main_branch
    print_success "On correct branch"

    CURRENT_VERSION=$(get_current_version)
    print_success "Current version: $CURRENT_VERSION"
    echo ""

    # Determine release type
    print_header "Release Type"
    echo "Choose release type:"
    echo "  1) Patch (bug fixes, minor changes)"
    echo "  2) Minor (new features, backwards compatible)"
    echo "  3) Major (breaking changes)"
    echo "  4) Custom version"
    echo ""
    read -p "Select (1-4): " release_type

    case $release_type in
        1)
            python bump.py patch
            ;;
        2)
            python bump.py minor
            ;;
        3)
            python bump.py major
            ;;
        4)
            read -p "Enter version (e.g., 1.2.3): " custom_version
            python bump.py "$custom_version"
            ;;
        *)
            print_error "Invalid selection"
            exit 1
            ;;
    esac

    NEW_VERSION=$(get_current_version)
    print_success "Version updated to: $NEW_VERSION"
    echo ""

    # Build
    print_header "Building Distribution"
    make clean
    make build
    print_success "Build complete"
    echo ""

    # Commit
    print_header "Git Operations"
    git add setup.py pyproject.toml
    git commit -m "Release: simexp v$NEW_VERSION

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
    print_success "Version commit created"

    git tag "v$NEW_VERSION"
    print_success "Git tag created: v$NEW_VERSION"
    echo ""

    # Upload
    print_header "PyPI Upload"
    echo "Ready to upload to PyPI?"
    read -p "Continue with upload? (y/n) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        make upload
        print_success "Uploaded to PyPI"

        # Push to GitHub
        print_header "GitHub Push"
        git push origin "$MAIN_BRANCH" --tags
        print_success "Pushed to GitHub with tags"
    else
        print_warning "Upload skipped. You can run 'make upload' manually later."
        echo ""
        print_warning "Don't forget to push to GitHub:"
        echo "  git push origin $MAIN_BRANCH --tags"
    fi

    echo ""
    print_header "Release Complete! 🎉"
    echo "SimExp v$NEW_VERSION is now available"
    echo ""
    echo "Verify installation with:"
    echo "  pip install --upgrade simexp"
    echo "  simexp --help"
}

# Run main function
main
