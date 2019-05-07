# Silicon Labs cp2110 Python library

This library provides a Python interface to the [Silicon Labs CP2110](https://www.silabs.com/documents/public/data-sheets/CP2110.pdf) HID USB to UART bridge.

At this point in time this library presents only the parts of the [available API](https://www.silabs.com/documents/public/application-notes/AN434-CP2110-4-Interface-Specification.pdf) that are required for basic UART access.

#  cp2110 Installation

Install via pip: `python -m pip install cp2110`.

The cp2110 library depends on the [pyhidapi](https://github.com/apmorton/pyhidapi) Python module, which itself requires the `hidapi` shared library.  On Linux distributions, this is generally in the repositories (for instance, under Debian you can install either libhidapi-hidraw0 or libhidapi-libusb0 depending on which backend you want to use).

# Example usage

```
  import cp2110
  import time

  # This will raise an exception if a device is not found.  Called with no
  # parameters, this looks for the default (VID, PID) of the CP2110, which are
  # (0x10c4, 0xEA80).
  try:
    d = cp2110.CP2110Device()
  except:
    pass

  # In some cases the device maker will override the VID and/or PID at the
  # factory, so you'll need to pass parameters
  try:
    cp2110.CP2110Device(vid=0xDEAD, pid=0xBEEF)
  except:
    pass

  # You can also find a device by path.
  cp2110.CP2110Device(path='/dev/hidraw0')

  # If you want to avoid the exception or want to detect the presence of a
  # device without creating an object as a side-effect, use the
  # `cp2110.enumerate` function.  This has the same default values as the
  # `CP2110Device` constructor.
  usb_info = cp2110.enumerate()
  if usb_info:
    print(usb_info.as_dict())

  usb_info = cp2110.enumerate(vid=0xDEAD, pid=0xBEEF)
  if usb_info:
    print(usb_info.as_dict())

  # Fetch the current uart configuration.  This is the UART connection from the
  # CP2110 to the microcontroller (or whatever) it's wired up to.
  c = d.get_uart_config()

  # The UART settings are dictated by the device that embeds the CP2110.  It
  # may be configured correctly by default, or you may need to set manually.
  d.set_uart_config(UARTConfig(
    baud=38400,
    parity=cp2110.PARITY.NONE,
    flow_control=cp2110.FLOW_CONTROL.DISABLED,
    data_bits=cp2110.DATA_BITS.EIGHT,
    stop_bits=STOP_BITS.SHORT))

  # If you ever need to disable the UART, you can.
  d.disable_uart()

  # And you can clear any pending data in the on-chip I/O buffers.
  d.purge_fifos()  # The default is cp2110.FIFO.BOTH
  d.purge_fifos(cp2110.FIFO.TX)
  d.purge_fifos(cp2110.FIFO.RX)

  # Check if the UART is enabled.
  print(d.is_uart_enabled())

  # The UART in your device may need to be explicitly enabled, particularly if
  # you've already explicitly disabled it as in this example.
  d.enable_uart()

  # The write method accepts byte strings or arrays of ints.
  d.write(b'hello world')
  d.write([0x01, 0xff])

  # The default read size will return 63 bytes (at most), which is the maximum
  # supported by this chip.  Reads do not block.
  rv = d.read()

```

