# Script to generate static json data for Github version of the dashboard #
import utils

start_months = ['1612', '1701', '1702', '1703', '1704', '1705', '1706', '1707', '1708', '1709', '1710', '1711']
algorithms = ['kmeans', 'lda']
views = ['overview', 'hierarchical', 'non-hierarchical']
duration = '1'
time_weight = '0'

utils.generate_json(views, start_months, algorithms, duration, time_weight)
