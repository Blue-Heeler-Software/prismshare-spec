# PrismShare naming and brand architecture

> **Document status**
>
> | field | value |
> |---|---|
> | role | editorial naming authority |
> | wire effect | none |
> | suite | PrismShare Protocol Suite |
> | updated | 2026-08-12 |

Names should make the system memorable without making the protocol obscure.
Every coined name therefore has a stable descriptive expansion.

## 1. The hierarchy

| name | kind | meaning | preferred first use |
|---|---|---|---|
| **PrismShare** | product and project | The applications and complete technology family. | “PrismShare, a one-way camera-to-screen sharing system” |
| **PrismShare Protocol Suite** | standard | The documents and vectors in this repository. | Use in repository, specification and conformance titles. |
| **PrismShare Code** | optical format | The colour 2D barcode defined by `FORMAT.md`. | “a PrismShare Code (PS Code) symbol” |
| **Aphotic Transfer** | payload protocol | Eventual, exact file delivery over `PS` pages. | “Aphotic Transfer, PrismShare's exact-file protocol” |
| **Aphotic Fountain** | repair mechanism | The deterministic rateless fountain inside Aphotic repair mode `0xFF`. | “the Aphotic Fountain rateless repair mechanism” |
| **PrismShare Stream** | payload protocol | Bounded-latency live delivery over `PV` frames. | “PrismShare Stream, the live redundancy protocol” |
| **Twin Window** | presentation technique | The informative two-symbol Stream layout carrying non-overlapping recent and older windows. | “the Twin Window two-symbol presentation” |

## 2. Short forms

After the first descriptive use in one document or screen:

- “PrismShare Code” may become “PS Code” or “the symbol.” Do not shorten it to
  “Prism Code”; the bare “Prism” form is deliberately avoided.
- “Aphotic Transfer” may become “Aphotic” or “the transfer.”
- “Aphotic Fountain” may become “the fountain.”
- “PrismShare Stream” may become “Stream” when it cannot be confused with a
  generic byte stream.
- “Twin Window” retains both words; “twin” alone is not a protocol term.

Source identifiers such as `Fountain`, `Transfer` and `VoiceStream`, and the
wire magics `PS` and `PV`, are compatibility artefacts. Editorial naming does
not require changing them. In prose, **PS Code** always means the optical
symbol; the wire value `PS` remains the Aphotic page magic and must not be
inferred from the abbreviation.

## 3. Names not used as the umbrella

- **Prism** alone is too crowded and too weakly searchable to be the product
  identity.
- **Prism-spec** is a repository slug, not a user-facing name.
- **PrismAphotic** obscures the useful distinction between product and protocol;
  use “PrismShare Aphotic Transfer” when the umbrella must be explicit.
- **Aphotic Fountain** names the repair mechanism, not the complete application
  or the optical symbol.
- **Prism Stream** should be avoided in first-use prose because unrelated
  streaming products use similar wording. Use “PrismShare Stream.”

## 4. Naming new mechanisms

A new coined name belongs in the suite only when it identifies a stable,
architecturally meaningful mechanism. It must:

1. have a plain technical expansion;
2. name one thing at one layer;
3. avoid changing an existing wire meaning;
4. be added here and to `GLOSSARY.md` in the same change; and
5. survive a basic collision search before publication.

Ordinary fields, constants and implementation tactics should remain descriptive.
The standard gains authority from precision; not every clever implementation
detail needs a brand.

## 5. Repository and package naming

Canonical and compatibility names:

| surface | preferred value |
|---|---|
| specification repository | `Mashr-Systems/prismshare-spec` |
| application repository | `prismshare` |
| specification title | `PrismShare Protocol Suite` |
| app-store title | `PrismShare` plus a descriptive subtitle |
| command | `prism` may remain as a concise compatibility command |

The specification repository moved from
`Blue-Heeler-Software/prism-spec` to `Mashr-Systems/prismshare-spec` on
2026-08-11. GitHub preserves the former address as a redirect. Package, signing
identity and app-store changes remain separate release operations.

## 6. Clearance note

This document is not a trade-mark opinion. “Prism” is crowded, and an unrelated
public GitHub repository already uses the exact string `PrismShare`. Ordinary
web and repository searches found no obvious use of “Aphotic Fountain” at the
time of writing, but absence from those searches is not legal clearance.
Professional searches should cover the intended jurisdictions and relevant
software, telecommunications and data-transfer classes before commercial use.
