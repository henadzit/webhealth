import datetime
import pytest

from webhealth.model import Metric


@pytest.fixture()
def metric_ok():
    now = datetime.datetime.utcnow()
    before = now - datetime.timedelta(seconds=10)
    return Metric('node_id', 'example.com', Metric.STATE_OK, before, now, 200)
