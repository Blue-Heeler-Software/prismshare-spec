# PrismShare Code format specification

PrismShare Code, shortened to **PS Code** after first use, is a colour 2D
barcode that stacks several ordinary QR Codes into
the red, green and blue channels of one symbol. Each stacked QR Code is a
complete, standard, Reed-Solomon protected symbol, so all of the error
correction work is done by a battle-tested implementation and Prism only has to
get the colour right.

> **Document status**
>
> | field | value |
> |---|---|
> | role | normative optical wire specification |
> | stable target | format version 2 |
> | proven profile | version 2, one bit per channel |
> | experimental target | format version 3; see `BIT-LOADING.md` |
> | payload protocols | Aphotic Transfer (`PS`) and PrismShare Stream (`PV`) are specified separately |

This document is the **normative** format: what bytes and colours are present in
a valid symbol. How a reader recovers them is described separately and
informatively in [DECODER.md](DECODER.md); an alternative decoder conforms if it
recovers the normative payload, however it does so internally.

---

## 0. Status, conformance and references

### What is proven, and what is merely defined

This distinction is placed first because it is the one most likely to mislead an
implementer. The format **defines** more configurations than have ever been
shown to work through a camera.

| configuration | bits per module | status |
|---|---|---|
| format version 2, `b = 1` | 3 | **Proven.** Rock solid on real handsets, and what ships. |
| format version 2, `b = 2` | 6 | Defined. Has never decoded from a camera, at any pixel density tested, including 40 px per module. |
| format version 2, `b = 3` | 9 | Defined. Has never decoded from a camera. |
| format version 3, profile 1 | 4 | Implemented and **falsified** on hardware. See [BIT-LOADING.md](BIT-LOADING.md). |
| format version 3, profiles 2..6 | 5..9 | Defined, untested through a camera. The measured result below leaves them no mechanism by which to work, but they have not themselves been put in front of one. |

Measured directly: **every channel gives out at one bit.** Profile 1, red at
two bits, decodes nothing; an ad-hoc R1 G2 B1 loading, green carrying the
second bit with the bootstrap held out of it, also decodes nothing. Two bits on
any tested channel fails, so uniform six fails three times over rather than
once on the weakest channel. Format version 3 exists because that was not
known in advance; the machinery is built, tested and inert.

The suspected root cause is not the loading but the **calibration ring itself**.
Diagnosing a phone-to-phone frame at a healthy 17 pixels per module, the fitted
black field puts black at 29 while the ring's black cells read 77, so they
correct to 0.37 instead of 0, while the whites land within 0.05 of where they
belong. A uniform glare term cannot do that, because it would lift the function
patterns the black field is fitted from by the same amount and subtract back
out. Only something that lifts one-module-wide features and not seven-module
ones can, which is bleed from the white on either side of a thin ring cell. That
bleed is a fixed fraction of a module however many pixels the module spans,
which is why more resolution has never rescued six bits. The `THICK` surround in
section 2 exists to test exactly this and its effect on hardware is not yet
established.

> An implementer should read this as: the capacity ceiling is a property of the
> current calibration path, not a proven property of colour barcodes. It may
> move. It has not moved yet.

An encoder MAY emit any defined configuration. An encoder SHOULD default to
format version 2 at `b = 1`. A conformance claim MUST state which
configurations it was tested against, and MUST NOT imply that a configuration
decodes from a camera merely because it round-trips losslessly in software.

### The measured operating envelope

A fleet test was run through a public video platform's transcode at several
playback resolutions, against a local playback control, using videos that carry
the same file at many encodings at once so each phone's first received file
names the densest configuration its whole chain supports. The numbers below are
from that test, on a 1080p source canvas; they are evidence, not requirements.

* **The proven universal operating point is a side-by-side pair of version 6
  symbols at correction H, one bit per channel, modules about 9 pixels on a
  1080p canvas** (4.5 chroma pixels per module after subsampling). Every camera
  tested received it, at every playback quality from 720p up, at both a 150 ms
  and a 100 ms page dwell. On the weakest cameras dwell was not the constraint;
  module size was.
* **Compression damage and camera damage do not add; the worse of the two
  governs.** At high playback quality the transcode was transparent, with every
  phone matching its local control exactly. At 720p only the strongest camera
  paid a density toll, because only it had been operating past what the codec
  preserves; the weaker cameras' own optics already filtered harder.
* **480p playback killed every configuration tested**, including the universal
  pair. A 1080p canvas downscaled that far leaves roughly two chroma samples
  per module on even the sparsest rung.
* **Dense configurations have no stable margin.** Version 20 at correction M in
  a pair, 2.0 chroma pixels per module, was received by the best camera in one
  orientation and not in another. A configuration that survives only in one
  orientation on the best hardware is a stunt, not an operating point.
* **Static symbols obey the same physics with the clock removed**: a version 10
  M still at 13 pixel modules read on every camera at 720p and up; 8 pixel and
  4 pixel stills read on none, though all decode losslessly from the file.
* One anomaly is recorded rather than resolved: single-symbol video parts
  failed on every phone in one test session while pairs with SMALLER modules
  passed alongside them, and the singles decode cleanly from the compressed
  file. The signal was intact, so the suspicion falls on the reference reader's
  video pipeline. Until it is isolated, the pair is the proven arrangement for
  video-embedded transfers and single-symbol video profiles should be treated
  as unverified.

Lossless software round-tripping of `b = 2`, `b = 3` and the version 3 profiles
does work, and is covered by the encoder and core decoder conformance classes in
section 8. That is a statement about the codec, not about optics.

### Normative language

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be interpreted
as described in RFC 2119. Text in blockquotes, and any passage that explains
*why* a rule exists, is explanatory and carries no requirement of its own.

### Normative references

* **ISO/IEC 18004:2015**, *Information technology - Automatic identification and
  data capture techniques - QR Code bar code symbology specification.* Every
  plane of a PS Code is a QR Code Model 2 symbol as defined there, and this
  document does not restate its content.
* **IETF RFC 2119**, key words for use in RFCs to indicate requirement levels.
* **IEC 61966-2-1**, sRGB colour space, for the rendered intensity values.

QR Code is a registered trademark of DENSO WAVE INCORPORATED. This
specification describes an independent format that embeds QR Code symbols; it is
not endorsed by or affiliated with the trademark holder. Implementers are
responsible for their own assessment of any intellectual property that applies
to QR Code encoding and decoding in their jurisdiction.

---

## 1. Bit planes

Let `V` be the QR version and `N = 4V + 17` the symbol size in modules. A Prism
Code is built from `P` bit planes. Every plane MUST be a complete standard QR
Code, and all planes of one matrix MUST share:

* the same QR version `V`,
* the same error correction level `L`,
* the same mask pattern `M`,
* exactly the same payload byte count `sliceLength`.

> Because version, EC level and mask agree across planes, every plane has
> byte-for-byte identical **function patterns**. This is the property the whole
> format rests on, and section 3 explains why it matters.

Identical across all planes, as a consequence: the three finder patterns, the
finder separators, both timing patterns, all alignment patterns, both copies of
the format information, the version information blocks for `V >= 7`, the dark
module, and any fixed light modules and remainder bits. **Only the data and
error correction codeword modules differ between planes.** The authoritative
list of which modules are function modules is ISO/IEC 18004; this document does
not maintain its own copy.

### Plane count and channel loading

Each channel carries some number of bits. Write the loading as `(bR, bG, bB)`.

```
P = bR + bG + bB          bits per module = P
```

Format version 2 can express only a **uniform** loading, where
`bR = bG = bB = b`, so `P = 3b`. Format version 3 can express one of seven
predefined loadings (section 4). A reader that supports only format version 2
therefore only ever sees uniform loadings, which is a valid constrained
conformance class.

### Plane to channel mapping

Planes run in order of significance, and within one level of significance in
red, green, blue order, skipping any channel that has already run out of bits:

```
for j in 0 .. max(bR, bG, bB) - 1:
    for c in R, G, B:
        if bits(c) > j: next plane carries channel c, significance j
```

with `j = 0` the most significant bit of that channel.

For a uniform loading this reduces exactly to `p = 3j + c`, so every symbol
produced before per-channel loading existed is produced byte for byte the same
way and reads on a version 2 reader.

**Plane 0 MUST be the most significant bit of red.** This is not a convention,
it is load bearing: a reader recovers plane 0 with a 50% threshold before it
knows the loading, reads the header out of it, and only then does the colour
work. The rule above guarantees it for every defined loading.

### Module colour

For a module at symbol coordinate `(x, y)`, and for each channel `c` carrying
`bits(c)` bits:

```
w = 0
for j in 0 .. bits(c)-1:
    w = (w << 1) | planeBit(planeOf(c, j), x, y)     # QR convention: 1 = dark
d = darknessOf(w, bits(c))                           # 0 .. 2^bits(c) - 1
intensity[c] = LEVELS[bits(c)][d]                    # 8-bit sRGB, see below
```

Darkness `d = 0` is full intensity and `d = 2^bits(c) - 1` is zero intensity,
and the intermediate levels are deliberately not evenly spaced.

### The level code

`darknessOf` is not plain binary and not a reflected Gray code. Three properties
are wanted from the mapping between a darkness level and the codeword its plane
bits spell out, and they pull against each other:

1. **Anchored endpoints.** Level 0 MUST be codeword all-zeros and the darkest
   level MUST be codeword all-ones. Only then does a module that is light in
   every plane render white and one that is dark in every plane render black,
   which is what keeps the shared function patterns neutral (section 3) and what
   gives the calibrator its illumination anchors.
2. **Threshold-recoverable top bit.** The most significant codeword bit MUST be
   exactly `d >= 2^(bits-1)`, so the most significant plane of each channel comes
   back from a plain 50% threshold with no knowledge of the loading. That is the
   header bootstrap (section 4).
3. **Single bit steps between neighbours,** so misreading a level as its
   neighbour costs one plane bit rather than several. One bit error in one
   plane's Reed-Solomon block is cheap; several is not.

> A reflected Gray code gives 2 and 3 but fails 1, because `grayEncode` of the
> largest level is never all-ones. That failure is not cosmetic: with a Gray code
> the finder patterns of a `b = 2` symbol render at 33% grey instead of black,
> and the illumination fit that assumes they are black is wrong everywhere.

**These three properties are the specification.** The tables below satisfy them
and MUST be used as written; a future editor who "tidies" them into a
conventional Gray code breaks property 1 and with it function pattern purity.

Forward, darkness `d` to codeword:

| bits | `d = 0` .. `d = 2^bits - 1` |
|-----|----------------------------|
| 1   | `0`, `1` |
| 2   | `00`, `01`, `10`, `11` |
| 3   | `000`, `001`, `011`, `010`, `110`, `100`, `101`, `111` |

Inverse, codeword to darkness, which a decoder needs and which is not derivable
by inspection at `bits = 3`:

| bits | codeword `0` .. `2^bits - 1` |
|-----|------------------------------|
| 1   | 0, 1 |
| 2   | 0, 1, 2, 3 |
| 3   | 0, 1, 3, 2, 5, 6, 4, 7 |

The first bit of each codeword is significance `j = 0`, the most significant
plane for that channel.

> All three properties hold at `bits = 1` and `bits = 3`. At `bits = 2` they
> cannot all hold: the 2-cube is bipartite and `00` and `11` share a parity, so
> no Hamiltonian path runs between them and at least one of the three steps must
> flip two bits. Plain binary is used there and achieves the minimum, four flips
> over three steps. Even that case is gentler than it looks, because the two bits
> that flip live in different planes, so it lands one error in each of two
> Reed-Solomon blocks rather than two errors in one.

### Level placement and the normative intensity tables

Module drive intensities are NOT evenly spaced. Level `d` of `2^bits - 1` sits at

```
t = (2^bits - 1 - d) / (2^bits - 1)
v = 0.5 * (1 + sign(2t - 1) * |2t - 1| ^ 1.35)      with sign(0) = 0
```

> an odd-symmetric spread toward the ends of the range, because a measured
> screen-to-camera transfer squeezes both ends and stretches the middle, and
> evenly spaced drive values arrive unevenly spaced where it matters. The odd
> symmetry keeps the extremes at exactly 0 and 1 (so shared function patterns
> stay pure black and white) and keeps "below half intensity" equal to the
> codeword's top bit (so the bootstrap threshold needs no knowledge of the
> loading).

Encoders MUST NOT be required to reproduce floating point exponentiation
identically. The formula is the design rationale; the following 8-bit tables are
normative, derived from it by `round(x) = floor(x + 0.5)`:

```
LEVELS[1] = [255, 0]
LEVELS[2] = [255, 156, 99, 0]
LEVELS[3] = [255, 208, 168, 137, 118, 87, 47, 0]
```

The same rounding rule applies to the calibration ring ramp values in section 2.

### Error correction is not diversified across planes

> Every plane shares version, EC level, mask and geometry, so codeword `n`
> occupies identical modules in every plane. Spatial damage therefore strikes the
> same codewords in all planes at once, and an implementer MUST NOT reason that
> some planes will survive damage that others did not. There is no diversity gain
> to be had across planes; the error correction level protects each plane against
> the same spatial damage, and every plane must decode for the payload to
> reassemble.

---

## 2. Symbol geometry

Prism symbols MUST use QR version 2 or greater.

> Version 1 is the only version with no alignment pattern, and without one a
> detector has to extrapolate the fourth corner of the symbol affinely from the
> three finder patterns. That is exact for a flat scan and wrong for anything
> shot at an angle, and the error is worst precisely where the calibration ring
> sits, outside the matrix. One version of extra size buys real perspective
> correction, so the floor is part of the format rather than a tuning knob.

```
+---------------------------------------------+
|  ringInset modules white                    |
|  +---------------------------------------+  |
|  |  calibration ring, ringThickness wide |  |
|  |  +---------------------------------+  |  |
|  |  |  quietZone modules white        |  |  |
|  |  |  +---------------------------+  |  |  |
|  |  |  |                           |  |  |  |
|  |  |  |    QR matrix, N modules   |  |  |  |
|  |  |  |                           |  |  |  |
|  |  |  +---------------------------+  |  |  |
|  |  +---------------------------------+  |  |
|  +---------------------------------------+  |
+---------------------------------------------+
```

### Surround layouts

A surround is described by three numbers:

```
margin          total modules between the QR matrix and the canvas edge
ringInset       white modules outside the ring
ringThickness   modules the ring band is thick, and therefore the size of one cell

quietZone = margin - ringInset - ringThickness
```

`ringInset` MUST be at least 1, `ringThickness` MUST be at least 1, and
`quietZone` MUST be at least 1. Canvas size for a single matrix is
`S = N + 2 * margin`.

Four layouts are defined for conformance:

| name | margin | ringInset | ringThickness | quiet zone | notes |
|------|-------:|----------:|--------------:|-----------:|-------|
| `COMPACT`  | 4 | 1 | 1 | 2 | tightest; halved quiet zone |
| `BALANCED` | 5 | 2 | 1 | 2 | halved quiet zone |
| `STANDARD` | 7 | 2 | 1 | 4 | default, full QR quiet zone |
| `THICK`    | 8 | 2 | 2 | 4 | two module ring cells |

`STANDARD` gives the QR specification's full 4 module quiet zone and is the
default. An encoder MUST use one of these four layouts. Some reference-reader
revisions also recognise an experimental `margin = 6` geometry, but it has no
standard name, is not a conforming encoder target, and is deliberately excluded
from decoder conformance claims until separately specified.

> The tighter layouts are real density and they are measurably not free. Halving
> the quiet zone makes a dense symbol at 6 pixels per module fail detection
> outright in the capture simulator, because the coloured ring moves close enough
> to the finder patterns for the binarizer to merge them. The simulator also
> always pads with clean white, so it says nothing at all about the other thing a
> quiet zone is for, which is keeping a busy background out of the symbol.

> At `ringThickness = 1` a cell is a single module with white on both the inward
> and outward side, so optical blur drags every reading toward white. That biases
> the black and white references the whole illumination fit is anchored on, and
> more resolution does not fix it, because the bleed is a fixed fraction of a
> module however many pixels the module spans. At thickness 2 a cell is a 2x2
> block sampled at its centre, a full module away from anything of a different
> colour in every direction; it costs one module of margin and half the cell
> count.

**The surround is not carried in the header.** A reader samples the ring at
every layout it supports and keeps whichever one explains the known ring colours
best, exactly as it does when deciding whether a capture was mirrored. Sampling
at the wrong radius lands the cells in the quiet zone or on the symbol, so the
residual separates the right layout from the wrong ones sharply. An encoder may
therefore pick a tighter surround without any reader needing to be told, and a
future revision can add a layout without a version bump.

### Calibration ring

A conforming symbol MUST carry a calibration ring in one of the defined
surround layouts.

> A reader MAY additionally attempt ordinary QR decoding when no Prism header is
> found, best-effort recovery from a cropped ring, or ringless recovery under
> favourable conditions. Those are reader conveniences. A symbol without a ring
> is not a conforming PS Code.

Let `a = ringInset`, `t = ringThickness`, and for a canvas of `W x H` modules:

```
perRow = floor((W - 2a) / t)          cells along the top and bottom edges
perCol = floor((H - 2a) / t)          cells along the left and right edges
lastX  = a + (perRow - 1) * t
lastY  = a + (perCol - 1) * t
cellCount = 2 * (perRow + perCol) - 4
```

`perRow` and `perCol` MUST each be at least 3. The ring is walked clockwise from
its top left corner, each cell being the `t x t` block whose top left module is:

```
top edge     (a + i*t, a)        for i = 0 .. perRow-1
right edge   (lastX, a + j*t)    for j = 1 .. perCol-1
bottom edge  (a + i*t, lastY)    for i = perRow-2 down to 0
left edge    (a, a + j*t)        for j = perCol-2 down to 1
```

Every corner appears exactly once, and the number of generated coordinates
equals `cellCount`.

**The remainder stays white.** When the band does not divide evenly into cells,
the leftover modules at the far edge MUST be left white rather than filled with
a runt cell.

> A partial cell samples as a blend of its colour and the white beside it, which
> is indistinguishable from a correctly sized cell under a different
> illumination, and it corrupts the very fit it would be feeding.

> A checkable consequence: `N = 4V + 17` is always odd, so a single-matrix
> `THICK` symbol, whose canvas is `N + 16` and whose band is therefore odd,
> always leaves exactly one module of white remainder on each side. An
> implementation that produces a runt cell there has the rule wrong.

Ring cell `i` MUST be painted with palette entry `i mod 32`. The palette is
fixed and does **not** depend on the loading, which is what lets a reader
calibrate before it knows the loading:

| index | colour |
|-------|--------|
| 0 | black |
| 1 | white |
| 2..7 | the six chromatic cube corners: red, green, blue, cyan, magenta, yellow |
| 8, 16, 24 | black |
| 9, 17, 25 | white |
| 10..15 | red ramp, `(round(255k/7), 0, 0)` for `k = 1..6` |
| 18..23 | green ramp, `(0, round(255k/7), 0)` for `k = 1..6` |
| 26..31 | blue ramp, `(0, 0, round(255k/7))` for `k = 1..6` |

Palette recurrence depends on the actual ring length, which varies with version
and layout. An implementation MUST NOT assume that 32 divides the ring length,
nor that each palette entry occurs a fixed number of times.

> Where the ring is long enough for entries to recur, each is measured at
> several different places in the frame, which is what makes the ring useful
> against an uneven illumination field and not just against a global cast. A
> black and a white cell recur every eight cells, and that spacing is deliberate:
> black and white are the only two colours a channel mix leaves unchanged, so
> they are the only two that may anchor the illumination field, and the field
> needs them spread along the border where the function patterns inside the
> symbol cannot reach.

> Each ramp only stores its six interior steps. Step 0 is black and step 7 is
> that channel's pure primary, both of which the palette already carries, so a
> full eight point ramp is reconstructed from one third of the slots. The cube
> corners fit the channel crosstalk and white balance; the per-channel ramps
> characterise each channel's response curve, so the level references for any
> loading can be interpolated from one fixed layout.

### Mosaics

**Status: experimental in this revision.** The interoperable profile is one
matrix. Mosaic geometry is defined below and implemented, but is not required
for conformance and has no conformance vectors yet.

A symbol MAY tile up to a 4x4 grid of matrices behind a single ring, separated
by 2 module white gutters. All matrices MUST share QR version, EC level, mask,
loading and `sliceLength`, and each carries its own header naming its grid slot,
so a reader never has to order them geometrically and any one matrix identifies
the whole symbol's shape. The gutter applies only between adjacent matrices;
the outside edge belongs to `margin` alone.

```
G = 2                                    gutter, modules
mosaicWidth  = C * N + (C - 1) * G       C columns
mosaicHeight = R * N + (R - 1) * G       R rows
canvasWidth  = mosaicWidth  + 2 * margin
canvasHeight = mosaicHeight + 2 * margin
matrixOrigin(r, c) = (margin + c * (N + G), margin + r * (N + G))
```

The ring walk of the previous section applies unchanged to a rectangular canvas.

> Tiling loses to one big matrix while a big matrix is possible: QR capacity per
> module rises steeply with version, so at live camera resolution a single square
> always wins. What a grid buys is headroom past the version 40 ceiling on high
> resolution still captures, where a 3x4 grid carries three to four times what
> the largest single symbol can. A reader that finds only some of the matrices
> derives the rest from a found matrix's transform, since the grid pitch is
> exact, and every derived matrix must still decode its own base plane before it
> is believed.

---

## 3. Why the composite is still detectable

Function patterns are identical across all planes. Identical plane bits means
every channel lands on the same darkness level, which means the module is a pure
grey: black where all planes are dark, white where all planes are light.

So in the rendered colour symbol the three finder patterns, the separators, the
timing patterns, the alignment patterns, the dark module and the format
information are all rendered in pure black and white, exactly as an ordinary QR
Code would render them. Only the data region is coloured. Prism reuses that:
geometry comes from a standard finder pattern search, and Prism only replaces
the sampling step, reading colour at each module centre instead of a binary
value.

Two limits on that claim, both of which matter to an implementer:

* Reliable location by a conventional QR detector is established for the
  `STANDARD` surround, which carries the full 4 module quiet zone. The tighter
  layouts halve it, and a dense symbol at 6 pixels per module is measured to
  fail detection outright under a conventional binarizer.
* Locating a PS Code is not the same as reading one. **A conventional QR
  payload decoder MUST NOT be expected to recover anything useful** from the
  composite luminance image, because the luminance of a coloured data module is
  not the black-or-white value any single plane holds. Prism is not payload
  compatible with ordinary QR readers, and no encoder should claim it is.

---

## 4. Frame and header

Each matrix carries its own 9 byte header at the start of its plane stream, and
the payload is one stream split across the matrices.

### Stream construction

```
completeStream = payload || crc32(payload)

perMatrixData  = P * sliceLength - 9
matrixData[m]  = completeStream[m * perMatrixData .. min((m+1) * perMatrixData, len))
matrixStream[m]= header[m] || matrixData[m] || zeroPadding to exactly P * sliceLength
plane p of matrix m carries matrixStream[m][p * sliceLength .. (p+1) * sliceLength)
```

Matrices are indexed row-major. Padding MUST be zero bytes. Every plane MUST
contain exactly `sliceLength` bytes.

A decoder MUST order matrices by the `matrixIndex` in their headers, not by
detected position; strip each 9 byte header; concatenate the per-matrix data
regions; read exactly `payloadLength` payload bytes followed by the four CRC
bytes; and verify the CRC-32. Remaining padding MUST be ignored. A decoder
SHOULD reject non-zero padding.

The complete payload is returned only when every matrix needed to cover
`payloadLength + 4` bytes has been recovered and the CRC passes. There is no
partial mosaic recovery; an outer erasure code, if wanted, belongs to a payload
profile.

### sliceLength

Every plane of one matrix MUST carry exactly the same number of bytes,
`sliceLength`. Its **upper bound** is the maximum Byte-mode capacity of the
selected QR version and EC level:

```
countBits    = 8 if V <= 9 else 16
maxSlice     = floor((8 * dataCodewords(V, L) - 4 - countBits) / 8)
9 <= sliceLength <= maxSlice
```

where `dataCodewords(V, L)` is taken from the ISO/IEC 18004 block tables. The
remaining four bits provide the QR terminator.

`sliceLength` is **not** required to equal `maxSlice`. An encoder chooses the QR
version to fit the payload and then sizes the slices to the payload, so planes
are normally shorter than capacity, and the symbol is correspondingly cheaper to
decode.

`sliceLength` is carried on the wire, in each plane's own QR **Byte mode
character count indicator**, which ISO/IEC 18004 defines as 8 bits for
`V <= 9` and 16 bits above. A conformant QR decoder therefore returns exactly
`sliceLength` bytes for every plane, and no Prism-level field is needed.

> An earlier revision justified this by saying "ZXing returns the exact byte
> count of the decoded segment", which reads as a dependency on one library's
> API and drew a reasonable objection. The justification was wrong; the design is
> not. The byte count is a field in the QR bitstream, not a property of a decoder
> implementation, and any conformant decoder recovers it.

A decoder MUST reject a matrix whose planes decode to differing byte counts. A
short plane is damage, not a signal, and combining planes of unequal length
would silently misalign the stream.

> Mandating `sliceLength = maxSlice`, which would let a decoder derive it from
> `V` and `L` without reading the count field, is a defensible alternative
> design. It is not adopted here because it would change the bytes in every
> existing symbol and so require a new format version, and it buys nothing a
> conformant QR decoder does not already provide.

### QR encoding profile

Every plane MUST use QR Code Model 2, versions 2 through 40, Byte mode only, in
exactly one Byte-mode segment of exactly `sliceLength` bytes, with no ECI
segment, no FNC1, no Structured Append, and no Kanji, Numeric or Alphanumeric
optimisation. Raw bytes are encoded without character set conversion. Standard
QR terminator, byte alignment, pad codewords, error correction generation,
interleaving and remainder bits apply as in ISO/IEC 18004.

**Mask pattern 0 MUST be used for every plane** in this revision.

> All planes must share a mask, or the function patterns diverge and section 3
> collapses. Fixing it at 0 is the least ambiguous way to guarantee that two
> independent encoders emit identical matrices. A future revision may adopt a
> selection rule, such as summing the standard mask penalty across all planes and
> taking the lowest-numbered minimum, but a rule that is not stated is worse than
> a constant, and "0 by default" left the door open to a library choosing
> per plane.

### Header

| offset | size | contents |
|--------|------|----------|
| 0..1   | 2 | magic, `0x50 0x52` (`"PR"`) |
| 2      | 1 | format version, 2 or 3 |
| 3      | 1 | packed shape, layout depends on format version |
| 4      | 1 | matrix index, row major |
| 5..7   | 3 | payload length in bytes, unsigned big endian, 24 bit, payload only |
| 8      | 1 | CRC-8 over bytes 0..7 |

Fields are listed most significant bit first.

Byte 3, format version 2, uniform loading only:

```
bits 7..6   b - 1           b in 1..3; the encoding 0b11 is reserved
bits 5..4   rows - 1        rows in 1..4
bits 3..2   columns - 1     columns in 1..4
bits 1..0   reserved, MUST be zero
```

The depth field is two bits wide but only three of its four encodings are legal.
`0b11`, which would mean `b = 4`, is reserved, and a decoder MUST reject a header
carrying it rather than inventing a fourth level table.

Byte 3, format version 3, per-channel loading:

```
bits 7..5   loading profile index, 0..7
bits 4..3   rows - 1        rows in 1..4
bits 2..1   columns - 1     columns in 1..4
bit  0      reserved, MUST be zero
```

Loading profiles, format version 3:

| index | `(bR, bG, bB)` | bits per module | status |
|------:|----------------|----------------:|--------|
| 0 | 1, 1, 1 | 3 | identical to version 2 `b = 1` |
| 1 | 2, 1, 1 | 4 | falsified on hardware |
| 2 | 2, 2, 1 | 5 | untested |
| 3 | 2, 2, 2 | 6 | never decoded |
| 4 | 3, 2, 2 | 7 | untested |
| 5 | 3, 3, 2 | 8 | untested |
| 6 | 3, 3, 3 | 9 | never decoded |
| 7 | reserved | - | MUST NOT be emitted |

An encoder MUST emit format version 2 whenever the loading is uniform with `b`
in 1..3, so that symbols expressible in version 2 are byte-identical to what a
version 2 encoder produces and remain readable by a version 2 reader. Format
version 3 MUST be used only for a loading version 2 cannot express.

Three consequences that MUST be honoured:

* **Byte 2 is dispatched on before byte 3 is interpreted.** The geometry fields
  move between versions: `rows - 1` sits at bits 5..4 in version 2 and at bits
  4..3 in version 3. A reader that decodes the shape byte before the version
  byte reads the wrong grid for one of them.
* **Profile indices are positional.** The wire value is an index into the profile
  table exactly as ordered above. Inserting, removing or reordering an entry
  silently re-maps every existing symbol's loading, so the table is append-only
  and a retired profile MUST be left in place as reserved.
* **A decoder MUST accept profiles 0, 3 and 6** even though a conformant encoder
  never emits them, since the version-selection rule sends those three out as
  format version 2 instead. A version 3 header naming them is well formed and
  unambiguous, and rejecting it would fail a symbol that is perfectly readable.

Every declared profile satisfies `bR >= bG >= bB`, gives every channel at least
one bit, and the table is non-decreasing in total bits. Those are properties of
the table rather than rules a decoder enforces, but a future editor adding a
profile MUST preserve them: a zero-depth channel has no level table and no
placement curve, and red carrying fewest bits would weaken the bootstrap the
whole format stands on.

> Profile 7 is reserved rather than assigned. It would want four bits on red, and
> the level code has tables for one, two and three; a fourth table is a design
> decision of the same kind as the existing ones and not something to add in
> passing.

### Header validation

A reader MUST reject a candidate matrix unless all of the following hold:

* bytes 0..1 equal `0x50 0x52`;
* byte 2 is a format version the reader supports;
* the CRC-8 over bytes 0..7 matches byte 8;
* the decoded loading is one this document defines, and the profile is not 7;
* `rows` and `columns` each decode to 1..4;
* reserved bits are zero;
* `matrixIndex < rows * columns`;
* `payloadLength` does not exceed the symbol's capacity (section 6).

`payloadLength` counts the payload alone. It excludes the four byte CRC-32
trailer and excludes the zero padding, both of which share the same stream.
`payloadLength` MAY be zero. All matrices belonging to one symbol MUST agree on
magic, format version, loading, rows, columns, payload length, QR version, EC
level and mask; a reader MUST reject the candidate symbol otherwise.

Identical duplicate matrices MAY be ignored. Two matrices claiming the same
index with differing content MUST cause the candidate symbol to be rejected,
unless one of them fails its own QR or header checks. A decoder MUST NOT combine
bytes from conflicting copies of one matrix index.

A reader MUST reject an unknown format version as a Prism payload rather than
guessing at its layout.

### Where the QR parameters come from

The Prism header carries neither the QR version, nor the error correction level,
nor the mask. All three are recovered from each plane's own QR format and version
information, which is a function pattern and therefore rendered in pure black and
white in the composite (section 3). A reader reads them exactly as it would from
an ordinary QR Code, before any colour work.

That is also why every matrix's header is byte-for-byte identical except byte 4,
which names its grid slot, and byte 8, which is the CRC-8 covering it.

### The bootstrap

`sliceLength` is at least 9 for every supported version, so the header always
lies wholly inside plane 0's slice. Plane 0 is the most significant bit of red,
which a reader recovers with a 50% threshold **in corrected ideal-intensity
space**, knowing nothing about the loading.

> The threshold is meaningful only after the response curve has been inverted. A
> raw camera reading cannot be thresholded at 50%, because 50% of the *reading*
> is not 50% of the *intensity* once a display gamma is in the way. Section 1 of
> DECODER.md gives the sequence the reference decoder uses.

### CRC parameters

**CRC-8**, over header bytes 0..7:

```
width 8, polynomial 0x07, init 0x00,
reflect in false, reflect out false, final xor 0x00
check value for ASCII "123456789": 0xF4
```

**CRC-32**, over exactly the `payloadLength` payload bytes and nothing else, no
header and no padding:

```
width 32, polynomial 0x04C11DB7 (reflected 0xEDB88320), init 0xFFFFFFFF,
reflect in true, reflect out true, final xor 0xFFFFFFFF
check value for ASCII "123456789": 0xCBF43926
```

The four CRC-32 bytes are appended to the payload in big endian order.

---

## 5. Rendering

A rendered symbol MUST be interpreted as follows:

* values are opaque 8-bit-per-channel sRGB code values, in red, green, blue
  order;
* alpha, where an image container carries it, MUST be 255;
* modules are axis-aligned squares with hard edges;
* encoders MUST NOT antialias between modules or between ring cells;
* encoders SHOULD render at an integer number of output pixels per module.

An application that displays a symbol at non-integer scale MUST use
nearest-neighbour sampling, or rasterise afresh at the exact displayed module
grid. Lossless PNG is the recommended interchange format. JPEG SHOULD NOT be
used as a source representation.

Colour management conversion after symbol generation is outside conformance
here. A print profile, which would have to define output colour space, dot gain,
ink spread and minimum module size, is not part of this revision, and the sRGB
values in this document MUST NOT be assumed to survive a print process
unchanged.

---

## 6. Capacity

Byte capacity of one plane at version `V` and EC level `L` is `sliceLength` as
defined in section 4. For `K = rows * columns` matrices:

```
perMatrixData    = P * sliceLength - 9
payloadCapacity  = K * perMatrixData - 4
                 = K * (P * sliceLength - 9) - 4
```

The 9 bytes are the per-matrix header, which is repeated in every matrix. The 4
bytes are the single CRC-32 appended to the complete payload.

Worked example, QR version 20 at EC level M, single matrix, `b = 2`:

```
dataCodewords(20, M) = 669
sliceLength = floor((8 * 669 - 4 - 16) / 8) = floor(5332 / 8) = 666 bytes
P = 6 planes
perMatrixData   = 6 * 666 - 9 = 3987
payloadCapacity = 3987 - 4     = 3983 bytes
```

against 666 bytes for the same QR symbol in black and white.

> An earlier revision of this document stated 666 data codewords, 664 bytes per
> plane, an 8 byte header and 3,972 payload bytes. All four were wrong: 666 is
> the slice length rather than the codeword count, and the header is 9 bytes
> everywhere else in this document.

---

## 7. Limits and security

The 24 bit length field caps a payload at **16,777,215 bytes**. An encoder MUST
NOT attempt a larger payload; a decoder MUST reject a header claiming one.

A decoder MUST treat a decoded payload as untrusted input:

* validate `payloadLength` against capacity **before** allocating for it;
* perform capacity arithmetic in a width that cannot overflow;
* bound the number of candidate layouts, orientations and colour hypotheses it
  will try;
* bound the matrix count at `rows * columns <= 16`;
* never execute or auto-open decoded content on the strength of the format
  alone.

CRC-32 detects accidental corruption. **It does not authenticate the sender**,
and neither does any other part of this format. An application that needs
authenticity MUST carry its own signature or MAC inside the payload.

---

## 8. Conformance

A conformance claim MUST name the classes it meets and the configurations it was
tested against (section 0).

**Encoder conformance.** Produces the exact expected module-colour matrix for
every canonical input vector.

**Core decoder conformance.** Recovers the payload from every canonical lossless
vector, and rejects every negative vector for the stated reason.

**Standard surround decoder.** Supports the `STANDARD` surround. This is the
minimum a reader MUST support.

**Full decoder.** Supports `COMPACT`, `BALANCED`, `STANDARD` and `THICK`, all
loadings this document defines, QR versions 2 through 40, and all four EC levels.

**Mosaic decoder.** Not defined in this revision; mosaics are experimental.

**Capture performance profile.** A non-core benchmark reporting decode success
against pixels per module, angle, blur, illumination, display type, camera model
and print process. Device performance claims MUST NOT be presented as bitstream
conformance.

### Conformance vectors

Canonical vectors are not yet published as an immutable set. Until they are, no
implementation can demonstrate interoperability, and this is the largest single
gap between this document and a freezable standard. The intended minimum set,
each with source payload, the full parameter tuple, header bytes, `sliceLength`,
per-plane byte slices, binary QR matrices, final RGB module matrix, a canonical
lossless PNG and its hash, and the expected result:

header serialisation and CRC-8; CRC-32 of empty and known payloads; plane to
channel mapping for every defined loading; level code forward and inverse;
intensity tables; ring coordinates and palette sequence for every surround
layout, including a case where the band does not divide evenly; a version 2
low-capacity symbol; a version 7 or later symbol exercising version information
modules; the version 20-M capacity vector; mirrored, perspective-distorted,
unevenly illuminated and channel-mixed captures; invalid header CRC; invalid
payload CRC; conflicting mosaic headers; duplicate matrix; cropped ring; and an
ordinary QR Code presented to a Prism reader.

---

## 9. Extension policy and version history

A new format version is required to change plane mapping, level tables, header
layout or module colours. Decoder-only improvements do not require one, and
neither do payload-level protocols.

Reserved bits MUST be zero in the versions defined here, and a reader MUST reject
non-zero reserved bits. Any future use of them MUST state whether older readers
are expected to reject or safely ignore the extension. Reserved bits MUST NOT be
consumed casually before that extension model is written down.

Format versions defined so far:

| version | adds | status |
|--------:|------|--------|
| 2 | uniform bit depth 1..3 | current, and the only version proven through a camera at `b = 1` |
| 3 | per-channel loading profiles | profile 1 falsified on hardware; profiles 2 to 6 implemented but untested; retained so the machinery and its measurements are not lost |

Support for format version 2 is mandatory for any reader claiming conformance
and will not be withdrawn without a deprecation notice in a published revision.

### What is deliberately out of scope

The Prism payload is arbitrary bytes. Sequencing, fountain coding,
retransmission, handshakes, latency control, session identity, codec identifiers
and timing all belong to payload protocols carried **inside** those bytes, and
MUST NOT cause a change to plane mapping, the calibration ring, the QR
encoding, the header, the CRCs or symbol geometry.

Two such payload protocols are defined as their own documents:

- **[APHOTIC.md](APHOTIC.md)** carries a file across a sequence of symbols, with
  rateless fountain repair so a reader that missed pages recovers without the
  sender ever repeating itself. This is complete-file, eventual delivery.
- **[STREAM.md](STREAM.md)** carries a live, disposable byte stream, with a
  redundancy window and a jitter buffer rather than a fountain, and an audio
  profile on top. This is real-time delivery that conceals what it cannot
  recover in time.

Neither touches this document. A reader tells the three payload kinds apart by
the first bytes of the decoded payload: `PS` for an Aphotic transfer page, `PV`
for a PrismShare Stream frame, and neither for a plain document. The complete
dispatch table is in the suite [README](README.md#payload-dispatch).

Asymmetric bit depth beyond the defined profiles, luminance compatibility with
ordinary QR payload decoders, and animated transfer are each a future format
version or a separate profile, not a clarification of this one.

---

## Acknowledgements

The first public revision of this specification incorporates a detailed format
review by **NomNomski**, whose change request drove the separation of the
normative format from the reference decoder, the correction of the capacity and
calibration-ring arithmetic, the honest accounting of which configurations are
proven versus merely defined, and the insistence that streaming and voice remain
payload protocols outside the symbol format. The [APHOTIC.md](APHOTIC.md) and
[STREAM.md](STREAM.md) companion documents are that separation carried out.
