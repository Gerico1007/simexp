.PHONY: clean bump build upload upload-test test-release help

help:
	@echo "SimExp MCP Build & Release Automation"
	@echo "====================================="
	@echo ""
	@echo "Development Commands:"
	@echo "  make clean              Remove build artifacts (build/, dist/, *.egg-info)"
	@echo "  make bump               Auto-increment patch version"
	@echo "  make build              Create wheel and source distributions"
	@echo ""
	@echo "Release Commands:"
	@echo "  make upload             Upload to production PyPI"
	@echo "  make upload-test        Upload to TestPyPI"
	@echo ""
	@echo "Combined Workflows:"
	@echo "  make test-release       FULL AUTOMATION: bump + clean + build + upload-test"
	@echo ""

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Clean complete"

bump:
	@echo "📦 Bumping version..."
	python3 ../bump.py mcp patch
	@echo "✅ Version bumped"

build: clean
	@echo "🔨 Building distributions..."
	python3 -m build
	@echo "✅ Build complete"
	@echo ""
	@echo "📋 Checking package integrity..."
	twine check dist/*
	@echo "✅ Package check passed"

upload: build
	@echo "🚀 Uploading to production PyPI..."
	twine upload dist/*
	@echo "✅ Upload complete"

upload-test: build
	@echo "🧪 Uploading to TestPyPI..."
	twine upload --repository testpypi dist/*
	@echo "✅ TestPyPI upload complete"

test-release: bump build upload-test
	@echo ""
	@echo "✨ Full test release workflow complete!"
	@echo "   Version updated, built, and uploaded to TestPyPI"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Test installation: pip install -i https://test.pypi.org/simple/ simexp-mcp"
	@echo "  2. Verify functionality with: simexp-mcp --help"
	@echo "  3. If successful, run: make upload"

.PHONY: clean bump build upload upload-test test-release help
