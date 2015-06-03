
import jsonpickle


class Metric(object):
    STATE_OK = 0
    STATE_BAD_HTTP_CODE = 1
    STATE_TIMEOUT = 2
    STATE_TOO_MANY_REDIRECTS = 3
    STATE_OTHER_FAILURE = 100

    def __init__(self, node_id, website, state, start, end, http_code):
        self.node_id = node_id
        self.website = website
        self.state = state
        self.start = start
        self.end = end
        self.http_code = http_code

    def to_json(self):
        return jsonpickle.encode(self)

    @staticmethod
    def from_json(json_str):
        return jsonpickle.decode(json_str)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        raise TypeError('unhashable type')