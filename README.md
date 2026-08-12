# PrismShare Protocol Suite

PrismShare moves files and live media across a one-way camera-to-screen link.
It needs no pairing, network, account or return channel. The open specification
is a small family of layers rather than one monolithic format.

**PrismShare** is the product and project name. **PrismShare Code**
(**PS Code**) is the colour 2D symbol at its foundation. **Aphotic Transfer**
carries exact files using the **Aphotic Fountain** for rateless repair.
**PrismShare Stream** carries live media with a bounded redundancy window.

This repository is the authoritative **PrismShare Protocol Suite**. The
reference implementation lives elsewhere; conformance depends on the normative
documents and vectors here, not on reproducing its internals.

> **Naming note.** The repository slug is an address, not the standard's name.
> The canonical repository is `Mashr-Systems/prismshare-spec`; GitHub preserves
> the former `Blue-Heeler-Software/prism-spec` address as a compatibility
> redirect. Prose and package listings use **PrismShare Protocol Suite**. See
> [BRANDING.md](BRANDING.md).

## Architecture

| layer or companion | document | status | purpose |
|---|---|---|---|
| optical symbol | **[FORMAT.md](FORMAT.md)** | normative | Bytes, colours, geometry and headers of a PrismShare Code symbol. |
| decoder guidance | **[DECODER.md](DECODER.md)** | informative | One measured way to recover a symbol through a camera. |
| optical experiment | **[BIT-LOADING.md](BIT-LOADING.md)** | experimental | Per-channel loading profiles, including the hardware result that falsified the first profile. |
| exact-object payload | **[APHOTIC.md](APHOTIC.md)** | normative | Aphotic Transfer pages and the Aphotic Fountain. |
| live payload | **[STREAM.md](STREAM.md)** | normative | PrismShare Stream frames, redundancy windows and the version 1 audio profile. |

The optical format does not know what its payload means. The payload protocols
do not know how the symbol is displayed or photographed. This separation is a
conformance boundary, not merely an editorial arrangement.

### Payload dispatch

After a PrismShare Code symbol has yielded its payload bytes, the first two
bytes select the next layer:

| prefix | payload family | required action |
|---|---|---|
| `PS` (`0x50 0x53`) | Aphotic Transfer | Parse as a 13-byte Aphotic page header followed by one chunk. |
| `PV` (`0x50 0x56`) | PrismShare Stream v1 | Parse as a 10-byte stream header followed by fixed-size packets. |
| neither | plain document | Deliver the payload to the application without interpreting it as either protocol. |

`PV` does **not** mean “fountain stream.” Exact files and live media deliberately
use different loss disciplines: Aphotic uses rateless coded pages; Stream uses
recent-packet repetition and a playout buffer.

## Conformance and implementation aids

- [CONFORMANCE.md](CONFORMANCE.md) defines claimable components and the present
  proof status.
- [VALIDATION.md](VALIDATION.md) collects required rejection and ignore rules.
- [EXAMPLES.md](EXAMPLES.md) provides worked wire examples.
- [GLOSSARY.md](GLOSSARY.md) fixes terminology used across the suite.
- [VERSIONING.md](VERSIONING.md) explains version fields, reserved values and
  compatibility policy.
- [SECURITY.md](SECURITY.md) describes trust boundaries and resource limits.
- [vectors/](vectors/) contains canonical protocol vectors and the scaffold for
  full symbol conformance vectors.
- [CHANGELOG.md](CHANGELOG.md) separates normative corrections from editorial
  changes.

## Status

This is a working specification, not yet a frozen standard.

- PrismShare Code format version 2 at one bit per channel is proven on real
  handsets. A paired version 6 H presentation survived a public video
  platform's transcode at every tested playback quality from 720p upward.
- Higher bit depths and format version 3's per-channel profiles are defined but
  are not proven through a camera. Profile 1 was implemented and falsified.
- Aphotic Transfer and the Aphotic Fountain are proven on real handsets,
  including through the same video transcode.
- PrismShare Stream v1 is verified end to end through real cameras. Codec2 1300
  inside a version 8 symbol pair carried contiguous speech on the weakest
  handset tested.
- Canonical Aphotic and Stream protocol vectors now seed the conformance set.
  Full symbol-image vectors remain a pre-freeze requirement; until they exist,
  no implementation can demonstrate complete optical interoperability.

## Branding and name clearance

“Prism” is heavily used in software and broadcast products. The suite therefore
uses **PrismShare** as its primary compound mark and avoids presenting bare
“Prism” as the product name. **Aphotic Fountain** is the distinctive name of the
rateless repair mechanism; “fountain code” remains beside it as the searchable
technical description.

This naming policy is product architecture, not legal clearance. Before a
commercial launch, obtain professional trade-mark searches in the intended
classes and countries and check app-store, package, domain and social handles.

## About QR Code

PrismShare is an independent open format. Every plane of a PrismShare Code
symbol is a QR Code, and **QR Code is a registered trademark of DENSO WAVE
INCORPORATED**. This project is not endorsed by or affiliated with the
trade-mark holder. Implementers are responsible for assessing any intellectual
property applicable to QR Code encoding and decoding in their jurisdiction.

## Author

PrismShare Code and its Aphotic Transfer and PrismShare Stream payload
protocols were created and authored by **[aXL333](https://github.com/aXL333)**
and are published by **MASHR Systems**.

## Author

PrismShare Code and its Aphotic file-transfer and Prism Stream payload protocols
were created and authored by **[aXL333](https://github.com/aXL333)** and are
published by **MASHR Systems**.

## Acknowledgements

The first public revision incorporates a detailed format review by
**[NomNomski](https://github.com/NomNomski)**. The review drove the split of the
normative format from the reference decoder, corrections to capacity and
calibration arithmetic, honest accounting of proven versus defined
configurations, and separate documents for file transfer and live streaming.

## License

These specifications are licensed under the Creative Commons Attribution 4.0
International License (CC BY 4.0). You may share and adapt them, including for
commercial use, with attribution. See [LICENSE](LICENSE).

SPDX-License-Identifier: CC-BY-4.0
