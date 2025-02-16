# $Id: dtp.py 23 2006-11-08 15:45:33Z dugsong $
# -*- coding: utf-8 -*-
"""Dynamic Trunking Protocol."""
from __future__ import absolute_import
import struct

from . import dpkt

TRUNK_NAME = 0x01
MAC_ADDR = 0x04


class DTP(dpkt.Packet):
    """Dynamic Trunking Protocol.

    TODO: Longer class information....

    Attributes:
        __hdr__: Header fields of DTP.
        TODO.
    """

    __hdr__ = (
        ('v', 'B', 0),
    )  # rest is TLVs

    def unpack(self, buf):
        dpkt.Packet.unpack(self, buf)
        buf = self.data
        tvs = []
        while buf:
            t, l_ = struct.unpack('>HH', buf[:4])
            v, buf = buf[4:4 + l_], buf[4 + l_:]
            tvs.append((t, v))
        self.data = tvs

    def __bytes__(self):
        return b''.join([struct.pack('>HH', t, len(v)) + v for t, v in self.data])
