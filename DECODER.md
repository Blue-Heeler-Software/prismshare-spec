# PrismShare Code reference decoder

> **Document status**
>
> | field | value |
> |---|---|
> | role | informative reference decoder |
> | conformance authority | `FORMAT.md`, not this document |
> | measured target | format version 2 at one bit per channel |
> | wire effect | none |

Nothing in this document is required for conformance.

A PS Code is defined by the bytes and colours in the symbol, which is
[FORMAT.md](FORMAT.md)'s job. How a reader recovers them is a quality-of-
implementation question, and pinning one algorithm as normative would freeze
today's calibration research into a permanent standard and forbid a better
decoder from conforming.

So this document describes the decoder that exists, in enough detail to
reimplement or to beat. An alternative decoder conforms if it recovers the
normative payload from the conformance vectors and rejects what those vectors
say to reject, however it does it internally.

Several quantities below are stated as the values this implementation uses
rather than as requirements: the sampling disc radius, the 14 pixels per module
threshold for ring-bleed removal, the worst-tenth outlier rule, the response
curve knot selection, and the residual model's fitting weights. They were
chosen by measurement against the capture simulator and real handsets. They are
not the only defensible choices.

---

## 1. Reading

1. **Binarise for geometry.** Take the luminance of the capture and run a
   standard QR finder pattern search over it. Recover the three finder centres,
   the alignment pattern, and the module dimension. A second pass is available
   that pushes saturated pixels toward mid grey before binarising, which flattens
   the colourful data region and makes the neutral finder patterns stand out.
2. **Build the transform.** Map QR module space to image space with the standard
   four point perspective transform. Because it is a projective map of the whole
   plane, it also addresses the quiet zone and the calibration ring at negative
   and beyond-`N` module coordinates.
3. **Sample.** Average a small disc of pixels at each module centre and at each
   ring cell centre.
4. **Settle the orientation and calibrate.** See below.
5. **Classify.** Correct every sampled module colour, snap each channel to the
   nearest level, encode through the level code, and fill in all `P` plane
   matrices.
6. **Decode.** Run each plane through the QR decoder. Concatenate the slices,
   check the CRC-32, and return the payload plus the per-plane count of symbols
   Reed-Solomon had to repair, which is a direct read on how much margin was
   left.

### Mirrored captures, and why step 4 is shaped the way it is

A capture through a mirror, or from a front camera, comes back with its finder
patterns in the opposite handedness. A standard detector normalises that, which
means the sampling grid it hands back is **transposed**.

Most function patterns do not care: the finder patterns, the separators, the
timing patterns and the alignment patterns all map onto themselves under
transposition, so a transposed grid reads the same values in the same places.

Two do not, and the reference decoder excludes them from its anchor set for
exactly that reason. The dark module at `(8, n-8)` transposes onto `(n-8, 8)`,
which is a format information module and is dark or light depending on the mask.
One wrong anchor out of a few dozen survives the illumination fit, which trims
outliers, but the quality residual is a plain RMS, and a single full scale error
there contributed `sqrt(1/28) = 0.189` with 28 fine anchors, enough to make a
perfectly good mirrored capture report zero usable bits. The calibration ring
cares a great deal, because ring cell `i` then lands where a different palette
entry is, and every fit built on top of it is built on scrambled references.

Reading plane 0 first and asking it whether the capture was mirrored does not
work either. Recovering plane 0 means thresholding at 50%, and 50% of the
*reading* is not 50% of the *intensity* once a display gamma is in the way. Undoing
that needs the ring's response curve, which needs the orientation, which is what
we were trying to learn.

So the orientation is settled on evidence rather than on ordering. Both
calibrations are built, ranked by how well each explains the known ring colours,
and the first whose base plane actually decodes wins. A third candidate with no
ring at all comes last: it is fitted from the function patterns alone, and it is
what catches an ordinary QR Code and a capture that cropped the ring off.

Once the base plane decodes, its header gives `b`, and if `b = 1` planes 0, 1
and 2 are already all there is.

---

## 2. Calibration

Applied in this order to every sampled colour:

0. **Ring bleed removal.** Ring cells are small patches surrounded by known
   colours, and optical blur mixes a fraction of the neighbours into every
   reading. Two coefficients (tangential, from the walk neighbours; radial,
   from the white either side) are estimated from the neutral cells only, since
   any global colour distortion cancels there by construction, and each cell is
   algebraically unmixed against its neighbours' observed readings. Applied only
   above 14 camera pixels per module: below that the data modules are as bled
   as the ring, and an uncorrected ring, softened the same way, models them
   better.

1. **Illumination field.** The symbol's own function patterns supply known black
   and known white modules spread across the whole symbol (finder patterns,
   timing patterns, alignment patterns), and the ring supplies more at the border
   and in the fourth corner. Per channel, a field

   ```
   a + bx + cy + dxy + ex^2 + fy^2
   ```

   is least-squares fitted to the black samples and to the white samples, then
   every sample is normalised to
   `t = (observed - black(x,y)) / (white(x,y) - black(x,y))`. Each fit is run
   twice, the second time with the worst tenth of residuals dropped, so a single
   misdetected anchor cannot tilt the whole surface.

   The two square terms are not decoration. Lens falloff goes as the square of
   the distance from the optical centre, and a purely bilinear surface cannot
   represent that at any coefficient: it leaves a residual bow across the symbol.
   At three bits per channel the levels are only 1/7 apart, and that bow alone is
   enough to lose planes.

2. **Response curve, inverted.** The per-channel ramps give eight points of each
   channel's transfer curve. Inverting it linearises the reading, which absorbs
   display gamma and camera tone curves.

   The inversion runs over a strictly increasing subset of the knots. A channel
   that clips, or that a tone curve has flattened, produces knots that repeat,
   and those carry no information: keeping them would turn a rounding error in
   the reading into a whole level of swing. Dropping them and extrapolating along
   the last informative segment is both stabler and closer to the truth.

3. **Channel mixing.** A 3x4 affine map (3x3 mixing plus offset) is least-squares
   fitted from the linearised readings to the ideal values, over every palette
   entry. This corrects white balance and the crosstalk that comes from a Bayer
   sensor and from display primaries that are not the ones the generator assumed.

The curve comes **before** the mix on purpose. A capture crosstalks in linear
light and then applies a tone curve, so undoing the tone curve first leaves a
genuinely linear relationship for the mix to solve, and the fit is then exact
rather than approximate. The other order puts a linear fit across a
nonlinearity, which holds up while only one of the two effects is present and
falls apart once gamma and crosstalk are both significant.

After these stages a corrected value is in ideal intensity units, 0 for the
darkest level and 1 for the brightest. Two refinements sit on top:

* **A residual model.** What the separable stages cannot absorb (a camera's
  tone curve applied to luminance rather than per channel) leaves a smooth
  residual that depends on a colour's luminance. A small model (four
  coefficients per channel over `[Y, Y^2, Y*u, Y^2*u]`, fitted to per colour
  means, kept only if it beats the zero model on the ring) shifts each
  *reference* to where the capture will actually put that colour.
* **Euclidean classification, whitened verdict.** Classification is nearest
  shifted reference in plain Euclidean distance; the residual covariance is
  deliberately NOT used as a classification metric, because it mixes noise with
  per colour misfit whose direction varies by colour, and using it measurably
  misreads the colours whose misfit lies off the average direction. The
  covariance is used where averaging is correct: the reported bit depth demands
  that the closest pair of expected colours be separated by `SEPARATION_SIGMAS`
  units in the whitened space where the ring residual is 1 per axis. That
  constant is **4.5** in the reference implementation.

### Bit depth estimation

The measure is the **end to end residual**: run every known colour in the frame
back through the finished correction and see how far off it lands.

That is deliberately not a noise estimate. A between-repeat spread measures
sensor noise and nothing else, and will happily report nine bits on a capture
that cannot decode six, because it is blind to a lighting field the model could
not quite follow, to a response curve that clipped, and to a mix that did not
fully undo the crosstalk. The residual sees all of them, in exactly the units
classification works in.

Two populations are scored per channel and the worse one wins:

* **the calibration ring**, which covers every palette entry and so probes the
  whole colour space, but sits at the border with white on both sides;
* **the timing and alignment pattern modules**, which are only black and white
  but are one module wide and surrounded by data, so they suffer the same
  neighbour bleed a real data module does. This is what makes the estimate react
  to focus rather than to noise alone.

Given the resulting `sigma`, the reportable depth is the largest `b` whose level
spacing clears it with headroom:

```
b_max = max { b in 1..3 : 1 / (2^b - 1) >= 4.5 * sigma }, else 0
bits per module = 3 * b_max
```

4.5 sigma is roughly 2.25 either side of the decision boundary. `b_max = 0`
means the capture cannot carry even `b = 1` reliably, which in practice means the
symbol is too small in frame, too blurred or too dark.

This measures the channel, not the symbol being read, so a reader can be pointed
at any PS Code and answer "how many bits per module will this setup carry".
The number is tuned to under-promise: across the simulated capture sweep it never
claims a depth that then fails to decode, and it frequently claims one less than
what works.

---

## 3. Matching the reader's rate to the sender

A looping sender ([Aphotic](APHOTIC.md), or any animated Prism transfer) steps
through its pages at a fixed dwell, and a reader has to keep up. On this link it
cannot ask the sender to slow down: a display cannot hear the camera watching it,
so there is no back channel and no negotiation to be had. What a reader can do is
measure, and adapt itself.

The page index in each transfer header is stamped, at the reader, with the time
it decoded. The rate that index advances **is** the sender's dwell, learned
without the sender ever stating it. Against that known rate, the one knob the
reader owns is its own analysis resolution: decode time scales with the number of
pixels analysed, so a reader falling behind spends fewer pixels and decodes
faster, catching every page instead of every third, while a reader that cannot
resolve the symbol at all spends more.

The rule is deliberately asymmetric. Falling behind is cheap to detect and cheap
to fix, so it acts quickly. Reading nothing is the more dangerous state, because
dropping resolution further would make it permanent, so resolution climbs back
the moment a symbol is seen but will not resolve, and a resolution that produced
no reads at all is remembered as a floor and not tried again.

None of this is rate negotiation, which a one-way link cannot support. It is the
reader matching the sender's fixed rate from its own side, and for the fountain
the sender's exact rate barely matters anyway: a reader that keeps up less well
simply collects useful coded pages over more laps.
