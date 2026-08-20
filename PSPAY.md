# PS Pay: a payment handshake over light

Status: experimental draft, wire version 1. Implemented and field-tested on
mock rails only. Nothing in this document settles real value, and the wire
format may still change while the status line says draft.

PS Pay is a three-message handshake between a merchant and a customer whose
phones face each other. Each message is one static PS Code shown on one
screen and read by the other phone's camera. The channel needs no network,
no server and no radio on either side, and both parties finish holding a
complete signed record of the sale.

PS Pay is not a settlement system. It carries an opaque payment payload for
whatever rail eventually settles (a signed chain transaction, an ecash
token, a mock byte string in the laboratory). What PS Pay itself promises is
narrower and checkable: every message is signed, every message binds the one
before it by hash, the displayed amount is taken from the signed bytes, and
any byte changed anywhere breaks the chain loudly.

## Why the channel shape matters

Deployed QR payments share two structural faults. The channel is one-way,
so the two parties at the till never exchange anything cryptographic with
each other; and nothing binds what a person sees to what gets signed. The
documented consequences range from industrial-scale sticker-overlay fraud
to wallet parsers that turned 1.5 units into 1.5 million by mishandling a
decimal string.

Two phones facing each other are a full-duplex optical channel.
Machine-verifiable messages and a human-readable display travel together on
the same screen, which is what makes the display-to-signature binding
possible at all.

## Payload dispatch

Under the suite's payload dispatch, a PS Pay message begins `PY`
(`0x50 0x59`). A reader that does not implement PS Pay treats such a payload
as a plain document.

## Wire encoding

All integers are big-endian. Four primitives:

| primitive | encoding |
|---|---|
| `u8` | one byte |
| `i32` | four bytes, two's complement |
| `i64` | eight bytes, two's complement |
| `bytes` | `i32` length, then that many bytes |
| `string` | `bytes` holding UTF-8 |

Every message is:

    0x50 0x59            magic "PY"
    u8   version         1
    u8   type            1 invoice, 2 authorisation, 3 receipt
    ...fields            fixed order per type, defined below
    bytes signature      Ed25519 over every byte before this field

The signed span (the "body") runs from the first magic byte to the end of
the last field, inclusive. The signer's public key is itself one of the
fields, encoded as an X.509 `SubjectPublicKeyInfo` (44 bytes for Ed25519);
the signature is the raw 64-byte Ed25519 form inside a `bytes` field.

There is exactly one encoding of a message. No optional fields, no
reordering, no compression. Hashing the bytes is therefore hashing the
meaning:

    hash(message) = SHA-256(body || signature)

A message that fails any check below is invalid. Readers MUST treat
unreadable and unauthentic identically: the message does not exist. No
partial results, no best effort.

## The three messages

### Invoice (type 1), merchant to customer

| field | primitive | meaning |
|---|---|---|
| amount | `i64` | total owed, integer minor units, MUST be positive |
| asset | `string` | asset label (mock rails use `MOCK`) |
| note | `string` | free-text order note, MAY be empty |
| item count | `i32` | number of line items, 0 for an unitemised invoice |
| items | repeated | per item: description `string`, quantity `i64`, unit price `i64` |
| nonce | `bytes` | at least 16 random bytes, fresh per invoice |
| issued at | `i64` | milliseconds since the Unix epoch |
| merchant key | `bytes` | the merchant's public key; the signature MUST verify against it |

Arithmetic rules, each closing a documented failure class:

- Amounts are integer minor units. The wire format has no decimal point
  anywhere, so the string-parsing bug class cannot be expressed.
- Every quantity MUST be positive and every unit price non-negative.
- When items are present, the total MUST equal the sum over items of
  quantity times unit price, computed without overflow. A correctly signed
  invoice whose total disagrees with its own lines is invalid. A lie does
  not become true by being signed.

### Authorisation (type 2), customer to merchant

| field | primitive | meaning |
|---|---|---|
| invoice hash | `bytes` | `hash(invoice)` of the exact invoice being paid |
| payment payload | `bytes` | rail-specific, opaque to PS Pay |
| customer key | `bytes` | the customer's public key; the signature MUST verify against it |

An authorisation answers exactly one invoice. Same amount, same merchant,
different nonce is a different hash and MUST NOT be honoured.

### Receipt (type 3), merchant to customer

| field | primitive | meaning |
|---|---|---|
| authorisation hash | `bytes` | `hash(authorisation)` being answered |
| settled | `u8` | 1 if the merchant considers the sale settled, else 0 |
| nonce | `bytes` | the invoice nonce, echoed |
| merchant key | `bytes` | MUST equal the invoice's merchant key |

After a receipt both parties hold the whole signed story: what was asked,
what was authorised, and what the merchant claims happened.

## What a reader owes the person paying

- Display the amount, and the line items when present, from the signed
  bytes, before asking for authorisation. Never display one number and sign
  another.
- Pin merchant keys on first sight (trust-on-first-use, as SSH does). When
  a previously seen merchant signs with a different key, refuse loudly and
  make paying anyway hard. This is the sticker-swap defence: the overlaid
  code still scans perfectly, and the changed key is the only tell.
- Carry each message as one static symbol, never a stream. The encoding
  guidance for PS Cards applies: 3 bits per module at error correction
  level H. Measured on the reference implementation, a three-line order is
  a version 9 symbol and a twenty-line order is version 19, so a full till
  docket fits one glance.
- Refuse on any failure with a human explanation, and treat "authorised but
  no receipt captured" as its own honest state, distinct from settled.
- Never settle silently. Authorising is a human act on the customer's
  device, taken while the signed amount is on screen.

## Physical protocol (informative)

The handshake is turn-taking, so no simultaneous display is required:
invoice shown by the merchant and scanned by the customer, authorisation
shown by the customer and scanned by the merchant, receipt shown by the
merchant and scanned by the customer.

Field-tested with both phones screen-to-screen using front cameras, one
continuous hold after the customer confirms: front cameras sit in the top
bezel, so two aligned portrait phones point their cameras at each other's
bezels. Crossing the phones like a T puts each camera over the middle of
the other screen. Since neither screen is visible in that posture, progress
is signalled by vibration and tone: one buzz per message landed, a double
buzz for settled, and screens SHOULD hold maximum brightness while facing.

## Security considerations

What version 1 defends, by construction: amount and item tampering
(signature), invoice substitution (hash binding), decimal misparsing
(integer-only wire), merchant impersonation against a returning customer
(key pinning), and display-versus-signature divergence (both screens render
from signed bytes).

Honest limits, stated before anyone falls for a demo:

- **Settlement is the rail's problem.** A deferred-broadcast transaction
  can be double-spent before it lands; an ecash rail settles offline; a
  mock rail settles nothing. The receipt's `settled` flag is the merchant's
  claim, not an oracle.
- **First contact is unauthenticated.** Trust-on-first-use protects
  returning customers only. Out-of-band pinning (a printed PS Card carrying
  the merchant key) hardens first contact.
- **No privacy claims.** Both public keys travel in clear inside the
  symbols, and anyone who can film both screens can read the whole
  handshake except nothing in it authorises a replay.

## Open questions before this leaves draft

- A merchant display-name field, so pinning can be per merchant name rather
  than one pin per reader, and so the confirm screen can name who is being
  paid.
- At least one defined payment payload profile on a real rail, including
  its settlement and double-spend story.
- Whether `asset` needs a registry or stays a free label.
