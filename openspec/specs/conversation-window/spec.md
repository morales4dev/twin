# conversation-window Specification

## Purpose

Bounds the prior chat that Turn B sends to the career model so context cost stays predictable. Oldest prior turns are dropped from that payload only; the visitor-facing Gradio transcript stays complete.

## Requirements

### Requirement: Turn B sends at most the newest eight prior turns
When Turn B runs, the career-completion messages SHALL be the twin system prompt, then at most the newest 8 prior turns from Gradio history, then the current user message. A prior turn is one user message and the assistant reply that follows it. If Gradio history contains 8 prior turns or fewer, Turn B SHALL send all of them. If it contains more, Turn B SHALL drop the oldest prior turns until 8 remain. The current user message MUST be appended after that window and MUST NOT be dropped as part of the cap. Dropped turns MUST be absent from the Turn B messages. The system MUST NOT replace them with a summary, verbatim anchors, or extracted metadata.

#### Scenario: History at or under the cap
- **WHEN** Turn B runs
- **AND** Gradio history contains 8 prior turns or fewer
- **THEN** the Turn B messages include every prior turn from that history
- **AND** the current user message is present after those turns

#### Scenario: History over the cap drops oldest turns
- **WHEN** Turn B runs
- **AND** Gradio history contains more than 8 prior turns
- **THEN** the Turn B messages omit the oldest prior turns
- **AND** the Turn B messages include the newest 8 prior turns
- **AND** the current user message is present after those 8 turns
- **AND** the omitted turns MUST NOT be replaced by a summary, anchors, or extracted metadata

#### Scenario: Current user message is never dropped
- **WHEN** Turn B runs with any length of Gradio history
- **THEN** the current user message is present in the Turn B messages
- **AND** it is the last user message in that payload

### Requirement: The window does not change the visible transcript
The system SHALL apply the window only when building Turn B messages. Gradio history and the visitor-facing chat transcript MUST remain complete. The system MUST NOT mutate the Gradio history list in place.

#### Scenario: Visitor still sees every prior bubble
- **WHEN** Turn B runs after more than 8 prior turns in the same Gradio session
- **THEN** the visitor-facing chat still shows every prior user and assistant bubble
- **AND** the dropped turns are absent only from the Turn B messages

#### Scenario: History list is not mutated
- **WHEN** Turn B windows Gradio history
- **THEN** the Gradio history list still contains every prior turn after Turn B returns

### Requirement: Earlier refusals follow the same window
An earlier canned refusal in the same Gradio session SHALL reach Turn B only when that refusal still sits inside the newest 8 prior turns.

#### Scenario: Recent refusal stays in the Turn B window
- **WHEN** a later turn is `IN_SCOPE`
- **AND** an earlier canned refusal is among the newest 8 prior turns
- **THEN** the Turn B messages include that refusal

#### Scenario: Old refusal is dropped from the Turn B window
- **WHEN** a later turn is `IN_SCOPE`
- **AND** an earlier canned refusal is older than the newest 8 prior turns
- **THEN** the Turn B messages MUST NOT include that refusal

### Requirement: Window applies only to Turn B prior history
Turn A MUST remain stateless. The current-turn Turn B tool loop MUST keep the same windowed prior turns used on the first Turn B call of that turn. It MUST NOT restore dropped turns or drop additional prior turns mid-loop.

#### Scenario: Turn A still has no history
- **WHEN** Turn A runs
- **THEN** the classifier request contains no Gradio history

#### Scenario: Tool loop keeps the same window
- **WHEN** Turn B makes a later tool-loop LLM call on the same turn
- **THEN** that call still includes the same windowed prior turns used on the first Turn B call
- **AND** MUST NOT include prior turns that were already dropped
