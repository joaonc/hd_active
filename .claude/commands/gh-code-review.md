---
description: Fetch a GitHub PR, review it, and post findings as a comment
argument-hint: <pr-number>
allowed-tools: mcp__github__get_pull_request, mcp__github__get_pull_request_files, mcp__github__get_pull_request_comments, mcp__github__add_issue_comment, Read, Grep, Glob
---

# GitHub PR Code Review

You will perform a comprehensive code review of a GitHub pull request and post findings as a comment to the PR. Do NOT make any code changes.

## Instructions

1. **Fetch PR Details**: Use the GitHub MCP tools to:
   - Get PR #$ARGUMENTS details (owner, repo, PR number)
   - Fetch the full diff/changed files
   - List the files that were modified

2. **Gather Context**:
   - Read the key files in the repository to understand the codebase architecture, patterns, and conventions
   - Focus on the main source files, config files, and any CLAUDE.md or README files that explain the project
   - Understand the tech stack and existing code style

3. **Comprehensive Review**: Analyze the PR changes across ALL dimensions:
   - **Security**: Auth, data validation, injection risks, secrets exposure
   - **Performance**: Algorithmic complexity, N+1 queries, memory usage, caching
   - **Style & Readability**: Naming, line length, unnecessary complexity
   - **Architecture**: Design patterns, separation of concerns, coupling
   - **Testing**: Test coverage, edge cases, test quality
   - **Error Handling**: Exception handling, graceful degradation, logging
   - **Documentation**: Comments, docstrings, README updates needed

4. **Post Review**: Use GitHub MCP to create a comment on PR #$ARGUMENTS with:
   - Summary of findings (1-2 sentences)
   - Issues grouped by severity (Critical → Info)
   - For each issue: the file, line (if applicable), what's wrong, and how to fix it
   - Praise for good patterns you found
   - No code diffs—just guidance

## Format for GitHub Comment

Use this structure for your PR comment:

```
## Code Review for PR #$ARGUMENTS

**Summary**: [1-2 sentence overview]

### 🔴 Critical Issues
- [Issue]: [File/Line] - Description and fix

### 🟡 Warnings
- [Issue]: [File/Line] - Description and fix

### 💡 Suggestions
- [Suggestion]: [File/Line] - Description and how to improve

### ✅ Strengths
- [Pattern]: [File] - What's done well
```

Do not make code changes. Do not approve or request changes—only provide detailed feedback.


