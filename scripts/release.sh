#!/bin/bash

# RepairGPT Release Script
# Automates the release process for RepairGPT

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default values
RELEASE_TYPE="patch"
DRY_RUN=false
SKIP_TESTS=false
SKIP_BUILD=false

# Help function
show_help() {
    cat << EOF
RepairGPT Release Script

Usage: $0 [OPTIONS]

Options:
    -t, --type TYPE         Release type: major, minor, patch (default: patch)
    -d, --dry-run          Show what would be done without executing
    -s, --skip-tests       Skip running tests
    -b, --skip-build       Skip building the package
    -h, --help             Show this help message

Examples:
    $0 --type minor                # Create a minor release
    $0 --dry-run                   # Show what would happen
    $0 --type patch --skip-tests   # Quick patch release without tests

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            RELEASE_TYPE="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -s|--skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        -b|--skip-build)
            SKIP_BUILD=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate release type
if [[ ! "$RELEASE_TYPE" =~ ^(major|minor|patch)$ ]]; then
    log_error "Invalid release type: $RELEASE_TYPE. Must be major, minor, or patch."
    exit 1
fi

# Check if we're on main branch
check_branch() {
    local current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "main" ]]; then
        log_error "You must be on the main branch to create a release. Current branch: $current_branch"
        exit 1
    fi
}

# Check for uncommitted changes
check_clean_working_tree() {
    if ! git diff-index --quiet HEAD --; then
        log_error "Working tree is not clean. Please commit or stash your changes."
        exit 1
    fi
}

# Get current version
get_current_version() {
    if [[ -f "setup.py" ]]; then
        python setup.py --version 2>/dev/null || echo "0.1.0"
    elif [[ -f "pyproject.toml" ]]; then
        grep '^version' pyproject.toml | cut -d'"' -f2 || echo "0.1.0"
    elif [[ -f "src/version.py" ]]; then
        grep '__version__' src/version.py | cut -d'"' -f2 || echo "0.1.0"
    else
        echo "0.1.0"
    fi
}

# Calculate new version
calculate_new_version() {
    local current_version=$1
    local release_type=$2
    
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    local major=${VERSION_PARTS[0]}
    local minor=${VERSION_PARTS[1]}
    local patch=${VERSION_PARTS[2]}
    
    case "$release_type" in
        "major")
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        "minor")
            minor=$((minor + 1))
            patch=0
            ;;
        "patch")
            patch=$((patch + 1))
            ;;
    esac
    
    echo "$major.$minor.$patch"
}

# Run tests
run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log_warning "Skipping tests as requested"
        return 0
    fi
    
    log_info "Running tests..."
    
    if [[ -d "tests" ]] && [[ "$(ls -A tests)" ]]; then
        if command -v pytest &> /dev/null; then
            pytest tests/ -v || {
                log_error "Tests failed. Release aborted."
                exit 1
            }
        else
            log_warning "pytest not found, skipping tests"
        fi
    else
        log_warning "No tests found, skipping test run"
    fi
    
    log_success "Tests passed"
}

# Build package
build_package() {
    if [[ "$SKIP_BUILD" == "true" ]]; then
        log_warning "Skipping build as requested"
        return 0
    fi
    
    log_info "Building package..."
    
    # Clean previous builds
    rm -rf dist/ build/ *.egg-info/
    
    # Create setup.py if it doesn't exist
    if [[ ! -f "setup.py" ]] && [[ ! -f "pyproject.toml" ]]; then
        log_info "Creating setup.py..."
        cat > setup.py << EOF
from setuptools import setup, find_packages

setup(
    name="repairgpt",
    version="$NEW_VERSION",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.9",
)
EOF
    fi
    
    # Build the package
    if command -v python -m build &> /dev/null; then
        python -m build
    else
        python setup.py sdist bdist_wheel
    fi
    
    log_success "Package built successfully"
}

# Update version files
update_version() {
    local new_version=$1
    
    log_info "Updating version to $new_version..."
    
    # Update src/version.py
    mkdir -p src
    echo "__version__ = \"$new_version\"" > src/version.py
    
    # Update setup.py if it exists
    if [[ -f "setup.py" ]]; then
        sed -i.bak "s/version=\"[^\"]*\"/version=\"$new_version\"/g" setup.py
        rm -f setup.py.bak
    fi
    
    # Update pyproject.toml if it exists
    if [[ -f "pyproject.toml" ]]; then
        sed -i.bak "s/^version = \"[^\"]*\"/version = \"$new_version\"/g" pyproject.toml
        rm -f pyproject.toml.bak
    fi
    
    log_success "Version updated to $new_version"
}

# Commit and tag
commit_and_tag() {
    local new_version=$1
    
    log_info "Committing version bump and creating tag..."
    
    git add -A
    git commit -m "Bump version to $new_version"
    git tag "v$new_version"
    
    log_success "Created tag v$new_version"
}

# Generate changelog
generate_changelog() {
    local new_version=$1
    
    log_info "Generating changelog..."
    
    local last_tag=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")
    local changelog_file="CHANGELOG-v$new_version.md"
    
    cat > "$changelog_file" << EOF
# RepairGPT v$new_version Release Notes

## What's Changed

EOF
    
    if [[ -z "$last_tag" ]]; then
        git log --pretty=format:"- %s (%h)" --no-merges >> "$changelog_file"
    else
        git log $last_tag..HEAD --pretty=format:"- %s (%h)" --no-merges >> "$changelog_file"
    fi
    
    cat >> "$changelog_file" << EOF

## Installation

\`\`\`bash
pip install repairgpt==$new_version
\`\`\`

## Docker

\`\`\`bash
docker pull repairgpt:$new_version
\`\`\`

**Full Changelog**: https://github.com/\$(git config --get remote.origin.url | sed 's/.*github\.com[:\/]//g' | sed 's/\.git$//g')/compare/$last_tag...v$new_version
EOF
    
    log_success "Changelog generated: $changelog_file"
}

# Main execution
main() {
    log_info "Starting RepairGPT release process..."
    log_info "Release type: $RELEASE_TYPE"
    log_info "Dry run: $DRY_RUN"
    
    # Pre-flight checks
    check_branch
    check_clean_working_tree
    
    # Get versions
    CURRENT_VERSION=$(get_current_version)
    NEW_VERSION=$(calculate_new_version "$CURRENT_VERSION" "$RELEASE_TYPE")
    
    log_info "Current version: $CURRENT_VERSION"
    log_info "New version: $NEW_VERSION"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN - Would perform the following actions:"
        log_info "1. Update version from $CURRENT_VERSION to $NEW_VERSION"
        log_info "2. Run tests (skip: $SKIP_TESTS)"
        log_info "3. Build package (skip: $SKIP_BUILD)"
        log_info "4. Commit changes and create tag v$NEW_VERSION"
        log_info "5. Generate changelog"
        exit 0
    fi
    
    # Confirm with user
    read -p "Proceed with release $NEW_VERSION? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Release cancelled"
        exit 0
    fi
    
    # Execute release steps
    run_tests
    update_version "$NEW_VERSION"
    build_package
    commit_and_tag "$NEW_VERSION"
    generate_changelog "$NEW_VERSION"
    
    log_success "Release $NEW_VERSION completed successfully!"
    log_info "Next steps:"
    log_info "1. Push the tag: git push origin v$NEW_VERSION"
    log_info "2. Push the main branch: git push origin main"
    log_info "3. The GitHub Actions workflow will handle the rest"
}

# Run main function
main "$@"