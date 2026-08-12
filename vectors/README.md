# PrismShare conformance vectors

Vectors are versioned separately from prose. `manifest.json` lists every vector
file, its SHA-256 digest, status and governing specification.

## Status meanings

- `canonical`: required for the applicable conformance claim.
- `draft`: under review and not yet a conformance requirement.
- `scaffold`: reserves the shape of a future vector set but contains no proof.

The current seed covers deterministic Aphotic Fountain values and PrismShare
Stream frame parsing. Full rendered-symbol vectors remain pending and are
represented by `symbol-vectors-v1.json` as a scaffold rather than being implied
to exist.

## Rules

1. Hex strings contain lowercase hexadecimal with no separators.
2. Integers are decimal unless the field name ends in `Hex`.
3. Every negative vector states one expected disposition: `reject`, `ignore`,
   or `not-this-protocol`.
4. A canonical file changes only with an explicit changelog entry.
5. Regeneration must be checked by an implementation independent of the
   generator before publication.

## Remaining optical set

The first full symbol vector release should include:

- format v2 at one, two and three bits per channel;
- every accepted surround layout and a rejected unknown layout;
- QR versions 2, 7, 20 and 40 at representative correction levels;
- exact plane bytes, matrix modules, rendered pixels and payload hashes;
- mirrored captures and damaged/negative symbols; and
- format v3 profile/header cases clearly labelled defined or experimental.

