# Hex injector

Use to inject data to a hex file.

Read objetive memory 0x64b24, 25 bytes

    python hex_injector.py -r -dir .pio/build/wiscore_rak4631/firmware.hex -addr 0x64b24 -data 25

Write in address 0x64b24.

    python hex_injector.py -dir .pio/build/wiscore_rak4631/firmware.hex -addr 0x64b24 -data 000102030405060708090A0B0C0DAAAAAAAAAAAAAAAAAAAAAAAAAAAABB

Read objetive memory 0x64b24, 25 bytes

    python hex_injector.py -r -dir .pio/build/wiscore_rak4631/firmware.hex -addr 0x64b24 -data 25
