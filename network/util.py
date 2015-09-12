from struct import pack


class _PacketBuilder:
    def __init__(self):
        self.fmt = []
        self.values = []

    def begin(self):
        self.fmt.clear()
        self.fmt.append('>')
        self.values.clear()

    def append(self, fmt, *vals):
        self.fmt.append(fmt)

        def _filtered(v):
            return v.encode('utf8') if isinstance(v, str) else v

        self.values.extend(_filtered(v) for v in vals)

    def build(self):
        return pack(''.join(self.fmt), *self.values)


class DebugPacketBuilder(_PacketBuilder):
    def append(self, fmt, *vals):
        super(DebugPacketBuilder, self).append(fmt, *vals)

        try:
            self.build()
        except Exception as E:
            print(E)
            print(repr(fmt))
            print(repr(vals))
            raise

    def build(self):
        ret = super(DebugPacketBuilder, self).build()
        print(repr(ret))
        return ret


PacketBuilder = _PacketBuilder
