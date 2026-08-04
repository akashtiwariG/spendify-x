---
name: write-tests
description: Generates pytest test cases for Spendly features based on feature specifications
---

# Test Writer Skill

This skill generates pytest test cases for Spendly features based on feature specifications, not implementation details.

## When to Use

Use this skill after implementing a feature based on a spec in `.claude/specs/`. 

## How It Works

1. You specify which spec file to use as the basis for tests
2. The skill reads the spec to understand what was implemented
3. It generates pytest test cases that verify the behavior described in the spec
4. Focus is on testing what the software should do, not how it's implemented
5. Outputs test code to the appropriate tests/ file

## Usage

After implementing a feature from a spec (e.g., `01-database-setup.md`):

You would invoke this skill and provide the spec identifier, and it would generate corresponding tests.

## Example

After implementing database setup from `01-database-setup.md`, running this skill would generate tests in `tests/test_database.py` that verify:
- Database connection properties
- Table creation and schema
- Seed data insertion
- Constraint enforcement
- And all other behaviors specified in the spec

## Implementation Notes

This skill would typically be implemented by an agent that:
- Reads the specified spec file
- Parses sections like Expected Behavior, Definition of Done, etc.
- Generates appropriate pytest test functions
- Creates proper test fixtures for isolation
- Follows pytest best practices