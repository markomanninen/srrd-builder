# Guide for AI Agents - SRRD-Builder Project

## Introduction

This guide provides specific instructions for AI agents contributing to the SRRD-Builder project. The project uses a neurosymbolic approach, combining traditional symbolic programming (rule-based systems, structured knowledge, logic) with neural networks/large language models to create scientific research requirement documents. All AI agents must follow these guidelines to ensure consistency, quality, and effective collaboration.
  
## Practical Chat-Agent Guidelines
When operating in a chat/assistant mode, AI agents should incorporate these practices to enhance code quality and design:
- Ask clarifying questions before implementation if requirements are unclear or incomplete.
- Explicitly state and confirm assumptions or uncertainties with the user.
- Decompose larger tasks into smaller, verifiable subtasks and seek approval at each step.
- Present design rationale and obtain user validation on architectures or API choices prior to coding.
- Summarize progress, outstanding tasks, and avoid prematurely claiming completion.
- Surface known AI limitations (hallucinations, overconfidence) and invite reality checks.
- Provide illustrative code examples paired with unit tests to verify functionality.
- Offer alternative solutions when relevant, highlighting trade-offs.
- Define clear acceptance criteria and confirm them before proceeding to the next phase.
- Conduct a post-implementation self-review covering correctness, edge cases, and adherence to project standards.

These guidelines are written for you—the AI-powered chat agent in VS Code—so you can autonomously ingest context, plan and validate your actions step-by-step, manage uncertainty, integrate natively with the editor, reflect on your reasoning, and enforce safety guardrails.

	1.	Workspace-Root Law — Always derive the workspace root from workspace.workspaceFolders[0].uri.fsPath and verify it matches git rev-parse --show-toplevel; if they differ, stop and alert the user.  ￼ ￼ ￼
	2.	Canonical-Path Law — Resolve every path to an absolute, canonical form (e.g., path.resolve, Path.resolve()); abort if the result no longer starts with the workspace root to block traversal attacks.  ￼ ￼ ￼
	3.	Controlled-CWD Law — Run scripts and tasks only with an explicit "options.cwd" (or equivalent), and restore the original working directory immediately afterward.  ￼ ￼
	4.	Remote-Root Law — When using Dev Containers or Remote SSH, refresh the detected root each session to account for path remapping.  ￼
	5.	Guardrail Enforcement Law — Enforce runtime guardrails that block commands, file accesses, or API calls outside whitelisted zones.  ￼
	6.	Validation Law — After every code edit or command, run the project’s configured linters and tests; halt on any failure before proceeding.  ￼
	7.	Clarification Law — If path, file, or intent is ambiguous—or your confidence is low—pause and ask targeted clarifying questions instead of guessing.  ￼
	8.	Token-Economy Law — Scan or list only the minimal subset of files needed for the current step, caching results to conserve tokens and latency.  ￼ ￼
	9.	Audit-Trail Law — Log every resolved path, directory change, command, and test result to an internal agent.pathlog for post-task auditing and improvement.  ￼ ￼
	10.	Dependency-Safety Law — Verify each external package or binary against the official registry (npm, PyPI, etc.) before install or import; reject unknown or spoofed names.  ￼
	11.	Self-Reflection Law — After completing a task, review your own reasoning chain and outputs, then update prompts or heuristics to reduce future errors.  ￼
	12.	Uncertainty-Propagation Law — Attach a confidence score to every reasoning step and propagate it forward; if any score drops below the safe threshold, trigger Law 7.  ￼
	13.	Minimal-Privilege Law — Operate with the least privileges necessary, requesting additional permissions only when a task demonstrably requires them.  ￼ ￼
	14.	Rollback Law — Keep a reversible edit buffer or Git stash; if validation fails, revert changes before retrying or asking the user.  ￼
	15.	Time-Budget Law — Cap chain-of-thought length and directory scans to a sensible limit (e.g., 30 s or 4 KB tokens) to maintain responsiveness.  ￼

## SRRD Project Core Principles

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

### 3. Development State Honesty
- **NEVER claim "production ready" unless ALL criteria are met**
- Be honest about current development state and limitations
- Use accurate status descriptions: "Development", "Testing", "Beta", "Production"
- Avoid overhyping or making premature maturity claims

### 4. Test Quality Standards (MANDATORY)
- **ALL tests must pass - 100% success rate is MANDATORY**
- **NO warnings allowed** - fix all warnings before claiming completion
- **NO skipped tests** - every test must be executed and pass
- **NO failures tolerated** - agent must continue solving until 100% pass rate
- Test suite must run to completion without hanging or timeouts
- Only claim test completion when these standards are met

### 5. Production Readiness Criteria
**Production Ready means ALL of the following are true:**
- ✅ **100% test pass rate** with comprehensive test coverage
- ✅ **Zero warnings** in all test runs and builds
- ✅ **Complete documentation** including installation, usage, and troubleshooting
- ✅ **Error handling** for all failure scenarios with graceful degradation
- ✅ **Security validation** with input sanitization and secure defaults
- ✅ **Performance validation** with acceptable response times under load
- ✅ **User acceptance testing** completed by actual users
- ✅ **Deployment procedures** tested and documented
- ✅ **Monitoring and logging** implemented for production issues
- ✅ **Backup and recovery** procedures tested and documented

**If ANY of these criteria are not met, the system is in DEVELOPMENT state**

### 6. Neurosymbolic Development
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

3. **Testing in `work/tests/` - RIGOROUS STANDARDS**
   - **MANDATORY**: ALL tests must pass (100% success rate)
   - **NO warnings allowed** - fix all warnings before proceeding
   - **NO skipped tests** - every test must execute and pass
   - **NO failures tolerated** - continue problem solving until 100% pass
   - Create unit tests for individual components
   - Develop integration tests for neurosymbolic interaction (symbolic-neural integration)
   - Test with various research scenarios
   - Validate output quality and consistency
   - **Test suite must complete without hanging or timeouts**

### Phase 3: Review and Refinement
1. **Self-Review Checklist - DEVELOPMENT STATE ASSESSMENT**
   - **HONEST status assessment** - avoid overhyping maturity
   - Code follows project conventions
   - Documentation is comprehensive and clear
   - **Tests achieve 100% pass rate with zero warnings**
   - Components integrate properly with existing system
   - Output meets scientific research standards
   - **System limitations and known issues documented**

2. **Validation Process - RIGOROUS STANDARDS**
   - Test with example research scenarios
   - Verify compliance with academic standards
   - Check for bias or methodological flaws
   - Ensure reproducibility of results
   - **Complete error handling validation**
   - **Performance under load testing**
   - **Security vulnerability assessment**

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

### Code Quality - MANDATORY STANDARDS
- **Documentation**: Every function and class must have comprehensive docstrings
- **Type Hints**: Use type hints throughout Python code
- **Testing**: **100% test pass rate required** - no failures, warnings, or skips allowed
- **Performance**: Profile and optimize critical paths
- **Security**: Validate all inputs and handle sensitive data appropriately
- **Error Handling**: Comprehensive error handling with graceful degradation

### Content Quality - RIGOROUS STANDARDS
- **Accuracy**: All scientific claims must be verifiable and properly cited
- **Completeness**: Generated documents must cover all essential research planning components
- **Clarity**: Use clear, precise language appropriate for scientific communication
- **Consistency**: Maintain consistent terminology and formatting throughout
- **Bias Awareness**: Actively identify and mitigate potential biases in generated content

### Integration Quality - PRODUCTION STANDARDS
- **Interfaces**: Design clean, well-documented interfaces between components
- **Error Handling**: Graceful degradation when components fail
- **Monitoring**: Implement logging and monitoring for system health
- **Scalability**: Design for handling increased load and complexity
- **Reliability**: System must handle edge cases and unexpected inputs

### Development State Communication - HONESTY REQUIRED
- **Accurate Status**: Use precise development state descriptions
  - **"Development"**: Core functionality incomplete, tests failing
  - **"Testing"**: Core functionality complete, achieving test pass rates
  - **"Beta"**: All tests pass, user testing in progress
  - **"Production Ready"**: ALL production criteria met (see criteria above)
- **Known Limitations**: Document all current limitations and issues
- **Avoid Overhyping**: Never claim higher maturity than actually achieved

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

### Anti-Patterns to Avoid - CRITICAL
- **Direct Production**: Never develop directly in production directories
- **Monolithic Design**: Avoid large, non-modular components that mix symbolic and neural logic
- **Hallucination Tolerance**: Never accept unverified neural/AI-generated facts without symbolic validation
- **Single Point of Failure**: Avoid dependencies on single LLM providers or single symbolic rule sets
- **Premature Status Claims**: Never claim "production ready" without meeting ALL criteria
- **Test Tolerance**: Never accept test failures, warnings, or skipped tests
- **Overhyping Maturity**: Avoid inflating current development state or capabilities
- **Incomplete Error Handling**: Never ignore edge cases or error conditions

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

### Technical Metrics - MANDATORY STANDARDS
- **Test Success Rate**: 100% pass rate - no failures, warnings, or skips allowed
- **Code Coverage**: Maintain >95% test coverage (not just 80%)
- **Performance**: Response time <5 seconds for standard documents
- **Reliability**: >99.9% uptime for production systems (when actually production)
- **Quality**: <1% error rate in generated documents
- **Zero Warnings**: All builds and tests must complete without warnings

### Research Quality Metrics - RIGOROUS STANDARDS
- **Scientific Validity**: 100% compliance with scientific method principles
- **Completeness**: All required research planning components present
- **Clarity**: Readable by target research community
- **Actionability**: Generated requirements can be directly implemented
- **Reproducibility**: All results must be reproducible
- **Ethical Compliance**: All ethical standards met

### Development State Metrics - HONEST ASSESSMENT
- **Feature Completeness**: Percentage of planned features implemented
- **Test Coverage**: Actual test coverage with pass rate breakdown
- **Known Issues**: Number and severity of outstanding bugs
- **Documentation Coverage**: Percentage of code/features documented
- **User Validation**: Results of actual user testing (if any)
- **Security Assessment**: Results of security testing and validation

### User Experience Metrics
- **Usability**: Users can generate documents with minimal training
- **Satisfaction**: High user satisfaction scores
- **Adoption**: Increasing usage across different research domains
- **Efficiency**: Significant time savings compared to manual planning

---

**Remember**: The goal is to enhance scientific research quality and accessibility while maintaining the highest standards of academic rigor and ethical responsibility. Every contribution should advance this mission.

## VSCode Environment for AI Agents

To ensure a consistent, productive setup in VSCode, install and configure the following:

1. Recommended Extensions
   - GitHub Copilot (GitHub.copilot)
   - VS Code AI Tools (ms-vscode.vscode-ai)
   - Markdown Linting (DavidAnson.vscode-markdownlint)
   - Prettier (esbenp.prettier-vscode)
   - GitLens (eamodio.gitlens)
2. Workspace Settings
   - Enable format on save for code and markdown.
   - Enable inline AI suggestions:
     ```json
     "editor.inlineSuggest.enabled": true,
     "github.copilot.inlineSuggest.enable": true
     ```
   - Lint Markdown on save:
     ```json
     "markdownlint.config": { "default": true }
     ```
3. Tasks and Snippets
   - Define tasks in `.vscode/tasks.json` for running tests (`npm test`/`pytest`) with zero warnings enforcement.
   - Provide AI-focused snippets (`.code-snippets/ai-agent.code-snippets`) for common templates (research outline, prompt skeleton).
4. Usage Tips
   - Use Copilot Chat for Socratic questioning and iterative draft refinement.
   - Leverage “AI: Explain Code” commands to document symbolic and neural interfaces.
   - Keep the central GUIDE open (`work/docs/GUIDE_FOR_AI_AGENTS.md`) as your single source of truth.
