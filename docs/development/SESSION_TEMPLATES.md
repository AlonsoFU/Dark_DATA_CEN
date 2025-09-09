# Claude Code Session Templates

## Quick Reference Templates for Session Handoffs

### **Template A: Starting a New Profile Development**

```markdown
## New Profile Development Session

**Document Type:** [e.g., financial_reports, legal_contracts, etc.]
**Session Goal:** Create processing profile from scratch
**Expected Duration:** 2-4 hours

### Context:
- Document characteristics: [size, language, format complexity]
- Critical data to extract: [companies, amounts, dates, etc.]
- Quality targets: [90% extraction accuracy, <X min processing time]

### Sample Documents Available:
- Primary test: `data/raw/{document_type}/sample_001.pdf`
- Validation: `data/raw/{document_type}/sample_002.pdf`

### Session Plan:
1. Analyze document structure and create chapter definitions
2. Develop extraction patterns for critical entities
3. Set up validation rules and quality thresholds
4. Test on sample documents and refine patterns
5. Document progress and handoff status

### Commands to Start:
```bash
make create-profile --name {document_type}
make analyze-structure --document "sample_001.pdf" --interactive
```

**Success Criteria:**
- [ ] Profile structure created
- [ ] Chapter detection >80% confidence
- [ ] Critical entities extraction >75% accuracy
- [ ] Processing pipeline functional
```

### **Template B: Continuing Profile Refinement**

```markdown
## Profile Refinement Session

**Profile:** {profile_name} (v{version})
**Last Session:** {date} - {duration} hours
**Current Status:** {overall_quality}% quality, {issues_count} issues remaining

### Previous Session Summary:
{load from session_history/latest_session.json}

### Priority Issues:
1. **{issue_1_name}** (Priority: {High/Medium/Low})
   - Current: {current_performance}
   - Target: {target_performance}
   - Affected: {specific_files/pages}

2. **{issue_2_name}** (Priority: {High/Medium/Low})
   - Current: {current_performance}
   - Target: {target_performance}
   - Affected: {specific_files/pages}

### Session Goals:
- [ ] Address priority issue #1
- [ ] Improve overall quality from {current}% to {target}%
- [ ] Validate improvements on test documents
- [ ] Update session progress log

### Commands to Start:
```bash
make load-profile --name {profile_name}
make load-session-context --profile {profile_name} --show-history
make test-chapter --chapter {problematic_chapter} --profile {profile_name}
```

### Quality Targets:
- Overall extraction: {current}% → {target}%
- Critical entities: {current}% → {target}%
- Processing speed: maintain <{time} per document
```

### **Template C: Production Validation Session**

```markdown
## Production Validation Session

**Profile:** {profile_name} (v{version})
**Development Status:** Feature-complete, ready for validation
**Validation Goal:** Confirm production readiness

### Quality Benchmarks Achieved:
- Overall extraction: {quality}% (target: >90%)
- Critical entities: {quality}% (target: >95%)
- Processing speed: {time} per document (target: <{target_time})
- Cross-document consistency: {consistency}% (target: >85%)

### Validation Test Suite:
- [ ] Test on {N} diverse documents
- [ ] Stress test with large documents (500+ pages)
- [ ] Performance benchmarking
- [ ] Error handling validation
- [ ] Quality consistency check

### Commands to Run:
```bash
make production-validation --profile {profile_name} --documents "data/test/{profile_name}/*.pdf"
make benchmark-performance --profile {profile_name}
make stress-test --profile {profile_name} --large-documents
```

### Production Deployment Checklist:
- [ ] All validation tests pass
- [ ] Quality metrics meet targets
- [ ] Performance within acceptable limits
- [ ] Error handling works correctly
- [ ] Documentation complete
- [ ] Rollback plan prepared

### Post-Validation:
If successful: `make deploy-profile --name {profile_name} --version {version} --to production`
If issues found: Document issues and return to refinement phase
```

---

## Session Progress Tracking Templates

### **Session Start Template**
```json
{
  "session_info": {
    "session_id": "session_{XXX}",
    "profile": "{profile_name}",
    "start_time": "{ISO_datetime}",
    "goals": [
      "Goal 1: specific objective",
      "Goal 2: specific objective"
    ],
    "estimated_duration_hours": 2.0
  },
  "baseline_metrics": {
    "overall_quality": 0.XX,
    "critical_issues_count": X,
    "processing_speed_minutes": X.X,
    "test_documents": ["doc1.pdf", "doc2.pdf"]
  },
  "focus_areas": [
    {
      "area": "chapter_detection", 
      "current_status": "XX% confidence",
      "target": ">90% confidence"
    }
  ]
}
```

### **Session Progress Update Template**
```json
{
  "session_id": "session_{XXX}",
  "timestamp": "{ISO_datetime}",
  "progress_update": {
    "achievements": [
      "Improved company extraction from 78% to 85%",
      "Fixed RUT number validation pattern"
    ],
    "current_metrics": {
      "overall_quality": 0.XX,
      "chapter_performance": {
        "technical_specs": 0.XX,
        "company_reports": 0.XX
      }
    },
    "issues_resolved": [
      "Company name variations now handled correctly"
    ],
    "new_issues_discovered": [
      "Page boundary detection failing on pages 200+"
    ]
  },
  "next_steps": [
    "Test updated patterns on validation documents",
    "Address page boundary detection issue"
  ]
}
```

### **Session End Template**
```json
{
  "session_info": {
    "session_id": "session_{XXX}",
    "profile": "{profile_name}",
    "end_time": "{ISO_datetime}",
    "actual_duration_hours": X.X,
    "status": "completed|paused|blocked"
  },
  "achievements": {
    "quality_improvements": {
      "overall": {"from": 0.XX, "to": 0.XX},
      "specific_chapters": {
        "chapter_name": {"from": 0.XX, "to": 0.XX}
      }
    },
    "issues_resolved": [
      "Issue 1 description and solution",
      "Issue 2 description and solution"
    ],
    "new_patterns_added": [
      "Pattern description and effectiveness"
    ]
  },
  "current_status": {
    "overall_quality": 0.XX,
    "production_readiness": "XX% complete",
    "critical_issues_remaining": X,
    "next_priorities": [
      "Priority 1 with specific target",
      "Priority 2 with specific target"
    ]
  },
  "handoff_notes": {
    "immediate_next_steps": [
      "Step 1: specific action",
      "Step 2: specific action"  
    ],
    "test_documents_status": {
      "primary_test_doc.pdf": "90% quality - good progress",
      "validation_doc.pdf": "85% quality - needs work on chapters 5-6"
    },
    "recommended_focus": "Focus area for next session"
  }
}
```

---

## Communication Templates

### **Status Report Template**
```markdown
## {Profile_Name} Development Status Report

**Date:** {current_date}
**Session:** {session_number}
**Time Invested:** {total_hours} hours across {session_count} sessions

### 📊 Quality Metrics:
- **Overall Extraction:** {XX}% (target: 90%+)
- **Critical Data:** {XX}% (companies, technical specs, etc.)
- **Processing Speed:** {X.X} minutes per 300-page document
- **Consistency:** {XX}% across different documents

### ✅ Completed Milestones:
- [x] Profile structure and configuration created
- [x] Chapter detection patterns developed
- [x] Critical entity extraction working
- [x] Validation framework implemented

### 🔄 Current Status:
**Phase:** {Discovery/Refinement/Validation/Production}
**Focus:** {current_focus_area}
**Issues:** {X} remaining issues

### 🎯 Next Session Goals:
1. {Specific goal 1}
2. {Specific goal 2} 
3. {Specific goal 3}

### 📋 Production Readiness:
- Extraction Quality: {✅/⚠️/❌}
- Processing Speed: {✅/⚠️/❌}
- Error Handling: {✅/⚠️/❌}
- Documentation: {✅/⚠️/❌}
```

### **Issue Report Template**
```markdown
## Issue Report: {Issue_Title}

**Profile:** {profile_name}
**Severity:** {High/Medium/Low}
**Chapter:** {affected_chapter}
**Discovery Date:** {date}

### Problem Description:
{Detailed description of what's not working}

### Current Behavior:
- Extraction accuracy: {XX}%
- Affected documents: {list}
- Specific pages/sections: {details}

### Expected Behavior:
- Target accuracy: {XX}%
- Should extract: {specific entities}
- Pattern should match: {pattern description}

### Steps to Reproduce:
1. Load profile: `make load-profile --name {profile_name}`
2. Test chapter: `make test-chapter --chapter {chapter_name}`
3. Review results: {specific observation}

### Potential Solutions:
1. **Option 1:** {solution description}
2. **Option 2:** {alternative solution}
3. **Option 3:** {fallback solution}

### Impact:
- Blocks production deployment: {Yes/No}
- Affects quality targets: {Yes/No}
- Workaround available: {Yes/No}
```

---

## Quick Commands Reference

### **Session Management:**
```bash
# Start new session
make start-session --profile {name} --goals "goal1,goal2"

# Load previous session context
make load-session-context --profile {name} --show-history

# Save current progress
make save-session-progress --profile {name} --notes "progress summary"

# End session with handoff notes
make end-session --profile {name} --handoff-notes "next steps"
```

### **Quality Monitoring:**
```bash
# Quick quality check
make quality-check --profile {name} --document "{test_doc}"

# Compare with previous session
make compare-quality --profile {name} --baseline "session_XXX"

# Generate status report
make status-report --profile {name} --format markdown
```

### **Issue Tracking:**
```bash
# Log new issue
make log-issue --profile {name} --title "issue_title" --severity high

# Update issue status  
make update-issue --profile {name} --issue-id XXX --status resolved

# List current issues
make list-issues --profile {name} --status open
```

These templates ensure consistent documentation, clear communication, and systematic progress tracking across all Claude Code sessions, enabling seamless collaboration and continuous improvement of document processing profiles.