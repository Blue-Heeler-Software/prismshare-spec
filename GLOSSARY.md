# PrismShare glossary

> **Document status:** editorial companion; no wire-format effect.

| term | meaning |
|---|---|
| **application** | A PrismShare sender, receiver or combined user-facing implementation. |
| **Aphotic Fountain** | The deterministic, integer-only rateless repair mechanism selected by Aphotic repair mode `0xFF`. |
| **Aphotic Transfer** | The `PS` payload protocol that delivers one exact, finite object eventually. |
| **chunk** | One fixed-size slice of an Aphotic transfer payload, zero-padded only at the end. |
| **coded page** | An Aphotic repair page whose body is the XOR of a deterministic source-chunk subset. |
| **conformance vector** | Canonical input, expected output and disposition used to test an implementation. |
| **document** | A plain PrismShare Code payload that is neither an Aphotic page nor a Stream frame. |
| **frame** | One complete `PV` PrismShare Stream payload carried in one symbol. |
| **packet** | One fixed-size codec unit inside a Stream frame. |
| **page** | One complete `PS` Aphotic header and chunk body carried in one symbol. |
| **payload** | Bytes recovered from the optical symbol before optional payload-protocol interpretation. |
| **plane** | One complete monochrome QR Code stacked into a colour channel of a PrismShare Code symbol. |
| **profile** | A versioned selection of wire semantics, such as Stream v1's fixed-rate audio codec table. |
| **PrismShare** | The product, application family and project umbrella. |
| **PrismShare Code** | The colour optical symbol defined by `FORMAT.md`; “PS Code” is the accepted short form. The wire value `PS` separately identifies an Aphotic page. |
| **PrismShare Protocol Suite** | The normative specifications, informative companions and vectors in this repository. |
| **PrismShare Stream** | The `PV` live protocol that delivers time-sensitive packets with bounded redundancy rather than eventual completeness. |
| **receiver** | An implementation that decodes symbols and optionally interprets their payload protocol. |
| **repair page** | An Aphotic page sent after the systematic pass to recover missing chunks. |
| **session** | A 16-bit Stream identity whose change resets receiver state. |
| **symbol** | One rendered PrismShare Code matrix and its required surround. |
| **systematic page** | An Aphotic page below `dataPages` that carries its source chunk verbatim. |
| **transfer** | One Aphotic object identified by its transfer id and pinned header shape. |
| **Twin Window** | The informative two-symbol Stream presentation whose symbols carry non-overlapping recent and older redundancy windows. |
| **window** | The newest run of Stream packets repeated in each transmitted frame. |
