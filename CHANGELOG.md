# PrismShare Protocol Suite changelog

Normative corrections are listed separately from editorial work so an
implementer can tell whether accepted bytes changed.

## Unreleased

### Editorial and conformance infrastructure

- Establish **PrismShare** as the umbrella product and project name.
- Name the suite **PrismShare Protocol Suite**, the optical format
  **PrismShare Code** with **PS Code** as its short form, the file protocol
  **Aphotic Transfer**, its rateless
  mechanism **Aphotic Fountain**, and the two-window presentation **Twin
  Window**.
- Replace the ambiguous document-family introduction with an explicit layer
  table and payload-dispatch table.
- Add naming, glossary, versioning, conformance, validation, security and worked
  example companions.
- Seed machine-readable Aphotic and Stream vectors and document the remaining
  full-symbol vector work.
- Remove the unnamed `margin = 6` geometry from the conformance surface while
  retaining it as an explicitly experimental reader compatibility case.

### Normative wire changes

- None. Names and companion documents do not change any wire byte.

### Normative clarifications

- Define the structural checks possible before ignoring a Stream frame whose
  codec id is unknown and therefore has no known packet size.

## 2026-08-08

### Normative corrections

- Require exact Aphotic page-count consistency.
- Require old Twin Window frames to clear Stream hint flags.
- Record strict unknown version/codec handling and Codec2 padding rules.

### Evidence

- Record PrismShare Stream results through real cameras and the measured link
  behaviours that define the reference receiver.

## 2026-08-06

- Publish Aphotic Transfer and PrismShare Stream as payload protocols separate
  from the optical format.
- Credit the independent review that drove the separation.

## 2026-08-06 (initial publication)

- Publish the initial optical format and informative reference decoder.
