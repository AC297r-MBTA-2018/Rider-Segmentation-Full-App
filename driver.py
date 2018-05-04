import time
from MBTAriderSegmentation.config import *
from MBTAriderSegmentation.visualization import Visualization
from MBTAriderSegmentation.profile import ClusterProfiler

# Cluter Profiler & Auto Report Generation
start_month='1711'
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

# Visualization
# start_month='1710'
# duration=1
# viz = Visualization(start_month=start_month, duration=duration)
# viz.load_data(by_cluster=True, hierarchical=True, w_time=None, algorithm='lda')
# print(viz.df)
