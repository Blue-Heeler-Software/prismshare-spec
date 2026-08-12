# PrismShare conformance

> **Document status:** normative conformance policy. It does not add wire
> fields or alter the protocol documents.

Conformance is claimed per component and configuration. “PrismShare compatible”
without a component, version and tested configuration is not a complete claim.

## 1. Claimable components

| component | normative authority | minimum claim |
|---|---|---|
| PrismShare Code encoder | `FORMAT.md` | format version, loading/profile, QR version range, correction levels and layouts emitted |
| PrismShare Code decoder | `FORMAT.md` | format versions, loading profiles, QR version range and layouts accepted |
| Aphotic sender | `APHOTIC.md` | fixed repair modes and/or Aphotic Fountain mode supported, plus maximum payload and page count |
| Aphotic receiver | `APHOTIC.md` | accepted repair modes, resource limits and envelope handling |
| Stream sender | `STREAM.md` | profile version, codec ids, maximum packet count and flag behaviour |
| Stream receiver | `STREAM.md` | profile version, codec ids and invalid-frame dispositions |

An implementation MAY claim any subset. It MUST NOT imply support for a layer or
configuration it has not tested.

## 2. Conformance classes

### Optical Core

A conforming optical encoder emits the bytes, planes, geometry, calibration and
intensities required by `FORMAT.md`. A conforming optical decoder recovers the
normative payload from every positive vector in its claimed configuration and
rejects every corresponding negative vector.

### Aphotic Transfer

A conforming sender emits internally consistent headers, an exact systematic
pass and repair pages for its claimed modes. A conforming receiver reconstructs
the exact transfer payload from positive vectors and rejects malformed or
shape-changing pages as required by `VALIDATION.md`.

### PrismShare Stream

A conforming sender emits complete version 1 frames with one to 200 valid codec
packets. A conforming receiver accepts supported frames, ignores unsupported
codec frames, rejects malformed frames and applies wrap/session rules without
mixing incompatible state.

## 3. Proof levels

Conformance and physical usefulness are separate statements:

| proof level | evidence |
|---|---|
| wire-conformant | Passes every applicable canonical positive and negative vector. |
| software-interoperable | Exchanges data with an independent implementation without sharing encoder internals. |
| camera-proven | Passes through a stated physical camera/display rig. |
| channel-proven | Survives a stated channel such as a video transcode, with the full configuration and result recorded. |

“Camera-proven” MUST identify the format configuration and device class. It MUST
NOT be generalized to untested bit depths, versions, layouts or codecs.

## 4. Present matrix

| component | wire implementation | independent implementation | camera evidence | canonical vectors |
|---|---:|---:|---:|---:|
| Code v2, one bit/channel | yes | partial JavaScript encoder | yes | pending full symbol set |
| Code v2, two or three bits/channel | yes | partial | no | pending |
| Code v3 profile 1 | yes | no | falsified | pending |
| Aphotic fixed parity | yes | yes | yes | scaffolded |
| Aphotic Fountain | yes | yes | yes | seeded |
| Stream v1 AMR | yes | no | yes | seeded |
| Stream v1 Codec2 1300 | yes | no | yes | seeded |
| Stream v1 Codec2 700C | yes | no | limited | seeded |

This table describes current evidence, not permanent protocol capability.

## 5. Vector rule

Files under `vectors/` are canonical only when their manifest entry has
`"status": "canonical"`. A scaffold or draft vector MUST NOT support a
conformance claim. Every canonical entry requires an origin description,
expected disposition and SHA-256 digest in `vectors/manifest.json`.
