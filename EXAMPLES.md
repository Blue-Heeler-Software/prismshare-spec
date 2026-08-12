# Worked wire examples

> **Document status:** informative. Machine-readable values under `vectors/`
> are the canonical form when an example and a vector differ.

Spaces in hexadecimal listings are for readability and are not transmitted.
All multi-byte integers are big-endian.

## 1. Aphotic systematic page

This example uses transfer id `19003` (`0x4A3B`), page index `0`, 79 data
pages, Aphotic Fountain mode `0xFF`, total payload length 5000 bytes and a
64-byte chunk.

```text
50 53 | 4A 3B | 00 00 | 00 4F | FF | 00 00 13 88
  PS  |   id  | index | pages |mode|    length
```

The complete page is 77 bytes: the 13-byte header above followed by source
chunk 0. Since `ceil(5000 / 64) = 79`, the header is internally consistent.
Indices `0..78` are systematic pages; coded indices begin at 79.

## 2. Aphotic Fountain coded page

For the same transfer, coded index 79 derives neighbours `[13, 22]`. Its body
is `chunk[13] XOR chunk[22]`; the neighbour list is not transmitted.

```text
50 53 | 4A 3B | 00 4F | 00 4F | FF | 00 00 13 88
```

An independent receiver reconstructs `[13, 22]` using only transfer id, page
index and data-page count. The canonical body and further neighbour sets are in
`vectors/aphotic-fountain-v1.json`.

## 3. PrismShare Stream AMR frame

This version 1 frame uses session `0x1234`, codec id 0 (AMR-NB mode 0), no
flags, head sequence 2 and two packets. Each packet begins with the required
`0x04` TOC and contains a zero test payload.

```text
50 56 | 01 | 12 34 | 00 | 00 00 02 | 02
  PV  |ver |session|c/f |   head    | K

04 00 00 00 00 00 00 00 00 00 00 00 00
04 00 00 00 00 00 00 00 00 00 00 00 00
```

The packets carry sequences 2 and 1, newest first. The exact length is
`10 + 2 * 13 = 36` bytes.

## 4. PrismShare Stream Codec2 frame

This version 1 frame uses session `0xBEEF`, codec id 8 (Codec2 1300), the
talkspurt flag, head sequence `0x00FFFE` and one seven-byte packet.

```text
50 56 | 01 | BE EF | 82 | 00 FF FE | 01 | 12 34 56 78 9A BC D0
```

The final nibble is zero because Codec2 1300 uses 52 of the 56 carried bits.
A receiver ignores those four padding bits; a sender must transmit them as zero.

## 5. Sequence wrap

If a frame's head sequence is zero and `K = 2`, packet positions map to:

| position | sequence |
|---:|---:|
| 0 | `0x000000` |
| 1 | `0xFFFFFF` |

The subtraction is modulo `2^24`; it is not signed arithmetic.

## 6. Invalid Stream frame

```text
50 56 01 12 34 00 00 00 00 00
```

This has a valid magic and version but `K = 0`. `STREAM.md` requires
`1 <= K <= 200`, so the frame must be rejected even though its ten-byte length
matches the empty count.

Other negative examples, including an unknown profile and unknown codec, are in
`vectors/stream-v1.json` with their required dispositions.

