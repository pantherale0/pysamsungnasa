"""Tests for device controllers."""

import pytest
from unittest.mock import Mock, AsyncMock
from pysamsungnasa.device.controllers import (
    DhwController,
    ClimateController,
    WaterLawMode,
    ControllerBase,
)
from pysamsungnasa.protocol.enum import (
    DataType,
    DhwOpMode,
    InOperationMode,
    InFsv2041WaterLawTypeHeating,
    InFsv2081WaterLawTypeCooling,
    InUseThermostat,
)


class TestWaterLawMode:
    """Tests for WaterLawMode enum."""

    def test_water_law_mode_values(self):
        """Test WaterLawMode enum values."""
        assert WaterLawMode.WATER_TARGET.value == "water_target"
        assert WaterLawMode.WATER_LAW_EXTERNAL_THERMOSTAT.value == "water_law_ext_thermo"
        assert WaterLawMode.WATER_LAW_INTERNAL_THERMOSTAT.value == "water_law_int_thermo"


class TestControllerBase:
    """Tests for ControllerBase class."""

    def test_controller_base_initialization(self):
        """Test ControllerBase initialization."""
        message_sender = Mock()
        controller = ControllerBase(address="200001", message_sender=message_sender)

        assert controller.address == "200001"
        assert controller.message_sender == message_sender
        assert controller.power is None

    def test_controller_base_with_power(self):
        """Test ControllerBase with power parameter."""
        message_sender = Mock()
        controller = ControllerBase(address="200001", message_sender=message_sender, power=True)

        assert controller.power is True


class TestDhwController:
    """Tests for DhwController class."""

    @pytest.fixture
    def setup_dhw(self):
        """Setup DHW controller with mock message sender."""
        message_sender = AsyncMock()
        controller = DhwController(address="200001", message_sender=message_sender)
        return controller, message_sender

    def test_dhw_controller_initialization(self, setup_dhw):
        """Test DhwController initialization."""
        controller, _ = setup_dhw

        assert controller.address == "200001"
        assert controller.operation_mode is None
        assert controller.target_temperature is None
        assert controller.current_temperature is None
        assert controller.power is None

    @pytest.mark.asyncio
    async def test_dhw_turn_on(self, setup_dhw):
        """Test turning on DHW."""
        controller, message_sender = setup_dhw

        await controller.turn_on()

        assert controller.power is True
        message_sender.assert_called_once()
        call_kwargs = message_sender.call_args[1]
        assert call_kwargs["destination"] == "200001"
        assert call_kwargs["request_type"] == DataType.REQUEST
        # Should have 1 message (power on)
        assert len(call_kwargs["messages"]) == 1

    @pytest.mark.asyncio
    async def test_dhw_turn_on_with_operation_mode(self, setup_dhw):
        """Test turning on DHW when operation_mode is set."""
        controller, message_sender = setup_dhw
        controller.operation_mode = DhwOpMode.POWER

        await controller.turn_on()

        assert controller.power is True
        message_sender.assert_called_once()
        call_kwargs = message_sender.call_args[1]
        # Should have 2 messages (operation mode + power on)
        assert len(call_kwargs["messages"]) == 2

    @pytest.mark.asyncio
    async def test_dhw_turn_on_without_operation_mode(self, setup_dhw):
        """Test turning on DHW when operation_mode is None."""
        controller, message_sender = setup_dhw
        controller.operation_mode = None

        await controller.turn_on()

        assert controller.power is True
        message_sender.assert_called_once()
        call_kwargs = message_sender.call_args[1]
        # Should have 1 message (power on) when operation_mode is None
        assert len(call_kwargs["messages"]) == 1
        assert call_kwargs["destination"] == "200001"
        assert call_kwargs["request_type"] == DataType.REQUEST

    @pytest.mark.asyncio
    async def test_dhw_turn_off(self, setup_dhw):
        """Test turning off DHW."""
        controller, message_sender = setup_dhw

        await controller.turn_off()

        assert controller.power is False
        message_sender.assert_called_once()
        call_kwargs = message_sender.call_args[1]
        assert call_kwargs["destination"] == "200001"
        assert call_kwargs["request_type"] == DataType.REQUEST

    @pytest.mark.asyncio
    async def test_dhw_set_target_temperature(self, setup_dhw):
        """Test setting DHW target temperature."""
        controller, message_sender = setup_dhw

        await controller.set_target_temperature(50.0)

        assert controller.target_temperature == 50.0
        message_sender.assert_called_once()
        call_kwargs = message_sender.call_args[1]
        assert call_kwargs["destination"] == "200001"

    @pytest.mark.asyncio
    async def test_dhw_set_operation_mode(self, setup_dhw):
        """Test setting DHW operation mode."""
        controller, message_sender = setup_dhw

        controller.operation_mode = DhwOpMode.ECO
        await controller.set_operation_mode(DhwOpMode.POWER)

        assert controller.operation_mode == DhwOpMode.POWER


class TestClimateController:
    """Tests for ClimateController class."""

    @pytest.fixture
    def setup_climate(self):
        """Setup climate controller with mock message sender."""
        message_sender = AsyncMock()
        controller = ClimateController(address="200001", message_sender=message_sender)
        return controller, message_sender

    def test_climate_controller_initialization(self, setup_climate):
        """Test ClimateController initialization."""
        controller, _ = setup_climate

        assert controller.address == "200001"
        assert controller.current_mode is None
        assert controller.current_temperature is None
        assert controller.target_temperature is None
        assert controller.water_law_mode is None
        assert controller.power is None

    def test_climate_controller_water_law_mode_default(self, setup_climate):
        """Test ClimateController water law mode default."""
        controller, _ = setup_climate

        # Water law mode can be None initially
        assert controller.water_law_mode is None

    @pytest.mark.asyncio
    async def test_climate_turn_on(self, setup_climate):
        """Test turning on climate."""
        controller, message_sender = setup_climate

        await controller.turn_on()

        assert controller.power is True
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_turn_off(self, setup_climate):
        """Test turning off climate."""
        controller, message_sender = setup_climate

        await controller.turn_off()

        assert controller.power is False
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_set_mode(self, setup_climate):
        """Test setting climate mode."""
        controller, message_sender = setup_climate

        await controller.set_mode(InOperationMode.COOL)

        assert controller.current_mode == InOperationMode.COOL
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_set_water_law_mode(self, setup_climate):
        """Test setting water law mode."""
        controller, _ = setup_climate

        await controller.set_water_law_mode(WaterLawMode.WATER_TARGET)

        assert controller.water_law_mode == WaterLawMode.WATER_TARGET

    @pytest.mark.asyncio
    async def test_climate_set_water_law_type_heating(self, setup_climate):
        """Test setting water law type for heating."""
        controller, message_sender = setup_climate

        await controller.set_water_law_type(heating_type=InFsv2041WaterLawTypeHeating.FLOOR)

        assert controller.heating_water_law_type == InFsv2041WaterLawTypeHeating.FLOOR
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_set_water_law_type_cooling(self, setup_climate):
        """Test setting water law type for cooling."""
        controller, message_sender = setup_climate

        await controller.set_water_law_type(cooling_type=InFsv2081WaterLawTypeCooling.FCU)

        assert controller.cooling_water_law_type == InFsv2081WaterLawTypeCooling.FCU
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_set_water_law_type_both(self, setup_climate):
        """Test setting water law type for both heating and cooling."""
        controller, message_sender = setup_climate

        await controller.set_water_law_type(
            heating_type=InFsv2041WaterLawTypeHeating.FLOOR,
            cooling_type=InFsv2081WaterLawTypeCooling.FCU,
        )

        assert controller.heating_water_law_type == InFsv2041WaterLawTypeHeating.FLOOR
        assert controller.cooling_water_law_type == InFsv2081WaterLawTypeCooling.FCU
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_set_external_thermostat_1(self, setup_climate):
        """Test setting external thermostat 1."""
        controller, message_sender = setup_climate

        await controller.set_external_thermostat(1, InUseThermostat.VALUE_1)

        assert controller.use_external_thermostat_1 == InUseThermostat.VALUE_1
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_set_external_thermostat_2(self, setup_climate):
        """Test setting external thermostat 2."""
        controller, message_sender = setup_climate

        await controller.set_external_thermostat(2, InUseThermostat.VALUE_2)

        assert controller.use_external_thermostat_2 == InUseThermostat.VALUE_2
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_set_external_thermostat_invalid_index(self, setup_climate):
        """Test setting external thermostat with invalid index raises error."""
        controller, _ = setup_climate

        with pytest.raises(ValueError, match="Thermostat index must be 1 or 2"):
            await controller.set_external_thermostat(3, InUseThermostat.VALUE_1)

    @pytest.mark.asyncio
    async def test_climate_set_target_temperature_cool_mode(self, setup_climate):
        """Test setting target temperature in COOL mode."""
        controller, message_sender = setup_climate
        controller.current_mode = InOperationMode.COOL

        await controller.set_target_temperature(22.0)

        assert controller.water_outlet_target_temperature == 22.0
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_set_target_temperature_heat_mode(self, setup_climate):
        """Test setting target temperature in HEAT mode."""
        controller, message_sender = setup_climate
        controller.current_mode = InOperationMode.HEAT

        await controller.set_target_temperature(25.0)

        assert controller.water_outlet_target_temperature == 25.0
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_set_target_temperature_auto_water_target(self, setup_climate):
        """Test setting target temperature in AUTO mode with WATER_TARGET."""
        controller, message_sender = setup_climate
        controller.current_mode = InOperationMode.AUTO
        controller.water_law_mode = WaterLawMode.WATER_TARGET

        await controller.set_target_temperature(23.0)

        assert controller.water_target_temperature_setpoint == 23.0
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_set_target_temperature_auto_external_thermostat(self, setup_climate):
        """Test setting target temperature in AUTO mode with EXTERNAL_THERMOSTAT."""
        controller, message_sender = setup_climate
        controller.current_mode = InOperationMode.AUTO
        controller.water_law_mode = WaterLawMode.WATER_LAW_EXTERNAL_THERMOSTAT

        await controller.set_target_temperature(24.0)

        assert controller.external_thermostat_setpoint == 24.0
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_set_target_temperature_auto_internal_thermostat(self, setup_climate):
        """Test setting target temperature in AUTO mode with INTERNAL_THERMOSTAT."""
        controller, message_sender = setup_climate
        controller.current_mode = InOperationMode.AUTO
        controller.water_law_mode = WaterLawMode.WATER_LAW_INTERNAL_THERMOSTAT

        await controller.set_target_temperature(21.0)

        assert controller.room_temperature_setpoint == 21.0
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_set_target_temperature_auto_no_water_law(self, setup_climate):
        """Test setting target temperature in AUTO mode without water law mode."""
        controller, message_sender = setup_climate
        controller.current_mode = InOperationMode.AUTO
        controller.water_law_mode = None

        await controller.set_target_temperature(20.0)

        assert controller.target_temperature == 20.0
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_climate_send_zone_1_temperature(self, setup_climate):
        """Test sending zone 1 temperature."""
        controller, message_sender = setup_climate

        await controller.send_zone_1_temperature(25.0)

        message_sender.assert_called_once()
        call_kwargs = message_sender.call_args[1]
        assert call_kwargs["destination"] == "B0FF00"
        assert call_kwargs["request_type"] == DataType.NOTIFICATION

    @pytest.mark.asyncio
    async def test_climate_send_zone_2_temperature(self, setup_climate):
        """Test sending zone 2 temperature."""
        controller, message_sender = setup_climate

        await controller.send_zone_2_temperature(26.0)

        message_sender.assert_called_once()
        call_kwargs = message_sender.call_args[1]
        assert call_kwargs["destination"] == "B0FF00"
        assert call_kwargs["request_type"] == DataType.NOTIFICATION

    def test_f_target_temperature_cool_mode(self, setup_climate):
        """Test computed target temperature in COOL mode."""
        controller, _ = setup_climate
        controller.current_mode = InOperationMode.COOL
        controller.water_outlet_target_temperature = 22.0
        controller.target_temperature = 25.0

        assert controller.f_target_temperature == 22.0

    def test_f_target_temperature_heat_mode(self, setup_climate):
        """Test computed target temperature in HEAT mode."""
        controller, _ = setup_climate
        controller.current_mode = InOperationMode.HEAT
        controller.water_outlet_target_temperature = 45.0

        assert controller.f_target_temperature == 45.0

    def test_f_target_temperature_auto_internal(self, setup_climate):
        """Test computed target temperature in AUTO with INTERNAL_THERMOSTAT."""
        controller, _ = setup_climate
        controller.current_mode = InOperationMode.AUTO
        controller.water_law_mode = WaterLawMode.WATER_LAW_INTERNAL_THERMOSTAT
        controller.target_temperature = 21.0

        assert controller.f_target_temperature == 21.0

    def test_f_target_temperature_auto_external(self, setup_climate):
        """Test computed target temperature in AUTO with EXTERNAL_THERMOSTAT."""
        controller, _ = setup_climate
        controller.current_mode = InOperationMode.AUTO
        controller.water_law_mode = WaterLawMode.WATER_LAW_EXTERNAL_THERMOSTAT
        controller.water_law_target_temperature = 20.0

        assert controller.f_target_temperature == 20.0

    def test_f_target_temperature_none(self, setup_climate):
        """Test computed target temperature when no mode is set."""
        controller, _ = setup_climate
        controller.current_mode = None

        assert controller.f_target_temperature is None

    def test_f_current_temperature_auto_mode(self, setup_climate):
        """Test computed current temperature in AUTO mode."""
        controller, _ = setup_climate
        controller.current_mode = InOperationMode.AUTO
        controller.current_temperature = 22.5

        assert controller.f_current_temperature == 22.5

    def test_f_current_temperature_cool_mode(self, setup_climate):
        """Test computed current temperature in COOL mode."""
        controller, _ = setup_climate
        controller.current_mode = InOperationMode.COOL
        controller.water_outlet_current_temperature = 23.0

        assert controller.f_current_temperature == 23.0

    def test_f_current_temperature_heat_mode(self, setup_climate):
        """Test computed current temperature in HEAT mode."""
        controller, _ = setup_climate
        controller.current_mode = InOperationMode.HEAT
        controller.water_outlet_current_temperature = 28.5

        assert controller.f_current_temperature == 28.5

    def test_f_current_temperature_none(self, setup_climate):
        """Test computed current temperature when no mode is set."""
        controller, _ = setup_climate
        controller.current_mode = None

        assert controller.f_current_temperature is None


class TestClimateControllerSetTargetTemperatureEdgeCases:
    """Additional tests for climate controller edge cases."""

    @pytest.fixture
    def setup_climate(self):
        """Setup climate controller with mock message sender."""
        message_sender = AsyncMock()
        controller = ClimateController(address="200001", message_sender=message_sender)
        return controller, message_sender

    @pytest.mark.asyncio
    async def test_set_target_temperature_auto_water_target_no_setpoint(self, setup_climate):
        """Test set_target_temperature in AUTO mode with WATER_TARGET but no setpoint."""
        controller, message_sender = setup_climate
        controller.current_mode = InOperationMode.AUTO
        controller.water_law_mode = WaterLawMode.WATER_TARGET
        # No water_target_temperature_setpoint set

        await controller.set_target_temperature(25.0)
        assert message_sender.call_count >= 1

    @pytest.mark.asyncio
    async def test_f_target_temperature_auto_water_target_mode(self, setup_climate):
        """Test f_target_temperature in AUTO mode with WATER_TARGET."""
        controller, _ = setup_climate
        controller.current_mode = InOperationMode.AUTO
        controller.water_law_mode = WaterLawMode.WATER_TARGET
        controller.target_temperature = 22.0
        controller.water_law_target_temperature = 45.0
        controller.water_outlet_target_temperature = 50.0

        # In WATER_TARGET mode, should return target_temperature
        assert controller.f_target_temperature == 22.0

    @pytest.mark.asyncio
    async def test_send_zone_temperature_valid_temperature(self, setup_climate):
        """Test send_zone_temperature with valid temperature."""
        controller, message_sender = setup_climate

        # Sending a valid temperature
        await controller.send_zone_1_temperature(22.5)
        # The method should call message_sender
        assert message_sender.called

    @pytest.mark.asyncio
    async def test_set_water_law_type_both_heating_and_cooling(self, setup_climate):
        """Test set_water_law_type with both heating and cooling types."""
        controller, message_sender = setup_climate

        await controller.set_water_law_type(
            heating_type=InFsv2041WaterLawTypeHeating.FLOOR, cooling_type=InFsv2081WaterLawTypeCooling.FCU
        )

        assert controller.heating_water_law_type == InFsv2041WaterLawTypeHeating.FLOOR
        assert controller.cooling_water_law_type == InFsv2081WaterLawTypeCooling.FCU
        message_sender.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_water_law_type_neither_heating_nor_cooling(self, setup_climate):
        """Test set_water_law_type with neither heating nor cooling."""
        controller, message_sender = setup_climate

        await controller.set_water_law_type(heating_type=None, cooling_type=None)

        # message_sender should not be called when no types are provided
        message_sender.assert_not_called()
