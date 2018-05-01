import time
from MBTAriderSegmentation.config import *
from MBTAriderSegmentation.visualization import Visualization
from MBTAriderSegmentation.profile import ClusterProfiler

t0 = time.time()
start_month='1710'
duration=1
profiler = ClusterProfiler(start_month=start_month, duration=duration, hierarchical=False)
profiler.extract_profile(algorithm='kmeans', by_cluster=True)
print("Profile time: ", time.time() - t0)

# start_month='1710'
# duration=1
# viz = Visualization(start_month=start_month, duration=duration)
# viz.load_data(by_cluster=True, hierarchical=True, w_time=None, algorithm='lda')
# print(viz.df)
