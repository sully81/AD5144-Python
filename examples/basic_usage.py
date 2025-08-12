# test_ad5144a.py
from time import sleep
from AD5144A import AD5144A

# Change to your device's I2C address
I2C_ADDRESS = 0x2C  # Example: check with `i2cdetect -y 1`

# Create device instance
pot = AD5144A(I2C_ADDRESS, bus_id=1)

print("Connecting to AD5144A at address 0x{:02X}...".format(I2C_ADDRESS))
if not pot.begin():
    print("Device not found. Check wiring and address.")
    exit(1)

print("Connected!")
print("Pot count:", pot.pm_count())
print("Max value:", pot.max_value())

# Sweep pot 0 from min to max
print("Sweeping pot 0 from 0 to max...")
for val in range(0, pot.max_value() + 1, 16):
    pot.write(0, val)
    print("Wrote", val)
    sleep(0.05)

# Midscale all
print("Setting all pots to midscale...")
pot.mid_scale_all()
sleep(0.5)

# Max all
print("Setting all pots to max...")
pot.max_all()
sleep(0.5)

# Zero all
print("Zeroing all pots...")
pot.zero_all()

# Read back value
val = pot.read(0)
print("Pot 0 readback value:", val)

print("Test complete.")
