# PrismShare Stream

**PrismShare Stream** carries live, time-sensitive packets over a sequence of
[PrismShare Code](FORMAT.md) symbols. It is a payload protocol: it rides inside
the symbol payload and changes nothing about the symbol format.

Version 1 is deliberately narrower than a general-purpose streaming layer. It
defines fixed-size, fixed-duration codec packets and an audio codec table. It
does not define arbitrary fragmentation, per-packet lengths, timestamps,
negotiation or authentication. Those require a future profile version; they are
not accidentally missing fields in version 1.

> **Document status**
>
> | field | value |
> |---|---|
> | role | normative live payload protocol with informative receiver guidance |
> | wire discriminator | `PV` (`0x50 0x56`) |
> | current profile | version 1, fixed-rate audio |
> | codecs | AMR-NB 4.75, Codec2 1300, Codec2 700C |
> | evidence | implemented, unit-tested and verified end to end through real cameras |

The frame format is proven in software against injected loss, and the audio
profile has carried live speech from a monitor to a fleet of handsets,
including contiguous playback on the weakest reader tested. Section 8 records
what the optical link measured.

---

## 1. What a stream is, and why it is not a transfer

[Aphotic](APHOTIC.md), the file-transfer protocol, delivers one exact object
eventually, taking as many laps as the losses demand. A live stream is the
opposite discipline. It wants whatever is ready **now**, on a playout clock, and
it would rather conceal a gap than wait for a retransmission that would arrive
too late to matter. A fountain peels a fixed object into completeness; a stream
is unbounded and disposable.

So PrismShare Stream does not use the Aphotic Fountain. It shares only the
symbol layer beneath it, which gives it one property worth stating plainly:

> A Prism symbol is Reed-Solomon protected and CRC-32 checked, so a decoded
> frame is byte-exact or absent up to the strength of a 32-bit check: an
> undetected corruption must survive Reed-Solomon decoding and then pass the
> CRC by chance, roughly one in four billion per damaged frame. A stream
> therefore handles **erasure** and treats corruption as negligible, which for
> disposable audio it is; that is why the frame below carries no checksum of
> its own, and also why this transport authenticates nothing.

## 2. Loss, and the redundancy window

A stream survives lost frames with plain redundancy rather than an erasure code.
Each transmitted frame carries the newest run of packets, so a packet first sent
in one frame is sent again in the next several, newest first. A receiver that
loses a whole frame recovers its packets from any later frame that still carries
them, up to the window's depth.

The one honest cost is latency. All redundancy is of **past** data, because the
future has not been produced yet, so recovering a lost packet from a later
frame's copy means the receiver must not have played it yet. The recoverable
outage is therefore bounded by two depths at once, the sender's redundancy
window and the receiver's playout buffer, and both cost delay.

Units, precisely, since an earlier draft mixed them: `W` is the window depth
in **packets**, `B` the playout buffer depth in **packets**, and `P` the
packets of fresh audio each new symbol advances, so outages are measured in
**consecutive lost symbols**:

```
recoverable outage  =  min(floor(W / P) - 1, floor(B / P))  lost symbols
playout latency     =  B                                    packets
```

Deeper recovery buys itself with latency, one for one. This is why PrismShare Stream
is a broadcast and push-to-talk medium and not a two-way call, quite apart from
the link being one-way.

The window half of that bound deserves its own statement, because its
consequence is counterintuitive. `W - P` packets of every frame are
repetition, so a receiver whose buffer is deep enough survives

```
consecutive lost symbols  =  floor(W / P) - 1
```

`W` is capped by the symbol's byte capacity, so the working lever is `P`, and a
shorter dwell lowers it. A faster symbol rate therefore makes a MORE robust
stream, not a less robust one: the display changes more often, but each frame
repeats more of what came before, so the reader is allowed to miss more of
them. The first listening tests were lost to the opposite intuition, as was an
entire preset whose window tolerated nothing.

## 3. Sequence numbers and sessions

Every packet has a 24-bit sequence number, monotonic within a session and
wrapping at 2^24. A **session** is a 16-bit identifier chosen once per stream. A
receiver seeing a new session id treats it as a new stream, from a different
source or a restart, and discards everything it held: the old buffer can never
continue it. A **codec change within one session** resets the receiver the same
way, since packets of the old and new codec cannot share a buffer.

Sequence numbers are not transmitted per packet. A frame states the sequence of
its **newest** packet in its header, and the packet at list position `i` carries
sequence `(headSequence - i) mod 2^24`. Packets are always fixed size for a
given codec, so no per-packet length is transmitted either.

## 4. Frame format

One PrismShare Stream frame is the byte payload of one symbol. All multi-byte fields
are big-endian.

| offset | size | field |
|--------|------|-------|
| 0..1   | 2 | magic, `0x50 0x56` (`"PV"`) |
| 2      | 1 | profile version, currently 1 |
| 3..4   | 2 | session identifier |
| 5      | 1 | codec identifier (high nibble) and flags (low nibble) |
| 6..8   | 3 | head sequence: the sequence of the newest packet, 24-bit |
| 9      | 1 | packet count `K` |
| 10..   |   | `K` codec packets, newest first, each of the codec's fixed size |

The packet count `K` MUST be in the range 1 to 200; the upper bound is a
defensive limit so a malformed count cannot make a reader allocate wildly. The
frame length MUST be exactly `10 + K * packetBytes`; a payload that does not
account for every byte is not a PrismShare Stream frame.

Unknowns are handled strictly: a payload naming an unknown profile version is
not a PrismShare Stream frame and MUST be rejected; a well-formed frame naming an
unknown codec identifier MUST be ignored whole. The two undefined flag bits
MUST be sent as zero and MUST be ignored on receipt, so a future revision can
assign them without breaking receivers already in the field. A reader distinguishes a
stream frame from an [Aphotic](APHOTIC.md) transfer page and a plain document by
the magic: `PV` here, `PS` for a transfer page, neither for a document.

An unknown codec's packet size is necessarily unknown, so a version 1 receiver
cannot apply the codec-dependent exact-length equation to it. For this rule,
“well-formed” means that the ten-byte header is present, the profile version is
known and `K` is in `1..200`; the receiver then ignores the complete candidate
payload without slicing its packet area.

**Flags** (low nibble of byte 5):

| bit | meaning |
|-----|---------|
| 0 | silence: this run is comfort noise, the source paused |
| 1 | talkspurt: the first frames of a resumed burst after silence |

The talkspurt flag is a hint a receiver uses to reset codec state and show that
the source is active. It rides several consecutive frames rather than one, so a
single torn frame cannot swallow it.

Flags describe the stream at the frame's **head sequence**, not at the moment
of display. A sender that emits deliberately delayed frames, such as the older
symbol of the pair in section 6, MUST clear the hint flags on them, so a stale
talkspurt cannot reset a receiver's codec state mid-word; the reference sender
sends the older symbol with a zero flag nibble.

## 5. The audio profile

The only codec identifiers defined so far carry speech. The transport never
looks inside a packet; it needs only the fixed packet size, to slice the frame,
and the frame duration, to reason about latency.

| id | codec | packet bytes | frame ms | note |
|---:|-------|-------------:|---------:|------|
| 0 | AMR narrowband, 4.75 kbit/s | 13 | 20 | the platform speech codec on every mobile handset; needs no separate build |
| 8 | Codec2 1300 | 7 | 40 | a fifth of the bytes of AMR; the verified robust default |
| 9 | Codec2 700C | 4 | 40 | maximum redundancy per byte |

The packet bytes are normative, exactly:

- **AMR** packets are the 13-byte storage-format frame of RFC 4867 section
  5.3: the table-of-contents byte first (`0x04` for mode 0, quality bit set),
  then the 95 payload bits packed into 12 bytes with the padding bits zero. A
  packet whose table-of-contents byte names any other mode is not a valid
  packet for codec identifier 0.
- **Codec2** packets are the packed bitstream `codec2_encode` emits and
  `codec2_decode` consumes, as frozen in codec2 release 1.2.0: bits packed
  most-significant-bit first into `ceil(bits/8)` bytes, 52 bits in 7 bytes
  for 1300 and 28 bits in 4 bytes for 700C. Padding bits MUST be sent as zero
  and MUST be ignored on receipt. Both bitstreams have been stable upstream
  for many years.

Codec2's low absolute rate is what makes a deep redundancy window affordable:
the window costs bytes linearly in the codec rate, and a speech codec at 700 to
1300 bit/s leaves room for seconds of redundancy inside one symbol's payload.
Measured end to end, that arithmetic is the whole story: the same 311 byte
symbol payload that carries 460 ms of AMR redundancy carries 1.7 seconds of
Codec2 1300, and section 8 shows what that difference buys.

> An audio-rate codec is not the only thing a future PrismShare Stream profile
> could carry. The
> transport is codec-agnostic; a future profile could define a different codec
> table, or a variable-rate codec, at which point a per-packet length and an
> explicit timestamp, both omitted here because a fixed-rate codec needs
> neither, would be added under a new profile version.

## 6. Twin Window: two symbols, two windows (informative)

A sender with room for two symbols side by side, which is Prism's normal pair
presentation, should not show the same frame twice, and should not show the
current frame beside the previous tick's frame either. Both were tried on real
cameras and both failed. A mirrored pair fails together: the two symbols share
every captured camera frame, so whatever tears one tears the other, and the
second symbol adds nothing. Adjacent ticks overlap by all but `P` packets, so
current-beside-previous adds only the few oldest packets to the pool.

The layout that works places the newest window in one symbol and the window
BEFORE it in the other: the frame the sender emitted one full window ago, its
head sequence `W` behind. The two windows overlap not at all, so the pair
jointly holds twice the depth. A reader that catches only the newer symbol
still has everything recent; the older symbol matters exactly when frames have
been missed, which is when depth pays. The older symbol is an ordinary, valid
frame, so a receiver needs no knowledge of the pairing and the scheme costs
nothing on the wire.

## 7. Receiver behaviour (informative)

How a receiver turns frames back into a stream is a quality-of-implementation
matter, not part of the wire format. The reference receiver:

- holds a jitter buffer a fixed number of packets deep, which is the stream's
  latency, and begins playback once a full buffer has arrived;
- plays in sequence order, on the playout clock, concealing a missing packet
  rather than waiting for it;
- never rewinds: a packet arriving behind the playhead is too late and is
  dropped, not inserted;
- for a push-to-talk burst too brief to fill the buffer, offers an explicit
  flush that begins playback immediately with whatever depth is available;
- resyncs toward the intended latency if it falls too far behind, so buffer size
  and latency stay bounded under a fast source or a catch-up burst.

Beyond those basics, four behaviours separated a receiver that measured well
from one that audibly failed, and each was learned from a failure:

- **The playout clock is the audio sink's own playback position** and nothing
  else. Every proxy tried, sleeping per packet, or letting a full sink's
  blocking write pace the loop, ran slow on some handset and fast on another,
  and either drains the buffer flat or grows it without bound.
- **The live edge is not a hole.** A receiver that has consumed everything it
  holds must wait for the next frame, not conceal; concealing there inserts
  time the stream never contained, and the inserted time compounds until the
  playout has drifted beyond its own resync. A hole BEHIND the live edge is
  real loss and is the thing to conceal.
- **The resync threshold needs slack above the buffer depth.** Frames arrive
  in bursts of `P` packets, so the buffered depth brushes its target on every
  arrival; a threshold set exactly at the target fires rhythmically and clips
  audio that was merely punctual.
- **The buffer depth is a constant of the receiver, not of the first frame.**
  A receiver that sizes its buffer from the first frame it happens to decode
  will, when it catches a stream in its opening seconds, freeze that accident
  in as its latency and its loss tolerance for the whole session.

One case deserves its own paragraph. A recorded broadcast played again arrives
with the SAME session id and its sequence rewound, because the id was chosen
when the recording was rendered. A receiver that treats every backward
sequence as the past will wedge: each replayed packet lands behind the
playhead and is dropped, forever, while the arriving frames keep the session
alive. The reference receiver treats a backward head jump too large for any
redundancy window (it uses 600 packets) as a restart and resets in place, as
if the session were new. Small backward jumps are normal and must not reset:
the older symbol of a pair and ordinary frame reordering both produce them.

## 8. What the optical link measured (informative)

One rig, one fleet, one afternoon; recorded so the next implementer knows what
to expect, not as a promise. The rig was a 1080p monitor showing the pair with
the phones on a stand: the strongest reader a recent flagship, the weakest a
budget handset that manages roughly two full-resolution decode attempts a
second.

- **AMR 4.75 in a version 8 symbol**, 23 packet window, 120 ms dwell,
  tolerance 2: the flagship played with 7 to 13 percent of packets concealed,
  audible as occasional dropouts in otherwise continuous audio.
- **Codec2 1300 in the same symbol**, 43 packet window, tolerance 13: minutes
  of playback with ZERO packets concealed on the flagship, and the weakest
  reader in the fleet, held still, streamed contiguous speech. The first
  fully clean runs the project produced.
- **A version 12 symbol was tried for depth first, and falsified.** Its window
  is deeper still, but its smaller modules cost the readers so many decode
  attempts that playback went stop-start with nothing concealed: depth works,
  and module size starves it. Depth in the easiest symbol beats capacity in a
  harder one, and the codec rate, not the symbol size, is the right place to
  buy it.
- **Two reader behaviours dominated everything else** once the transport was
  correct. The reader must attempt decodes at least as often as symbols
  change, which for a reader that also serves slower duties means streaming
  must claim the same priority as an active transfer; and continuous
  autofocus must be locked while reading is going well, because focus hunting
  tears holes of several seconds that no affordable window covers.

A note on content: a 1300 bit/s vocoder models a human vocal tract, and it
carries speech intelligibly and music as mush. For music, AMR at the shallower
window is the better trade when the link is good. The deep window is for what
the medium is for: a voice, delivered as light, surviving a shaky camera.

---

## Acknowledgements

The separation of a generic streaming layer from both the symbol format and the
audio profile follows a review of the format by **NomNomski**, who argued that
sequencing, loss handling, session identity and codec semantics are payload
concerns that must not touch the optical symbol. This document, and the
[Aphotic](APHOTIC.md) transfer protocol beside it, are that separation carried
out.

## License

This specification is licensed under the Creative Commons Attribution 4.0
International License (CC BY 4.0). SPDX-License-Identifier: CC-BY-4.0
