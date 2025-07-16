# Guide for AI Agents - SRRD-Builder Project

## Introduction

This guide provides specific instructions for AI agents contributing to the SRRD-Builder project. The project uses a neurosymbolic approach, combining traditional symbolic programming (rule-based systems, structured knowledge, logic) with neural networks/large language models to create scientific research requirement documents. All AI agents must follow these guidelines to ensure consistency, quality, and effective collaboration.

## Core Principles

### 1. Work Directory First Approach
- **ALWAYS** start development in the `work/` directory
- Use `work/docs/` for document drafts
- Use `work/code/` for code development
- Use `work/tests/` for testing prototypes
- Only move to production directories (`src/`, `docs/`, etc.) after review and approval

### 2. Scientific Rigor
- Maintain high standards of scientific methodology in all generated content
- Validate research requirements against established academic standards
- Ensure all suggestions are evidence-based and citable
- Consider ethical implications in all research planning components

### 3. Neurosymbolic Development
- Create reusable components that can be combined for different research types
- Maintain clear separation between symbolic programming (rules, logic, structured knowledge) and neural/LLM components
- Design for extensibility across different scientific domains
- Document all interfaces and integration points between symbolic and neural components

## Development Workflow for AI Agents

### Phase 1: Analysis and Planning
1. **Requirement Analysis**
   - Analyze the specific research requirement document request
   - Identify required components (objectives, methodology, timeline, etc.)
   - Determine appropriate templates and knowledge base resources
   - Plan the neurosymbolic integration approach (how symbolic rules/logic will interface with LLM components)

2. **Context Gathering**
   - Research relevant scientific literature and standards
   - Identify domain-specific requirements and conventions
   - Gather institutional and regulatory requirements
   - Collect example documents for pattern analysis

### Phase 2: Draft Development
1. **Create Initial Drafts in `work/docs/`**
   - Start with outline and structure
   - Develop content iteratively
   - Document decision rationale
   - Include multiple alternative approaches when applicable

2. **Code Development in `work/code/`**
   - Implement symbolic programming components first (rule engines, knowledge graphs, logical validators)
   - Integrate neural/LLM components with clear interfaces
   - Create modular, testable code
   - Follow established coding standards and patterns

3. **Testing in `work/tests/`**
   - Create unit tests for individual components
   - Develop integration tests for neurosymbolic interaction (symbolic-neural integration)
   - Test with various research scenarios
   - Validate output quality and consistency

### Phase 3: Review and Refinement
1. **Self-Review Checklist**
   - Code follows project conventions
   - Documentation is comprehensive and clear
   - Tests provide adequate coverage
   - Components integrate properly with existing system
   - Output meets scientific research standards

2. **Validation Process**
   - Test with example research scenarios
   - Verify compliance with academic standards
   - Check for bias or methodological flaws
   - Ensure reproducibility of results

### Phase 4: Integration and Deployment
1. **Move to Production Directories**
   - Relocate approved code to appropriate `src/` subdirectories
   - Update main documentation in `docs/`
   - Add examples to `examples/` directory
   - Update project configuration files

2. **Final Integration Testing**
   - Run full system tests
   - Verify backward compatibility
   - Test user interface integration
   - Validate performance metrics

## Component-Specific Guidelines

### Symbolic Programming Components (`src/symbolic/`)
- **Knowledge Graphs**: Use standardized ontologies and structured knowledge representations
- **Rule Engines**: Implement clear, auditable logical rules with source citations
- **Templates**: Create flexible templates that adapt to various research types using structured logic
- **Validators**: Implement comprehensive validation with detailed error messages using rule-based systems

### Neural/LLM Integration Components (`src/llm/`)
- **Prompt Engineering**: Design robust prompts that consistently generate quality output
- **Model Selection**: Choose appropriate neural models for specific tasks (generation vs. analysis)
- **Context Management**: Implement effective context windowing and information prioritization
- **Output Processing**: Create reliable parsing and validation of neural network/LLM outputs

### Core Application Logic (`src/core/`)
- **Orchestration**: Manage the neurosymbolic integration between symbolic programming and neural components
- **Data Management**: Handle research data, templates, and generated documents
- **Configuration**: Provide flexible configuration for different use cases
- **Error Handling**: Implement comprehensive error handling and recovery

### MCP Server Components (`src/mcp/`)
- **Interactive Guidance**: Implement Socratic questioning system for requirement clarification
- **Methodology Advisory**: Provide expert-level guidance on research methodologies
- **Research Lifecycle Management**: Guide users through complete research process from planning to publication
- **Quality Assurance Integration**: Implement comprehensive quality gates and peer review simulation
- **Collaborative Features**: Enable multi-user interaction and ideation sessions

### User Interface Components (`src/ui/`)
- **Usability**: Design intuitive interfaces for researchers and AI systems
- **Visualization**: Create clear visualizations of research requirements and progress
- **Interactivity**: Enable real-time editing and refinement of generated documents
- **Accessibility**: Ensure accessibility for users with different needs and capabilities

## Quality Standards

### Code Quality
- **Documentation**: Every function and class must have comprehensive docstrings
- **Type Hints**: Use type hints throughout Python code
- **Testing**: Minimum 80% test coverage for all new code
- **Performance**: Profile and optimize critical paths
- **Security**: Validate all inputs and handle sensitive data appropriately

### Content Quality
- **Accuracy**: All scientific claims must be verifiable and properly cited
- **Completeness**: Generated documents must cover all essential research planning components
- **Clarity**: Use clear, precise language appropriate for scientific communication
- **Consistency**: Maintain consistent terminology and formatting throughout
- **Bias Awareness**: Actively identify and mitigate potential biases in generated content

### Integration Quality
- **Interfaces**: Design clean, well-documented interfaces between components
- **Error Handling**: Graceful degradation when components fail
- **Monitoring**: Implement logging and monitoring for system health
- **Scalability**: Design for handling increased load and complexity

## Collaboration Guidelines

### Communication
- **Documentation**: Document all decisions and rationale
- **Comments**: Use clear, informative code comments
- **Commit Messages**: Write descriptive commit messages following conventional commit format
- **Issue Tracking**: Use issue tracking for bug reports and feature requests

### Version Control
- **Branching**: Use feature branches for all development
- **Pull Requests**: All changes must go through pull request review
- **Testing**: Ensure all tests pass before submitting pull requests
- **Documentation**: Update documentation with all changes

### Knowledge Sharing
- **Best Practices**: Share discovered best practices with the team
- **Lessons Learned**: Document challenges and solutions for future reference
- **Research Insights**: Share relevant scientific research and methodological insights
- **Tool Recommendations**: Recommend useful tools and resources

## Ethical Considerations

### Research Ethics
- **IRB Compliance**: Ensure generated documents address appropriate ethical review processes
- **Consent Protocols**: Include proper consent mechanisms in research designs
- **Data Privacy**: Address data protection and privacy requirements
- **Vulnerable Populations**: Provide appropriate protections for vulnerable research subjects

### AI Ethics
- **Transparency**: Make AI involvement in document generation clear
- **Bias Mitigation**: Actively work to identify and reduce bias in generated content
- **Human Oversight**: Ensure appropriate human review of AI-generated research plans
- **Responsibility**: Maintain clear accountability for AI-generated recommendations

### Academic Integrity
- **Originality**: Ensure generated content is original and properly attributed
- **Citation Standards**: Follow appropriate citation standards for all domains
- **Plagiarism Prevention**: Implement checks to prevent accidental plagiarism
- **Credit Assignment**: Properly credit all contributors, including AI systems

## Common Patterns and Anti-Patterns

### Recommended Patterns
- **Template-First Design**: Start with structured symbolic templates and enhance with neural AI
- **Layered Validation**: Multiple validation layers from syntax to semantics using both rule-based and AI validation
- **Incremental Generation**: Build documents incrementally with user feedback using neurosymbolic approaches
- **Domain Adaptation**: Customize approaches for specific scientific domains using both symbolic knowledge and neural adaptation

### Anti-Patterns to Avoid
- **Direct Production**: Never develop directly in production directories
- **Monolithic Design**: Avoid large, non-modular components that mix symbolic and neural logic
- **Hallucination Tolerance**: Never accept unverified neural/AI-generated facts without symbolic validation
- **Single Point of Failure**: Avoid dependencies on single LLM providers or single symbolic rule sets

## Troubleshooting and Support

### Common Issues
- **LLM Inconsistency**: Implement multiple retry strategies and validation
- **Knowledge Base Gaps**: Provide mechanisms for knowledge base updates
- **Template Limitations**: Design flexible template extension mechanisms
- **Integration Failures**: Implement robust error handling and fallback strategies

### Getting Help
- **Documentation**: Check existing documentation first
- **Issue Tracking**: Search existing issues before creating new ones
- **Code Review**: Request code review for complex implementations
- **Domain Experts**: Consult with domain experts for scientific validation

## Success Metrics

### Technical Metrics
- **Code Coverage**: Maintain >80% test coverage
- **Performance**: Response time <5 seconds for standard documents
- **Reliability**: >99% uptime for production systems
- **Quality**: <5% error rate in generated documents

### Research Quality Metrics
- **Scientific Validity**: 100% compliance with scientific method principles
- **Completeness**: All required research planning components present
- **Clarity**: Readable by target research community
- **Actionability**: Generated requirements can be directly implemented

### User Experience Metrics
- **Usability**: Users can generate documents with minimal training
- **Satisfaction**: High user satisfaction scores
- **Adoption**: Increasing usage across different research domains
- **Efficiency**: Significant time savings compared to manual planning

---

**Remember**: The goal is to enhance scientific research quality and accessibility while maintaining the highest standards of academic rigor and ethical responsibility. Every contribution should advance this mission.
