
import bisect
from collections import defaultdict
import datetime
import MySQLdb
import pandas as pd


class AnalysisHelper(object):
    """
    Some of operations require data pre-processing, here some commands:
    alter table metrics_upd add column end_time_n datetime not null;
    update metrics_upd set end_time_n = FROM_UNIXTIME(UNIX_TIMESTAMP(end_time) - UNIX_TIMESTAMP(end_time) % 60);

    alter table metrics_upd change success failure tinyint not null;
    update metrics_upd set failure = if(reason=0, 0, 1);
    """
    def __init__(self, username, password, db_name, host='localhost'):
        self.db = MySQLdb.connect(host=host,
                                  user=username,
                                  passwd=password,
                                  db=db_name)

    def get_probes_count(self, node_id):
        # this assumes that all website got approximately equal number of probes
        c = self.db.cursor()
        c.execute('select count(*) as c from metrics '
                  'where node_id = %s '
                  'group by website '
                  'order by c desc', (node_id,))
        probe_count = int(c.fetchone()[0])
        c.close()
        return probe_count

    def get_node_ids(self):
        c = self.db.cursor()
        c.execute('select distinct node_id from metrics')
        node_ids = [c.fetchone()[0] for _ in range(c.rowcount)]
        c.close()
        return node_ids

    def get_failures(self, node_id, threshold_secs=90, upper_failure_threshold=0.2):
        """Find websites which have experienced two or more consecutive failures
        """
        probes_count = self.get_probes_count(node_id)

        c = self.db.cursor()
        c.execute('select website, end_time from metrics where reason != 0 '
                  'and node_id = %s order by end_time', (node_id,))

        failed_websites = set()
        website2failure_time = defaultdict(list)
        for _ in range(c.rowcount):
            website, end_time = c.fetchone()

            if not website2failure_time[website]:
                website2failure_time[website].append(end_time)
            else:
                if end_time <= website2failure_time[website][-1] + datetime.timedelta(seconds=threshold_secs):
                    failed_websites.add(website)

                website2failure_time[website].append(end_time)
        c.close()

        for k, v in list(website2failure_time.iteritems()):
            # I don't think it makes sense to take seriously websites which fail
            # more than certain rate
            if 1.0 * len(v) / probes_count > upper_failure_threshold:
                failed_websites.remove(k)

        return {w: website2failure_time[w] for w in failed_websites}

    def find_failure_intersection(self, failures_dict0, failures_dict1, threshold_sec=60, threshold_occ=1):
        overlapped_websites = defaultdict(int)

        for w0, failures0 in failures_dict0.iteritems():
            for f0 in failures0:
                if w0 not in failures_dict1 or not failures_dict1[w0]:
                    continue

                failures1 = failures_dict1[w0]

                i = bisect.bisect_right(failures1, f0)

                # checking left
                if i == len(failures1):
                    # reached the right end
                    i -= 1

                if abs((f0 - failures1[i]).total_seconds()) <= threshold_sec:
                    # overlap!
                    overlapped_websites[w0] += 1
                    continue

                # checking right
                i += 1

                if i == len(failures1):
                    # reached the right end again
                    continue

                if (failures1[i] - f0).total_seconds() <= threshold_sec:
                    # overlap!
                    overlapped_websites[w0] += 1
                    break

        return set([k for k, v in overlapped_websites.iteritems() if v >= threshold_occ])

    def plot_duration_and_success(self, website):
        c = self.db.cursor()

        c.execute('select sum(failure), sum(duration), end_time_n from metrics_upd '
                  'where website=%s '
                  'group by end_time_n '
                  'having count(end_time_n) >= 2', (website,))

        result = {'time': [], 'sum(failure)': [], 'sum(duration)': []}

        for _ in range(c.rowcount):
            failure, duration, time = c.fetchone()

            result['time'].append(time)
            result['sum(failure)'].append(int(failure))
            result['sum(duration)'].append(float(duration))
        c.close()

        df = pd.DataFrame(result)
        return df.plot(x='time', secondary_y='sum(failure)', figsize=(16, 12))
