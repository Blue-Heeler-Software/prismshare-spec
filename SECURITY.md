# Security and trust boundaries

> **Document status:** normative where it states required input handling;
> otherwise security guidance. PrismShare provides transport, not trust.

## 1. No authentication

PrismShare Code CRCs detect accidental damage with a residual collision
probability; they do not authenticate a sender. Aphotic Transfer and
PrismShare Stream add no signature, message authentication code or encryption.
Anyone who can place a readable symbol in the camera's view can offer content.

Applications that require origin, integrity against an adversary or secrecy
MUST provide a signed, authenticated or encrypted object inside the payload.
The UI must not describe CRC acceptance as verification of the sender.

## 2. Untrusted files and names

An Aphotic filename is display metadata supplied by an untrusted sender. A
receiver MUST:

- remove or neutralize directory separators and traversal components;
- refuse absolute paths and device names;
- choose the destination directory itself;
- avoid overwriting an existing file without an explicit local policy; and
- retain the complete payload as unnamed data when the envelope is malformed.

Opening a received file invokes risks belonging to its file type. Automatic
execution, installation or active-document opening is outside the protocol and
SHOULD be disabled by default.

## 3. Resource exhaustion

Wire maxima are not allocation instructions. Validate lengths, counts and exact
shape before allocating or indexing. Receivers SHOULD publish and enforce
limits for:

- maximum accepted payload bytes;
- concurrent Aphotic transfers;
- retained fountain equations per transfer;
- Stream packets and jitter depth;
- filename bytes; and
- time or symbol count spent on inactive state.

A camera can repeatedly present valid but incomplete transfers. Eviction must
be deterministic and must not let a new sender inherit old state solely because
a 16-bit identifier collided.

## 4. Identifier collisions and replay

Aphotic transfer ids and Stream session ids are 16-bit correlation values, not
identities or nonces. Collisions are possible. Receivers pin all structural
fields for an active Aphotic transfer and reset Stream state on session or codec
change, but a deliberate same-shape collision remains possible.

Recorded Stream content naturally reuses its session id and sequence numbers.
Replay handling prevents a receiver wedge; it does not establish freshness.
Applications that require freshness need an authenticated timestamp or nonce in
a future profile or inside the carried content.

## 5. Privacy

The optical channel is broadcast. Bystanders and other cameras can receive any
visible symbol. A display may also reveal filenames, progress, sender identity
or media context outside the encoded payload. Encrypt sensitive content before
sending and design user interfaces with shoulder-surfing in mind.

## 6. External codecs and tools

Media decoders, QR libraries and tools such as ffmpeg process attacker-controlled
input. Implementations SHOULD use maintained versions, argument arrays rather
than shell interpolation, bounded temporary storage and least-privilege process
execution. A protocol-conformant frame is not proof that its codec payload is
safe for a particular decoder.
