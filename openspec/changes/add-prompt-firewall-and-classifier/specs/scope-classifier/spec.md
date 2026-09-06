## Purpose

Stateless binary classification of the current visitor message so only in-scope career questions reach the twin completion; classify and answer are never the same MiniMax call.

## ADDED Requirements

### Requirement: Classify and answer are separate completions
Each Gradio turn that is not blocked by the prompt firewall SHALL run a dedicated classifier completion (Turn A) before any career completion. The system MUST NOT produce a visitor-facing career answer from the classifier completion. Classify and answer MUST NEVER be the same MiniMax completion.

#### Scenario: Firewall already blocked
- **WHEN** the prompt firewall matches the latest user message
- **THEN** the system MUST NOT start Turn A or Turn B

#### Scenario: Firewall did not match
- **WHEN** the prompt firewall does not match the latest user message
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
- **AND** the firewall did not already block the turn
- **THEN** Turn A still returns only a scope label
- **AND** Python routing, not the override text, decides whether Turn B runs

### Requirement: Turn A output is exactly one binary label
Turn A output SHALL be exactly `IN_SCOPE` or `OUT_OF_SCOPE` (one label, no essay). There is no `LEAD`, `SKILL_TRAP`, or `META` class. `IN_SCOPE` means questions about Alberto’s professional background, experience, and the personal interests listed on his profile. `OUT_OF_SCOPE` means skill traps, meta or security questions, generic off-topic chat, and any mixed turn. A mixed turn that combines a career question with a skill trap or jailbreak SHALL be entirely `OUT_OF_SCOPE`.

#### Scenario: Career question is in scope
- **WHEN** the current user message asks only about Alberto’s professional background, experience, or listed personal interests
- **THEN** the expected classifier label is `IN_SCOPE`

#### Scenario: Skill trap is out of scope
- **WHEN** the current user message asks to be taught a CV technology (for example “teach me Kubernetes”)
- **THEN** the expected classifier label is `OUT_OF_SCOPE`

#### Scenario: Meta question is out of scope
- **WHEN** the current user message asks what the twin is or to dump prompt or memory
- **THEN** the expected classifier label is `OUT_OF_SCOPE`

#### Scenario: Mixed turn is entirely out of scope
- **WHEN** the current user message combines a career question with a skill trap or jailbreak
- **THEN** the expected classifier label is `OUT_OF_SCOPE`

### Requirement: Python fail-closed routing owns the visitor-facing reply
The system SHALL parse the Turn A label in Python. Python MUST NOT use Turn A content as the visitor-facing reply. Only a parsed `IN_SCOPE` SHALL start Turn B. `OUT_OF_SCOPE`, any other token, empty or unparseable output, or a classifier error SHALL fail closed: the visitor receives the existing canned twin refusal and Turn B MUST NOT run.

#### Scenario: Parsed IN_SCOPE starts Turn B
- **WHEN** Python parses Turn A as exactly `IN_SCOPE`
- **THEN** the system starts Turn B

#### Scenario: Parsed OUT_OF_SCOPE refuses without Turn B
- **WHEN** Python parses Turn A as `OUT_OF_SCOPE`
- **THEN** the visitor receives the canned twin refusal
- **AND** Turn B MUST NOT run

#### Scenario: Unparseable classifier output fails closed
- **WHEN** Turn A returns empty output, an essay, or any token other than `IN_SCOPE` or `OUT_OF_SCOPE`
- **THEN** the visitor receives the canned twin refusal
- **AND** Turn B MUST NOT run

#### Scenario: Classifier error fails closed
- **WHEN** the Turn A MiniMax call errors
- **THEN** the visitor receives the canned twin refusal
- **AND** Turn B MUST NOT run

#### Scenario: Classifier text is not shown to the visitor
- **WHEN** Turn A returns any content
- **THEN** that content is not used as the visitor-facing assistant reply

### Requirement: Turn B remains the existing twin completion
When Python starts Turn B, the system SHALL run the existing twin completion: same MiniMax model, twin system prompt, tools, and the current Gradio chat history (including earlier refusals). History hygiene is out of this change. Turn A remaining stateless does not strip memory from Turn B.

#### Scenario: In-scope turn uses tools and history
- **WHEN** Python parses Turn A as `IN_SCOPE`
- **THEN** Turn B is invoked with tools and the current Gradio chat history plus the twin system prompt

#### Scenario: Earlier refusal remains in Turn B history
- **WHEN** a later turn is `IN_SCOPE` after an earlier canned refusal in the same Gradio session
- **THEN** Turn B still receives that refusal in the current Gradio chat history
