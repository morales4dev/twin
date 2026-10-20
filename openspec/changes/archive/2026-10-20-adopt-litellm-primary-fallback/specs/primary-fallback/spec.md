## Purpose

Gives every classify and complete call a configured primary model and a fallback model so a raised primary call can still return a normal result instead of failing the turn.

## ADDED Requirements

### Requirement: Raised calls retry the same model then try fallback
Each classify (Turn A) or complete (Turn B) LLM call SHALL start on the configured primary model. The primary model SHALL be an OpenAI-compatible model (default identifier `MiniMax-M2.5`). The fallback model SHALL be an Anthropic model (default identifier `claude-haiku-4-5-20251001`). Each attempt MUST use the configured call deadline (default 30 seconds). When an attempt raises (deadline, provider, or network error), the system MUST retry that same model up to the configured retry count (default 2) before switching models. After primary retries are exhausted, the system MUST try fallback with the same deadline and retry rule. After fallback retries are exhausted, that LLM call has failed. These retries are transport retries only. They MUST NOT re-prompt to fix labels, schema, or content.

#### Scenario: Primary succeeds on the first attempt
- **WHEN** the primary LLM call returns a response
- **THEN** the system uses that response
- **AND** MUST NOT call fallback

#### Scenario: Primary raises then fallback succeeds
- **WHEN** the primary LLM call raises after its retries
- **AND** the fallback LLM call returns a response
- **THEN** the system uses the fallback response as a normal result for that call

#### Scenario: Deadline expiry follows retry-then-fallback
- **WHEN** a primary attempt exceeds the configured call deadline
- **THEN** the system treats that attempt as a raised call
- **AND** continues same-model retries, then fallback

#### Scenario: Both models fail
- **WHEN** primary and fallback both raise after their retries
- **THEN** that LLM call has failed

### Requirement: Each LLM call is independent
Each classify or complete LLM call SHALL start at primary. A call that landed on fallback MUST NOT force a later call onto fallback. There is no sticky model for a Gradio turn or for the Turn B tool loop.

#### Scenario: Turn B starts at primary after Turn A used fallback
- **WHEN** Turn A succeeded via fallback
- **AND** Python starts Turn B
- **THEN** the first Turn B LLM call starts at primary

#### Scenario: A later Turn B tool-loop call starts at primary
- **WHEN** an earlier Turn B LLM call on the same turn succeeded via fallback
- **AND** the tool loop makes another LLM call
- **THEN** that later call starts at primary

### Requirement: Successful output does not trigger fallback
Fallback SHALL run only when the LLM call raises. A successful response with `OUT_OF_SCOPE`, an unparseable label, or a canned refusal MUST NOT trigger retries or fallback.

#### Scenario: Parsed OUT_OF_SCOPE does not try fallback
- **WHEN** the primary Turn A call returns a parseable `OUT_OF_SCOPE`
- **THEN** the system MUST NOT retry that call
- **AND** MUST NOT call fallback

#### Scenario: Unparseable label does not try fallback
- **WHEN** the primary Turn A call returns empty output, an essay, or any token other than `IN_SCOPE` or `OUT_OF_SCOPE`
- **THEN** the system MUST NOT retry that call
- **AND** MUST NOT call fallback

### Requirement: Tools are passed through per call
The LLM client SHALL pass through the tools argument of each call. It MUST NOT add tools to a call that omitted them. Turn A still omits tools. Turn B still sends tools.

#### Scenario: Turn A omits tools on primary and fallback
- **WHEN** Turn A calls primary or fallback
- **THEN** that request omits tools

#### Scenario: Turn B sends tools on primary and fallback
- **WHEN** Turn B calls primary or fallback
- **THEN** that request includes the twin tools
