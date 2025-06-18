"""Library implementing a fake NASA device by starting a telnet server and sending raw bytes."""

import binascii
import logging
import socket
import threading
import time

from ..pysamsungnasa.protocol.enum import OutdoorOperationStatus, DhwOpMode, InOperationMode
from ..pysamsungnasa.helpers import hex2bin, bin2hex
from .messages import MESSAGES

_LOGGER = logging.getLogger(__name__)


class FakeNasa:
    """Fake NASA device."""

    _fake_model = "FAKE_MODEL_V1"
    _fake_serial = "FAKE_SERIAL_1234567890"

    def __init__(self, host="127.0.0.1", port=7000):
        """Initialize the fake NASA device."""
        self._host = host
        self._port = port
        self._server_socket = None
        self._client_socket = None
        self._server_thread = None
        self._messaging_thread = None
        self._running = False
        self._packet_number_counter = 0
        self._water_heater_power_state = 0
        self._water_heater_mode = DhwOpMode.STANDARD

    @property
    def _outdoor_operation_state(self) -> OutdoorOperationStatus:
        """Get the current outdoor unit operation state."""
        if self._water_heater_power_state == 0:
            return OutdoorOperationStatus.OP_STOP
        if self._water_heater_power_state == 1:
            return OutdoorOperationStatus.OP_NORMAL
        else:
            return OutdoorOperationStatus.OP_SAFETY

    def start(self):
        """Start the fake NASA device."""
        if self._running:
            _LOGGER.warning("Fake NASA server is already running.")
            return
        self._running = True
        self._server_thread = threading.Thread(target=self._run_server)
        self._messaging_thread = threading.Thread(target=self._messaging_loop)
        self._messaging_thread.daemon = True
        self._server_thread.daemon = True
        self._server_thread.start()
        self._messaging_thread.start()
        _LOGGER.info("Fake NASA server started on %s:%s", self._host, self._port)

    def stop(self):
        """Stop the fake NASA device."""
        if not self._running:
            _LOGGER.warning("Fake NASA server is not running.")
            return

        self._running = False
        if self._client_socket:
            try:
                self._client_socket.close()
            except OSError:
                pass
            self._client_socket = None
        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass
            self._server_socket = None
        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=1)
        _LOGGER.info("Fake NASA server stopped.")

    def _messaging_loop(self):
        """Loop to send fake messages to the client."""
        while self._running:
            time.sleep(1)  # Wait before sending the next message
            if not self._running:
                break
            if self._client_socket:
                try:
                    # Increment and prepare packet number (1 byte)
                    for msg in MESSAGES:
                        if "4065" in msg:
                            self._water_heater_power_state = 1 - self._water_heater_power_state  # Toggle 0 and 1
                            current_payload_hex = f"{self._water_heater_power_state:02x}"
                        elif "4066" in msg:
                            current_payload_hex = f"{self._water_heater_mode.value:02x}"
                        elif "8001" in msg:
                            current_payload_hex = f"{self._outdoor_operation_state.value:02x}"
                        elif "4001" in msg:
                            current_payload_hex = f"{InOperationMode.COOL.value:02x}"
                        elif "061a" in msg:
                            # STR_AD_PRODUCT_MODEL_NAME message
                            model_name_hex = self._fake_model.encode("utf-8").hex().upper()
                            current_payload_hex = model_name_hex
                        else:
                            continue
                        self._packet_number_counter = (self._packet_number_counter + 1) % 256
                        current_packet_num_hex = f"{self._packet_number_counter:02x}"
                        data_for_crc_hex = msg.format(
                            CUR_PACK_NUM=current_packet_num_hex,
                            PAYLOAD_HEX=current_payload_hex,
                        )
                        data_bytes = hex2bin(data_for_crc_hex)
                        packet_size = len(data_bytes) + 4
                        packet_size_hex = f"{packet_size:04x}"
                        crc_val = binascii.crc_hqx(data_bytes, 0)
                        crc_hex = f"{crc_val:04x}"
                        full_packet_hex = (
                            f"32{packet_size_hex}{data_for_crc_hex}{crc_hex}34"  # STX, Size(17=0x11), Data, CRC, ETX
                        )
                        message = hex2bin(full_packet_hex)
                        self._client_socket.sendall(message)
                        _LOGGER.debug("Sent message: %s", full_packet_hex)
                except (BrokenPipeError, ConnectionResetError):
                    _LOGGER.warning("Client disconnected, stopping messaging loop.")
                    self._client_socket = None
        _LOGGER.info("Messaging loop stopped.")

    def _run_server(self):
        """Run the telnet server."""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._server_socket.bind((self._host, self._port))
            self._server_socket.listen(1)
            while self._running:
                try:
                    self._client_socket, _ = self._server_socket.accept()
                    _LOGGER.info("Fake NASA client connected.")
                    while self._running:
                        try:
                            data = self._client_socket.recv(1024)
                            if not data:
                                break
                            _LOGGER.info("Received data: %s", bin2hex(data))
                        except ConnectionResetError:
                            break
                        except Exception as e:
                            _LOGGER.error("Error receiving data: %s", e)
                            break
                except Exception as e:
                    _LOGGER.error("Error accepting connection: %s", e)
                    break
        except Exception as e:
            _LOGGER.error("Error starting server: %s", e)
        finally:
            if self._server_socket:
                self._server_socket.close()
            self._server_socket = None
            if self._client_socket:
                self._client_socket.close()
            self._client_socket = None
            self._running = False
            _LOGGER.info("Fake NASA server stopped.")
