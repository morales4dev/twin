## ADDED Requirements

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
