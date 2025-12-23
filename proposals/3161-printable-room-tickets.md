# MSC3161: Printable Room Tickets for Matrix

This proposal specifies a standardized format for printable room tickets that can be used to invite users to Matrix rooms or allow them to knock on rooms. The design draws inspiration from TAP TSI (Technical Specification for Interoperability - Telematics Applications for Passenger Services) train tickets, which use Aztec codes for machine-readable data encoding. This approach enables offline room joining scenarios where users may not have immediate access to digital devices or network connectivity.

## Background

Matrix room invites are currently distributed through digital means: direct invites via the client-server API, matrix.to links, or QR codes displayed on screens. However, there are scenarios where physical, printable tickets would be beneficial:

- Conference and event registration where attendees receive printed materials
- Educational institutions distributing room access to students
- Organizations providing room access to visitors without requiring them to have the Matrix app installed beforehand
- Archival purposes where a physical record of room access is desired
- Accessibility scenarios where users may have difficulty with digital-only distribution

The TAP TSI standard, used extensively in European railway ticketing, demonstrates that Aztec codes can reliably encode complex structured data for ticket validation. This proposal adapts similar principles for Matrix room access tickets.

## Proposal

### 2D Barcode Specification

Printable room tickets shall feature Aztec codes as the machine-readable component. Aztec codes are chosen over alternatives like QR codes because they do not require a quiet zone, have strong error correction capabilities, and are proven in high-volume ticketing applications per ISO/IEC 24778:2008.

#### Data Density Considerations

Matrix room tickets require higher data density than typical transportation tickets. Both railway tickets (per TAP TSI) and airline boarding passes (per IATA BCBP) primarily encode compact journey identifiers, passenger references, and cryptographic signatures using fixed-field or compressed formats optimized for their specific use cases. In contrast, Matrix room tickets must encode complete room identifiers (which include server hostnames that can be lengthy), federation routing information (multiple via servers), optional invite tokens, and human-readable join reasons. This results in payloads that may approach 500-1000 bytes for fully-featured tickets, compared to the approximately 100-300 bytes typical of transportation tickets in either rail or aviation sectors.

Dedicated barcode scanners capable of reliably reading high-density Aztec codes (21+ layers, 99×99 modules) have been widely deployed in transportation ticketing since the late 2000s, following the standardization of Aztec codes in ISO/IEC 24778:2008 and the rollout of electronic ticketing standards like UIC 918-3. Modern smartphone cameras with appropriate software can also decode these symbols reliably. Implementers should ensure their scanning solutions support full-range Aztec symbols up to 32 layers (151×151 modules) to accommodate the larger payloads required by this specification.

The barcode shall use the following parameters:

- Symbol type: Aztec Code (full-range symbol)
- Layers: Minimum 4 layers, maximum 32 layers (automatically selected based on data size)
- Error correction: Minimum 23% of symbol capacity dedicated to error correction codewords (recommended 33% for tickets that may be folded or worn)
- Color scheme: Dark modules on light background (standard). Light modules on dark background (inverse) is permitted for specialized media such as photosensitive materials
- Module size: Minimum 0.5mm per module when printed at the specified barcode dimensions

### Data Format

The Aztec code shall encode a binary data structure. The data is organized into three logical sections following the pattern established by TAP TSI: a header for format identification, open data containing the ticket information, and an optional signature for authenticity verification.

#### Header (8 bytes)

| Offset | Length | Field | Description |
|--------|--------|-------|-------------|
| 0 | 6 | Magic | ASCII string "MXROOM" |
| 6 | 1 | Version | Format version (0x01 for this specification) |
| 7 | 1 | Flags | Bit flags (see below) |

Flag bits:
- Bit 0: Invite type (0 = public/knock room, 1 = invite-only with token)
- Bit 1: Join reason included (0 = no, 1 = yes)
- Bit 2: Expiry timestamp included (0 = no, 1 = yes)
- Bit 3: Signature included (0 = no, 1 = yes)
- Bit 4-7: Reserved (must be 0)

#### Open Data (variable length)

The open data section uses a tag-length-value (TLV) encoding scheme for flexibility and forward compatibility.

| Tag | Name | Required | Description |
|-----|------|----------|-------------|
| 0x01 | Room ID | Yes | The room ID (e.g., `!roomid:server.example`) encoded as UTF-8 |
| 0x02 | Via Servers | Yes | Comma-separated list of servers for federation routing (e.g., `server.example,backup.example`) |
| 0x03 | Room Name | No | Human-readable room name for display on the ticket |
| 0x04 | Invite Token | Conditional | For invite-only rooms, the invite token or code |
| 0x05 | Join Reason | No | Pre-filled reason for joining/knocking, UTF-8 encoded, max 500 bytes |
| 0x06 | Expiry | Conditional | Unix timestamp (4 bytes, big-endian) after which the ticket is invalid |
| 0x07 | Issuer MXID | No | Matrix ID of the user who created the ticket |
| 0x08 | Issuer Display Name | No | Display name of the issuer for printing on the ticket |
| 0x09 | Room Avatar Hash | No | First 8 bytes of SHA-256 hash of room avatar for verification |
| 0x0A | Ticket ID | No | Unique identifier for this ticket (for tracking/revocation) |

Each TLV entry is encoded as:
- 1 byte: Tag
- 2 bytes: Length (big-endian, indicating the number of bytes in the value)
- N bytes: Value

#### Signature (optional, 64 bytes when present)

When the signature flag is set, the ticket includes a digital signature for authenticity verification. The signature is computed over the header and open data sections using Ed25519, with the signing key being the room creator's or an authorized issuer's signing key.

The signature enables ticket validators to verify that the ticket was issued by an authorized party without requiring network connectivity at validation time.

### Room Join Behavior

When a Matrix client scans a room ticket barcode, it shall:

1. Parse the header and verify the magic bytes and version
2. Decode the TLV entries from the open data section
3. If an expiry timestamp is present and the current time exceeds it, display an error indicating the ticket has expired
4. If a signature is present, verify it against known trusted issuers (implementation-defined)
5. Attempt to join the room using the room ID and via servers:
   - For public rooms: Send a join request directly
   - For knock rooms: Send a knock request, including the join reason if present
   - For invite-only rooms with a token: Use the token to claim the invite, then join

If the join reason field is present, clients should pre-populate the reason field in the join or knock request with this value, allowing the user to modify it before sending if desired.

### Paper Layout Specifications

The ticket layout specifications are derived from TCDD (Turkish State Railways) ticket printer specifications, which implement TAP TSI standards. The large format dimensions are also similar to ICAO Doc 9303 compliant airline boarding passes, making the format familiar to users and compatible with existing ticket printing infrastructure across transportation sectors. Two standard formats are defined to accommodate different printing equipment and use cases.

Unlike ICAO Doc 9303/IATA BCBP and TAP TSI standards, which allow considerable flexibility in visual layout to accommodate diverse printing equipment and organizational branding requirements, this specification defines strict layout zones and element positioning. This deliberate constraint ensures that Matrix room tickets are immediately recognizable as tickets at a glance, establishing a consistent visual identity across different issuers and implementations. The predictable appearance also aids users in quickly locating the barcode for scanning and understanding the ticket's purpose.

#### Large Format (210mm x 74mm)

This format is designed for compatibility with standard ticket printers used at transportation hubs, event venues, and similar locations. The dimensions align with both TAP TSI railway ticket standards and ICAO boarding pass specifications, enabling use of existing printing equipment. It can also be produced on standard A4 paper by printing and cutting into four equal longitudinal strips.

All coordinates are specified as (X, Y) from the top-left corner of the ticket, with dimensions as Width × Height.

**Barcode zone:**

| Element | Position (X, Y) | Dimensions | Notes |
|---------|-----------------|------------|-------|
| Aztec code | (5mm, 12.25mm) | 49.5mm × 49.5mm | Vertically centered; includes 2mm effective quiet zone from edges |

**Text zone** (starts at X=60mm, extends to X=205mm):

| Element | Position (X, Y) | Dimensions | Font | Alignment |
|---------|-----------------|------------|------|-----------|
| Room name | (60mm, 8mm) | 140mm × 18mm | Bold, 14-18pt | Left-aligned, single line with ellipsis truncation |
| Room ID | (60mm, 28mm) | 140mm × 10mm | Monospace, 8-10pt | Left-aligned, truncate with ellipsis if needed |
| Issuer display name | (60mm, 40mm) | 90mm × 10mm | Regular, 9-11pt | Left-aligned |
| Expiry date/time | (155mm, 40mm) | 50mm × 10mm | Regular, 9-11pt | Right-aligned, format: "Valid until: YYYY-MM-DD HH:MM" |
| Description/Instructions | (60mm, 52mm) | 140mm × 18mm | Regular, 8-10pt | Left-aligned, up to 2 lines |

**Optional branding zone** (bottom strip):

| Element | Position (X, Y) | Dimensions | Notes |
|---------|-----------------|------------|-------|
| Organization logo | (5mm, 64mm) | 50mm × 8mm | Optional; must not obscure barcode |
| Additional QR code | (160mm, 52mm) | 18mm × 18mm | Optional; for supplementary URL only |

#### Small Format (54mm x 89mm)

This format matches standard business card dimensions and is suitable for handheld thermal printers, badge printers, and similar compact devices.

All coordinates are specified as (X, Y) from the top-left corner of the ticket, with dimensions as Width × Height.

**Barcode zone:**

| Element | Position (X, Y) | Dimensions | Notes |
|---------|-----------------|------------|-------|
| Aztec code | (2.25mm, 5mm) | 49.5mm × 49.5mm | Horizontally centered with 5mm top margin |

**Text zone** (starts at Y=57mm, extends to Y=87mm):

| Element | Position (X, Y) | Dimensions | Font | Alignment |
|---------|-----------------|------------|------|-----------|
| Room name | (2mm, 57mm) | 50mm × 12mm | Bold, 10-12pt | Left-aligned, single line with ellipsis truncation |
| Room ID | (2mm, 70mm) | 50mm × 8mm | Monospace, 7-8pt | Left-aligned, truncate with ellipsis if needed |
| Issuer/Expiry | (2mm, 79mm) | 50mm × 8mm | Regular, 7-8pt | Left-aligned; format expiry as "Until: YYYY-MM-DD" |

### Printing Requirements

To ensure reliable scanning, the following printing requirements apply:

- Resolution: Minimum 203 DPI (8 dots/mm), recommended 300 DPI (12 dots/mm) or higher
- Barcode module mapping: Each barcode module should map to an integer number of printer dots to maintain sharp edges
- At the specified 49.5mm barcode size with a 99-module Aztec code (21 layers), each module is 0.5mm, requiring at least 4 dots per module at 203 DPI
- Contrast: Minimum 70% contrast ratio between dark and light modules
- Paper: Any paper stock suitable for the printing technology; thermal paper, bond paper, and card stock are all acceptable

## Potential Issues

### Barcode Scanning Reliability

Aztec codes are designed for reliable scanning even when damaged, but tickets that are heavily folded, wet, or faded may become unreadable. The 33% error correction recommendation mitigates this but cannot guarantee readability in all conditions. Users should be advised to keep tickets in reasonable condition.

### Token Security

For invite-only rooms, the invite token embedded in the barcode grants room access to anyone who scans it. Physical tickets can be photographed or photocopied. Implementations should consider:
- Single-use tokens that are invalidated after first use
- Time-limited tokens with expiry timestamps
- Ticket IDs that allow server-side revocation

### Offline Verification Limitations

While the signature mechanism allows offline verification of ticket authenticity, it cannot verify whether a ticket has been revoked or whether the room still exists. Full validation requires network connectivity.

### Character Encoding

Room IDs and other Matrix identifiers use a restricted character set, but room names and join reasons may contain arbitrary Unicode text. Implementations must handle UTF-8 encoding correctly and should validate that encoded data does not exceed the Aztec code capacity (approximately 1900 bytes for a 32-layer symbol with 23% error correction).

## Alternatives

### QR Codes Instead of Aztec Codes

QR codes are more widely recognized and have broader scanner support. However, Aztec codes offer advantages for ticketing applications: no quiet zone requirement (allowing more compact layouts), better performance when printed on curved surfaces, and established use in transportation ticketing. The TAP TSI standard's choice of Aztec codes for railway tickets validates this selection for similar use cases.

### matrix.to URLs in Barcodes

An alternative approach would be to encode matrix.to URLs directly in standard QR codes. This would be simpler but has limitations: matrix.to URLs cannot carry invite tokens, join reasons, or expiry information. The structured binary format proposed here provides richer functionality while remaining compact.

### JSON-Based Data Format

A JSON-based format would be more human-readable and easier to debug. However, JSON encoding is significantly less space-efficient than binary TLV encoding, which matters when barcode capacity is limited. The binary format also aligns with TAP TSI conventions.

## Security Considerations

### Invite Token Exposure

Tickets containing invite tokens for private rooms represent bearer credentials. Anyone who obtains the ticket (physically or through a photograph) can potentially join the room. Mitigations include:
- Using single-use tokens where the server invalidates the token after first use
- Setting short expiry times on tickets
- Using the ticket ID field to enable server-side revocation
- For high-security rooms, requiring additional authentication after scanning

### Signature Trust

The optional signature mechanism requires clients to maintain a list of trusted issuer keys. The specification does not define how this trust is established. Implementations might use:
- Room power levels to determine authorized issuers
- Organization-specific key distribution
- Integration with existing Matrix cross-signing infrastructure

Without proper trust establishment, signatures provide limited security value.

### Denial of Service

A malicious ticket could contain a room ID for a room that does not exist or a server that is unresponsive, causing the client to hang while attempting to join. Clients should implement reasonable timeouts and provide clear feedback when room joining fails.

### Privacy Considerations

Tickets may contain personally identifiable information (issuer MXID, display names). Users creating tickets should be aware that this information will be visible to anyone who views the ticket. The room avatar hash field is intentionally truncated to prevent the ticket from serving as a covert channel for arbitrary data.

## Unstable Prefix

No unstable prefix is required for this proposal as it does not introduce new client-server API endpoints or event types. The barcode format is self-contained and identified by its magic bytes.

Implementations experimenting with this specification before it is finalized should use version byte 0x00 to distinguish experimental implementations from the final specification.

## References

- ISO/IEC 24778:2008 - Information technology - Automatic identification and data capture techniques - Aztec Code bar code symbology specification
- TAP TSI TD B.12 - Digital Security Elements for Rail Passenger Ticketing (European Union Agency for Railways)
- TAP TSI TD B.11 - Layout for Electronically Issued Rail Passenger Tickets (European Union Agency for Railways)
- UIC 918-3 - Electronic Ticket Standard for Rail Passenger Transport (International Union of Railways)
- ICAO Doc 9303 - Machine Readable Travel Documents (International Civil Aviation Organization) - for boarding pass dimension compatibility
- Matrix Specification - Room Membership (https://spec.matrix.org/latest/client-server-api/#room-membership)

## Acknowledgements

This proposal builds upon the original MSC3161 draft and incorporates concepts from the TAP TSI railway ticketing standards. The paper size specifications are derived from TCDD (Turkish State Railways) ticket printer specifications.
