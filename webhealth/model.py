
import jsonpickle


class Metric(object):
    STATE_OK = 0
    STATE_BAD_HTTP_CODE = 1
    STATE_TIMEOUT = 2
    STATE_TOO_MANY_REDIRECTS = 3
    STATE_OTHER_FAILURE = 100

    def __init__(self, website, state, start, end, http_code):
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