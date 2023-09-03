# SPDX-FileCopyrightText: 2023 Trevor Beaton for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# MIT License

# Copyright (c) 2023 Trevor Beaton

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import time
import gc
import board
from adafruit_clue import clue
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from plotter import Plotter
from plot_source import TemperaturePlotSource

ble = BLERadio()
uart_server = UARTService()
advertisement = ProvideServicesAdvertisement(uart_server)

ble.start_advertising(advertisement)
# Set desired temperature range in degrees Celsius.
min_temperature = 24
max_temperature = 30

# Set desired humidity range in percent.
min_humidity = 20
max_humidity = 65

# Set to true to enable audible alarm tone.
alarm_enable = False

clue_display = clue.simple_text_display(text_scale=3, colors=(clue.WHITE,))

clue_display[0].text = "Temperature &"
clue_display[1].text = "Humidity"

temp_source = TemperaturePlotSource(clue, mode="Fahrenheit")

# Start the temperature source to prepare for data collection
temp_source.start()

while True:
    # Get the temperature data
    temperature = temp_source.data()

    # Print the temperature
    print(f"Temperature: {temperature}°F")
    gc.collect()
    print("Free memory after collection:", gc.mem_free())
    # Send temperature over BLE UART when connected
    while ble.connected:
        uart_server.write("{}\n".format(temperature))
        time.sleep(10)


    alarm = False

    temperature = clue.temperature
    humidity = clue.humidity

    clue_display[3].text = "Temp: {:.1f} C".format(temperature)
    clue_display[5].text = "Humi: {:.1f} %".format(humidity)

    if temperature < min_temperature:
        clue_display[3].color = clue.BLUE
        alarm = True
    elif temperature > max_temperature:
        clue_display[3].color = clue.RED
        alarm = True
    else:
        clue_display[3].color = clue.WHITE

    if humidity < min_humidity:
        clue_display[5].color = clue.BLUE
        alarm = True
    elif humidity > max_humidity:
        clue_display[5].color = clue.RED
        alarm = True
    else:
        clue_display[5].color = clue.WHITE
    clue_display.show()

    if alarm and alarm_enable:
        clue.start_tone(2000)
    else:
        clue.stop_tone()
