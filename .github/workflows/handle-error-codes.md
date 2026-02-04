---
description: |
  Automatic error code mapping handler. When new error code issues are created,
  this workflow extracts the error code and description, finds the appropriate
  mapping file in the codebase, adds the new error code entry, and creates
  a pull request with the changes.

on:
  issues:
    types: [opened]

permissions: read-all

safe-outputs:
  create-pull-request:

tools:
  edit:
  web-fetch:

timeout-minutes: 10
---

# Error Code Handler

You are a software developer helping to maintain error code mappings in the pysamsungnasa project.

When a new issue is created with the "error-code" label, your job is to process it and add the error code mapping.

## Steps

1. **Extract error details** from issue #${{ github.event.issue.number }}:
   - Read the issue to find the error code (decimal format, e.g., 101)
   - Read the error description

2. **Find the error code mapping file**: 
   - The error codes are mapped in `pysamsungnasa/protocol/factory/errors.py`
   - This file contains an `ERROR_CODES` dictionary

3. **Add the new error code**:
   - Insert the error code and description to the `ERROR_CODES` dictionary
   - Keep the dictionary sorted by error code number
   - Use snake_case for description names (e.g., "test_error_code")

4. **Create a pull request**:
   - Create a PR with title: "Add error code mapping: E{code} - {description}"
   - Include a reference to the issue in the PR body
   - Link the PR to the original issue

## Implementation

Extract the decimal error code and description from the issue, then add it to the ERROR_CODES dictionary in the correct sorted position with the format `{code}: "{snake_case_description}"`.
