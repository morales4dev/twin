## RENAMED Requirements

### Requirement: Input guardrail match skips MiniMax and returns the canned refusal
**FROM:** Input guardrail match skips MiniMax and returns the canned refusal
**TO:** Input guardrail match skips the LLM and returns the canned refusal

## MODIFIED Requirements

### Requirement: Input guardrail match skips MiniMax and returns the canned refusal
When the input guardrail matches, the system SHALL return the existing canned twin refusal as the visitor-facing assistant reply. The system MUST NOT call the LLM (primary or fallback) for classification (Turn A) and MUST NOT call the LLM (primary or fallback) for a career completion (Turn B) on that turn. The Gradio chat UI SHALL remain the same ChatInterface; the blocked reply SHALL appear as a normal assistant message.

#### Scenario: Blocked turn never calls the model
- **WHEN** the latest user message matches the deny-list
- **THEN** the visitor receives the canned twin refusal
- **AND** no LLM call is sent for that turn on primary or fallback

#### Scenario: Refusal text is the existing canned phrase
- **WHEN** the input guardrail blocks a turn
- **THEN** the assistant reply is exactly: "As the digital twin of Alberto Morales, I am only authorized to discuss his professional background, experience, and the specific personal interests listed on his profile."

### Requirement: Typed email is recorded even when the input guardrail blocks
If the latest user message contains a typed email address, the system SHALL record that email in Python for follow-up. The system MUST record a typed email even when the input guardrail later blocks the turn or when the rest of the message is out of scope. The system MUST NOT invent, infer, or record an email that the visitor did not type in the latest user message.

#### Scenario: Email plus jailbreak still records the typed address
- **WHEN** the latest user message contains a typed email address and also matches the deny-list
- **THEN** the system records that typed email in Python
- **AND** the visitor still receives the canned refusal
- **AND** the visitor MUST NOT receive a lead acknowledgement
- **AND** no LLM call is made for that turn on primary or fallback

#### Scenario: Blocked turn without a typed email records nothing
- **WHEN** the latest user message matches the deny-list and contains no typed email address
- **THEN** the system MUST NOT record an email
- **AND** the visitor receives the canned refusal

#### Scenario: Email is not inferred from context
- **WHEN** the latest user message matches the deny-list and does not contain a typed email address
- **AND** an email appeared only in earlier history or in the twin sandbox
- **THEN** the system MUST NOT record that earlier or sandbox email
