"""Messages from the network layer."""

from ..messaging import EnumMessage

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
