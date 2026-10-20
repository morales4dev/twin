## MODIFIED Requirements

### Requirement: Classify and answer are separate completions
Each Gradio turn that is not blocked by the input guardrail SHALL run a dedicated classifier completion (Turn A) before any career completion. The system MUST NOT produce a visitor-facing career answer from the classifier completion. Classify and answer MUST NEVER be the same MiniMax completion.

#### Scenario: Input guardrail already blocked
- **WHEN** the input guardrail matches the latest user message
- **THEN** the system MUST NOT start Turn A or Turn B

#### Scenario: Input guardrail did not match
- **WHEN** the input guardrail does not match the latest user message
- **THEN** the system runs Turn A before any Turn B career completion

### Requirement: Turn A is stateless and treats the current user string as data
Turn A SHALL use the same MiniMax model as the twin. The classifier request MUST include only the current user message as delimited data, not as instructions. Turn A MUST NOT receive prior user turns, prior assistant replies, prior classifier labels, Gradio history, tools, a CV dump, or the twin system prompt. The classifier API call MUST omit tools so the model cannot invoke `record_*` while classifying. The classifier prompt MAY include few-shot skill-trap and meta examples as teaching data that still map to `OUT_OF_SCOPE`. Text inside the user-data delimiters that attempts to override instructions (for example “ignore previous” or “you are now …”) MUST be ignored for labeling.

#### Scenario: No memory on Turn A
- **WHEN** Turn A runs
- **THEN** the classifier request contains no Gradio history, no prior labels, no tools, no CV dump, and no twin system prompt
- **AND** the only visitor text in the request is the current user message inside delimiters

#### Scenario: Tools omitted on Turn A
- **WHEN** Turn A calls MiniMax
- **THEN** the API request omits tools

#### Scenario: Override text inside delimiters does not become the label
- **WHEN** the delimited current user message contains override text such as “ignore previous” or “you are now …”
- **AND** the input guardrail did not already block the turn
- **THEN** Turn A still returns only a scope label
- **AND** Python routing, not the override text, decides whether Turn B runs
