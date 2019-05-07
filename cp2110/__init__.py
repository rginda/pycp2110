# Copyright 2019 Robert Ginda <rginda@gmail.com>
# This code is licensed under MIT license (see LICENSE.md for details)
#

"""
Python driver for the cp2110 UART-HID bridge.

See the [CP2110 Interface Specification](https://www.silabs.com/documents/public/application-notes/AN434-CP2110-4-Interface-Specification.pdf)
for more details
"""

from enum import IntEnum, unique
from ctypes import *

import hid
import logging


# Default Vendor/Product IDs for the CP2110.
CP2110_VID = 0x10c4
CP2110_PID = 0xEA80


# The CP2110 supports up to a 64 byte report size, but we need one of those
# bytes from every packet to store the report id.
RX_TX_MAX = 63


@unique
class REPORT(IntEnum):
  """USB HID Report Ids we make use of.

  There are many others.  Read the interface specification mentioned at the
  top of this file to learn more."""
  GET_SET_UART_ENABLE = 0x41
  PURGE_FIFOS = 0x43
  GET_VERSION_INFO = 0x46
  GET_SET_UART_CONFIG = 0x50


@unique
class FIFO(IntEnum):
  """FIFOs passed in to purge_fifos."""
  TX = 0
  RX = 1
  BOTH = 2


@unique
class PARITY(IntEnum):
  """UARTConfig parity values."""
  NONE = 0
  ODD = 1
  EVEN = 2
  MARK = 3
  SPACE = 4


@unique
class FLOW_CONTROL(IntEnum):
  """UARTConfig flow control values."""
  DISABLED = 0
  ENABLED = 1


@unique
class DATA_BITS(IntEnum):
  """UARTConfig data bits values."""
  FIVE = 0
  SIX = 1
  SEVEN = 2
  EIGHT = 3


@unique
class STOP_BITS(IntEnum):
  """UARTConfig stop bits values."""
  SHORT = 0
  LONG = 1


class UARTConfig(object):
  def __init__(self, baud, parity, flow_control, data_bits,
               stop_bits):
    self.baud = baud
    self.parity = parity
    self.flow_control = flow_control
    self.data_bits = data_bits
    self.stop_bits = stop_bits

  @staticmethod
  def from_feature_report(buf):
    return UARTConfig(
      baud = (buf[1] << (8*3) | buf[2] << (8*2) | buf[3] << 8 | buf[4]),
      parity = PARITY(buf[5]),
      flow_control = FLOW_CONTROL(buf[6]),
      data_bits = DATA_BITS(buf[7]),
      stop_bits = STOP_BITS(buf[8]))

  def to_feature_report(self):
    buf = create_string_buffer(9)

    buf[0] = REPORT.GET_SET_UART_CONFIG
    for i in range(4):
      buf[i + 1] = (0xff & (self.baud >> ((3 - i) * 8)))

    buf[5] = self.parity.value
    buf[6] = self.flow_control.value
    buf[7] = self.data_bits.value
    buf[8] = self.stop_bits.value

    return buf


def enumerate(vid=CP2110_VID, pid=CP2110_PID):
  """Enumerate the CP2110 device, return hid_info struct if found."""
  rv = hid.hidapi.hid_enumerate(vid, pid)
  try:
    rv = rv.contents
  except ValueError:
    rv = None

  return rv


def outbuf(*ary):
  buf = create_string_buffer(len(ary) + 1)
  for i in range(len(ary)):
    buf[i] = ary[i]
  return buf


class DeviceNotFound(Exception):
  pass


class CP2110Device(object):
  def __init__(self, vid=None, pid=None, serial=None, path=None):
    if path:
      self.device = hid.Device(path=path)
    elif serial:
      self.device = hid.Device(serial=serial)
    else:
      if vid is None:
        vid = CP2110_VID

      if pid is None:
        pid = CP2110_PID

      self.device = hid.Device(vid=vid, pid=pid)

    self.device.nonblocking = 1

  def is_uart_enabled(self):
    rv = self.device.get_feature_report(REPORT.GET_SET_UART_ENABLE, 2)
    return rv[1] == 1

  def enable_uart(self):
    return self.device.send_feature_report(
      outbuf(REPORT.GET_SET_UART_ENABLE, 1))

  def disable_uart(self):
    return self.device.send_feature_report(
      outbuf(REPORT.GET_SET_UART_ENABLE, 0))

  def purge_fifos(self, which_fifo=FIFO.BOTH):
    return self.device.send_feature_report(
      outbuf(REPORT.PURGE_FIFOS, which_fifo))

  def get_version_info(self):
    return self.device.get_feature_report(REPORT.GET_VERSION_INFO, 3)[1:]

  def set_uart_config(self, config):
    return self.device.send_feature_report(config.to_feature_report())

  def get_uart_config(self):
    buf = self.device.get_feature_report(REPORT.GET_SET_UART_CONFIG, 9)
    return UARTConfig.from_feature_report(buf)

  def write(self, data):
    offset = 0
    bytes_left = len(data)
    while bytes_left > 0:
      chunk_size = bytes_left
      if chunk_size > RX_TX_MAX - 1:
        chunk_size = RX_TX_MAX - 1

      # Add one for the length, and one for null termination.
      buf = create_string_buffer(chunk_size + 2)

      # Store the length (including this byte) of this chunk.
      buf[0] = chunk_size + 1

      # And stuff whatever bits from `data` we can fit in the rest.
      buf[1 : 1 + chunk_size] = data[offset : offset + chunk_size]

      self.device.write(buf)

      # Advance the offset/reduce bytes_left by the amount we consumed.
      offset += chunk_size
      bytes_left -= chunk_size

  def read(self, size=None):
    if size is None:
      size = cp2110.RX_TX_MAX + 1

    return self.device.read(size)[1:]
