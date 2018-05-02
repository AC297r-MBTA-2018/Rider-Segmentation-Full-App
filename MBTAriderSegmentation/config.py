import os, sys
import warnings
warnings.filterwarnings('ignore')

DATA_PATH = os.path.dirname(os.path.abspath(__file__)) + '/data/'
INPUT_PATH = 'input/'  # this is for afc_odx, stops, fareprod, census, geojson
FEATURE_PATH = 'cached_features/'  # output of FeatureExtractor
CLUSTER_PATH = 'cached_clusters/'  # output of Segmentation
PROFILE_PATH = 'cached_profiles/'  # output of ClusterProfiler
VIZ_PATH = 'cached_viz/'
REPORT_PATH = 'report_models/'

FEATURE_FILE_PREFIX = 'rider_features_'
CLUSTER_FILE_PREFIX = 'rider_clusters_'
PROFILE_FILE_PREFIX = 'cluster_profiles_'

# global params for segmentation.py
ALGORITHMS = ['kmeans', 'lda']
RANDOM_STATE = 12345
MAX_ITER = 200
TOL = 1e-3

# global params for visualization.py
COLORMAP = 'Paired'  # colormap

# rider type mapping for generative report
RIDER_LABEL_DICT = {
    0: 'random riders',
    1: 'weekend riders',
    2: 'less flexible commuters with normal commute hours',
    3: 'less flexible commuters with early commute hours',
    4: 'more flexible commuters with normal commute hours',
    5: 'more flexible commuters with early commute hours',
    6: 'weekend riders who also ride over weekdays'
}
