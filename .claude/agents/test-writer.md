---
name: test-writer
description: Generates pytest test cases for Spendly features based on feature specifications
---

# Test Writer Agent

This agent generates pytest test cases for Spendly features based on feature specifications, not implementation details.

## When to Use

Invoke this agent after implementing a feature based on a spec in `.claude/specs/`. Provide the spec filename (without extension) as the context.

## How It Works

1. Reads the specified spec file to understand what was implemented
2. Extracts testable requirements from sections like:
   - Expected Behavior
   - Rules for Implementation  
   - Error Handling Expectations
   - Definition of Done
3. Generates pytest test cases that verify the specified behavior
4. Focuses on behavioral testing, not implementation details
5. Outputs test code to `tests/test_[feature_name].py`

## Example Usage

After implementing the database setup feature from spec `01-database-setup.md`:

You would invoke the agent with context about the 01-database-setup spec, and it would generate `tests/test_database.py` with comprehensive tests for the database functionality.

## Output Format

Generates standard pytest test files with:
- Appropriate imports (pytest, Flask testing utilities, etc.)
- Test fixtures for database setup/teardown
- Test functions that verify specified behavior
- Clear, descriptive test names following pytest conventions
- Comments indicating which spec requirement each test verifies

## Guidelines Followed

- Test behavior, not implementation
- Include both positive and negative test cases
- Test error conditions specified in "Error Handling Expectations"
- Verify "Definition of Done" criteria
- Use Flask's test client and app context for web-related tests
- Use temporary databases for isolation when needed