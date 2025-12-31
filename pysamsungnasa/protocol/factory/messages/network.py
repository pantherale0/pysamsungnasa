"""Messages from the network layer."""

from ..messaging import EnumMessage, RawMessage

from ...enum import NmNetworkPositionLayer, NmNetworkTrackingState


class NmNetworkPositionLayerMessage(EnumMessage):
    """Parser for message 0x200F (Network Position Layer)."""

    MESSAGE_ID = 0x200F
    MESSAGE_NAME = "Network Position Layer"
    MESSAGE_ENUM = NmNetworkPositionLayer


class NmNetworkTrackingStateMessage(EnumMessage):
    """Parser for message 0x2010 (Network Tracking State)."""

    MESSAGE_ID = 0x2010
    MESSAGE_NAME = "Network Tracking State"
    MESSAGE_ENUM = NmNetworkTrackingState


class NmVariableNm1Message(RawMessage):
    """Parser for message 0x22F7 (Variable NM 1)."""

    MESSAGE_ID = 0x22F7
    MESSAGE_NAME = "Variable NM 1"


class NmVariableNm2Message(RawMessage):
    """Parser for message 0x22F9 (Variable NM 2)."""

    MESSAGE_ID = 0x22F9
    MESSAGE_NAME = "Variable NM 2"


class NmVariableNm3Message(RawMessage):
    """Parser for message 0x22FA (Variable NM 3)."""

    MESSAGE_ID = 0x22FA
    MESSAGE_NAME = "Variable NM 3"


class NmVariableNm4Message(RawMessage):
    """Parser for message 0x22FB (Variable NM 4)."""

    MESSAGE_ID = 0x22FB
    MESSAGE_NAME = "Variable NM 4"


class NmVariableNm5Message(RawMessage):
    """Parser for message 0x22FC (Variable NM 5)."""

    MESSAGE_ID = 0x22FC
    MESSAGE_NAME = "Variable NM 5"


class NmVariableNm6Message(RawMessage):
    """Parser for message 0x22FD (Variable NM 6)."""

    MESSAGE_ID = 0x22FD
    MESSAGE_NAME = "Variable NM 6"


class NmVariableNm7Message(RawMessage):
    """Parser for message 0x22FE (Variable NM 7)."""

    MESSAGE_ID = 0x22FE
    MESSAGE_NAME = "Variable NM 7"


class NmVariableNm8Message(RawMessage):
    """Parser for message 0x22FF (Variable NM 8)."""

    MESSAGE_ID = 0x22FF
    MESSAGE_NAME = "Variable NM 8"


class NmAllLayerDeviceCountMessage(RawMessage):
    """Parser for message 0x2400 (All Layer Device Count)."""

    MESSAGE_ID = 0x2400
    MESSAGE_NAME = "All Layer Device Count"


class NmLayerVariableNm1Message(RawMessage):
    """Parser for message 0x2401 (Layer Variable NM 1)."""

    MESSAGE_ID = 0x2401
    MESSAGE_NAME = "Layer Variable NM 1"


class NmLayerVariableNm2Message(RawMessage):
    """Parser for message 0x24FB (Layer Variable NM 2)."""

    MESSAGE_ID = 0x24FB
    MESSAGE_NAME = "Layer Variable NM 2"
