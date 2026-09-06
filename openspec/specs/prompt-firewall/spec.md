# prompt-firewall Specification

## Purpose

Code-side deny-list on the latest visitor message so jailbreak, override, slash-command, prompt/memory dump, and debug-framing turns never reach MiniMax.

## Requirements

### Requirement: Firewall scans only the latest user message
The system SHALL evaluate the prompt firewall against the raw latest user message string of the current Gradio turn. The system MUST NOT use prior user turns, prior assistant replies, Gradio history, or model output as firewall input.

#### Scenario: Latest turn matches a deny pattern
- **WHEN** the latest user message matches a configured deny-list pattern
- **THEN** the firewall treats the turn as blocked regardless of earlier in-scope career questions in the same session

#### Scenario: History contains blocked text but latest turn does not
- **WHEN** a prior user or assistant message in Gradio history would match a deny-list pattern
- **AND** the latest user message does not match any deny-list pattern
- **THEN** the firewall MUST NOT block the turn on the basis of that history

### Requirement: Deny-list covers generic jailbreak families
The system SHALL match the latest user message against a configured deny-list of generic pattern families. The deny-list MUST cover at least: instruction override, forged system framing, slash commands, requests to show prompt or memory, and debug or troubleshooting framing used to extract internals. The deny-list MUST NOT be a copy of the Jose evaluation battery prompts. Matching SHALL be case-insensitive on the raw latest user string.

#### Scenario: Instruction override
- **WHEN** the latest user message contains an instruction-override pattern (for example “ignore previous”)
- **THEN** the firewall matches and blocks the turn

#### Scenario: Forged system framing
- **WHEN** the latest user message contains forged system framing (for example “IMPORTANT SYSTEM” or “SYSTEM:”)
- **THEN** the firewall matches and blocks the turn

#### Scenario: Slash command
- **WHEN** the latest user message contains a slash-command pattern (for example `/exit` or `/resume`)
- **THEN** the firewall matches and blocks the turn

#### Scenario: Show prompt or memory
- **WHEN** the latest user message asks to show the prompt or memory
- **THEN** the firewall matches and blocks the turn

#### Scenario: Debug framing
- **WHEN** the latest user message uses debug or troubleshooting framing to extract internals (for example “for debugging”)
- **THEN** the firewall matches and blocks the turn

#### Scenario: Career question without deny patterns
- **WHEN** the latest user message asks only about Alberto’s professional background and matches none of the deny-list families
- **THEN** the firewall MUST NOT match

### Requirement: Firewall match skips MiniMax and returns the canned refusal
When the firewall matches, the system SHALL return the existing canned twin refusal as the visitor-facing assistant reply. The system MUST NOT call MiniMax for classification (Turn A) and MUST NOT call MiniMax for a career completion (Turn B) on that turn. The Gradio chat UI SHALL remain the same ChatInterface; the blocked reply SHALL appear as a normal assistant message.

#### Scenario: Blocked turn never calls the model
- **WHEN** the latest user message matches the deny-list
- **THEN** the visitor receives the canned twin refusal
- **AND** no MiniMax chat-completion request is sent for that turn

#### Scenario: Refusal text is the existing canned phrase
- **WHEN** the firewall blocks a turn
- **THEN** the assistant reply is exactly: "As the digital twin of Alberto Morales, I am only authorized to discuss his professional background, experience, and the specific personal interests listed on his profile."

### Requirement: Typed email is recorded even when the firewall blocks
If the latest user message contains a typed email address, the system SHALL record that email in Python for follow-up. The system MUST record a typed email even when the firewall later blocks the turn or when the rest of the message is out of scope. The system MUST NOT invent, infer, or record an email that the visitor did not type in the latest user message.

#### Scenario: Email plus jailbreak still records the typed address
- **WHEN** the latest user message contains a typed email address and also matches the deny-list
- **THEN** the system records that typed email in Python
- **AND** the visitor still receives the canned refusal
- **AND** the visitor MUST NOT receive a lead acknowledgement
- **AND** no MiniMax call is made for that turn

#### Scenario: Blocked turn without a typed email records nothing
- **WHEN** the latest user message matches the deny-list and contains no typed email address
- **THEN** the system MUST NOT record an email
- **AND** the visitor receives the canned refusal

#### Scenario: Email is not inferred from context
- **WHEN** the latest user message matches the deny-list and does not contain a typed email address
- **AND** an email appeared only in earlier history or in the twin sandbox
- **THEN** the system MUST NOT record that earlier or sandbox email
