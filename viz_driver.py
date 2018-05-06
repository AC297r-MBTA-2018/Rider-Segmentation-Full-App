import time
from MBTAriderSegmentation.config import *
from MBTAriderSegmentation.visualization import Visualization

# load data
start_month='1710'
duration=1
viz = Visualization(start_month=start_month, duration=duration)
viz.load_data(by_cluster=True, hierarchical=True, w_time=None, algorithm='lda')

# plot cluster_size, avg_num_trips
viz.plot_cluster_size()
viz.plot_avg_num_trips()

# PCA plot
viz.visualize_clusters_2d()

# plot temporal patterns
viz.plot_all_hourly_patterns()

# generate geographical patterns as html files
unique_clusters = list(viz.df['cluster'].unique())
map_urls = []
for cluster in unique_clusters:
    map_urls.append(viz.plot_cluster_geo_pattern(cluster))

# plot demographics distribution
viz.plot_demographics(grp='race', stacked=True)
viz.plot_demographics(grp='edu', stacked=False)
