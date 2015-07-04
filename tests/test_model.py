
from webhealth.model import Metric


def test_json(metric_ok):
    json = metric_ok.to_json()

    deserialized = Metric.from_json(json)

    assert metric_ok == deserialized


def test_end_1min(metric_ok):
    assert 0 == metric_ok.end_1min.second
    assert 0 == metric_ok.end_1min.microsecond


def test_end_5min(metric_ok):
    assert 0 == metric_ok.end_5min.second
    assert 0 == metric_ok.end_5min.microsecond
    assert 0 == metric_ok.end_5min.minute % 5