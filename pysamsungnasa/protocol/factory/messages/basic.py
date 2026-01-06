"""Standard parsers available to all device types."""

from ..types import StructureMessage


class SerialNumber(StructureMessage):
    """Parser for message 0x0607 (Serial Number).

    This is a string structure message containing the device serial number.
    Type: STR (String structure)

    IMPORTANT: This structure returns INCOMPLETE data via submessages:
    - 0x0730: Manufacturer/model prefix (e.g., "TYXP")
    - 0x4654: Serial number suffix (e.g., "900834F")

    Known device example:
    Physical label: "0TYXPAFT900834F"
    """

    MESSAGE_ID = 0x0607
    MESSAGE_NAME = "Serial Number"

    @classmethod
    def parse_payload(cls, payload: bytes) -> "SerialNumber":
        """Parse the payload into a string."""
        # Convert the payload bytes to ASCII string, stripping null bytes
        ascii_string = payload.decode("ascii").rstrip("\x00")
        return cls(value=ascii_string, raw_payload=payload)


class DbCodeMiComMainMessage(StructureMessage):
    """Parser for message 0x0608 (DB Code MiCom Main Message).

    This is a structure message containing the microcontroller database code.
    Type: STRUCT (Structure message)

    Structure:
    - Bytes 0-1: Series and variant code (e.g., 0x91 0x02 = DB91-02)
    - Bytes 2-3: Model code variant (e.g., 0x09 0x1b)
    - Bytes 4-6: Date in YYMMDD format (e.g., 0x22 0x08 0x02 = 2022-08-02)
    - Bytes 7-9: Additional identifier (e.g., time or build number)

    Examples:
    - Outdoor: 9102091b220802000000 = DB91-02, date 2022-08-02
    - Indoor: 9102103b220614090909 = DB91-02, date 2022-06-14, time 09:09:09
    """

    MESSAGE_ID = 0x0608
    MESSAGE_NAME = "DB Code MiCom Main Message"

    @classmethod
    def parse_payload(cls, payload: bytes) -> "DbCodeMiComMainMessage":
        """Parse the payload into structured DB code information."""
        if len(payload) < 10:
            return cls(value=payload.hex() if payload else None)

        try:
            # Helper to decode BCD (Binary Coded Decimal)
            def bcd_decode(byte_val):
                return (byte_val >> 4) * 10 + (byte_val & 0x0F)

            # Series and variant code
            series_code = f"DB{payload[0]:02X}-{payload[1]:02X}"
            model_variant = f"{payload[2]:02X}{payload[3]:02X}"

            # Date from nibbles: year (BCD) + month (nibble sum) + day (cross-byte)
            year = 2000 + bcd_decode(payload[4])
            month = (payload[6] & 0x0F) + ((payload[6] >> 4) & 0x0F)
            day = ((payload[6] & 0xF0) >> 4) * 10 + (payload[5] & 0x0F)
            date_str = f"{year:04d}.{month:02d}.{day:02d}"

            # Time from BCD
            time_str = f"{bcd_decode(payload[7]):02d}{bcd_decode(payload[8]):02d}{bcd_decode(payload[9]):02d}"

            return cls(value=f"{series_code} ({model_variant}) {date_str} {time_str}", raw_payload=payload)
        except (IndexError, ValueError):
            return cls(value=payload.hex() if payload else None, raw_payload=payload)


class ProductModelName(StructureMessage):
    """Parser for message 0x061A (Product Model Name).

    This is a structure message containing the product model name.
    Type: STR (String structure)

    Structure:
    - Byte 0: Type/variant identifier (e.g., 0x09, 0x11)
    - Bytes 1+: Null-terminated ASCII string with model name

    Examples:
    - 09454853204d4f4e4f00 = type 0x09, "EHS MONO"
    - 11454853204D4F4E4F204C4F5754454D5000 = type 0x11, "EHS MONO LOWTEMP"
    """

    MESSAGE_ID = 0x061A
    MESSAGE_NAME = "Product Model Name"

    @classmethod
    def parse_payload(cls, payload: bytes) -> "ProductModelName":
        """Parse the payload into a model name string."""
        if not payload or len(payload) < 2:
            return cls(value=payload.hex() if payload else None)

        try:
            # First byte is type/variant identifier
            type_id = payload[0]

            # Remaining bytes are null-terminated ASCII string
            model_name = payload[1:].rstrip(b"\x00").decode("ascii")

            return cls(
                value={
                    "type_id": type_id,
                    "model_name": model_name,
                    "formatted": f"{model_name} (type: 0x{type_id:02X})",
                },
                raw_payload=payload,
            )
        except (UnicodeDecodeError, IndexError):
            # Fallback to hex if decoding fails
            return cls(value=payload.hex() if payload else None, raw_payload=payload)
