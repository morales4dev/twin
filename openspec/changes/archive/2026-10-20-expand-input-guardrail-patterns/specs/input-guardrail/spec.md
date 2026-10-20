## MODIFIED Requirements

### Requirement: Deny-list covers generic jailbreak families
The system SHALL match the latest user message against a configured deny-list of generic pattern families. The deny-list MUST cover at least: instruction override, forged system framing, slash commands, requests to show prompt or memory, debug or troubleshooting framing used to extract internals, role hijack, forget-override, and forged markup tags. The deny-list MUST NOT be a copy of the Jose evaluation battery prompts. Matching SHALL be case-insensitive on the raw latest user string. The deny-list MUST NOT treat “disregard” phrasing as its own family.

#### Scenario: Instruction override
- **WHEN** the latest user message contains an instruction-override pattern (for example “ignore previous”)
- **THEN** the input guardrail matches and blocks the turn

#### Scenario: Forged system framing
- **WHEN** the latest user message contains forged system framing (for example “IMPORTANT SYSTEM” or “SYSTEM:”)
- **THEN** the input guardrail matches and blocks the turn

#### Scenario: Slash command
- **WHEN** the latest user message contains a slash-command pattern (for example `/exit` or `/resume`)
- **THEN** the input guardrail matches and blocks the turn

#### Scenario: Show prompt or memory
- **WHEN** the latest user message asks to show the prompt or memory
- **THEN** the input guardrail matches and blocks the turn

#### Scenario: Debug framing
- **WHEN** the latest user message uses debug or troubleshooting framing to extract internals (for example “for debugging”)
- **THEN** the input guardrail matches and blocks the turn

#### Scenario: Role hijack without system framing
- **WHEN** the latest user message contains a role-hijack pattern (for example “you are now”)
- **AND** the message does not contain forged system framing such as “SYSTEM:”
- **THEN** the input guardrail matches and blocks the turn

#### Scenario: Forget-override
- **WHEN** the latest user message contains a forget-override pattern (for example “forget everything”, “forget all”, or “forget previous”)
- **THEN** the input guardrail matches and blocks the turn

#### Scenario: Forged markup
- **WHEN** the latest user message contains a forged markup tag (for example `</system>`, `<system>`, `<instructions>`, or `<prompt>`)
- **THEN** the input guardrail matches and blocks the turn

#### Scenario: Career question without deny patterns
- **WHEN** the latest user message asks only about Alberto’s professional background and matches none of the deny-list families
- **THEN** the input guardrail MUST NOT match

#### Scenario: Disregard phrasing is not a deny family
- **WHEN** the latest user message uses “disregard” phrasing and matches none of the other deny-list families
- **THEN** the input guardrail MUST NOT match
