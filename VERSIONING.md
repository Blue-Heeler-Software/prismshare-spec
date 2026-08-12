# Versioning and extension policy

> **Document status:** normative where it states receiver behaviour; otherwise
> editorial guidance for future revisions.

## 1. Independent layers

PrismShare Code, Aphotic Transfer and PrismShare Stream are independently
versioned protocol layers. A revision to one MUST NOT silently reinterpret
bytes owned by another.

- PrismShare Code carries its format version in the symbol header.
- Aphotic version 1 has no separate version byte. Its magic, repair-mode values
  and exact header shape define the current protocol. An incompatible Aphotic
  revision therefore requires a new magic or an explicitly allocated extension
  mechanism; it MUST NOT reinterpret an existing repair-mode value.
- PrismShare Stream carries a profile version at frame offset 2. An incompatible
  frame or packet-table change MUST allocate a new profile version.

## 2. Unknown and reserved values

| location | sender rule | receiver rule |
|---|---|---|
| unknown PrismShare Code format version | MUST NOT emit without a published specification | MUST reject as PrismShare Code |
| unrecognised Aphotic magic | MUST NOT emit as Aphotic | treat as not Aphotic |
| unallocated Aphotic repair mode | none remain in v1 | requires a future incompatible extension; do not guess |
| unknown Stream profile version | MUST NOT emit without a published profile | MUST reject as Stream |
| unknown Stream codec id in a known profile | MUST NOT emit without allocation | MUST ignore the whole frame |
| undefined Stream flag bits | MUST send zero | MUST ignore |
| reserved optical header bits | MUST send zero unless their defining revision says otherwise | follow `FORMAT.md` for the detected version |

## 3. Compatibility promises

An editorial revision changes no accepted byte sequence. A normative correction
may narrow or clarify acceptance where the existing prose was contradictory or
unsafe; it must be recorded in `CHANGELOG.md` and accompanied by vectors. A new
wire feature must state:

1. the allocating version or discriminator;
2. old-reader behaviour;
3. new-reader behaviour for old values;
4. resource bounds;
5. security consequences; and
6. positive and negative conformance vectors.

## 4. Stability labels

| label | meaning |
|---|---|
| **proven** | Successfully exercised through a real camera link in the stated operating envelope. |
| **implemented** | Present in the reference implementation and covered by software tests. |
| **defined** | Normatively specified but not proven through a camera. |
| **experimental** | May change or be removed; not a stable conformance target. |
| **falsified** | Implemented and tested, but failed the stated physical objective. |
