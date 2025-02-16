# $Id: ssl.py 90 2014-04-02 22:06:23Z andrewflnr@gmail.com $
# Portion Copyright 2012 Google Inc. All rights reserved.
# -*- coding: utf-8 -*-
"""Secure Sockets Layer / Transport Layer Security."""
from __future__ import absolute_import

import struct
import binascii

from . import dpkt
from . import ssl_ciphersuites
from .compat import compat_ord

#
# Note from April 2011: cde...@gmail.com added code that parses SSL3/TLS messages more in depth.
#
# Jul 2012: afleenor@google.com modified and extended SSL support further.
#


# SSL 2.0 is deprecated in RFC 6176
class SSL2(dpkt.Packet):
    __hdr__ = (
        ('len', 'H', 0),
        ('msg', 's', b''),
        ('pad', 's', b''),
    )

    def unpack(self, buf):
        dpkt.Packet.unpack(self, buf)
        if self.len & 0x8000:
            n = self.len = self.len & 0x7FFF
            self.msg, self.data = self.data[:n], self.data[n:]
        else:
            n = self.len = self.len & 0x3FFF
            padlen = compat_ord(self.data[0])
            self.msg = self.data[1:1 + n]
            self.pad = self.data[1 + n:1 + n + padlen]
            self.data = self.data[1 + n + padlen:]


# SSL 3.0 is deprecated in RFC 7568
# Use class TLS for >= SSL 3.0
class TLS(dpkt.Packet):
    __hdr__ = (
        ('type', 'B', ''),
        ('version', 'H', ''),
        ('len', 'H', ''),
    )

    def __init__(self, *args, **kwargs):
        self.records = []
        dpkt.Packet.__init__(self, *args, **kwargs)

    def unpack(self, buf):
        dpkt.Packet.unpack(self, buf)
        pointer = 0
        while len(self.data[pointer:]) > 0:
            end = pointer + 5 + struct.unpack("!H", buf[pointer + 3:pointer + 5])[0]
            self.records.append(TLSRecord(buf[pointer:end]))
            pointer = end
            self.data = self.data[pointer:]


# SSLv3/TLS versions
SSL3_V = 0x0300
TLS1_V = 0x0301
TLS11_V = 0x0302
TLS12_V = 0x0303

ssl3_versions_str = {
    SSL3_V: 'SSL3',
    TLS1_V: 'TLS 1.0',
    TLS11_V: 'TLS 1.1',
    TLS12_V: 'TLS 1.2'
}

SSL3_VERSION_BYTES = set((b'\x03\x00', b'\x03\x01', b'\x03\x02', b'\x03\x03'))


# Alert levels
SSL3_AD_WARNING = 1
SSL3_AD_FATAL = 2
alert_level_str = {
    SSL3_AD_WARNING: 'SSL3_AD_WARNING',
    SSL3_AD_FATAL: 'SSL3_AD_FATAL'
}

# SSL3 alert descriptions
SSL3_AD_CLOSE_NOTIFY = 0
SSL3_AD_UNEXPECTED_MESSAGE = 10  # fatal
SSL3_AD_BAD_RECORD_MAC = 20  # fatal
SSL3_AD_DECOMPRESSION_FAILURE = 30  # fatal
SSL3_AD_HANDSHAKE_FAILURE = 40  # fatal
SSL3_AD_NO_CERTIFICATE = 41
SSL3_AD_BAD_CERTIFICATE = 42
SSL3_AD_UNSUPPORTED_CERTIFICATE = 43
SSL3_AD_CERTIFICATE_REVOKED = 44
SSL3_AD_CERTIFICATE_EXPIRED = 45
SSL3_AD_CERTIFICATE_UNKNOWN = 46
SSL3_AD_ILLEGAL_PARAMETER = 47  # fatal

# TLS1 alert descriptions
TLS1_AD_DECRYPTION_FAILED = 21
TLS1_AD_RECORD_OVERFLOW = 22
TLS1_AD_UNKNOWN_CA = 48  # fatal
TLS1_AD_ACCESS_DENIED = 49  # fatal
TLS1_AD_DECODE_ERROR = 50  # fatal
TLS1_AD_DECRYPT_ERROR = 51
TLS1_AD_EXPORT_RESTRICTION = 60  # fatal
TLS1_AD_PROTOCOL_VERSION = 70  # fatal
TLS1_AD_INSUFFICIENT_SECURITY = 71  # fatal
TLS1_AD_INTERNAL_ERROR = 80  # fatal
TLS1_AD_USER_CANCELLED = 90
TLS1_AD_NO_RENEGOTIATION = 100
# /* codes 110-114 are from RFC3546 */
TLS1_AD_UNSUPPORTED_EXTENSION = 110
TLS1_AD_CERTIFICATE_UNOBTAINABLE = 111
TLS1_AD_UNRECOGNIZED_NAME = 112
TLS1_AD_BAD_CERTIFICATE_STATUS_RESPONSE = 113
TLS1_AD_BAD_CERTIFICATE_HASH_VALUE = 114
TLS1_AD_UNKNOWN_PSK_IDENTITY = 115  # fatal


# Mapping alert types to strings
alert_description_str = {
    SSL3_AD_CLOSE_NOTIFY: 'SSL3_AD_CLOSE_NOTIFY',
    SSL3_AD_UNEXPECTED_MESSAGE: 'SSL3_AD_UNEXPECTED_MESSAGE',
    SSL3_AD_BAD_RECORD_MAC: 'SSL3_AD_BAD_RECORD_MAC',
    SSL3_AD_DECOMPRESSION_FAILURE: 'SSL3_AD_DECOMPRESSION_FAILURE',
    SSL3_AD_HANDSHAKE_FAILURE: 'SSL3_AD_HANDSHAKE_FAILURE',
    SSL3_AD_NO_CERTIFICATE: 'SSL3_AD_NO_CERTIFICATE',
    SSL3_AD_BAD_CERTIFICATE: 'SSL3_AD_BAD_CERTIFICATE',
    SSL3_AD_UNSUPPORTED_CERTIFICATE: 'SSL3_AD_UNSUPPORTED_CERTIFICATE',
    SSL3_AD_CERTIFICATE_REVOKED: 'SSL3_AD_CERTIFICATE_REVOKED',
    SSL3_AD_CERTIFICATE_EXPIRED: 'SSL3_AD_CERTIFICATE_EXPIRED',
    SSL3_AD_CERTIFICATE_UNKNOWN: 'SSL3_AD_CERTIFICATE_UNKNOWN',
    SSL3_AD_ILLEGAL_PARAMETER: 'SSL3_AD_ILLEGAL_PARAMETER',
    TLS1_AD_DECRYPTION_FAILED: 'TLS1_AD_DECRYPTION_FAILED',
    TLS1_AD_RECORD_OVERFLOW: 'TLS1_AD_RECORD_OVERFLOW',
    TLS1_AD_UNKNOWN_CA: 'TLS1_AD_UNKNOWN_CA',
    TLS1_AD_ACCESS_DENIED: 'TLS1_AD_ACCESS_DENIED',
    TLS1_AD_DECODE_ERROR: 'TLS1_AD_DECODE_ERROR',
    TLS1_AD_DECRYPT_ERROR: 'TLS1_AD_DECRYPT_ERROR',
    TLS1_AD_EXPORT_RESTRICTION: 'TLS1_AD_EXPORT_RESTRICTION',
    TLS1_AD_PROTOCOL_VERSION: 'TLS1_AD_PROTOCOL_VERSION',
    TLS1_AD_INSUFFICIENT_SECURITY: 'TLS1_AD_INSUFFICIENT_SECURITY',
    TLS1_AD_INTERNAL_ERROR: 'TLS1_AD_INTERNAL_ERROR',
    TLS1_AD_USER_CANCELLED: 'TLS1_AD_USER_CANCELLED',
    TLS1_AD_NO_RENEGOTIATION: 'TLS1_AD_NO_RENEGOTIATION',
    TLS1_AD_UNSUPPORTED_EXTENSION: 'TLS1_AD_UNSUPPORTED_EXTENSION',
    TLS1_AD_CERTIFICATE_UNOBTAINABLE: 'TLS1_AD_CERTIFICATE_UNOBTAINABLE',
    TLS1_AD_UNRECOGNIZED_NAME: 'TLS1_AD_UNRECOGNIZED_NAME',
    TLS1_AD_BAD_CERTIFICATE_STATUS_RESPONSE: 'TLS1_AD_BAD_CERTIFICATE_STATUS_RESPONSE',
    TLS1_AD_BAD_CERTIFICATE_HASH_VALUE: 'TLS1_AD_BAD_CERTIFICATE_HASH_VALUE',
    TLS1_AD_UNKNOWN_PSK_IDENTITY: 'TLS1_AD_UNKNOWN_PSK_IDENTITY'
}


# struct format strings for parsing buffer lengths
# don't forget, you have to pad a 3-byte value with \x00
_SIZE_FORMATS = ['!B', '!H', '!I', '!I']


def parse_variable_array(buf, lenbytes):
    """
    Parse an array described using the 'Type name<x..y>' syntax from the spec
    Read a length at the start of buf, and returns that many bytes
    after, in a tuple with the TOTAL bytes consumed (including the size). This
    does not check that the array is the right length for any given datatype.
    """
    # first have to figure out how to parse length
    assert lenbytes <= 4  # pretty sure 4 is impossible, too
    size_format = _SIZE_FORMATS[lenbytes - 1]
    padding = b'\x00' if lenbytes == 3 else b''
    # read off the length
    size = struct.unpack(size_format, padding + buf[:lenbytes])[0]
    # read the actual data
    data = buf[lenbytes:lenbytes + size]
    # if len(data) != size: insufficient data
    return data, size + lenbytes


def parse_extensions(buf):
    """
    Parse TLS extensions in passed buf. Returns an ordered list of extension tuples with
    ordinal extension type as first value and extension data as second value.
    Passed buf must start with the 2-byte extensions length TLV.
    http://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml
    """
    extensions_length = struct.unpack('!H', buf[:2])[0]
    extensions = []

    pointer = 2
    while pointer < extensions_length:
        ext_type = struct.unpack('!H', buf[pointer:pointer + 2])[0]
        pointer += 2
        ext_data, parsed = parse_variable_array(buf[pointer:], 2)
        extensions.append((ext_type, ext_data))
        pointer += parsed
    return extensions


class SSL3Exception(Exception):
    pass


class TLSRecord(dpkt.Packet):
    """
    SSLv3 or TLSv1+ packet.

    In addition to the fields specified in the header, there are
    compressed and decrypted fields, indicating whether, in the language
    of the spec, this is a TLSPlaintext, TLSCompressed, or
    TLSCiphertext. The application will have to figure out when it's
    appropriate to change these values.
    """

    __hdr__ = (
        ('type', 'B', 0),
        ('version', 'H', 0),
        ('length', 'H', 0),
    )

    def __init__(self, *args, **kwargs):
        # assume plaintext unless specified otherwise in arguments
        self.compressed = kwargs.pop('compressed', False)
        self.encrypted = kwargs.pop('encrypted', False)
        # parent constructor
        dpkt.Packet.__init__(self, *args, **kwargs)
        # make sure length and data are consistent
        self.length = len(self.data)

    def unpack(self, buf):
        dpkt.Packet.unpack(self, buf)
        header_length = self.__hdr_len__
        self.data = buf[header_length:header_length + self.length]
        # make sure buffer was long enough
        if len(self.data) != self.length:
            raise dpkt.NeedData('TLSRecord data was too short.')
        # assume compressed and encrypted when it's been parsed from
        # raw data
        self.compressed = True
        self.encrypted = True


class TLSChangeCipherSpec(dpkt.Packet):
    """
    ChangeCipherSpec message is just a single byte with value 1
    """
    __hdr__ = (('type', 'B', 1),)


class TLSAppData(str):
    """
    As far as TLSRecord is concerned, AppData is just an opaque blob.
    """
    pass


class TLSAlert(dpkt.Packet):
    __hdr__ = (
        ('level', 'B', 1),
        ('description', 'B', 0),
    )


class TLSHelloRequest(dpkt.Packet):
    __hdr__ = tuple()


class TLSClientHello(dpkt.Packet):
    __hdr__ = (
        ('version', 'H', 0x0301),
        ('random', '32s', '\x00' * 32),
    )  # the rest is variable-length and has to be done manually

    def unpack(self, buf):
        dpkt.Packet.unpack(self, buf)
        # now session, cipher suites, extensions are in self.data
        self.session_id, pointer = parse_variable_array(self.data, 1)
        # print 'pointer',pointer
        # handle ciphersuites
        ciphersuites, parsed = parse_variable_array(self.data[pointer:], 2)
        pointer += parsed
        num_ciphersuites = int(len(ciphersuites) / 2)
        try:
            self.ciphersuites = [
                ssl_ciphersuites.BY_CODE[code] for code in struct.unpack('!' + num_ciphersuites * 'H', ciphersuites)]
        except KeyError as e:
            raise SSL3Exception('Unknown or invalid cipher suite type %x' % int(e.args[0]))
        # check len(ciphersuites) % 2 == 0 ?
        # compression methods
        compression_methods, parsed = parse_variable_array(self.data[pointer:], 1)
        pointer += parsed
        self.compression_methods = struct.unpack('{0}B'.format(len(compression_methods)), compression_methods)
        # Parse extensions if present
        if len(self.data[pointer:]) >= 6:
            self.extensions = parse_extensions(self.data[pointer:])


class TLSServerHello(dpkt.Packet):
    __hdr__ = (
        ('version', 'H', '0x0301'),
        ('random', '32s', '\x00' * 32),
    )  # session is variable, forcing rest to be manual

    def unpack(self, buf):
        try:
            dpkt.Packet.unpack(self, buf)
            self.session_id, pointer = parse_variable_array(self.data, 1)
            # single cipher suite
            try:
                code = struct.unpack('!H', self.data[pointer:pointer + 2])[0]
                self.cipher_suite = ssl_ciphersuites.BY_CODE[code]
            except KeyError as e:
                raise SSL3Exception('Unknown or invalid cipher suite type %x' % int(e.args[0]))
            pointer += 2
            # single compression method
            self.compression = struct.unpack('!B', self.data[pointer:pointer + 1])[0]
            pointer += 1
            # Parse extensions if present
            if len(self.data[pointer:]) >= 6:
                self.extensions = parse_extensions(self.data[pointer:])
        except struct.error:
            # probably data too short
            raise dpkt.NeedData


class TLSCertificate(dpkt.Packet):
    __hdr__ = tuple()

    def unpack(self, buf):
        try:
            dpkt.Packet.unpack(self, buf)
            all_certs, all_certs_len = parse_variable_array(self.data, 3)
            self.certificates = []
            pointer = 3
            while pointer < all_certs_len:
                cert, parsed = parse_variable_array(self.data[pointer:], 3)
                self.certificates.append((cert))
                pointer += parsed
        except struct.error:
            raise dpkt.NeedData


class TLSUnknownHandshake(dpkt.Packet):
    __hdr__ = tuple()


TLSNewSessionTicket = TLSUnknownHandshake
TLSServerKeyExchange = TLSUnknownHandshake
TLSCertificateRequest = TLSUnknownHandshake
TLSServerHelloDone = TLSUnknownHandshake
TLSCertificateVerify = TLSUnknownHandshake
TLSClientKeyExchange = TLSUnknownHandshake
TLSFinished = TLSUnknownHandshake


# mapping of handshake type ids to their names
# and the classes that implement them
HANDSHAKE_TYPES = {
    0: ('HelloRequest', TLSHelloRequest),
    1: ('ClientHello', TLSClientHello),
    2: ('ServerHello', TLSServerHello),
    4: ('NewSessionTicket', TLSNewSessionTicket),
    11: ('Certificate', TLSCertificate),
    12: ('ServerKeyExchange', TLSServerKeyExchange),
    13: ('CertificateRequest', TLSCertificateRequest),
    14: ('ServerHelloDone', TLSServerHelloDone),
    15: ('CertificateVerify', TLSCertificateVerify),
    16: ('ClientKeyExchange', TLSClientKeyExchange),
    20: ('Finished', TLSFinished),
}


class TLSHandshake(dpkt.Packet):
    """
    A TLS Handshake message

    This goes for all messages encapsulated in the Record layer, but especially
    important for handshakes and app data: A message may be spread across a
    number of TLSRecords, in addition to the possibility of there being more
    than one in a given Record. You have to put together the contents of
    TLSRecord's yourself.
    """

    # struct.unpack can't handle the 3-byte int, so we parse it as bytes
    # (and store it as bytes so dpkt doesn't get confused), and turn it into
    # an int in a user-facing property
    __hdr__ = (
        ('type', 'B', 0),
        ('length_bytes', '3s', 0),
    )

    def unpack(self, buf):
        dpkt.Packet.unpack(self, buf)
        # Wait, might there be more than one message of self.type?
        embedded_type = HANDSHAKE_TYPES.get(self.type, None)
        if embedded_type is None:
            raise SSL3Exception('Unknown or invalid handshake type %d' %
                                self.type)
        # only take the right number of bytes
        self.data = self.data[:self.length]
        if len(self.data) != self.length:
            raise dpkt.NeedData
        # get class out of embedded_type tuple
        self.data = embedded_type[1](self.data)

    @property
    def length(self):
        return struct.unpack('!I', b'\x00' + self.length_bytes)[0]


RECORD_TYPES = {
    20: TLSChangeCipherSpec,
    21: TLSAlert,
    22: TLSHandshake,
    23: TLSAppData,
}


class SSLFactory(object):
    def __new__(cls, buf):
        v = buf[1:3]
        if v in SSL3_VERSION_BYTES:
            return TLSRecord(buf)
        # SSL2 has no characteristic header or magic bytes, so we just assume
        # that the msg is an SSL2 msg if it is not detected as SSL3+
        return SSL2(buf)


def tls_multi_factory(buf):
    """
    Attempt to parse one or more TLSRecord's out of buf

    Args:
      buf: string containing SSL/TLS messages. May have an incomplete record
        on the end

    Returns:
      [TLSRecord]
      int, total bytes consumed, != len(buf) if an incomplete record was left at
        the end.

    Raises SSL3Exception.
    """
    i, n = 0, len(buf)
    msgs = []
    while i + 5 <= n:
        v = buf[i + 1:i + 3]
        if v in SSL3_VERSION_BYTES:
            try:
                msg = TLSRecord(buf[i:])
                msgs.append(msg)
            except dpkt.NeedData:
                break
        else:
            raise SSL3Exception('Bad TLS version in buf: %r' % buf[i:i + 5])
        i += len(msg)
    return msgs, i


_hexdecode = binascii.a2b_hex


class TestTLS(object):
    """
    Test basic TLS functionality.
    Test that each TLSRecord is correctly discovered and added to TLS.records
    """

    @classmethod
    def setup_class(cls):
        cls.p = TLS(
            b'\x16\x03\x00\x02\x06\x01\x00\x02\x02\x03\x03\x58\x5c\x2f\xf7\x2a\x65\x99\x49\x87\x71\xf5'
            b'\x95\x14\xf1\x0a\xf6\x8c\x68\xf9\xef\x30\xd0\xda\xdc\x9e\x1a\xf6\x4d\x10\x91\x47\x6a\x00'
            b'\x00\x84\xc0\x2b\xc0\x2c\xc0\x86\xc0\x87\xc0\x09\xc0\x23\xc0\x0a\xc0\x24\xc0\x72\xc0\x73'
            b'\xc0\x08\xc0\x07\xc0\x2f\xc0\x30\xc0\x8a\xc0\x8b\xc0\x13\xc0\x27\xc0\x14\xc0\x28\xc0\x76'
            b'\xc0\x77\xc0\x12\xc0\x11\x00\x9c\x00\x9d\xc0\x7a\xc0\x7b\x00\x2f\x00\x3c\x00\x35\x00\x3d'
            b'\x00\x41\x00\xba\x00\x84\x00\xc0\x00\x0a\x00\x05\x00\x04\x00\x9e\x00\x9f\xc0\x7c\xc0\x7d'
            b'\x00\x33\x00\x67\x00\x39\x00\x6b\x00\x45\x00\xbe\x00\x88\x00\xc4\x00\x16\x00\xa2\x00\xa3'
            b'\xc0\x80\xc0\x81\x00\x32\x00\x40\x00\x38\x00\x6a\x00\x44\x00\xbd\x00\x87\x00\xc3\x00\x13'
            b'\x00\x66\x01\x00\x01\x55\x00\x05\x00\x05\x01\x00\x00\x00\x00\x00\x00\x00\x11\x00\x0f\x00'
            b'\x00\x0c\x77\x77\x77\x2e\x69\x61\x6e\x61\x2e\x6f\x72\x67\xff\x01\x00\x01\x00\x00\x23\x00'
            b'\x00\x00\x0a\x00\x0c\x00\x0a\x00\x13\x00\x15\x00\x17\x00\x18\x00\x19\x00\x0b\x00\x02\x01'
            b'\x00\x00\x0d\x00\x1c\x00\x1a\x04\x01\x04\x02\x04\x03\x05\x01\x05\x03\x06\x01\x06\x03\x03'
            b'\x01\x03\x02\x03\x03\x02\x01\x02\x02\x02\x03\x00\x15\x00\xf4\x00\xf2\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        )

    def test_records_length(self):
        assert (len(self.p.records) == 1)

    def test_record_type(self):
        assert (self.p.records[0].type == 22)

    def test_record_version(self):
        assert (self.p.records[0].version == 768)


class TestTLSRecord(object):
    """
    Test basic TLSRecord functionality
    For this test, the contents of the record doesn't matter, since we're not parsing the next layer.
    """

    @classmethod
    def setup_class(cls):
        # add some extra data, to make sure length is parsed correctly
        cls.p = TLSRecord(b'\x17\x03\x01\x00\x08abcdefghzzzzzzzzzzz')

    def test_content_type(self):
        assert (self.p.type == 23)

    def test_version(self):
        assert (self.p.version == 0x0301)

    def test_length(self):
        assert (self.p.length == 8)

    def test_data(self):
        assert (self.p.data == b'abcdefgh')

    def test_initial_flags(self):
        assert (self.p.compressed is True)
        assert (self.p.encrypted is True)

    def test_repack(self):
        p2 = TLSRecord(type=23, version=0x0301, data=b'abcdefgh')
        assert (p2.type == 23)
        assert (p2.version == 0x0301)
        assert (p2.length == 8)
        assert (p2.data == b'abcdefgh')
        assert (p2.pack() == self.p.pack())

    def test_total_length(self):
        # that len(p) includes header
        assert (len(self.p) == 13)

    def test_raises_need_data_when_buf_is_short(self):
        import pytest
        pytest.raises(dpkt.NeedData, TLSRecord, b'\x16\x03\x01\x00\x10abc')


class TestTLSChangeCipherSpec(object):
    """It's just a byte. This will be quick, I promise"""

    @classmethod
    def setup_class(cls):
        cls.p = TLSChangeCipherSpec(b'\x01')

    def test_parses(self):
        assert (self.p.type == 1)

    def test_total_length(self):
        assert (len(self.p) == 1)


class TestTLSAppData(object):
    """AppData is basically just a string"""

    def test_value(self):
        d = TLSAppData('abcdefgh')
        assert (d == 'abcdefgh')


class TestTLSHandshake(object):
    @classmethod
    def setup_class(cls):
        cls.h = TLSHandshake(b'\x00\x00\x00\x01\xff')

    def test_created_inside_message(self):
        assert (isinstance(self.h.data, TLSHelloRequest) is True)

    def test_length(self):
        assert (self.h.length == 0x01)

    def test_raises_need_data(self):
        import pytest
        pytest.raises(dpkt.NeedData, TLSHandshake, b'\x00\x00\x01\x01')


class TestClientHello(object):
    """This data is extracted from and verified by Wireshark"""

    @classmethod
    def setup_class(cls):
        cls.data = _hexdecode(
            b"01000199"  # handshake header
            b"0301"  # version
            b"5008220ce5e0e78b6891afe204498c9363feffbe03235a2d9e05b7d990eb708d"  # rand
            b"2009bc0192e008e6fa8fe47998fca91311ba30ddde14a9587dc674b11c3d3e5ed1"  # session id
            # cipher suites
            b"005200ffc00ac0140088008700390038c00fc00500840035c007c009c011c0130045004400330032"
            b"c00cc00ec002c0040096004100050004002fc008c01200160013c00dc003000ac006c010c00bc00100020001"
            b"0100"  # compresssion methods
            # extensions
            b"00fc0000000e000c0000096c6f63616c686f7374000a00080006001700180019000b000201000023"
            b"00d0a50b2e9f618a9ea9bf493ef49b421835cd2f6b05bbe1179d8edf70d58c33d656e8696d36d7e7"
            b"e0b9d3ecc0e4de339552fa06c64c0fcb550a334bc43944e2739ca342d15a9ebbe981ac87a0d38160"
            b"507d47af09bdc16c5f0ee4cdceea551539382333226048a026d3a90a0535f4a64236467db8fee22b"
            b"041af986ad0f253bc369137cd8d8cd061925461d7f4d7895ca9a4181ab554dad50360ac31860e971"
            b"483877c9335ac1300c5e78f3e56f3b8e0fc16358fcaceefd5c8d8aaae7b35be116f8832856ca6114"
            b"4fcdd95e071b94d0cf7233740000"
            b"FFFFFFFFFFFFFFFF")  # random garbage
        cls.p = TLSHandshake(cls.data)

    def test_client_hello_constructed(self):
        """Make sure the correct class was constructed"""
        # print self.p
        assert (isinstance(self.p.data, TLSClientHello) is True)

    #   def testClientDateCorrect(self):
    #       self.assertEqual(self.p.random_unixtime, 1342710284)

    def test_client_random_correct(self):
        assert (self.p.data.random == _hexdecode(b'5008220ce5e0e78b6891afe204498c9363feffbe03235a2d9e05b7d990eb708d'))

    def test_cipher_suite(self):
        assert (tuple([c.code for c in self.p.data.ciphersuites]) == struct.unpack('!{0}H'.format(
            len(self.p.data.ciphersuites)), _hexdecode(
            b'00ffc00ac0140088008700390038c00fc00500840035c007c009c011c0130045004400330032c00c'
            b'c00ec002c0040096004100050004002fc008c01200160013c00dc003000ac006c010c00bc00100020001')))
        assert (len(self.p.data.ciphersuites) == 41)

    def test_session_id(self):
        assert (self.p.data.session_id == _hexdecode(b'09bc0192e008e6fa8fe47998fca91311ba30ddde14a9587dc674b11c3d3e5ed1'))

    def test_compression_methods(self):
        assert (list(self.p.data.compression_methods) == [0x00, ])

    def test_total_length(self):
        assert (len(self.p) == 413)


class TestServerHello(object):
    """Again, from Wireshark"""

    @classmethod
    def setup_class(cls):
        cls.data = _hexdecode(
            b'0200004d03015008220c8ec43c5462315a7c99f5d5b6bff009ad285b51dc18485f352e9fdecd2009'
            b'bc0192e008e6fa8fe47998fca91311ba30ddde14a9587dc674b11c3d3e5ed10002000005ff01000100')
        cls.p = TLSHandshake(cls.data)

    def test_constructed(self):
        assert (isinstance(self.p.data, TLSServerHello) is True)

    #    def testDateCorrect(self):
    #        self.assertEqual(self.p.random_unixtime, 1342710284)

    def test_random_correct(self):
        assert (self.p.data.random == _hexdecode(b'5008220c8ec43c5462315a7c99f5d5b6bff009ad285b51dc18485f352e9fdecd'))

    def test_cipher_suite(self):
        assert (self.p.data.cipher_suite.name == 'TLS_RSA_WITH_NULL_SHA')

    def test_total_length(self):
        assert (len(self.p) == 81)


class TestTLSCertificate(object):
    """We use a 2016 certificate record from iana.org as test data."""

    @classmethod
    def setup_class(cls):
        cls.p = TLSHandshake(
            b'\x0b\x00\x0b\x45\x00\x0b\x42\x00\x06\x87\x30\x82\x06\x83\x30\x82\x05\x6b\xa0\x03\x02\x01\x02\x02\x10\x09\xca'
            b'\xbb\xe2\x19\x1c\x8f\x56\x9d\xd4\xb6\xdd\x25\x0f\x21\xd8\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x0b'
            b'\x05\x00\x30\x70\x31\x0b\x30\x09\x06\x03\x55\x04\x06\x13\x02\x55\x53\x31\x15\x30\x13\x06\x03\x55\x04\x0a\x13'
            b'\x0c\x44\x69\x67\x69\x43\x65\x72\x74\x20\x49\x6e\x63\x31\x19\x30\x17\x06\x03\x55\x04\x0b\x13\x10\x77\x77\x77'
            b'\x2e\x64\x69\x67\x69\x63\x65\x72\x74\x2e\x63\x6f\x6d\x31\x2f\x30\x2d\x06\x03\x55\x04\x03\x13\x26\x44\x69\x67'
            b'\x69\x43\x65\x72\x74\x20\x53\x48\x41\x32\x20\x48\x69\x67\x68\x20\x41\x73\x73\x75\x72\x61\x6e\x63\x65\x20\x53'
            b'\x65\x72\x76\x65\x72\x20\x43\x41\x30\x1e\x17\x0d\x31\x34\x31\x30\x32\x37\x30\x30\x30\x30\x30\x30\x5a\x17\x0d'
            b'\x31\x38\x30\x31\x30\x33\x31\x32\x30\x30\x30\x30\x5a\x30\x81\xa3\x31\x0b\x30\x09\x06\x03\x55\x04\x06\x13\x02'
            b'\x55\x53\x31\x13\x30\x11\x06\x03\x55\x04\x08\x13\x0a\x43\x61\x6c\x69\x66\x6f\x72\x6e\x69\x61\x31\x14\x30\x12'
            b'\x06\x03\x55\x04\x07\x13\x0b\x4c\x6f\x73\x20\x41\x6e\x67\x65\x6c\x65\x73\x31\x3c\x30\x3a\x06\x03\x55\x04\x0a'
            b'\x13\x33\x49\x6e\x74\x65\x72\x6e\x65\x74\x20\x43\x6f\x72\x70\x6f\x72\x61\x74\x69\x6f\x6e\x20\x66\x6f\x72\x20'
            b'\x41\x73\x73\x69\x67\x6e\x65\x64\x20\x4e\x61\x6d\x65\x73\x20\x61\x6e\x64\x20\x4e\x75\x6d\x62\x65\x72\x73\x31'
            b'\x16\x30\x14\x06\x03\x55\x04\x0b\x13\x0d\x49\x54\x20\x4f\x70\x65\x72\x61\x74\x69\x6f\x6e\x73\x31\x13\x30\x11'
            b'\x06\x03\x55\x04\x03\x0c\x0a\x2a\x2e\x69\x61\x6e\x61\x2e\x6f\x72\x67\x30\x82\x02\x22\x30\x0d\x06\x09\x2a\x86'
            b'\x48\x86\xf7\x0d\x01\x01\x01\x05\x00\x03\x82\x02\x0f\x00\x30\x82\x02\x0a\x02\x82\x02\x01\x00\x9d\xbd\xfd\xde'
            b'\xb5\xca\xe5\x3a\x55\x97\x47\xe2\xfd\xa6\x37\x28\xe4\xab\xa6\x0f\x18\xb7\x9a\x69\xf0\x33\x10\xbf\x01\x64\xe5'
            b'\xee\x7d\xb6\xb1\x5b\xf5\x6d\xf2\x3f\xdd\xba\xe6\xa1\xbb\x38\x44\x9b\x8c\x88\x3f\x18\x10\x2b\xbd\x8b\xb6\x55'
            b'\xac\x0e\x2d\xac\x2e\xe3\xed\x5c\xf4\x31\x58\x68\xd2\xc5\x98\x06\x82\x84\x85\x4b\x24\x89\x4d\xcd\x4b\xd3\x78'
            b'\x11\xf0\xad\x3a\x28\x2c\xd4\xb4\xe5\x99\xff\xd0\x7d\x8d\x2d\x3f\x24\x78\x55\x4f\x81\x02\x0b\x32\x0e\xe1\x2f'
            b'\x44\x94\x8e\x2e\xa1\xed\xbc\x99\x0b\x83\x0c\xa5\xcc\xa6\xb4\xa8\x39\xfb\x27\xb5\x18\x50\xc9\x84\x7e\xac\x74'
            b'\xf2\x66\x09\xeb\x24\x36\x5b\x97\x51\xfb\x1c\x32\x08\xf5\x69\x13\xba\xcb\xca\xe4\x92\x01\x34\x7c\x78\xb7\xe5'
            b'\x4a\x9d\x99\x97\x94\x04\xc3\x7f\x00\xfb\x65\xdb\x84\x9f\xd7\x5e\x3a\x68\x77\x0c\x30\xf2\xab\xe6\x5b\x33\x25'
            b'\x6f\xb5\x9b\x45\x00\x50\xb0\x0d\x81\x39\xd4\xd8\x0d\x36\xf7\xbc\x46\xda\xf3\x03\xe4\x8f\x0f\x07\x91\xb2\xfd'
            b'\xd7\x2e\xc6\x0b\x2c\xb3\xad\x53\x3c\x3f\x28\x8c\x9c\x19\x4e\x49\x33\x7a\x69\xc4\x96\x73\x1f\x08\x6d\x4f\x1f'
            b'\x98\x25\x90\x07\x13\xe2\xa5\x51\xd0\x5c\xb6\x05\x75\x67\x85\x0d\x91\xe6\x00\x1c\x4c\xe2\x71\x76\xf0\x95\x78'
            b'\x73\xa9\x5b\x88\x0a\xcb\xec\x19\xe7\xbd\x9b\xcf\x12\x86\xd0\x45\x2b\x73\x78\x9c\x41\x90\x5d\xd4\x70\x97\x1c'
            b'\xd7\x3a\xea\x52\xc7\x7b\x08\x0c\xd7\x79\xaf\x58\x23\x4f\x33\x72\x25\xc2\x6f\x87\xa8\xc1\x3e\x2a\x65\xe9\xdd'
            b'\x4e\x03\xa5\xb4\x1d\x7e\x06\xb3\x35\x3f\x38\x12\x9b\x23\x27\xa5\x31\xec\x96\x27\xa2\x1d\xc4\x23\x73\x3a\xa0'
            b'\x29\xd4\x98\x94\x48\xba\x33\x22\x89\x1c\x1a\x56\x90\xdd\xf2\xd2\x5c\x8e\xc8\xaa\xa8\x94\xb1\x4a\xa9\x21\x30'
            b'\xc6\xb6\xd9\x69\xa2\x1f\xf6\x71\xb6\x0c\x4c\x92\x3a\x94\xa9\x3e\xa1\xdd\x04\x92\xc9\x33\x93\xca\x6e\xdd\x61'
            b'\xf3\x3c\xa7\x7e\x92\x08\xd0\x1d\x6b\xd1\x51\x07\x66\x2e\xc0\x88\x73\x3d\xf4\xc8\x76\xa7\xe1\x60\x8b\x82\x97'
            b'\x3a\x0f\x75\x92\xe8\x4e\xd1\x55\x79\xd1\x81\xe7\x90\x24\xae\x8a\x7e\x4b\x9f\x00\x78\xeb\x20\x05\xb2\x3f\x9d'
            b'\x09\xa1\xdf\x1b\xbc\x7d\xe2\xa5\xa6\x08\x5a\x36\x46\xd9\xfa\xdb\x0e\x9d\xa2\x73\xa5\xf4\x03\xcd\xd4\x28\x31'
            b'\xce\x6f\x0c\xa4\x68\x89\x58\x56\x02\xbb\x8b\xc3\x6b\xb3\xbe\x86\x1f\xf6\xd1\xa6\x2e\x35\x02\x03\x01\x00\x01'
            b'\xa3\x82\x01\xe3\x30\x82\x01\xdf\x30\x1f\x06\x03\x55\x1d\x23\x04\x18\x30\x16\x80\x14\x51\x68\xff\x90\xaf\x02'
            b'\x07\x75\x3c\xcc\xd9\x65\x64\x62\xa2\x12\xb8\x59\x72\x3b\x30\x1d\x06\x03\x55\x1d\x0e\x04\x16\x04\x14\xc7\xd0'
            b'\xac\xef\x89\x8b\x20\xe4\xb9\x14\x66\x89\x33\x03\x23\x94\xf6\xbf\x3a\x61\x30\x1f\x06\x03\x55\x1d\x11\x04\x18'
            b'\x30\x16\x82\x0a\x2a\x2e\x69\x61\x6e\x61\x2e\x6f\x72\x67\x82\x08\x69\x61\x6e\x61\x2e\x6f\x72\x67\x30\x0e\x06'
            b'\x03\x55\x1d\x0f\x01\x01\xff\x04\x04\x03\x02\x05\xa0\x30\x1d\x06\x03\x55\x1d\x25\x04\x16\x30\x14\x06\x08\x2b'
            b'\x06\x01\x05\x05\x07\x03\x01\x06\x08\x2b\x06\x01\x05\x05\x07\x03\x02\x30\x75\x06\x03\x55\x1d\x1f\x04\x6e\x30'
            b'\x6c\x30\x34\xa0\x32\xa0\x30\x86\x2e\x68\x74\x74\x70\x3a\x2f\x2f\x63\x72\x6c\x33\x2e\x64\x69\x67\x69\x63\x65'
            b'\x72\x74\x2e\x63\x6f\x6d\x2f\x73\x68\x61\x32\x2d\x68\x61\x2d\x73\x65\x72\x76\x65\x72\x2d\x67\x33\x2e\x63\x72'
            b'\x6c\x30\x34\xa0\x32\xa0\x30\x86\x2e\x68\x74\x74\x70\x3a\x2f\x2f\x63\x72\x6c\x34\x2e\x64\x69\x67\x69\x63\x65'
            b'\x72\x74\x2e\x63\x6f\x6d\x2f\x73\x68\x61\x32\x2d\x68\x61\x2d\x73\x65\x72\x76\x65\x72\x2d\x67\x33\x2e\x63\x72'
            b'\x6c\x30\x42\x06\x03\x55\x1d\x20\x04\x3b\x30\x39\x30\x37\x06\x09\x60\x86\x48\x01\x86\xfd\x6c\x01\x01\x30\x2a'
            b'\x30\x28\x06\x08\x2b\x06\x01\x05\x05\x07\x02\x01\x16\x1c\x68\x74\x74\x70\x73\x3a\x2f\x2f\x77\x77\x77\x2e\x64'
            b'\x69\x67\x69\x63\x65\x72\x74\x2e\x63\x6f\x6d\x2f\x43\x50\x53\x30\x81\x83\x06\x08\x2b\x06\x01\x05\x05\x07\x01'
            b'\x01\x04\x77\x30\x75\x30\x24\x06\x08\x2b\x06\x01\x05\x05\x07\x30\x01\x86\x18\x68\x74\x74\x70\x3a\x2f\x2f\x6f'
            b'\x63\x73\x70\x2e\x64\x69\x67\x69\x63\x65\x72\x74\x2e\x63\x6f\x6d\x30\x4d\x06\x08\x2b\x06\x01\x05\x05\x07\x30'
            b'\x02\x86\x41\x68\x74\x74\x70\x3a\x2f\x2f\x63\x61\x63\x65\x72\x74\x73\x2e\x64\x69\x67\x69\x63\x65\x72\x74\x2e'
            b'\x63\x6f\x6d\x2f\x44\x69\x67\x69\x43\x65\x72\x74\x53\x48\x41\x32\x48\x69\x67\x68\x41\x73\x73\x75\x72\x61\x6e'
            b'\x63\x65\x53\x65\x72\x76\x65\x72\x43\x41\x2e\x63\x72\x74\x30\x0c\x06\x03\x55\x1d\x13\x01\x01\xff\x04\x02\x30'
            b'\x00\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x0b\x05\x00\x03\x82\x01\x01\x00\x70\x31\x4c\x38\xe7\xc0'
            b'\x2f\xd8\x08\x10\x50\x0b\x9d\xf6\xda\xe8\x5d\xe9\xb2\x3e\x29\xfb\xd6\x8b\xfd\xb5\xf2\x34\x11\xc8\x9a\xcf\xaf'
            b'\x9a\xe0\x5a\xf9\x12\x3a\x8a\xa6\xbc\xe6\x95\x4a\x4e\x68\xdc\x7c\xfc\x48\x0a\x65\xd7\x6f\x22\x9c\x4b\xd5\xf5'
            b'\x67\x4b\x0c\x9a\xc6\xd0\x6a\x37\xa1\xa1\xc1\x45\xc3\x95\x61\x20\xb8\xef\xe6\x7c\x88\x7a\xb4\xff\x7d\x6a\xa9'
            b'\x50\xff\x36\x98\xf2\x7c\x4a\x19\xd5\x9d\x93\xa3\x9a\xca\x5a\x7b\x6d\x6c\x75\xe3\x49\x74\xe5\x0f\x5a\x59\x00'
            b'\x05\xb3\xcb\x66\x5d\xdb\xd7\x07\x4f\x9f\xcb\xcb\xf9\xc5\x02\x28\xd5\xe2\x55\x96\xb6\x4a\xda\x16\x0b\x48\xf7'
            b'\x7a\x93\xaa\xce\xd2\x26\x17\xbf\xe0\x05\xe0\x0f\xe2\x0a\x53\x2a\x0a\xdc\xb8\x18\xc8\x78\xdc\x5d\x66\x49\x27'
            b'\x77\x77\xca\x1a\x81\x4e\x21\xd0\xb5\x33\x08\xaf\x40\x78\xbe\x45\x54\x71\x5e\x4c\xe4\x82\x8b\x01\x2f\x25\xff'
            b'\xa1\x3a\x6c\xeb\x30\xd2\x0a\x75\xde\xba\x8a\x34\x4e\x41\xd6\x27\xfa\x63\x8f\xef\xf3\x8a\x30\x63\xa0\x18\x75'
            b'\x19\xb3\x9b\x05\x3f\x71\x34\xd9\xcd\x83\xe6\x09\x1a\xcc\xf5\xd2\xe3\xa0\x5e\xdf\xa1\xdf\xbe\x18\x1a\x87\xad'
            b'\x86\xba\x24\xfe\x6b\x97\xfe\x00\x04\xb5\x30\x82\x04\xb1\x30\x82\x03\x99\xa0\x03\x02\x01\x02\x02\x10\x04\xe1'
            b'\xe7\xa4\xdc\x5c\xf2\xf3\x6d\xc0\x2b\x42\xb8\x5d\x15\x9f\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x0b'
            b'\x05\x00\x30\x6c\x31\x0b\x30\x09\x06\x03\x55\x04\x06\x13\x02\x55\x53\x31\x15\x30\x13\x06\x03\x55\x04\x0a\x13'
            b'\x0c\x44\x69\x67\x69\x43\x65\x72\x74\x20\x49\x6e\x63\x31\x19\x30\x17\x06\x03\x55\x04\x0b\x13\x10\x77\x77\x77'
            b'\x2e\x64\x69\x67\x69\x63\x65\x72\x74\x2e\x63\x6f\x6d\x31\x2b\x30\x29\x06\x03\x55\x04\x03\x13\x22\x44\x69\x67'
            b'\x69\x43\x65\x72\x74\x20\x48\x69\x67\x68\x20\x41\x73\x73\x75\x72\x61\x6e\x63\x65\x20\x45\x56\x20\x52\x6f\x6f'
            b'\x74\x20\x43\x41\x30\x1e\x17\x0d\x31\x33\x31\x30\x32\x32\x31\x32\x30\x30\x30\x30\x5a\x17\x0d\x32\x38\x31\x30'
            b'\x32\x32\x31\x32\x30\x30\x30\x30\x5a\x30\x70\x31\x0b\x30\x09\x06\x03\x55\x04\x06\x13\x02\x55\x53\x31\x15\x30'
            b'\x13\x06\x03\x55\x04\x0a\x13\x0c\x44\x69\x67\x69\x43\x65\x72\x74\x20\x49\x6e\x63\x31\x19\x30\x17\x06\x03\x55'
            b'\x04\x0b\x13\x10\x77\x77\x77\x2e\x64\x69\x67\x69\x63\x65\x72\x74\x2e\x63\x6f\x6d\x31\x2f\x30\x2d\x06\x03\x55'
            b'\x04\x03\x13\x26\x44\x69\x67\x69\x43\x65\x72\x74\x20\x53\x48\x41\x32\x20\x48\x69\x67\x68\x20\x41\x73\x73\x75'
            b'\x72\x61\x6e\x63\x65\x20\x53\x65\x72\x76\x65\x72\x20\x43\x41\x30\x82\x01\x22\x30\x0d\x06\x09\x2a\x86\x48\x86'
            b'\xf7\x0d\x01\x01\x01\x05\x00\x03\x82\x01\x0f\x00\x30\x82\x01\x0a\x02\x82\x01\x01\x00\xb6\xe0\x2f\xc2\x24\x06'
            b'\xc8\x6d\x04\x5f\xd7\xef\x0a\x64\x06\xb2\x7d\x22\x26\x65\x16\xae\x42\x40\x9b\xce\xdc\x9f\x9f\x76\x07\x3e\xc3'
            b'\x30\x55\x87\x19\xb9\x4f\x94\x0e\x5a\x94\x1f\x55\x56\xb4\xc2\x02\x2a\xaf\xd0\x98\xee\x0b\x40\xd7\xc4\xd0\x3b'
            b'\x72\xc8\x14\x9e\xef\x90\xb1\x11\xa9\xae\xd2\xc8\xb8\x43\x3a\xd9\x0b\x0b\xd5\xd5\x95\xf5\x40\xaf\xc8\x1d\xed'
            b'\x4d\x9c\x5f\x57\xb7\x86\x50\x68\x99\xf5\x8a\xda\xd2\xc7\x05\x1f\xa8\x97\xc9\xdc\xa4\xb1\x82\x84\x2d\xc6\xad'
            b'\xa5\x9c\xc7\x19\x82\xa6\x85\x0f\x5e\x44\x58\x2a\x37\x8f\xfd\x35\xf1\x0b\x08\x27\x32\x5a\xf5\xbb\x8b\x9e\xa4'
            b'\xbd\x51\xd0\x27\xe2\xdd\x3b\x42\x33\xa3\x05\x28\xc4\xbb\x28\xcc\x9a\xac\x2b\x23\x0d\x78\xc6\x7b\xe6\x5e\x71'
            b'\xb7\x4a\x3e\x08\xfb\x81\xb7\x16\x16\xa1\x9d\x23\x12\x4d\xe5\xd7\x92\x08\xac\x75\xa4\x9c\xba\xcd\x17\xb2\x1e'
            b'\x44\x35\x65\x7f\x53\x25\x39\xd1\x1c\x0a\x9a\x63\x1b\x19\x92\x74\x68\x0a\x37\xc2\xc2\x52\x48\xcb\x39\x5a\xa2'
            b'\xb6\xe1\x5d\xc1\xdd\xa0\x20\xb8\x21\xa2\x93\x26\x6f\x14\x4a\x21\x41\xc7\xed\x6d\x9b\xf2\x48\x2f\xf3\x03\xf5'
            b'\xa2\x68\x92\x53\x2f\x5e\xe3\x02\x03\x01\x00\x01\xa3\x82\x01\x49\x30\x82\x01\x45\x30\x12\x06\x03\x55\x1d\x13'
            b'\x01\x01\xff\x04\x08\x30\x06\x01\x01\xff\x02\x01\x00\x30\x0e\x06\x03\x55\x1d\x0f\x01\x01\xff\x04\x04\x03\x02'
            b'\x01\x86\x30\x1d\x06\x03\x55\x1d\x25\x04\x16\x30\x14\x06\x08\x2b\x06\x01\x05\x05\x07\x03\x01\x06\x08\x2b\x06'
            b'\x01\x05\x05\x07\x03\x02\x30\x34\x06\x08\x2b\x06\x01\x05\x05\x07\x01\x01\x04\x28\x30\x26\x30\x24\x06\x08\x2b'
            b'\x06\x01\x05\x05\x07\x30\x01\x86\x18\x68\x74\x74\x70\x3a\x2f\x2f\x6f\x63\x73\x70\x2e\x64\x69\x67\x69\x63\x65'
            b'\x72\x74\x2e\x63\x6f\x6d\x30\x4b\x06\x03\x55\x1d\x1f\x04\x44\x30\x42\x30\x40\xa0\x3e\xa0\x3c\x86\x3a\x68\x74'
            b'\x74\x70\x3a\x2f\x2f\x63\x72\x6c\x34\x2e\x64\x69\x67\x69\x63\x65\x72\x74\x2e\x63\x6f\x6d\x2f\x44\x69\x67\x69'
            b'\x43\x65\x72\x74\x48\x69\x67\x68\x41\x73\x73\x75\x72\x61\x6e\x63\x65\x45\x56\x52\x6f\x6f\x74\x43\x41\x2e\x63'
            b'\x72\x6c\x30\x3d\x06\x03\x55\x1d\x20\x04\x36\x30\x34\x30\x32\x06\x04\x55\x1d\x20\x00\x30\x2a\x30\x28\x06\x08'
            b'\x2b\x06\x01\x05\x05\x07\x02\x01\x16\x1c\x68\x74\x74\x70\x73\x3a\x2f\x2f\x77\x77\x77\x2e\x64\x69\x67\x69\x63'
            b'\x65\x72\x74\x2e\x63\x6f\x6d\x2f\x43\x50\x53\x30\x1d\x06\x03\x55\x1d\x0e\x04\x16\x04\x14\x51\x68\xff\x90\xaf'
            b'\x02\x07\x75\x3c\xcc\xd9\x65\x64\x62\xa2\x12\xb8\x59\x72\x3b\x30\x1f\x06\x03\x55\x1d\x23\x04\x18\x30\x16\x80'
            b'\x14\xb1\x3e\xc3\x69\x03\xf8\xbf\x47\x01\xd4\x98\x26\x1a\x08\x02\xef\x63\x64\x2b\xc3\x30\x0d\x06\x09\x2a\x86'
            b'\x48\x86\xf7\x0d\x01\x01\x0b\x05\x00\x03\x82\x01\x01\x00\x18\x8a\x95\x89\x03\xe6\x6d\xdf\x5c\xfc\x1d\x68\xea'
            b'\x4a\x8f\x83\xd6\x51\x2f\x8d\x6b\x44\x16\x9e\xac\x63\xf5\xd2\x6e\x6c\x84\x99\x8b\xaa\x81\x71\x84\x5b\xed\x34'
            b'\x4e\xb0\xb7\x79\x92\x29\xcc\x2d\x80\x6a\xf0\x8e\x20\xe1\x79\xa4\xfe\x03\x47\x13\xea\xf5\x86\xca\x59\x71\x7d'
            b'\xf4\x04\x96\x6b\xd3\x59\x58\x3d\xfe\xd3\x31\x25\x5c\x18\x38\x84\xa3\xe6\x9f\x82\xfd\x8c\x5b\x98\x31\x4e\xcd'
            b'\x78\x9e\x1a\xfd\x85\xcb\x49\xaa\xf2\x27\x8b\x99\x72\xfc\x3e\xaa\xd5\x41\x0b\xda\xd5\x36\xa1\xbf\x1c\x6e\x47'
            b'\x49\x7f\x5e\xd9\x48\x7c\x03\xd9\xfd\x8b\x49\xa0\x98\x26\x42\x40\xeb\xd6\x92\x11\xa4\x64\x0a\x57\x54\xc4\xf5'
            b'\x1d\xd6\x02\x5e\x6b\xac\xee\xc4\x80\x9a\x12\x72\xfa\x56\x93\xd7\xff\xbf\x30\x85\x06\x30\xbf\x0b\x7f\x4e\xff'
            b'\x57\x05\x9d\x24\xed\x85\xc3\x2b\xfb\xa6\x75\xa8\xac\x2d\x16\xef\x7d\x79\x27\xb2\xeb\xc2\x9d\x0b\x07\xea\xaa'
            b'\x85\xd3\x01\xa3\x20\x28\x41\x59\x43\x28\xd2\x81\xe3\xaa\xf6\xec\x7b\x3b\x77\xb6\x40\x62\x80\x05\x41\x45\x01'
            b'\xef\x17\x06\x3e\xde\xc0\x33\x9b\x67\xd3\x61\x2e\x72\x87\xe4\x69\xfc\x12\x00\x57\x40\x1e\x70\xf5\x1e\xc9\xb4'
        )

    def test_num_certs(self):
        assert (len(self.p.data.certificates) == 2)


class TestTLSMultiFactory(object):
    """Made up test data"""

    @classmethod
    def setup_class(cls):
        cls.data = _hexdecode(b'1703010010'  # header 1
                              b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'  # data 1
                              b'1703010010'  # header 2
                              b'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'  # data 2
                              b'1703010010'  # header 3
                              b'CCCCCCCC')  # data 3 (incomplete)
        cls.msgs, cls.bytes_parsed = tls_multi_factory(cls.data)

    def test_num_messages(self):
        # only complete messages should be parsed, incomplete ones left
        # in buffer
        assert (len(self.msgs) == 2)

    def test_bytes_parsed(self):
        assert (self.bytes_parsed == (5 + 16) * 2)

    def test_first_msg_data(self):
        assert (self.msgs[0].data == _hexdecode(b'AA' * 16))

    def test_second_msg_data(self):
        assert (self.msgs[1].data == _hexdecode(b'BB' * 16))

    def test_incomplete(self):
        msgs, n = tls_multi_factory(_hexdecode(b'17'))
        assert (len(msgs) == 0)
        assert (n == 0)
        msgs, n = tls_multi_factory(_hexdecode(b'1703'))
        assert (len(msgs) == 0)
        assert (n == 0)
        msgs, n = tls_multi_factory(_hexdecode(b'170301'))
        assert (len(msgs) == 0)
        assert (n == 0)
        msgs, n = tls_multi_factory(_hexdecode(b'17030100'))
        assert (len(msgs) == 0)
        assert (n == 0)
        msgs, n = tls_multi_factory(_hexdecode(b'1703010000'))
        assert (len(msgs) == 1)
        assert (n == 5)
