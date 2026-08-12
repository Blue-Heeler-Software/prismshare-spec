# Aphotic Transfer

**Aphotic Transfer** is PrismShare's exact-file payload protocol. Shortened to
**Aphotic** after first use, it carries a file across a sequence of
[PrismShare Code](FORMAT.md) symbols. A
sender displays a file as an endless loop of symbols and a reader recovers it by
watching; the link is one way, and Aphotic is what makes a one-way, lossy,
camera-to-screen channel deliver an exact file anyway.

It is a payload protocol: every page rides inside a Prism symbol's payload and
Aphotic changes nothing about the symbol format.

> **Document status**
>
> | field | value |
> |---|---|
> | role | normative exact-object payload protocol |
> | wire discriminator | `PS` (`0x50 0x53`) |
> | current revision | Aphotic Transfer version 1, identified by its fixed header and allocations |
> | repair modes | none, fixed parity, and Aphotic Fountain (`0xFF`) |
> | evidence | implemented and proven through real cameras at one bit per channel |

The wire format below is what the reference sender emits and the reference
reader accepts.

---

## 1. What Aphotic Transfer is, and what it relies on

A file is split into fixed-size **chunks**. Each chunk, wrapped in a 13-byte
**page header**, is one **page**, and one page is the payload of one symbol. The
sender shows the pages in a loop; the reader collects them in whatever order the
camera happens to catch, fills each chunk into its place, and has the file once
every chunk is in hand.

Aphotic delivers one exact object, eventually, taking as many laps as the losses
demand. That is the opposite of [PrismShare Stream](STREAM.md), which delivers
a live stream in real time and conceals what it cannot recover in time. A reader tells
the two apart, and both apart from a plain document, by the first two payload
bytes: `PS` for an Aphotic page, `PV` for a stream frame, neither for a document.

**Aphotic adds no integrity check of its own.** No CRC, no checksum, not in the
header, not over a page body, not over the assembled file. It relies entirely on
the symbol layer beneath it:

> A Prism symbol is Reed-Solomon protected and CRC-32 checked, so a damaged
> page is either repaired exactly or, overwhelmingly, rejected: delivering a
> corrupt page requires damage that both survives Reed-Solomon decoding and
> then passes a 32-bit check by chance, roughly one in four billion per damaged
> symbol. Aphotic is built on that near-guarantee and would be unsafe without
> it. The residual risk is stated because a specification should not print
> "never", and CRC-32 authenticates nothing: an application that needs
> certainty about the assembled file, or integrity against an adversary rather
> than against noise, MUST carry its own digest or signature inside the
> payload. Several of the rules below note failures that "nothing downstream
> would catch, because the assembled file carries no checksum": those are
> consequences of this choice, and an implementation MUST honour the bounds
> that prevent them.

## 2. The page header

Every page begins with a fixed 13-byte header. All multi-byte fields are
**big-endian**. The same layout is used by every page, whether a data page, a
parity page or a coded page.

| offset | size | field |
|--------|------|-------|
| 0..1   | 2 | magic, `0x50 0x53` (`"PS"`) |
| 2..3   | 2 | transfer id |
| 4..5   | 2 | page index |
| 6..7   | 2 | data page count |
| 8      | 1 | repair mode (see below) |
| 9..12  | 4 | total file length in bytes |

The chunk body follows at offset 13, so every page is exactly `13 + chunkSize`
bytes and every symbol of the loop is the same shape.

- **transfer id** identifies the file being sent, so a reader can tell a
  restarted or different transfer from the one it is assembling.
- **page index** is 0 to `dataPages - 1` for data pages, and `dataPages` and
  above for repair pages, in the same 16-bit field.
- **data page count** is the number of *data* pages only, not the total. A
  reader derives the total when it needs it.
- **total length** is the byte count of the **transfer payload**: the file with
  its optional name envelope (section 7) already prepended. The envelope is
  applied BEFORE chunking, so this field counts it; a reader reassembles exactly
  this many bytes, trimming the final chunk's zero padding, and only then opens
  the envelope. A field that counted the bare file would make reassembly cut
  the file short by the envelope's length. The field is 32 bits wide but
  carried as a signed value, so the payload is at least 1 byte and at most
  `0x7FFFFFFF` bytes, about 2 GiB. A sender MUST NOT set the high bit; a reader
  MUST reject a length that is zero or negative.
- **repair mode**, byte 8, selects how lost pages are recovered:

| value | meaning |
|------:|---------|
| 0 | no repair pages; data pages only |
| 1..254 | fixed parity: one XOR parity page per this many data pages |
| 255 (`0xFF`) | rateless: repair pages are a fountain (section 5) |

The chunk size is not transmitted. A reader learns it as `pageSize - 13` from
any page. All pages of one transfer MUST carry identical header fields apart
from the page index, and a reader MUST reject a page whose chunk size, data
page count, repair mode or total length disagrees with the transfer already in
progress: such a page is a corrupt read that survived its checks, or two
senders colliding on an id, and mixing it in would poison a reassembly that
carries no checksum of its own. A reader MUST also reject a page whose fields
are internally inconsistent: `dataPages` MUST equal
`ceil(totalLength / chunkSize)` exactly. A count too small truncates the file;
a count too large drives the repair arithmetic and the completion test with
pages that can never arrive, so the transfer wedges. Either way the header is
lying about its own shape, and no later page can repair a transfer built on
it.

`chunkSize` MUST be at least 32 bytes.

## 3. Chunking and the systematic pass

```
payload   = envelope || file          when a name rides along (section 7)
          = file                      otherwise
dataPages = ceil(len(payload) / chunkSize)        len(payload) >= 1
chunk[i]  = payload bytes [i*chunkSize, (i+1)*chunkSize), the last zero-padded to chunkSize
```

An empty payload is out of scope; a transfer carries at least one byte and
therefore at least one data page.

The **systematic pass** is the file sent once in order: for `i` in
`0 .. dataPages-1`, a page with index `i` whose body is `chunk[i]` verbatim. Both
repair schemes begin with an identical systematic pass; they differ only in the
pages that follow.

## 4. Fixed parity

The simplest repair scheme, marked by a repair-mode byte of 1 to 254. After the
data pages, one XOR **parity page** is emitted per group of `groupSize`
consecutive data pages:

```
parityPages = ceil(dataPages / groupSize)
parity page g has index dataPages + g
its body = chunk[g*groupSize] XOR chunk[g*groupSize + 1] XOR ... (up to groupSize members, clipped at dataPages)
```

A reader recovers **exactly one** lost page per group by XORing the parity page
with the group's surviving members. Two losses in a group are not recoverable by
parity and wait for another lap. The default group size is 8.

A fixed-parity sender's repair-mode byte MUST be in the range 0 to 254. The value
255 is reserved for the fountain and MUST NOT be emitted by the fixed scheme; a
fixed-parity page stamped 255 would be misread as a coded page and corrupt the
transfer, which nothing downstream would catch.

`dataPages + parityPages` MUST NOT exceed `0xFFFF`.

> If it did, a parity index would wrap into the data-index range, a reader would
> file parity bytes as file content, and nothing would catch it, because the
> assembled file has no checksum. The bound is normative for exactly that
> reason.

## 5. Aphotic Fountain rateless repair

Marked by a repair-mode byte of `0xFF`, which the fixed scheme can never emit, so
the byte disambiguates the two on the receive side.

After the systematic pass, the sender emits **coded pages** without end. A coded
page's body is the XOR of a pseudo-random subset of the source chunks, and the
subset is derived from nothing but the transfer id and the page index, so a
reader reconstructs which chunks a coded page combined from the header alone. A
reader that missed pages of the systematic pass no longer waits for those
specific pages: nearly any coded page resolves one of them, directly or by
cascading through pages buffered earlier, and no page is ever "the one we are
waiting for".

Coded page indices occupy the 16-bit index space **above** the data pages:

```
codedIndex(ordinal) = dataPages + (ordinal mod (65536 - dataPages))       ordinal = 0, 1, 2, ...
```

and `dataPages` MUST NOT exceed 60000, leaving room for coded indices below the
16-bit ceiling.

### 5.1 The rule against floating point

The subset of chunks a coded page combines is **wire-visible**: sender and reader
each derive it independently and MUST agree bit for bit, or a coded page XORs the
wrong chunks together and the file corrupts silently, because Aphotic carries no
end-to-end checksum.

Therefore **no floating-point arithmetic may touch this derivation.** The degree
distribution below is produced by integer arithmetic alone. A robust-soliton
distribution built from `ln` and `sqrt` in floating point is exactly the kind of
thing two platforms are permitted to disagree about by one unit in the last
place: `Math.log` differs between C library builds and is implementation-defined
in JavaScript, and one ulp at a distribution boundary is a different degree, a
different subset, and a corrupt file.

### 5.2 The pseudo-random generator

All state is a 32-bit integer in two's-complement, with silent wraparound on
overflow. Two multipliers are used, the golden ratio and a second widely-used
mixing constant:

```
mix(id, index):
    seed = (id + 1) * 0x9E3779B9   XOR   index * 0x85EBCA77      # 32-bit multiply, wrapping
    if seed == 0: seed = 1                                       # avoid the xorshift dead state
    return seed

next(x):                                                         # xorshift32
    x = x XOR (x << 13)
    x = x XOR (x >>> 17)                                         # LOGICAL right shift
    x = x XOR (x << 5)
    return x                                                     # 32-bit
```

> **Implementer note.** These multiplies and shifts must be done in true 32-bit
> arithmetic. In JavaScript use `Math.imul(a, b)` for the multiplies and `>>>`
> for the middle shift of `next`, and treat every state as `x >>> 0` when an
> unsigned value is needed; a plain `*` on JavaScript numbers, or an arithmetic
> right shift, silently produces a different sequence and a corrupt file. The
> middle shift of `next` is unsigned; the two others are left shifts masked to
> 32 bits.

### 5.3 The degree, in integers only

For a coded page, let `draw` be `next(mix(id, index))`, treated as its unsigned
32-bit bit pattern:

```
branch = draw >>> 26                                # top 6 bits, 0..63

degree =
    1                                               if branch == 0            # seed the cascade
    min(dataPages, 2 * isqrt(dataPages) + 1)        if branch == 1 or 2       # the closing spike
    min(dataPages, ceil(2^20 / u))                  otherwise, where
                                                    u = ((draw >>> 6) AND 0xFFFFF) + 1

isqrt(n): the largest s with s*s <= n, by loop, never a library sqrt
```

> The body of the distribution is the ideal soliton, produced exactly by a
> classic identity: for `u` uniform on `1..M`, `ceil(M / u)` is distributed as
> `P(d) = 1 / (d(d-1))`, which is the soliton's whole body, in one integer
> division. Here `M = 2^20`. The degree-one seed and the spike at
> `2*isqrt(dataPages)+1` are the robust distribution's two additions, taken as
> fixed-probability branches on the top bits of the same draw.

### 5.4 The neighbour set

```
neighbors(id, index, dataPages):
    state = next(mix(id, index))
    degree = degreeFor(state, dataPages)
    picked = ordered set, empty
    while picked has fewer than degree entries:
        state = next(state)
        picked.add( (unsigned32(state)) mod dataPages )      # unsigned modulo
    return picked
```

The reduction to a chunk index MUST be unsigned: zero-extend the 32-bit state to
unsigned before the modulo (`state.toLong() and 0xFFFFFFFF` in Kotlin,
`(state >>> 0)` in JavaScript). A signed modulo yields negative or wrong indices.
`picked` is an insertion-ordered set of distinct indices in `[0, dataPages)`.

A coded page's body is the XOR of `chunk[n]` over every `n` in the neighbour set.
The systematic page for `index < dataPages` is simply `chunk[index]`; the general
rule `body = XOR of neighbours` reduces to that because a systematic page's
"neighbour set" is the single chunk it carries.

## 6. Reassembly (informative)

How a reader turns pages back into a file is an implementation matter; any reader
that recovers the exact file conforms. The reference reader:

- keys chunks by page index in a map, so pages fill their slots in any order and
  duplicates are ignored;
- for fixed parity, reconstructs a group's one missing member from the parity
  page once every other member is in hand;
- for the fountain, XORs known chunks out of each coded page; a coded page then
  reduced to a single unknown **is** that chunk, and resolving it can cascade
  through other buffered coded pages, so one lucky page can resolve many;
- bounds the buffer of not-yet-reduced coded pages (the reference cap is 512),
  dropping the oldest on overflow, since the stream never stops making new ones;
- assembles up to a few transfers at once (the reference holds 4), keyed by
  transfer id, evicting the least recently fed when full.

**A transfer is complete exactly when the number of held data chunks equals the
data page count.** Parity and coded pages are a means to that end and are not
counted. The assembled file is the data chunks in index order, the final chunk
trimmed to the total length field.

## 7. The envelope: carrying a file name

A file name rides **once**, in front of the file, inside chunk 0, so a reader
can show it the moment that chunk arrives rather than at the end. It is optional
and backward compatible: a payload that does not begin with the envelope magic is
simply a file with no name.

The envelope is prepended **before** chunking. It is part of the transfer
payload: the header's total length field counts it, `dataPages` is computed
over it, and reassembly reproduces it, after which opening the envelope yields
the name and the file.

```
envelope = "PRNM" (0x50 0x52 0x4E 0x4D)  ||  nameLength (1 byte)  ||  name (UTF-8)  ||  file bytes
```

The name is at most 200 bytes of UTF-8; a longer name is truncated, not refused.
The length byte is unsigned (0..255) and MUST be read as such.

A reader treats the payload as **nameless**, returning the whole payload as the
file, unless all of these hold: the payload is at least 5 bytes; the four magic
bytes match; the name length is non-zero; the envelope end (`5 + nameLength`)
does not run past the payload; and the name contains no control character and no
`/` or `\`.

> The size-agreement check is the deliberate defence against a compressed file
> whose first four bytes happen to spell `PRNM`: the magic alone is not enough,
> and the declared name length must also be consistent with the payload before a
> name is believed.

## 8. Constants

| constant | value |
|---|---|
| page header size | 13 bytes |
| page magic | `PS` (`0x50 0x53`) |
| minimum chunk size | 32 bytes |
| default parity group | 8 |
| rateless repair-mode byte | `0xFF` |
| maximum data pages (rateless) | 60000 |
| page index ceiling (data + parity) | 65535 |
| maximum transfer payload | `0x7FFFFFFF` bytes (~2 GiB), envelope included |
| envelope magic | `PRNM` (`0x50 0x52 0x4E 0x4D`) |
| maximum file name | 200 bytes UTF-8 |

---

## Acknowledgements

That sequencing, loss handling and file identity are payload concerns that must
live outside the optical symbol format, in a document of their own, was argued in
a format review by **NomNomski**. This specification, and the
[PrismShare Stream](STREAM.md) protocol beside it, are that argument carried out.

## License

This specification is licensed under the Creative Commons Attribution 4.0
International License (CC BY 4.0). SPDX-License-Identifier: CC-BY-4.0
