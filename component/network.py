from component import BaseComponent


class NetworkViewer(BaseComponent):
    _data = {
        'socket': None,
    }

    @classmethod
    def connect(cls, entity, data, socket):
        data.socket = socket
        # send snapshot

        # then update based upon...???
    @classmethod
    def update(cls, entity, data, schedule_info):
        entity.island.schedule()

    @classmethod
    def disconnect(cls, entity, data):
        data.socket = None
