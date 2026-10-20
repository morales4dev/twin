## MODIFIED Requirements

### Requirement: Turn B remains the existing twin completion
When Python starts Turn B, the system SHALL run the existing twin completion: primary-then-fallback LLM calls, twin system prompt, tools, and the conversation-windowed Gradio history. The history sent to the career model SHALL be at most the newest 8 prior turns plus the current user message, as defined by conversation-window. An earlier canned refusal SHALL reach Turn B only when it still sits inside those 8 turns. Turn A remaining stateless does not strip that windowed memory from Turn B.

#### Scenario: In-scope turn uses tools and history
- **WHEN** Python parses Turn A as `IN_SCOPE`
- **THEN** Turn B is invoked with tools, the twin system prompt, and at most the newest 8 prior turns plus the current user message

#### Scenario: Earlier refusal remains in Turn B history
- **WHEN** a later turn is `IN_SCOPE` after an earlier canned refusal in the same Gradio session
- **AND** that refusal still sits inside the newest 8 prior turns
- **THEN** Turn B still receives that refusal in the windowed history
