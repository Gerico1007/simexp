#!/bin/bash

# SimExp Coordinated Release Script
# Handles releases for both simexp and simexp-mcp packages
# Ensures version coordination and proper release sequencing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
MAIN_BRANCH="main"
MAIN_PACKAGE="simexp"
MCP_PACKAGE="simexp-mcp"

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${CYAN}  $1${BLUE}║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
}

print_section() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
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

get_main_version() {
    python3 -c "import re; content = open('setup.py').read(); match = re.search(r'version\s*=\s*[\"\']([\d.]+)[\"\']', content); print(match.group(1) if match else '')"
}

get_mcp_version() {
    python3 -c "import re; content = open('simexp-mcp/pyproject.toml').read(); match = re.search(r'version\s*=\s*[\"\']([\d.]+)[\"\']', content); print(match.group(1) if match else '')"
}

# Main workflow
main() {
    print_header "SimExp Coordinated Release System"
    echo ""
    echo "This script manages releases for:"
    echo "  1. simexp (main package)"
    echo "  2. simexp-mcp (MCP server package)"
    echo ""
    echo "It ensures proper version coordination and release sequencing."
    echo ""

    # Pre-flight checks
    print_section "Pre-flight Checks"
    check_clean_working_tree
    print_success "Working directory clean"

    check_on_main_branch
    print_success "On correct branch"

    MAIN_VER=$(get_main_version)
    MCP_VER=$(get_mcp_version)

    print_success "Main package version: $MAIN_VER"
    print_success "MCP package version: $MCP_VER"
    echo ""

    # Release strategy
    print_section "Release Strategy"
    echo ""
    echo "Choose release scope:"
    echo ""
    echo "  1) Release main package only (simexp)"
    echo "  2) Release MCP package only (simexp-mcp)"
    echo "  3) Release both packages (coordinated)"
    echo "  4) Test releases (both to TestPyPI)"
    echo ""
    read -p "Select (1-4): " scope

    case $scope in
        1)
            release_main_only
            ;;
        2)
            release_mcp_only
            ;;
        3)
            release_both_coordinated
            ;;
        4)
            test_release_both
            ;;
        *)
            print_error "Invalid selection"
            exit 1
            ;;
    esac

    echo ""
    print_header "Release Complete! 🎉"
}

release_main_only() {
    print_section "Releasing Main Package Only"
    echo ""
    echo "Running release workflow for simexp..."
    echo ""

    bash release.sh
}

release_mcp_only() {
    print_section "Releasing MCP Package Only"
    echo ""
    echo "Running release workflow for simexp-mcp..."
    echo ""

    cd simexp-mcp
    bash release.sh
    cd ..
}

release_both_coordinated() {
    print_section "Coordinated Release: Both Packages"
    echo ""

    # Step 1: Release main package
    echo -e "${CYAN}Step 1: Releasing main package (simexp)${NC}"
    bash release.sh

    MAIN_NEW_VER=$(get_main_version)
    echo ""
    print_success "Main package released: v$MAIN_NEW_VER"

    # Step 2: Release MCP package
    echo ""
    echo -e "${CYAN}Step 2: Releasing MCP package (simexp-mcp)${NC}"
    cd simexp-mcp
    bash release.sh
    cd ..

    MCP_NEW_VER=$(get_mcp_version)
    echo ""
    print_success "MCP package released: v$MCP_NEW_VER"

    # Summary
    echo ""
    print_section "Coordinated Release Summary"
    echo ""
    echo -e "${GREEN}✅ Main Package (simexp): v$MAIN_NEW_VER${NC}"
    echo -e "${GREEN}✅ MCP Package (simexp-mcp): v$MCP_NEW_VER${NC}"
    echo ""
    echo "Both packages are now available on PyPI with coordinated versions."
    echo ""
    echo "Next steps:"
    echo "  1. Verify both packages on PyPI:"
    echo "     - https://pypi.org/project/simexp/"
    echo "     - https://pypi.org/project/simexp-mcp/"
    echo "  2. Test installation:"
    echo "     - pip install --upgrade simexp simexp-mcp"
    echo "  3. Verify functionality:"
    echo "     - simexp --help"
    echo "     - simexp-mcp --help"
}

test_release_both() {
    print_section "Test Release: Both Packages to TestPyPI"
    echo ""

    # Main package test release
    echo -e "${CYAN}Step 1: Test release main package${NC}"
    make test-release

    MAIN_NEW_VER=$(get_main_version)
    echo ""
    print_success "Main package test released: v$MAIN_NEW_VER"

    # MCP package test release
    echo ""
    echo -e "${CYAN}Step 2: Test release MCP package${NC}"
    cd simexp-mcp
    make test-release
    cd ..

    MCP_NEW_VER=$(get_mcp_version)
    echo ""
    print_success "MCP package test released: v$MCP_NEW_VER"

    # Summary
    echo ""
    print_section "Test Release Summary"
    echo ""
    echo -e "${GREEN}✅ Main Package (simexp): v$MAIN_NEW_VER${NC}"
    echo -e "${GREEN}✅ MCP Package (simexp-mcp): v$MCP_NEW_VER${NC}"
    echo ""
    echo "Both packages are now available on TestPyPI."
    echo ""
    echo "Test installation:"
    echo "  pip install -i https://test.pypi.org/simple/ simexp==$MAIN_NEW_VER simexp-mcp==$MCP_NEW_VER"
    echo ""
    echo "After verification, run production releases:"
    echo "  bash release-all.sh  # Choose option 3 for coordinated release"
}

# Run main function
main
