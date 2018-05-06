import time
from MBTAriderSegmentation.config import *
from MBTAriderSegmentation.segmentation import Segmentation

# Hierarchical pipeline
import time
t0 = time.time()
start_month='1710'
duration=1
segmentation = Segmentation(start_month=start_month, duration=duration)
segmentation.get_rider_segmentation(hierarchical=True)
print("Hierarchical clustering time: ", time.time() - t0)

# Non-hierarchical pipeline
t0 = time.time()
start_month='1710'
duration=1
segmentation = Segmentation(start_month=start_month, duration=duration)
segmentation.get_rider_segmentation(hierarchical=False)
print("Non-hierarchical clustering time: ", time.time() - t0)
