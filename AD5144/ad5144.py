# AD5144.py
# Python port of Rob Tillaart's AD5144A C++ library
#    https://github.com/RobTillaart/AD5144A
# Requires smbus2 for I2C communication
# pip install smbus2

from smbus2 import SMBus

# Status codes
AD51XXA_OK = 0
AD51XXA_INVALID_POT = 1
AD51XXA_INVALID_VALUE = 2
AD51XXA_ERROR = 3


class AD51XX:
    def __init__(self, address, bus_id=1):
        self._address = address
        self._bus = SMBus(bus_id)
        self._potCount = 0
        self._maxValue = 255
        self._lastValue = [0] * 4  # max 4 pots

    def begin(self, do_reset=True):
        if not self.is_connected():
            return False
        if do_reset:
            self.reset()
        return True

    def get_address(self):
        return self._address

    def is_connected(self):
        try:
            self._bus.write_quick(self._address)
            return True
        except:
            return False

    def reset(self):
        cmd = 0xB0
        ret_val = self.send(cmd, 0x00)
        if ret_val == AD51XXA_OK:
            for rdac in range(self._potCount):
                self._lastValue[rdac] = self.read_back(rdac, 0x01)
        return ret_val

    # --- READ / WRITE ---
    def read(self, rdac):
        if self._maxValue == 127:
            return self._lastValue[rdac] >> 1
        return self._lastValue[rdac]

    def write(self, rdac, value):
        if rdac >= self._potCount:
            return AD51XXA_INVALID_POT
        if value > self._maxValue:
            return AD51XXA_INVALID_VALUE

        send_value = value << 1 if self._maxValue == 127 else value
        self._lastValue[rdac] = send_value
        cmd = 0x10 | rdac
        return self.send(cmd, send_value)

    def write_all(self, value):
        if value > self._maxValue:
            return AD51XXA_INVALID_VALUE
        send_value = value << 1 if self._maxValue == 127 else value
        for pm in range(self._potCount):
            self._lastValue[pm] = send_value
        return self.send(0x18, send_value)

    def zero_all(self):
        return self.write_all(0)

    def mid_scale_all(self):
        return self.write_all((self._maxValue + 1) // 2)

    def max_all(self):
        return self.write_all(self._maxValue)

    def zero(self, rdac):
        return self.write(rdac, 0)

    def mid_scale(self, rdac):
        return self.write(rdac, (self._maxValue + 1) // 2)

    def max_value(self, rdac):
        return self.write(rdac, self._maxValue)

    # --- EEPROM ---
    def store_eeprom(self, rdac, value=None):
        if rdac >= self._potCount:
            return AD51XXA_INVALID_POT
        if value is None:
            cmd = 0x70 | rdac
            return self.send(cmd, 0x01)
        if value > self._maxValue:
            return AD51XXA_INVALID_VALUE
        send_value = value << 1 if self._maxValue == 127 else value
        cmd = 0x80 | rdac
        return self.send(cmd, send_value)

    def recall_eeprom(self, rdac):
        if rdac >= self._potCount:
            return AD51XXA_INVALID_POT
        self._lastValue[rdac] = self.read_back(rdac, 0x01)
        cmd = 0x70 | rdac
        return self.send(cmd, 0x00)

    # --- SCALE ---
    def set_top_scale(self, rdac):
        if rdac >= self._potCount:
            return AD51XXA_INVALID_POT
        return self.send(0x90 | rdac, 0x81)

    def clr_top_scale(self, rdac):
        if rdac >= self._potCount:
            return AD51XXA_INVALID_POT
        return self.send(0x90 | rdac, 0x80)

    def set_top_scale_all(self):
        return self.send(0x98, 0x81)

    def clr_top_scale_all(self):
        return self.send(0x98, 0x80)

    def set_bottom_scale(self, rdac):
        if rdac >= self._potCount:
            return AD51XXA_INVALID_POT
        return self.send(0x90 | rdac, 0x01)

    def clr_bottom_scale(self, rdac):
        if rdac >= self._potCount:
            return AD51XXA_INVALID_POT
        return self.send(0x90 | rdac, 0x00)

    def set_bottom_scale_all(self):
        return self.send(0x98, 0x01)

    def clr_bottom_scale_all(self):
        return self.send(0x98, 0x00)

    # --- MODE ---
    def set_linear_mode(self, rdac):
        mask = self.read_back(rdac, 0x02)
        return self.send(0xD0, mask | 0x04)

    def set_potentiometer_mode(self, rdac):
        mask = self.read_back(rdac, 0x02)
        return self.send(0xD0, mask & ~0x04)

    def get_operational_mode(self, rdac):
        mask = self.read_back(rdac, 0x02)
        return (mask & 0x04) > 0

    # --- INCREMENT / DECREMENT ---
    def increment_linear(self, rdac):
        if rdac >= self._potCount:
            return AD51XXA_INVALID_POT
        return self.send(0x40 | rdac, 0x01)

    def increment_linear_all(self):
        return self.send(0x48, 0x01)

    def decrement_linear(self, rdac):
        if rdac >= self._potCount:
            return AD51XXA_INVALID_POT
        return self.send(0x40 | rdac, 0x00)

    def decrement_linear_all(self):
        return self.send(0x48, 0x00)

    def increment_6db(self, rdac):
        if rdac >= self._potCount:
            return AD51XXA_INVALID_POT
        return self.send(0x50 | rdac, 0x01)

    def increment_6db_all(self):
        return self.send(0x58, 0x01)

    def decrement_6db(self, rdac):
        if rdac >= self._potCount:
            return AD51XXA_INVALID_POT
        return self.send(0x50 | rdac, 0x00)

    def decrement_6db_all(self):
        return self.send(0x58, 0x00)

    # --- PRELOAD / SYNC ---
    def preload(self, rdac, value):
        if rdac >= self._potCount:
            return AD51XXA_INVALID_POT
        if value > self._maxValue:
            return AD51XXA_INVALID_VALUE
        send_value = value << 1 if self._maxValue == 127 else value
        return self.send(0x20 | rdac, send_value)

    def preload_all(self, value):
        if value > self._maxValue:
            return AD51XXA_INVALID_VALUE
        send_value = value << 1 if self._maxValue == 127 else value
        return self.send(0x28, send_value)

    def sync(self, mask):
        if mask > 0x0F:
            return AD51XXA_ERROR
        ret_val = self.send(0x60 | mask, 0x00)
        if ret_val == AD51XXA_OK:
            m = 0x01
            for rdac in range(self._potCount):
                if mask & m:
                    self._lastValue[rdac] = self.read_back(rdac, 0x03)
                m <<= 1
        return ret_val

    # --- MISC ---
    def pm_count(self):
        return self._potCount

    def max_value(self):
        return self._maxValue

    def shutdown(self):
        return self.send(0xC8, 0x01)

    def read_back_input(self, rdac):
        value = self.read_back(rdac, 0x00)
        return value >> 1 if self._maxValue == 127 else value

    def read_back_eeprom(self, rdac):
        value = self.read_back(rdac, 0x01)
        return value >> 1 if self._maxValue == 127 else value

    def read_back_control(self, rdac):
        return self.read_back(rdac, 0x02)

    def read_back_rdac(self, rdac):
        value = self.read_back(rdac, 0x03)
        return value >> 1 if self._maxValue == 127 else value

    def write_control_register(self, mask):
        return self.send(0xD0, mask)

    # --- Internal I2C ---
    def send(self, cmd, value):
        try:
            self._bus.write_i2c_block_data(self._address, cmd, [value])
            return AD51XXA_OK
        except:
            return AD51XXA_ERROR

    def read_back(self, rdac, mask):
        try:
            self._bus.write_i2c_block_data(self._address, 0x30 | rdac, [mask])
            data = self._bus.read_i2c_block_data(self._address, 0, 1)
            return data[0]
        except:
            return 0


# --- Derived classes ---
class AD5123(AD51XX):
    def __init__(self, address, bus_id=1):
        super().__init__(address, bus_id)
        self._potCount = 4
        self._maxValue = 127


class AD5124(AD51XX):
    def __init__(self, address, bus_id=1):
        super().__init__(address, bus_id)
        self._potCount = 4
        self._maxValue = 127


class AD5143(AD51XX):
    def __init__(self, address, bus_id=1):
        super().__init__(address, bus_id)
        self._potCount = 4
        self._maxValue = 255


class AD5144(AD51XX):
    def __init__(self, address, bus_id=1):
        super().__init__(address, bus_id)
        self._potCount = 4
        self._maxValue = 255


class AD5144A(AD51XX):
    def __init__(self, address, bus_id=1):
        super().__init__(address, bus_id)
        self._potCount = 4
        self._maxValue = 255


class AD5122A(AD51XX):
    def __init__(self, address, bus_id=1):
        super().__init__(address, bus_id)
        self._potCount = 2
        self._maxValue = 127


class AD5142A(AD51XX):
    def __init__(self, address, bus_id=1):
        super().__init__(address, bus_id)
        self._potCount = 2
        self._maxValue = 255


class AD5121(AD51XX):
    def __init__(self, address, bus_id=1):
        super().__init__(address, bus_id)
        self._potCount = 1
        self._maxValue = 127


class AD5141(AD51XX):
    def __init__(self, address, bus_id=1):
        super().__init__(address, bus_id)
        self._potCount = 1
        self._maxValue = 255
