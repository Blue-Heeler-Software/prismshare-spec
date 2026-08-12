# PrismShare Code

**PrismShare Code** (**PS Code**) is an open colour 2D barcode. It stacks several
ordinary QR Codes into the red, green and blue channels of one symbol, so a
single code carries several times the data of the black and white QR Code it is
built from, while staying locatable by an ordinary QR detector.

This repository is the **specification**, published for independent
implementation and review. The reference implementation lives elsewhere; nothing
here depends on it.

## The family

Three layers, three documents. The symbol format knows nothing of what it
carries; the payload protocols know nothing of the optics.

- **[FORMAT.md](FORMAT.md)** - the normative symbol format: exactly what bytes
  and colours one PS Code contains. Read this to build an encoder or decoder.
- **[DECODER.md](DECODER.md)** - the reference decoder, informative. How a reader
  recovers the payload, including calibration, bit-depth estimation, and matching
  the reader's rate to a sender it cannot talk back to.
- **[BIT-LOADING.md](BIT-LOADING.md)** - per-channel bit loading, a format
  extension whose first profile was implemented and falsified on real hardware;
  the remaining profiles are implemented but untested. Kept so the dead end, and
  the measurements that closed it, are not lost.

Two payload protocols ride inside Prism symbols and are specified separately, so
they can never disturb the optical format:

- **[APHOTIC.md](APHOTIC.md)** - a **file** across a sequence of symbols, with
  rateless fountain repair so a reader that missed pages recovers without the
  sender ever repeating itself. Complete-file, eventual delivery.
- **[STREAM.md](STREAM.md)** - a **live stream**, with a redundancy window and a
  jitter buffer rather than a fountain, and an audio profile on top. Real-time
  delivery that conceals what it cannot recover in time.

Start with [FORMAT.md](FORMAT.md) section 0, which states plainly which
configurations are proven through a camera and which are only defined.

## Status

This is a working specification, not yet a frozen standard.

- The symbol format at one bit per channel, and the Aphotic file transfer on top
  of it, are proven on real handsets, including through a public video
  platform's transcode: a paired version 6 H configuration was received by
  every camera tested at every playback quality from 720p up. Section 0 of the
  format records the measured envelope.
- Higher bit depths, and format version 3's per-channel loading, are defined but
  have not decoded from a camera. Section 0 of the format is explicit about this.
- Prism Stream is verified end to end through real cameras: with Codec2 1300
  inside a version 8 symbol pair, the weakest handset tested streamed
  contiguous speech from a monitor, and the strongest played minutes with no
  packets concealed. STREAM.md section 8 has the measurements.
- Canonical conformance vectors do not exist yet. Until they do, no
  implementation can demonstrate interoperability, and the specification says so.

Corrections and review are welcome through this repository's issues.

## About the name

PrismShare Code is an independent open format. Every plane of a symbol is a QR
Code, and **QR Code is a registered trademark of DENSO WAVE INCORPORATED**;
this project is not endorsed by or affiliated with the trademark holder, and
implementers are responsible for their own assessment of any intellectual
property that applies to QR Code encoding and decoding in their jurisdiction.

## Author

PrismShare Code and its Aphotic file-transfer and Prism Stream payload protocols
were created and authored by **[aXL333](https://github.com/aXL333)** and are
published by **MASHR Systems**.

## Acknowledgements

The first public revision of these documents incorporates a detailed format
review by **[NomNomski](https://github.com/NomNomski)**, whose change request
drove the split of the normative format from the reference decoder, the
correction of the capacity and calibration arithmetic, the honest accounting of
proven versus defined configurations, and the separation of the file-transfer and
streaming protocols into documents of their own.

## License

These specifications are licensed under the Creative Commons Attribution 4.0
International License (CC BY 4.0). You may share and adapt them, including for
commercial use, with attribution. See [LICENSE](LICENSE).

SPDX-License-Identifier: CC-BY-4.0
