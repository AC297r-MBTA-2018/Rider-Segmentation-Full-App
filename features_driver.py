import time
from MBTAriderSegmentation.config import *
from MBTAriderSegmentation.features import FeatureExtractor

import time
t0 = time.time()
start_month='1710'
duration=1
extractor = FeatureExtractor(start_month=start_month, duration=duration).extract_features()
print("feature extraction time: ", time.time() - t0)
