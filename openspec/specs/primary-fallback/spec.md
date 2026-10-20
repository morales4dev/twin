# primary-fallback Specification

## Purpose

Gives every classify and complete call a configured primary model and a fallback model so a raised primary call can still return a normal result instead of failing the turn.

## Requirements

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

### Requirement: Blank LLM settings use the configured defaults
When the process reads LLM settings, a missing or blank `PRIMARY_MODEL`, `FALLBACK_MODEL`, `LLM_TIMEOUT`, or `LLM_RETRIES` SHALL use the same defaults this spec already names (`MiniMax-M2.5`, `claude-haiku-4-5-20251001`, 30 seconds, 2 retries). A blank value MUST be treated as unset, not as a parse error. Missing or blank API keys and `OPENAI_BASE_URL` MUST remain allowed so the process can still boot.

#### Scenario: Blank timeout uses the default
- **WHEN** `LLM_TIMEOUT` is missing or blank
- **AND** an LLM call reads settings
- **THEN** that call uses a 30-second deadline

#### Scenario: Blank retries use the default
- **WHEN** `LLM_RETRIES` is missing or blank
- **AND** an LLM call reads settings
- **THEN** that call uses 2 same-model retries

#### Scenario: Blank model names use the defaults
- **WHEN** `PRIMARY_MODEL` and `FALLBACK_MODEL` are missing or blank
- **AND** an LLM call reads settings
- **THEN** primary is `MiniMax-M2.5` and fallback is `claude-haiku-4-5-20251001`

#### Scenario: Blank API keys still boot
- **WHEN** `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_BASE_URL` is missing or blank
- **AND** the process reads LLM settings
- **THEN** that read MUST NOT fail because those keys are blank

### Requirement: Invalid LLM settings fail with a field-level error
When an LLM settings value is present and cannot parse as its field type, the settings read SHALL fail before any provider call. The error MUST name the invalid field. This failure is not a primary-then-fallback transport error and MUST NOT start a provider call.

#### Scenario: Non-integer timeout fails before the provider call
- **WHEN** `LLM_TIMEOUT` is set to a non-integer value
- **AND** an LLM call reads settings
- **THEN** the settings read fails with an error that names `LLM_TIMEOUT`
- **AND** the system MUST NOT call the primary or fallback provider for that read
