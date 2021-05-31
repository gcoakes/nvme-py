from ctypes import *
from fcntl import ioctl
from collections import namedtuple


NVME_IOCTL_ADMIN_CMD = 0xC0484E41
NVME_IOCTL_IO_CMD = 0xC0484E43


CmdResult = namedtuple("CmdResult", "status, data, metadata")


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
                self._data_buf = create_string_buffer(data_len)
                self.addr = c_uint64(addressof(self._data_buf))
            else:
                self._data_buf = None
                self.addr = 0
        else:
            self._data_buf = None
            self.addr = addr
        self.data_len = data_len

        if metadata is None:
            if metadata_len > 0:
                # Keep a reference alive in pure python.
                self._metadata_buf = create_string_buffer(metadata_len)
                self.metadata = c_uint64(addressof(self._metadata_buf))
            else:
                self._metadata_buf = None
                self.metadata = 0
        else:
            self._metadata_buf = None
            self.metadata = metadata
        self.metadata_len = metadata_len

    def submit(self, req, dev):
        status = ioctl(dev.fileno(), req, self)
        return CmdResult(status, self._data_buf, self._metadata_buf)

    def submit_admin(self, dev):
        return self.submit(NVME_IOCTL_ADMIN_CMD, dev)

    def submit_io(self, dev):
        return self.submit(NVME_IOCTL_IO_CMD, dev)
