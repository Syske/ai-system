---
name: mock-test
description: Generate Mockito unit tests for Java classes. Use when writing or extending unit tests for services, mappers, or facades — creating mocks, stubbing dependencies, verifying interactions, and covering edge cases with idiomatic Mockito patterns.
---

## Scope

1. Identify the class and method under test
2. Determine what needs mocking (dependencies, external calls)
3. Check if tests already exist — only add if coverage is missing

## Test Generation

1. Use Mockito for mocking, JUnit 5 as the test framework
2. Write focused unit tests — one logical assertion per test method
3. Name tests descriptively: `methodName_scenario_expectedBehavior`
4. Cover: happy path, edge cases, error conditions

## Validation

1. Verify tests compile and pass
2. Confirm tests actually test the target logic (not mocks of mocks)
3. Check for unnecessary mocking or overspecification

## Output

Return: list of test files created/modified, what they test, and any coverage gaps.
