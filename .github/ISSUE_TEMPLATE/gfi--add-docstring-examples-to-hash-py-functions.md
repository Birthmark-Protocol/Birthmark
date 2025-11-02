---
name: 'GFI: Add docstring examples to hash.py functions'
about: Help new contributors understand our core hashing logic by adding practical
  examples to the function documentation.
title: ''
labels: ''
assignees: ''

---

## Description
The functions in `src/birthmark/hash.py` have docstrings but could use more detailed examples. Add example code snippets showing realistic use cases.

## Tasks
- [ ] Add examples to `compute_image_hash()` showing how to hash an image file
- [ ] Add examples to `compute_file_hash()` demonstrating memory-efficient processing
- [ ] Add examples to `verify_hash()` showing verification workflow
- [ ] Include error handling examples for each function
- [ ] Ensure all examples use runnable code (not pseudocode)

## Acceptance Criteria
- Each public function has at least one example in its docstring
- Examples are runnable code snippets
- Edge cases are demonstrated (file not found, invalid algorithm, etc.)

## Suggested Approach
Look at the existing docstrings in `src/birthmark/hash.py` and expand the "Example:" sections with more realistic use cases. Follow Google-style docstring format.

## Resources
- Current code: `src/birthmark/hash.py`
- Google docstring guide: https://google.github.io/styleguide/pyguide.html#383-functions-and-methods
