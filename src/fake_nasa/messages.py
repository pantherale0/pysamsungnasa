"""Fake NASA messages."""

ENUM_OPERATION_MODE = (
    "200000"  # Source Address (Class 20, Chan 00, Addr 00)
    "B0FFFF"  # Destination Address (Class B0, Chan FF, Addr FF)
    "00"  # Packet Info/ProtoVer/Retry
    "14"  # PacketType (1=Normal), DataType (4=Notification)
    "{CUR_PACK_NUM}"  # Packet Number
    "01"  # Capacity (Number of Messages)
    "4001"  # Message Number (ENUM_OPERATION_MODE)
    "{PAYLOAD_HEX}"  # Message Payload
)

ENUM_IN_WATER_HEATER_POWER = (
    "200000"  # Source Address (Class 20, Chan 00, Addr 00)
    "B0FFFF"  # Destination Address (Class B0, Chan FF, Addr FF)
    "00"  # Packet Info/ProtoVer/Retry
    "14"  # PacketType (1=Normal), DataType (4=Notification)
    "{CUR_PACK_NUM}"  # Packet Number
    "01"  # Capacity (Number of Messages)
    "4065"  # Message Number (ENUM_IN_WATER_HEATER_POWER)
    "{PAYLOAD_HEX}"  # Message Payload
)

ENUM_WATER_HEATER_OP_MODE = (
    "200000"  # Source Address (Class 20, Chan 00, Addr 00)
    "B0FFFF"  # Destination Address (Class B0, Chan FF, Addr FF)
    "00"  # Packet Info/ProtoVer/Retry
    "14"  # PacketType (1=Normal), DataType (4=Notification)
    "{CUR_PACK_NUM}"  # Packet Number
    "01"  # Capacity (Number of Messages)
    "4066"  # Message Number (ENUM_WATER_HEATER_OP_MODE)
    "{PAYLOAD_HEX}"  # Message Payload
)

OUT_OPERATION_STATUS = (
    "100000"  # Source Address (Class 10, Chan 00, Addr 00)
    "B0FFFF"  # Destination Address (Class B0, Chan FF, Addr FF)
    "00"  # Packet Info/ProtoVer/Retry
    "14"  # PacketType (1=Normal), DataType (4=Notification)
    "{CUR_PACK_NUM}"  # Packet Number
    "01"  # Capacity (Number of Messages)
    "8001"  # Message Number (OUT_OPERATION_STATUS)
    "{PAYLOAD_HEX}"  # Message Payload
)

STR_AD_PRODUCT_MODEL_NAME = (
    "100000"  # Source Address (Class 10 Outdoor, Chan 00, Addr 00)
    "B0FFFF"  # Destination Address (Class B0, Chan FF, Addr FF - Broadcast-like)
    "00"  # Packet Info/ProtoVer/Retry (PacketInfo=0, ProtoVer=0, RetryCount=0)
    "14"  # PacketType (1=Normal), DataType (4=Notification)
    "{CUR_PACK_NUM}"  # Packet Number (placeholder, filled during sending)
    "01"  # Capacity (Number of Messages, 1 for this structure message)
    "061a"  # Message Number (STR_AD_PRODUCT_MODEL_NAME)
    # Message Payload: Hexadecimal representation of the ASCII model name string.
    # Example: "MY_COOL_MODEL" would be "4D595F434F4F4C5F4D4F44454C"
    # This {PAYLOAD_HEX} will be the actual model name string in hex.
    # The current parser, when it detects a structure type via the message number (0x061a),
    # will treat the message number bytes (061a) plus these payload bytes together
    # as the "structure data" for a synthetic message with ID -1.
    "{PAYLOAD_HEX}"
)

MESSAGES = [
    STR_AD_PRODUCT_MODEL_NAME,
    ENUM_OPERATION_MODE,
    ENUM_IN_WATER_HEATER_POWER,
    ENUM_WATER_HEATER_OP_MODE,
    OUT_OPERATION_STATUS,
]
