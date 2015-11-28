import logging
import struct
from binascii import hexlify
from functools import wraps
from isoweb_time import clock
import ujson
from util import to_bytes

log = logging.getLogger(__name__)


def rpc_json(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        packet_type, data = func(self, *args, **kwargs)

        data = ujson.dumps(
            data,
            double_precision=3
        )

        data = struct.pack(
                '>BfH%ds' % len(data),
                packet_type, clock(), len(data), to_bytes(data)
        )

        log.debug('rpc_json: %s', hexlify(data))
        self.entity.socket.send(data)

    return inner

