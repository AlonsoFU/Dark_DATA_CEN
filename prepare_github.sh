#!/bin/bash
# GitHub Repository Preparation Script
# Run this script to prepare the repository for GitHub

echo "🚀 Preparing Dark Data Platform for GitHub..."
echo "============================================="

# 1. Replace README with GitHub version
echo "📝 Updating README for GitHub..."
if [ -f "README_GITHUB.md" ]; then
    cp README_GITHUB.md README.md
    rm README_GITHUB.md
    echo "✅ README.md updated for GitHub"
else
    echo "⚠️  README_GITHUB.md not found, keeping existing README.md"
fi

# 2. Clean temporary files
echo "🧹 Cleaning temporary files..."
rm -f demo_extraction.py simple_page_extractor.py
echo "✅ Temporary demo files removed"

# 3. Set up git hooks (if not already done)
echo "🔧 Setting up git hooks..."
if [ -f ".git/hooks/pre-commit" ]; then
    echo "✅ Pre-commit hooks already configured"
else
    if command -v pre-commit &> /dev/null; then
        pre-commit install
        echo "✅ Pre-commit hooks installed"
    else
        echo "⚠️  pre-commit not found, install with: pip install pre-commit"
    fi
fi

# 4. Check Git status
echo "📊 Git repository status..."
git status --porcelain | head -10

echo ""
echo "🎯 GitHub Preparation Complete!"
echo "================================"
echo ""
echo "📂 Files created/updated:"
echo "  ✅ .gitignore (enhanced with project-specific patterns)"
echo "  ✅ README.md (GitHub-ready version)"
echo "  ✅ LICENSE (MIT license)"
echo "  ✅ CONTRIBUTING.md (contribution guidelines)" 
echo "  ✅ .github/workflows/ci.yml (GitHub Actions CI)"
echo "  ✅ .github/ISSUE_TEMPLATE/ (bug reports, feature requests)"
echo "  ✅ .github/PULL_REQUEST_TEMPLATE.md (PR template)"
echo ""
echo "🚀 Next steps:"
echo "  1. Review all files and make any final adjustments"
echo "  2. Commit all changes: git add . && git commit -m 'feat: prepare repository for GitHub'"
echo "  3. Create GitHub repository"
echo "  4. Push to GitHub: git remote add origin <your-repo-url> && git push -u origin main"
echo ""
echo "🌟 Your Dark Data Platform is ready for GitHub!"