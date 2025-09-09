# Contributing to Dark Data Platform

Thank you for your interest in contributing to the Dark Data Platform! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/dark-data-platform.git
   cd dark-data-platform
   ```

2. **Set up development environment**
   ```bash
   make install-dev  # Installs dependencies and pre-commit hooks
   ```

3. **Run tests to ensure everything works**
   ```bash
   make test-quick
   ```

## 🎯 Current Development Priorities

### **High Priority (Help Needed)**
- **Complete ANEXO 1 extraction** (Pages 31-62) - Currently 50% complete
- **Develop ANEXO 5 & 6 patterns** - High business value chapters
- **Improve OCR accuracy** for power plant name recognition
- **Enhance validation algorithms** for data quality

### **Medium Priority**
- Add support for new document types
- Improve web dashboard visualizations  
- Expand MCP tool capabilities
- Add batch processing features

## 🏗️ Development Workflow

### **1. Choose Your Contribution Area**

#### **Document Processing** (Most Needed)
- Location: `scripts/eaf_processing/chapters/`
- Focus: Complete extraction scripts for individual chapters
- Skills: Python, PDF processing, OCR, pattern recognition

#### **Core Platform** 
- Location: `dark_data/`
- Focus: Database, processors, analyzers, web interface
- Skills: Python, SQLite, Flask, MCP protocol

#### **Quality & Testing**
- Location: `tests/`
- Focus: Test coverage, validation scripts, quality assurance
- Skills: pytest, quality assurance, validation logic

### **2. Development Process**

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes following our standards**
   - Type hints required for all functions
   - Follow existing code patterns
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   make lint      # Code quality checks
   make format    # Auto-format code
   make test      # Run full test suite
   ```

4. **Commit with descriptive messages**
   ```bash
   git commit -m "feat: add ANEXO 5 extraction patterns"
   ```

5. **Create pull request**
   - Use our PR template
   - Include tests and documentation
   - Reference related issues

## 📋 Code Standards

### **Python Code Quality**
- **Type hints**: Required for all function parameters and returns
- **Formatting**: Black + isort (run `make format`)
- **Linting**: flake8 + mypy (run `make lint`)
- **Testing**: pytest with coverage (run `make test`)

### **Document Processing Standards**
- **User validation**: All extractions must be user-validated
- **No hallucinations**: Implement safeguards against AI hallucinations
- **Pattern reuse**: Create reusable patterns for similar documents
- **Quality metrics**: Track and report extraction accuracy

### **Commit Message Format**
```
type(scope): short description

Longer description if needed

- Bullet points for details
- Reference issues: Fixes #123
```

**Types**: feat, fix, docs, style, refactor, test, chore

## 🎯 Specific Contribution Opportunities

### **🔥 High Impact - ANEXO 1 Completion**
**Current Status**: 50% complete (Pages 1-30 working, Pages 31-62 need work)

**What's Needed**:
- Improve OCR accuracy for pages 31-62
- Enhance table boundary detection
- Validate power plant name recognition
- Complete structured data extraction

**Files to Work On**:
- `scripts/eaf_processing/chapters/anexo_01_generation_programming/content_extraction/extract_anexo1_with_ocr_per_row.py`
- `scripts/eaf_processing/chapters/anexo_01_generation_programming/validation_quality/apply_corrections_with_review_summary.py`

### **🎯 Next Priority - ANEXO 5 & 6**
**Business Value**: High - Company reports and compliance data

**What's Needed**:
- Analyze ANEXO 5 & 6 document structure  
- Develop extraction patterns for company failure reports
- Create compliance data validation logic
- Build quality assurance for regulatory data

**Files to Create**:
- `scripts/eaf_processing/chapters/anexo_05_company_reports/content_extraction/`
- `scripts/eaf_processing/chapters/anexo_06_compliance_data/content_extraction/`

### **🛠️ Platform Enhancement**
- **Web Dashboard**: Improve visualizations in `dark_data/web/`
- **MCP Integration**: Enhance AI tools in `dark_data/mcp/`
- **Database Layer**: Optimize queries in `dark_data/database/`
- **CLI Tools**: Improve user experience in `dark_data/cli/`

## 🧪 Testing Guidelines

### **Test Organization**
```
tests/
├── unit/              # Fast isolated tests
├── integration/       # Database and API tests  
├── e2e/              # End-to-end workflow tests
```

### **Testing Document Processing**
- Test extraction accuracy with sample data
- Validate user interaction workflows  
- Ensure no hallucinations in output
- Test edge cases and error handling

### **Running Tests**
```bash
make test              # Full test suite
make test-quick        # Unit tests only  
pytest tests/unit/specific_test.py -v  # Specific test
```

## 📚 Documentation

### **Code Documentation**
- Type hints for all functions
- Docstrings for complex functions
- README files for each major component
- Update CLAUDE.md for development guidance

### **User Documentation**
- Update main README.md for new features
- Add examples for new document types
- Document new CLI commands or options

## 🔍 Code Review Process

### **Before Submitting PR**
- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes (or clearly marked)
- [ ] Manual testing completed

### **PR Review Checklist**
- Code quality and consistency
- Test coverage and correctness
- Documentation completeness
- User validation workflow (for extraction features)
- Performance impact assessment

## 🎯 Document Processing Best Practices

### **Interactive Validation Pattern**
```python
# Always use user validation for extractions
results = extract_data(document)
validated_results = user_validate(results)  # User approves each extraction
save_results(validated_results)  # Only save user-approved data
```

### **Quality Assurance**
- Cross-reference multiple extraction methods
- Implement confidence scoring
- Provide audit trails for all extractions
- Enable easy correction of extraction errors

### **Pattern Recognition**
- Create reusable patterns for similar documents
- Build pattern libraries for document families
- Enable pattern learning from user corrections

## 🆘 Getting Help

- **Documentation**: Check `CLAUDE.md` and existing README files
- **Issues**: Browse existing GitHub issues for context
- **Questions**: Open a new issue with the "question" label
- **Discussion**: Use GitHub Discussions for broader topics

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Project documentation  
- Release notes for significant contributions

Thank you for helping transform buried document intelligence into actionable insights!

---

**Happy Contributing!** 🎉