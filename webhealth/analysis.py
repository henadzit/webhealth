
import bisect
import MySQLdb


class AnalysisHelper(object):
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

    def find_failure_intersection(self, failures_dict0, failures_dict1, threshold=120):
        overlapped_websites = set()

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

                if abs((f0 - failures1[i]).total_seconds()) <= threshold:
                    # overlap!
                    overlapped_websites.add(w0)
                    break

                # checking right
                i += 1

                if i == len(failures1):
                    # reached the right end again
                    continue

                if (failures1[i] - f0).total_seconds() <= threshold:
                    # overlap!
                    overlapped_websites.add(w0)
                    break

        return overlapped_websites