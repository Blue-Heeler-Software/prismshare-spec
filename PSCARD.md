# PS Card: a business card in a single PS Code

Status: normative profile, version 1. Verified against the reference
implementation.

A PS Card is not a new format. It is a profile that pins down how a business
card travels as a PS Code, so that any conforming reader can present it as a
card rather than as bytes.

## The payload is a vCard

The payload of a PS Card is a standard vCard (RFC 6350), UTF-8, carried
verbatim. Version 4.0 is recommended; readers SHOULD accept 3.0 as well,
because the parsing below does not depend on the difference.

A reader detects a PS Card by looking at the decoded payload, not at any
transport flag: if the text begins with `BEGIN:VCARD` (case-insensitive,
after optional whitespace or a byte-order mark), it is a card. Under the
suite's payload dispatch a card carries neither the `PS` nor the `PV`
prefix; it is a plain document that happens to introduce itself.

## Always static, never a stream

A PS Card MUST fit in one static symbol. It is never fountain-coded, never
animated, never split across pages. Two reasons:

1. A card is exchanged in a glance, from a phone screen, a slide, a printed
   page or an email signature. None of those can animate reliably, and a
   printed card cannot animate at all.
2. A single static symbol decodes from one clean frame. That is the right
   latency for handing someone your name.

If a vCard does not fit the symbol, shrink the vCard, not the module size:
drop PHOTO (never embed one), trim NOTE, use one URL. A card that needs a
stream is a document, and documents already have the transfer format.

Encoding guidance: 1 bit per channel (3 bits per module) at error correction
level H is the rugged end of the format and is RECOMMENDED for cards, which
must survive glossy print, projector wash and phone-to-phone rescans.

## The colour extension

One extended property is defined:

    X-PS-ACCENT:#RRGGBB[;#RRGGBB...]

Brand colours, one to four, separated by `;` or `,`. A colour-native reader
SHOULD show them with the card (an accent strip, a tinted header, whatever
fits its design). A monochrome QR pipeline has nowhere to put a brand
colour; a PS Code reader does. Unknown X- properties MUST be ignored, so
the extension costs nothing to readers that do not know it.

## What a reader owes the person scanning

A conforming reader presents a decoded PS Card as a card:

- show FN prominently, with ORG, TITLE, NOTE, URL, EMAIL and TEL as card
  fields, not as raw text;
- offer at least: save to contacts, open the URL, share the vCard onward,
  and a way to dismiss;
- never act on the card by itself. Saving, opening and dialling are human
  acts. A hostile card must not be able to do anything by being scanned.

## Example

    BEGIN:VCARD
    VERSION:4.0
    KIND:org
    FN:Blue Heeler Software
    ORG:Blue Heeler Software
    URL:https://prismshare.app
    EMAIL:contact@bhsoftware.net
    NOTE:PrismShare. Files as light.
    X-PS-ACCENT:#FF3B30;#34C759;#0A84FF
    END:VCARD

227 bytes, which fits a version 8 symbol at 3 bits per module and EC level H
with room to spare. The live example is on the front page of
<https://prismshare.app>.
