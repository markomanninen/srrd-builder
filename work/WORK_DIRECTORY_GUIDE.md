# Work Directory Guide

## Purpose

The `work/` directory serves as the development sandbox for the SRRD-Builder project. All initial development, prototyping, and experimentation happens here before components are promoted to production directories.

## Directory Structure

```text
work/
├── docs/                      # Draft documents and specifications
│   ├── README_DRAFT.md        # Project README draft
│   ├── GUIDE_FOR_AI_AGENTS.md # AI agent collaboration guide
│   └── specifications/        # Technical specifications
├── code/                      # Development code
│   ├── prototypes/           # Early prototypes and experiments
│   ├── symbolic/             # Symbolic reasoning components
│   ├── llm/                  # LLM integration experiments
│   └── integration/          # Component integration tests
└── tests/                     # Test cases and validation
    ├── unit/                 # Unit tests
    ├── integration/          # Integration tests
    └── validation/           # Content validation tests
```

## Development Workflow

### 1. Start Here Always

- All new features begin in `work/`
- Create appropriate subdirectories as needed
- Document your approach in `work/docs/`

### 2. Iterative Development

- Develop incrementally
- Test frequently
- Document decisions and rationale
- Keep track of alternative approaches

### 3. Quality Gates

Before moving to production directories, ensure:

- [ ] Code is well-documented
- [ ] Tests provide adequate coverage
- [ ] Documentation is complete
- [ ] Components integrate properly
- [ ] Scientific accuracy is validated

### 4. Promotion Process

When ready for production:

1. Review all work directory contents
2. Move code to appropriate `src/` subdirectories
3. Update main project documentation
4. Run full integration tests
5. Archive work directory contents with version tags

## Current Status

### Completed

- [x] README draft with comprehensive project overview
- [x] AI agent collaboration guide
- [x] Work directory structure and guidelines

### In Progress

- [ ] Technical specifications for core components
- [ ] Prototype symbolic reasoning engine
- [ ] LLM integration framework
- [ ] Template system design

### Next Steps

1. Define technical specifications for each component
2. Create initial prototypes in `work/code/prototypes/`
3. Develop test cases for validation
4. Begin integration experiments

## Guidelines for Contributors

### File Naming

- Use descriptive, lowercase names with underscores
- Include version or draft indicators: `_draft`, `_v1`, `_prototype`
- Date stamp important milestones: `_20250716`

### Documentation

- Document all decisions and rationale
- Include alternative approaches considered
- Note dependencies and requirements
- Track issues and resolutions

### Version Control

- Commit frequently with descriptive messages
- Use feature branches for significant changes
- Tag important milestones
- Keep work directory history for reference

---

This directory is the foundation for all development activities. Use it to experiment, learn, and refine before committing to production implementations.
