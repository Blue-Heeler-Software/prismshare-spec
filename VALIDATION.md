# Validation and disposition matrix

> **Document status:** normative index of rules already owned by `FORMAT.md`,
> `APHOTIC.md` and `STREAM.md`. If this index conflicts with a protocol
> document, the protocol document controls and the index must be corrected.

“Reject” means do not deliver the candidate as that protocol. “Ignore” means
the protocol was recognized but the complete unit contributes no receiver
state. Neither action permits partial bytes to enter an assembly or playout
buffer.

## 1. Payload dispatch

| condition | disposition |
|---|---|
| valid `PS` prefix | validate as Aphotic; never reinterpret a malformed Aphotic page as Stream |
| valid `PV` prefix | validate as Stream; never reinterpret a malformed Stream frame as Aphotic |
| neither prefix | deliver as a plain document if the application accepts documents |
| payload shorter than the selected protocol's header | reject as that protocol |

## 2. Aphotic Transfer

| condition | disposition |
|---|---|
| payload shorter than 13 bytes | reject |
| chunk size below 32 bytes | reject |
| total length zero, negative or high bit set | reject |
| `dataPages` is zero | reject |
| `dataPages != ceil(totalLength / chunkSize)` | reject |
| page index outside the legal range for its repair mode | reject |
| fixed parity would exceed index `0xFFFF` | sender MUST NOT emit |
| Aphotic Fountain has more than 60000 data pages | sender MUST NOT emit; receiver rejects an impossible shape |
| chunk size, page count, repair mode or total length changes for one transfer id | reject the conflicting page without poisoning retained state |
| duplicate systematic or coded page | MAY ignore; MUST NOT corrupt or duplicate output |
| malformed `PRNM` envelope | deliver the complete reassembled payload as unnamed data; never truncate it using an untrusted name length |

## 3. PrismShare Stream v1

| condition | disposition |
|---|---|
| payload shorter than 10 bytes | reject as Stream |
| unknown profile version | reject as Stream |
| unknown codec id in version 1 | ignore the complete frame |
| packet count below 1 or above 200 | reject |
| frame length differs from `10 + K * packetBytes` | reject |
| undefined flag bits received | ignore those bits; do not reject an otherwise valid frame |
| undefined flag bits sent | non-conforming sender |
| AMR codec id with TOC other than the version 1 mode-0 form | reject the complete frame |
| non-zero Codec2 padding bits | receiver ignores padding; sender is non-conforming |
| session id changes | reset buffered stream state before accepting new packets |
| codec changes inside one session | reset buffered stream state |
| backward head jump greater than the implementation's replay threshold | treat as recorded-session restart; reference threshold is 600 packets |
| older Twin Window frame carries silence or talkspurt hint | non-conforming sender; receiver uses flags only at the frame's head |

## 4. Resource discipline

Before allocation, validate every transmitted count against the relevant
protocol ceiling and the implementation's declared local ceiling. Receivers MAY
apply stricter local limits, but SHOULD surface that policy rather than describe
a resource refusal as malformed wire data.

An implementation processing multiple visible senders MUST bound concurrent
assemblies, retained coded equations, frame buffers and filenames. Eviction MUST
discard a complete transfer/session state; it MUST NOT merge partial state under
a recycled identifier.
