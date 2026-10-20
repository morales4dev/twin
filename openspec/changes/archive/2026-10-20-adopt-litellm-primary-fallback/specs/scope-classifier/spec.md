## MODIFIED Requirements

### Requirement: Classify and answer are separate completions
Each Gradio turn that is not blocked by the input guardrail SHALL run a dedicated classifier completion (Turn A) before any career completion. The system MUST NOT produce a visitor-facing career answer from the classifier completion. Classify and answer MUST NEVER be the same LLM call.

#### Scenario: Input guardrail already blocked
- **WHEN** the input guardrail matches the latest user message
- **THEN** the system MUST NOT start Turn A or Turn B

#### Scenario: Input guardrail did not match
- **WHEN** the input guardrail does not match the latest user message
- **THEN** the system runs Turn A before any Turn B career completion

### Requirement: Turn A is stateless and treats the current user string as data
Turn A SHALL use the same primary-then-fallback LLM rule as Turn B. The classifier request MUST include only the current user message as delimited data, not as instructions. Turn A MUST NOT receive prior user turns, prior assistant replies, prior classifier labels, Gradio history, tools, a CV dump, or the twin system prompt. The classifier API call MUST omit tools so the model cannot invoke `record_*` while classifying. The classifier prompt MAY include few-shot skill-trap and meta examples as teaching data that still map to `OUT_OF_SCOPE`. Text inside the user-data delimiters that attempts to override instructions (for example “ignore previous” or “you are now …”) MUST be ignored for labeling.

#### Scenario: No memory on Turn A
- **WHEN** Turn A runs
- **THEN** the classifier request contains no Gradio history, no prior labels, no tools, no CV dump, and no twin system prompt
- **AND** the only visitor text in the request is the current user message inside delimiters

#### Scenario: Tools omitted on Turn A
- **WHEN** Turn A makes an LLM call
- **THEN** the API request omits tools

#### Scenario: Override text inside delimiters does not become the label
- **WHEN** the delimited current user message contains override text such as “ignore previous” or “you are now …”
- **AND** the input guardrail did not already block the turn
- **THEN** Turn A still returns only a scope label
- **AND** Python routing, not the override text, decides whether Turn B runs

### Requirement: Python fail-closed routing owns the visitor-facing reply
The system SHALL parse the Turn A label in Python. Before reading a label, Python MUST discard any `<think>…</think>` reasoning blocks in Turn A content (those blocks MAY span multiple lines). After those blocks are removed, the remaining text MUST parse as exactly `IN_SCOPE` or `OUT_OF_SCOPE` (optional surrounding whitespace or blank lines). Python MUST NOT treat a label that appears only inside a reasoning block as the parsed label. Python MUST NOT use Turn A content as the visitor-facing reply. Only a parsed `IN_SCOPE` SHALL start Turn B. `OUT_OF_SCOPE`, any other token, empty or unparseable output, or a Turn A LLM call that failed on both primary and fallback SHALL fail closed: Turn B MUST NOT run. When Turn B does not run and the latest user message contained a typed email address, the visitor-facing reply SHALL be a Python lead acknowledgement that interpolates that extracted address (LEAD_ACK). When Turn B does not run and the latest user message contained no typed email address, the visitor SHALL receive the existing canned twin refusal. The LLM MUST NOT generate LEAD_ACK. A successful fallback classify is a normal `IN_SCOPE` or `OUT_OF_SCOPE`. `OUT_OF_SCOPE` and unparseable labels MUST NOT be treated as a call error and MUST NOT trigger fallback.

#### Scenario: Parsed IN_SCOPE starts Turn B
- **WHEN** Python parses Turn A as exactly `IN_SCOPE`
- **THEN** the system starts Turn B

#### Scenario: Parsed OUT_OF_SCOPE refuses without Turn B
- **WHEN** Python parses Turn A as `OUT_OF_SCOPE`
- **AND** the latest user message contains no typed email address
- **THEN** the visitor receives the canned twin refusal
- **AND** Turn B MUST NOT run

#### Scenario: Parsed OUT_OF_SCOPE with typed email acknowledges the lead
- **WHEN** Python parses Turn A as `OUT_OF_SCOPE`
- **AND** the latest user message contains a typed email address
- **THEN** the system records that typed email in Python
- **AND** the visitor receives LEAD_ACK interpolating that extracted address
- **AND** Turn B MUST NOT run

#### Scenario: Think block then IN_SCOPE is in scope
- **WHEN** Turn A content contains a `<think>…</think>` block followed by `IN_SCOPE`
- **THEN** Python parses Turn A as `IN_SCOPE`
- **AND** the system starts Turn B

#### Scenario: Think block then OUT_OF_SCOPE is out of scope
- **WHEN** Turn A content contains a `<think>…</think>` block followed by `OUT_OF_SCOPE`
- **AND** the latest user message contains no typed email address
- **THEN** Python parses Turn A as `OUT_OF_SCOPE`
- **AND** the visitor receives the canned twin refusal
- **AND** Turn B MUST NOT run

#### Scenario: Label only inside a think block fails closed
- **WHEN** Turn A content names `IN_SCOPE` or `OUT_OF_SCOPE` only inside a `<think>…</think>` block
- **AND** nothing parseable as a label remains after that block is removed
- **AND** the latest user message contains no typed email address
- **THEN** the visitor receives the canned twin refusal
- **AND** Turn B MUST NOT run

#### Scenario: Unparseable classifier output fails closed
- **WHEN** Turn A returns empty output, an essay, or any token other than `IN_SCOPE` or `OUT_OF_SCOPE`
- **AND** the latest user message contains no typed email address
- **THEN** the visitor receives the canned twin refusal
- **AND** Turn B MUST NOT run
- **AND** the system MUST NOT try fallback for that unparseable output

#### Scenario: Classifier error fails closed
- **WHEN** both the primary and fallback LLM calls for Turn A fail
- **AND** the latest user message contains no typed email address
- **THEN** the visitor receives the canned twin refusal
- **AND** Turn B MUST NOT run

#### Scenario: Primary failure with fallback success is a normal classify
- **WHEN** the Turn A primary call fails
- **AND** the Turn A fallback call returns a parseable label
- **THEN** Python treats that label as a normal Turn A result
- **AND** MUST NOT fail closed for the primary error

#### Scenario: Fail-closed with typed email acknowledges the lead
- **WHEN** Turn A is unparseable or both primary and fallback LLM calls for Turn A fail
- **AND** the latest user message contains a typed email address
- **THEN** the system records that typed email in Python
- **AND** the visitor receives LEAD_ACK interpolating that extracted address
- **AND** Turn B MUST NOT run

#### Scenario: Classifier text is not shown to the visitor
- **WHEN** Turn A returns any content
- **THEN** that content is not used as the visitor-facing assistant reply

### Requirement: Turn B remains the existing twin completion
When Python starts Turn B, the system SHALL run the existing twin completion: primary-then-fallback LLM calls, twin system prompt, tools, and the current Gradio chat history (including earlier refusals). History hygiene is out of this change. Turn A remaining stateless does not strip memory from Turn B.

#### Scenario: In-scope turn uses tools and history
- **WHEN** Python parses Turn A as `IN_SCOPE`
- **THEN** Turn B is invoked with tools and the current Gradio chat history plus the twin system prompt

#### Scenario: Earlier refusal remains in Turn B history
- **WHEN** a later turn is `IN_SCOPE` after an earlier canned refusal in the same Gradio session
- **THEN** Turn B still receives that refusal in the current Gradio chat history
