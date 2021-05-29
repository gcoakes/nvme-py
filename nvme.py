from ctypes import *
from fcntl import ioctl
from collections import namedtuple


class Cmd(LittleEndianStructure):
    _fields_ = [
        ("opcode", c_uint8),
        ("flags", c_uint8),
        ("rsvd1", c_uint16),
        ("nsid", c_uint32),
        ("cdw2", c_uint32),
        ("cdw3", c_uint32),
        ("metadata", c_uint64),
        ("addr", c_uint64),
        ("metadata_len", c_uint32),
        ("data_len", c_uint32),
        ("cdw10", c_uint32),
        ("cdw11", c_uint32),
        ("cdw12", c_uint32),
        ("cdw13", c_uint32),
        ("cdw14", c_uint32),
        ("cdw15", c_uint32),
        ("timeout_ms", c_uint32),
        ("result", c_uint32),
    ]
    _pack_ = 1

    def __init__(
        self,
        opcode=0,
        flags=0,
        rsvd1=0,
        nsid=0,
        cdw2=0,
        cdw3=0,
        metadata=None,
        addr=None,
        metadata_len=0,
        data_len=0,
        cdw10=0,
        cdw11=0,
        cdw12=0,
        cdw13=0,
        cdw14=0,
        cdw15=0,
        timeout_ms=0,
        result=0,
    ):
        self.opcode = c_uint8(opcode)
        self.flags = c_uint8(flags)
        self.rsvd1 = c_uint16(rsvd1)
        self.nsid = c_uint32(nsid)
        self.cdw2 = c_uint32(cdw2)
        self.cdw3 = c_uint32(cdw3)
        self.cdw10 = c_uint32(cdw10)
        self.cdw11 = c_uint32(cdw11)
        self.cdw12 = c_uint32(cdw12)
        self.cdw13 = c_uint32(cdw13)
        self.cdw14 = c_uint32(cdw14)
        self.cdw15 = c_uint32(cdw15)
        self.timeout_ms = c_uint32(timeout_ms)
        self.result = c_uint32(result)

        if addr is None:
            if data_len > 0:
                # Keep a reference alive in pure python.
                self._addr = create_string_buffer(data_len)
                self.addr = c_uint64(addressof(self._addr))
            else:
                self.addr = 0
        else:
            self.addr = addr
        self.data_len = data_len

        if metadata is None:
            if metadata_len > 0:
                # Keep a reference alive in pure python.
                self._metadata = create_string_buffer(metadata_len)
                self.metadata = c_uint64(addressof(self._metadata))
            else:
                self.metadata = 0
        else:
            self.metadata = metadata
        self.metadata_len = metadata_len


CmdResult = namedtuple("CmdResult", "status, data, metadata")


NVME_IOCTL_ADMIN_CMD = 0xC0484E41
NVME_IOCTL_IO_CMD = 0xC0484E43


def submit_cmd(req, dev, cmd):
    status = ioctl(dev.fileno(), req, cmd)
    if cmd.addr:
        data = (c_char * cmd.data_len).from_address(cmd.addr).value
    else:
        data = None
    if cmd.metadata:
        (c_char * cmd.metadata_len).from_address(cmd.metadata).value
    else:
        metadata = None
    return CmdResult(status, data, metadata)


def admin_cmd(dev, cmd):
    return submit_cmd(NVME_IOCTL_ADMIN_CMD, dev, cmd)


def io_cmd(dev, cmd):
    return submit_cmd(NVME_IOCTL_IO_CMD, dev, cmd)
