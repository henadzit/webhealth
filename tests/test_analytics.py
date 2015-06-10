
import datetime
import mock
import pytest

from webhealth.analysis import AnalysisHelper


@pytest.fixture()
def mocked_cursor(request):
    patcher = mock.patch('webhealth.analysis.MySQLdb.connect')

    def fin():
        patcher.stop()
    request.addfinalizer(fin)

    return patcher.start().return_value.cursor.return_value


@pytest.fixture()
def analysis_helper(mocked_cursor):
    # mocked_cursor fixture is here only to force the order of
    # fixture initialization
    return AnalysisHelper('test_username',
                          'test_password,',
                          'test_db')


def test_get_probes_count(analysis_helper, mocked_cursor):
    mocked_cursor.fetchone.return_value = (1,)

    assert 1 == analysis_helper.get_probes_count('test_node_id')
    assert 1 == mocked_cursor.execute.call_count


def _ts(secs):
    return datetime.datetime.utcfromtimestamp(secs)


@pytest.mark.parametrize('failures_dict0, failures_dict1, expected', [
    # simple, positive
    ({'a.com': [_ts(15)]}, {'a.com': [_ts(70)]}, {'a.com'}),
    ({'a.com': [_ts(70)]}, {'a.com': [_ts(15)]}, {'a.com'}),
    # simple, positive
    ({'a.com': [_ts(1000)]}, {'a.com': [_ts(10), _ts(1010)]}, {'a.com'}),
    ({'a.com': [_ts(10), _ts(1010)]}, {'a.com': [_ts(1000)]}, {'a.com'}),
    # simple, negative
    ({'a.com': [_ts(10000)]}, {'a.com': [_ts(10), _ts(70)]}, set()),
    ({'a.com': [_ts(10), _ts(70)]}, {'a.com': [_ts(10000)]}, set()),
    # multiple
    ({'a.com': [_ts(10)], 'b.com': [_ts(1000)]},
     {'a.com': [_ts(20)], 'b.com': [_ts(1010)]},
     {'a.com', 'b.com'}),
    ({'a.com': [_ts(10)], 'b.com': [_ts(10)]},
     {'a.com': [_ts(10)], 'b.com': [_ts(1000)]},
     {'a.com'}),
])
def test_find_failure_intersection(analysis_helper, failures_dict0, failures_dict1, expected):
    assert expected == analysis_helper.find_failure_intersection(failures_dict0, failures_dict1, 120)