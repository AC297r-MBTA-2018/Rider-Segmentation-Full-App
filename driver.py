import time
from MBTAriderSegmentation.config import *
from MBTAriderSegmentation.profile import ClusterProfiler

# profile.py & report.py
start_months = ['1612','1701','1702','1703','1704','1705','1706','1707','1708','1709','1710','1711']
for start_month in start_months:
    print('Profiling month = {}...'.format(start_month))
    duration=1
    hier_flags = [True, False]
    algo_types = ['kmeans', 'lda']
    # by_cluster = True
    for hier_flag in hier_flags:
        for algo_type in algo_types:
            t0 = time.time()
            profiler = ClusterProfiler(start_month=start_month, duration=duration, hierarchical=hier_flag)
            profiler.extract_profile(algorithm=algo_type, by_cluster=True)
            print("[by_cluster = True] Profile time: ", time.time() - t0)
    # by_cluster = False
    t0 = time.time()
    profiler = ClusterProfiler(start_month=start_month, duration=duration, hierarchical=True)
    profiler.extract_profile(algorithm='kmeans', by_cluster=False)
    print("[by_cluster = False] Profile time: ", time.time() - t0)
