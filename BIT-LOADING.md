# PrismShare Code per-channel bit loading

> **Document status**
>
> | field | value |
> |---|---|
> | role | experimental format-version-3 extension |
> | stable conformance target | no |
> | implementation | profiles defined; profile 1 implemented |
> | camera result | profile 1 falsified; remaining profiles unproven |
> | wire authority | `FORMAT.md` section 4 controls where the texts overlap |

Status: implemented in the reference codec, and **the premise did not survive
hardware**. Read the last section before building on any of this. Format
version 2 and three bits per module remain what ships.

## The observation

Red, green and blue are not one channel. They are three, they have measurably
different signal to noise, and the format currently pretends otherwise.

Every failure diagnosed over two days of hardware testing failed in the same
order. Blue first, then green, and red last, without exception. The neighbour
bleed figures the calibrator reports on a capture that decodes cleanly are
representative:

| channel | neighbour bleed, working capture | bleed, failing capture |
|---------|----------------------------------|------------------------|
| red     | 0.052                            | 0.202                  |
| green   | 0.093                            | 0.231                  |
| blue    | 0.156                            | 0.299                  |

Blue is roughly three times as contaminated as red on the same frame. This is
not a surprise once stated: a Bayer sensor has half its photosites on green and
a quarter each on red and blue, so blue is the most interpolated channel before
anything optical happens to it, and the shorter wavelength focuses to a
different plane than red through the same lens.

Yet `b` is a single number in the header, applied to all three planes alike.

## Why this probably explains the six bit cliff

Three bits per module is rock solid on real handsets. Six has never decoded,
not once, not even at forty camera pixels per module where every other excuse
has been removed. That has been recorded as a cliff in the format's capacity.

Six bits per module is two bits per channel applied uniformly. If blue cannot
carry two bits, the symbol dies on blue alone, however good red is, because
every plane must decode for the payload to reassemble. A uniform loading fails
at the weakest channel and reports nothing about the others.

That is the same mistake a DSL modem would make by loading every subcarrier
identically regardless of its measured signal to noise, and it is the reason
DSL does not do that. Water-filling puts bits where the channel can carry them.

If the diagnosis holds, there is capacity sitting between the three bits we use
and the six that fails, and it has been invisible because only uniform loadings
were ever tried.

## The proposal

Replace the single `b` with a loading profile: a per-channel bit depth, chosen
from a small table rather than encoded freely.

A table rather than three independent fields for two reasons. It fits the
existing header without growing it, and arbitrary combinations are not useful:
the ordering red greater than or equal to green greater than or equal to blue
falls out of the physics and there is no reason to spend bits describing
loadings nobody should send.

| profile | red | green | blue | bits per module |
|---------|-----|-------|------|-----------------|
| 0       | 1   | 1     | 1    | 3               |
| 1       | 2   | 1     | 1    | 4               |
| 2       | 2   | 2     | 1    | 5               |
| 3       | 2   | 2     | 2    | 6               |
| 4       | 3   | 2     | 2    | 7               |
| 5       | 3   | 3     | 2    | 8               |
| 6       | 3   | 3     | 3    | 9               |
| 7       | reserved |  |     |                 |

Profile 0 is exactly what ships today. Profiles 3 and 6 are the uniform six and
nine that do not work, kept in the table at their natural places so the ladder
reads continuously and so a profile sweep can confirm they still fail rather
than assuming it. Profiles 1, 2, 4 and 5 are new, and 1 and 2 are the
interesting ones: they are the first two rungs above what works today, and they
ask nothing more of blue than blue already delivers.

Profile 7 is reserved rather than spent. The obvious next rung is red at four
bits, and the level code has tables for one, two and three only. That code is
endpoint anchored and deliberately not a Gray code, so that its extreme levels
land exactly on black and white and the shared function patterns stay pure. A
sixteen level table is a decision of the same kind and wants making on purpose,
not as a side effect of widening a table.

### Header

Format version 3. Byte 3 changes from

```
[b-1:2][rows-1:2][cols-1:2][reserved:2]
```

to

```
[profile:3][rows-1:2][cols-1:2][reserved:1]
```

The header stays nine bytes and the version byte already distinguishes the two
readings, so a version 3 reader can read version 2 symbols by mapping `b` to
the uniform profiles 0, 3 and 6.

### Planes

Plane count becomes `bR + bG + bB` rather than `3b`. Planes are ordered red
most significant first, then green, then blue, so plane 0 remains the most
significant bit of red.

That last point matters more than it looks. The bootstrap depends on plane 0
being recoverable by a fifty percent threshold against the illumination field
by a reader that does not yet know the loading. Red always carries at least one
bit and is always the strongest channel, so plane 0 is not merely still
readable, it is the most readable plane in the symbol. The bootstrap gets
better under this scheme, not worse.

### Level placement and the ring

Each channel gets its own placement curve over its own level count, using the
existing 1.35 exponent, since the transfer curve being corrected for is a
property of the display and camera rather than of the bit depth.

The calibration ring must sample each channel's levels, so its palette becomes
per-channel rather than a single 32 entry table. The ring's neutral cells,
which anchor the illumination field, are unaffected: they are neutral in every
channel by construction.

### Error correction

Left uniform in this proposal. Per-channel EC sized to per-channel error rate
is the obvious next step and the closer analogue of what DSL does, but it
compounds two changes at once and the first should be measurable on its own.

## Choosing a profile without a back channel

A screen cannot hear the camera watching it, so the sender cannot be told which
profile the link will carry. Three options, in increasing order of how much they
use what already exists:

1. The user picks, as they pick version today. The reader reports what a capture
   could support, so in principle the user reads it off and sets the sender.
   **This does not work on the handsets tested.** That estimate is derived from
   the calibration ring, and the ring does not resolve on phone captures at the
   distances that actually read: every frame reports zero ring cells and the
   decode succeeds from the fitted model instead. So the number is available on
   marginal captures and absent on exactly the good ones whose spare capacity
   you would want to spend. Fixing the ring is a prerequisite for this option
   and is an open problem in its own right.

2. The sender cycles profiles across laps. Costs a lap per profile tried and
   converges slowly on a long file.

3. **The sender shows two symbols at different profiles at once.** This is the
   one worth building. Two symbols per frame already ship, and the second symbol
   is free in pixels per module because a reader cannot focus close enough to
   fill its frame with one. Put a conservative profile on one and an aggressive
   profile on the other, and every frame is simultaneously a transfer and a rate
   probe. The reader takes whatever decodes, learns which profile is carrying,
   and the pair can then converge on two copies of the winner.

Option 3 is rate adaptation with no back channel and no probing overhead, which
is a thing a one way link is not supposed to be able to do. It exists only
because of the two symbol work, and it is the strongest argument for doing this
on top of that rather than instead of it.

It is also, given that option 1 depends on a ring that does not resolve, the
only one of the three that works on the hardware in front of us. A profile that
decodes is its own proof that the channel carries it, which needs no
measurement at all.

## What would falsify this

Profiles 1 and 2 failing while profile 0 succeeds, on a capture where the
reader's own quality estimate says red could carry two bits. That would mean
the six bit cliff is not a weak blue channel but something shared across all
three planes, and the whole premise is wrong.

That check was attempted and came back partial. On marginal captures the
asymmetry is unambiguous and in the predicted direction:

```
red   sigma 0.1202, 2 usable levels
green sigma 0.1807, 1 usable levels
blue  sigma 0.4503, 1 usable levels
supports up to 0 bits per channel
```

Red resolves twice the levels blue does on the same frame, and the uniform
estimate reports zero because it takes the minimum across channels, discarding
red's headroom entirely. That is the proposal's premise, measured.

What could not be measured is the same asymmetry on captures that decode
cleanly, because quality is derived from the calibration ring and the ring does
not resolve on those frames. So the direction is confirmed and the magnitude at
the operating point is not. Profile 1 is therefore the right first thing to
build: it asks blue for nothing it is not already delivering, and if it carries,
the premise is settled by the only measurement that matters.

## What happened when it was tested

Profile 1 was built and put in front of a camera. It decodes nothing at all: a
Pixel 7 reading a moto g06 at eight pixels per module, dual symbols, camera
locked, in the same conditions where profile 0 collects 140 to 153 pages of 180.

Three explanations were tested and two are dead.

**Not the warm decoder.** Forcing a cold calibration on every frame changes
nothing: profile 0 reads 153 of 180 cold and 149 warm, profile 1 reads nothing
either way.

**Not the bootstrap, though it should have been.** Plane 0 is red's most
significant bit, so putting red at two bits gives it four levels near 0, 0.385,
0.615 and 1.0, and the fifty percent threshold then has 0.115 of margin against
a black lift measured at 0.086. That is precisely the trace already recorded for
why uniform six bits fails, and this document claimed the opposite, that an
uneven loading would make the bootstrap stronger. It does the reverse whenever
the extra bit lands on red.

So a loading of R1 G2 B1 was tried, which carries the same four bits a module
while leaving red at two levels and the bootstrap at its full half of margin.
It also decodes nothing.

**So: no channel here carries a second bit.** Not red, which is the cleanest,
and not green with the bootstrap held out of it. The asymmetry between channels
is real and was measured, but being three times cleaner than the worst channel
is not the same as having a whole bit spare, and this document conflated the
two. Three bits per module is not an artefact of loading every channel the same.
It is what this link carries.

That leaves the six bit cliff explained more simply than by any of this: every
channel gives out at one bit, so two on any of them fails, and uniform six fails
three times over rather than once on blue.

### What would change the answer

A better operating point, and a way to know when you have one. All of the above
is one pairing at eight pixels per module in a dim room. Per-channel capacity on
a capture that decodes cleanly has never been measured, because that number
comes from the calibration ring and the ring does not resolve on phone captures
at any distance that reads.

That makes the ring the blocker, not the loading. Fix the ring, measure a good
capture, and this proposal becomes answerable instead of speculative. Until
then the machinery is built, tested and inert, which is the right place for it.
