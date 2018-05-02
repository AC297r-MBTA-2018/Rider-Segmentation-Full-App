from copy import deepcopy
import json
import numpy as np
import pandas as pd
import re
from datetime import datetime

import sys, os
sys.path.append('././')  # allow access to MBTAriderSegmentation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # allow reading files from within MBTAriderSegmentation

from MBTAriderSegmentation.config import *  # setting global file params
from MBTAriderSegmentation.features import FeatureExtractor
from MBTAriderSegmentation.segmentation import Segmentation
from MBTAriderSegmentation.profile import ClusterProfiler

#######################################################################
# ######################## HELPER FUNCTIONS ##########################
#######################################################################

def _get_profile_path(start_month, duration):
    start = datetime.strptime(start_month, "%y%m").strftime("%Y-%b")
    if int(duration) > 1:
        end = datetime.strptime(str(int(start_month) + duration - 1), "%y%m").strftime("%Y-%b")
        profile_path = DATA_PATH + PROFILE_PATH + start + '_to_' + end + '/'

    else:
        profile_path = DATA_PATH + PROFILE_PATH + start + '/'
    return profile_path

def _get_day_hr_array():
    """
    Function to generate day and hour arrays
    """
    day_id = np.array([x for x in range(1, 8)])
    day = [np.asscalar(x) for x in np.repeat(day_id, [24], axis=0)]
    hour = [x for x in range(1, 25)] * 7
    return day, hour


def _get_col_group_info(prefix, exceptions, df):
    """
    Function to get the column names, column indices and group values
    This groups features into groups such as race, agesex, temporal patterns...etc.
    and enables access to the right columns when df is turned into matrix form
    """
    # get all col names with prefix
    col_names = [col for col in df.columns if prefix in col]
    # if exceptions are specified
    if exceptions:
        # filter out col names with exceptions
        for exception in exceptions:
            col_names = [col for col in col_names if exception not in col]
    # get column indices of the finalized col names in the df
    col_index_list = [list(df.columns.values).index(col) for col in col_names]
    # group values are col_names minus the prefix
    col_group_values = [col.split('_', 1)[1] for col in col_names]
    return col_names, col_index_list, col_group_values

def _get_vis_params(backend_data):
    """
    Function to configure the parameters needed for visualization based on cols of backend_data
    """
    # params for temporal patterns
    day, hour = _get_day_hr_array()
    hr_cols, hr_cols_idx, _ = _get_col_group_info('hr_', None, backend_data)

    # params for geographical patterns
    filename = DATA_PATH + INPUT_PATH + 'geojson/ma_massachusetts_zip_codes_geo.min.json'
    if filename:
        with open(filename, 'r') as f:
            ma_zipcode_geojson = json.load(f)
    zip_cols, zip_cols_idx, zipcodes = _get_col_group_info('zipcode_', None, backend_data)

    # params for purchasing patterns
    _, user_cols_idx, user_grps = _get_col_group_info('usertype_', None, backend_data)
    _, tariff_cols_idx, tariff_grps = _get_col_group_info('tariff_', None, backend_data)
    _, servicebrand_cols_idx, servicebrand_grps = _get_col_group_info('servicebrand_', None, backend_data)

    # params for cluster info
    _, clust_info_cols_idx, clust_info_grps = _get_col_group_info('cluster_', None, backend_data)
    _, viz_cols_idx, viz_grps = _get_col_group_info('viz_', None, backend_data)

    # params for demographics
    _, race_cols_idx, race_grps = _get_col_group_info('race_', ['_nb'], backend_data)
    _, agesex_cols_idx, agesex_grps = _get_col_group_info('as_', ['_nb'], backend_data)
    _, income_cols_idx, income_grps = _get_col_group_info('inc_', ['_nb', '_med'], backend_data)
    _, edu_cols_idx, edu_grps = _get_col_group_info('edu_', ['_nb'], backend_data)
    _, pov_cols_idx, pov_grps = _get_col_group_info('pov_', ['_nb'], backend_data)
    _, emp_cols_idx, emp_grps = _get_col_group_info('emp_', ['_nb'], backend_data)
    _, hu_cols_idx, hu_grps = _get_col_group_info('hu_', ['_nb'], backend_data)
    _, hstat_cols_idx, hstat_grps = _get_col_group_info('hstat_', ['_nb'], backend_data)

    vis_params = {
        # temporal pattern params
        'day': day,
        'hour': hour,
        'hr_cols_idx': hr_cols_idx,

        # geographical pattern params
        'zipcodes': zipcodes,
        'zip_cols_idx': zip_cols_idx,
        'ma_zipcode_geojson': ma_zipcode_geojson,

        # purchasing pattern params
        'usertype_cols_idx': user_cols_idx,
        'usertype_grps': user_grps,
        'tariff_cols_idx': tariff_cols_idx,
        'tariff_grps': tariff_grps,
        'servicebrand_cols_idx': servicebrand_cols_idx,
        'servicebrand_grps': servicebrand_grps,

        # cluster info params
        'clust_info_cols_idx': clust_info_cols_idx,
        'clust_info_grps': clust_info_grps,

        # visualizing cluster on pca components params
        'viz_cols_idx': viz_cols_idx,
        'viz_grps': viz_grps,

        # demographics params
        'race_cols_idx': race_cols_idx,
        'race_grps': race_grps,
        'agesex_cols_idx': agesex_cols_idx,
        'agesex_grps': agesex_grps,
        'income_cols_idx': income_cols_idx,
        'income_grps': income_grps,
        'edu_cols_idx': edu_cols_idx,
        'edu_grps': edu_grps,
        'pov_cols_idx': pov_cols_idx,
        'pov_grps': pov_grps,
        'emp_cols_idx': emp_cols_idx,
        'emp_grps': emp_grps,
        'hu_cols_idx': hu_cols_idx,
        'hu_grps': hu_grps,
        'hstat_cols_idx': hstat_cols_idx,
        'hstat_grps': hstat_grps,

    }
    return vis_params


def _format_time_patterns(day, hour, hr_cols_idx, data_matrix):
    """
    Function to format temporal patterns into frontend format
    """
    temporal_patterns = []
    for cluster in data_matrix:
        pattern_i = {'day': day, 'hour': hour, 'value': [np.asscalar(x) for x in cluster[hr_cols_idx]]}
        pattern_i = [dict(zip(pattern_i, col)) for col in zip(*pattern_i.values())]
        temporal_patterns.append(pattern_i)
    return temporal_patterns

def _format_geo_patterns(zipcodes, zip_cols_idx, ma_zipcode_geojson, data_matrix):
    """
    Functino to format geographical patterns into frontend format
    """
    # filter the MA geojson to only consider zipcodes in the riders_df for processing efficiency
    zoi_geojson = [d for d in ma_zipcode_geojson['features'] if d['properties']['ZCTA5CE10'] in zipcodes]
    geographical_patterns = []
    for cluster in data_matrix:
        pattern_i = deepcopy(zoi_geojson)  # make a zoi_geojson for each cluster
        # loop through each zipcode geojson and push the value for that zipcode in
        for zipcode_geo in pattern_i:
            # the current zipcode in the loop
            zipcode_i = zipcode_geo['properties']['ZCTA5CE10']
            # the value count fot the current zipcode in cluster
            value = np.asscalar(cluster[zip_cols_idx][zipcodes.index(zipcode_i)])
            # push value into zipcode geojson
            zipcode_geo['properties']['value'] = value
        geographical_patterns.append(pattern_i)
    return geographical_patterns

def _format_one_group_pattern(grps, cols_idx, data_matrix):
    """
    Function to format one group pattern (e.g. race or usertype) into frontend format
    """
    group_pattern = []
    for cluster in data_matrix:
        pattern_i = {}
        for grp, idx in zip(grps, cols_idx):
            pattern_i[grp] = np.asscalar(cluster[idx])
        group_pattern.append(pattern_i)
    return group_pattern

def _format_group_patterns(grp_names, vis_params, data_matrix):
    """
    Function to format multiple group patterns
    INPUT:
        grp_names: A list of strings, the group prefix in vis_params
            keys e.g. race or clust_info, required
        vis_params: A dictionary of visualization parameters
            This is the output of _get_vis_params(), required
        data_matrix: A matrix, backend_data in matrix form, required
    RETURN:
        group_patterns: A dictionary of group patterns
            in the form of {'grp_name': [{pattern for cluster 1}, {pattern for cluster 2}]}
            e.g. {'race': [patterns], 'agesex': [patterns]...}
    """
    group_patterns = {}
    for name in grp_names:
        grps = name + '_grps'
        cols_idx = name + '_cols_idx'
        group_patterns[name] = _format_one_group_pattern(vis_params[grps],
                                                         vis_params[cols_idx], data_matrix)
    return group_patterns

def _rename_group_labels(frontend_data):
    """
    Function to rename group labels so it is easier to plot in frontend
    """
    renamed = deepcopy(frontend_data)
    group_rename_dict = {
        'race': {'asn': 'Asian', 'blk': 'Black', 'hisp': 'Hispanic', 'othr': 'Other', 'wht': 'White'},
        'agesex': {'f_br0': 'Female Age 0-9', 'f_br1': 'Female Age 10-19', 'f_br2': 'Female Age 20-29',
                   'f_br3': 'Female Age 30-39', 'f_br4': 'Female Age 40-49', 'f_br5': 'Female Age 50-59',
                   'f_br6': 'Female Age 60-69', 'f_br7': 'Female Age 70+', 'm_br0': 'Male Age 0-9',
                   'm_br1': 'Male Age 10-19', 'm_br2': 'Male Age 20-29', 'm_br3': 'Male Age 30-39',
                   'm_br4': 'Male Age 40-49', 'm_br5': 'Male Age 50-59', 'm_br6': 'Male Age 60-69',
                   'm_br7': 'Male Age 70+'},
        'clust_info': {'id': 'ID', 'avg_num_trips': 'Average # of Trips', 'demo_fam': 'Number of Families',
                       'demo_hh': 'Number of Households', 'demo_house_unit': 'Number of House Units',
                       'demo_med_income': 'Median House Income', 'demo_pop': 'Population',
                       'demo_pop_16': 'Population over 16 (Labor Force)', 'demo_pop_25': 'Population over 25',
                       'size': 'Size'},
        'edu': {'bd': '4: Bachelor', 'gd': '5: Graduate', 'hs': '2: High School',
                'sc': '3: Some College', 'nd': '1: No Degree'},
        'emp': {'employed': 'Employed', 'unemployed': 'Unemployed'},
        'hstat': {'fam': 'Family Households', 'mcf': 'Married Couple Families',
                  'mcf_nchild': 'Married Coule Families - No Children',
                  'mcf_ychild': 'Married Coule Families - With Children', 'nf': 'Not Family Households',
                  'nf_alone': 'Not Family Living Alone',
                  'nf_with_ui': 'Not Family Living with Unreleated Individuals',
                  'spf': 'Single Parent Family Households',
                  'spf_nchild': 'Single Parent Families - No Children',
                  'spf_ychild': 'Single Parent Families - With Children'},
        'hu': {'occ_hh': 'Occupied Households', 'unocc': 'Unoccupied Households'},
        'income': {'br0': '1: <$25K', 'br1': '2: $25K-$50K', 'br2': '3: $50K-$75K',
                   'br3': '4: $75K-$100K', 'br4': '5: $100K-$150K', 'br5': '6: $150K-$200K',
                   'br6': '7: $200K+'},
        'pov': {'fam_in_pov': 'Families in Poverty', 'fam_not_in_pov': 'Families Not in Poverty'}}
    for cluster, info in frontend_data.items():
        for item, groups in info.items():
            if item not in ['viz', 'usertype', 'tariff', 'servicebrand', 'temporal_patterns', 'geographical_patterns', 'report']:
                renamed[cluster][item] = dict((group_rename_dict[item][key], value) for (key, value) in groups.items())
    return renamed


#######################################################################
# ######################## BACKEND FUNCTIONS ##########################
#######################################################################

def get_backend_data(view='overview', start_month='1710', duration='1',
                     time_weight='0', algorithm='lda'):
    """
    """
    # parse request to generate profile filename
    profile_path = _get_profile_path(start_month=start_month, duration=duration)
    if view == 'overview':
        profile_filename = profile_path + view + '_' + PROFILE_FILE_PREFIX + start_month + '_' + duration + '.csv'
    elif view in ['hierarchical', 'non-hierarchical']:
        profile_filename = profile_path + view + '_' + PROFILE_FILE_PREFIX + start_month + '_' + duration + '_' + time_weight + '_' + algorithm + '.csv'
    else:
        print('File Not Found: {}'.format(profile_filename))
        raise FileNotFoundError
    try:
        backend_data = pd.read_csv(profile_filename, index_col=0)
    except FileNotFoundError:
        print("Recluster....")
        backend_data = None

    # collapse some groups for better visualization e.g. usertype should only have adult, student, senior/TAP and others
    usertype_cols = [col for col in backend_data.columns if "usertype_" in col]
    usertype_to_keep = ['usertype_Adult', 'usertype_Senior', 'usertype_Senior/TAP', 'usertype_Student']
    race_cols = [col for col in backend_data.columns if "race_" in col]
    race_to_keep = ['race_asn', 'race_blk', 'race_hisp', 'race_wht']

    # usertype keep: adult, student, senior + senior/TAP, others
    usertype_to_collapse = [col for col in usertype_cols if col not in usertype_to_keep]
    usertype_othr = backend_data[usertype_to_collapse].sum(axis=1)
    usertype_seniors_TAP = backend_data['usertype_Senior'] + backend_data['usertype_Senior/TAP']  # add senior and senior/TAP
    backend_data.drop(['usertype_Senior', 'usertype_Senior/TAP'] + usertype_to_collapse, axis=1, inplace=True)
    idx_to_insert = backend_data.columns.get_loc("usertype_Adult")
    backend_data.insert(loc=idx_to_insert, column='usertype_Others', value=usertype_othr)
    backend_data.insert(loc=idx_to_insert, column='usertype_Senior/TAP', value=usertype_seniors_TAP)

    # race keep: white, black, hispanic, asian, others
    race_to_collapse = [col for col in race_cols if col not in race_to_keep]
    race_othr = backend_data[race_to_collapse].sum(axis=1)
    backend_data.drop(race_to_collapse, axis=1, inplace=True)
    idx_to_insert = backend_data.columns.get_loc("race_asn")
    backend_data.insert(loc=idx_to_insert, column='race_othr', value=race_othr)

    return backend_data

def get_frontend_data(backend_data):
    """
    """
    vis_params = _get_vis_params(backend_data=backend_data)
    # data_matrix = backend_data.values
    data_matrix = backend_data.drop(['report', 'rider_type'], axis=1).values
    # format temporal patterns
    time_data = _format_time_patterns(vis_params['day'], vis_params['hour'],
                                      vis_params['hr_cols_idx'], data_matrix)
    # format geographical patterns
    geo_data = _format_geo_patterns(vis_params['zipcodes'], vis_params['zip_cols_idx'],
                                    vis_params['ma_zipcode_geojson'], data_matrix)

    # format all other patterns including ticket purchasing patterns, cluster information
    # and demographics distributions
    grp_names = ['usertype', 'tariff', 'servicebrand',  # ticket purchasing groups
                 'clust_info', 'viz',  # cluster info groups e.g. size and avg number of trips
                 # demographics groups
                 'race', 'agesex', 'income', 'edu', 'pov', 'emp', 'hu', 'hstat']
    other_data = _format_group_patterns(grp_names, vis_params, data_matrix)
    other_data = [dict(zip(other_data, col)) for col in zip(*other_data.values())]

    # gather all formatted data and store in a dictionary
    frontend_data = {}
    # append other_data first
    for cluster_id, cluster_data in zip(backend_data['cluster'], other_data):  # each item in other_data is a cluster
        frontend_data[str(cluster_id)] = cluster_data
    # append temporal and geo data
    for i, (cluster_id, cluster_data) in enumerate(frontend_data.items()):
        cluster_data['report'] = backend_data.loc[i, 'report']
        cluster_data['temporal_patterns'] = time_data[int(i)]
        cluster_data['geographical_patterns'] = geo_data[int(i)]

    frontend_data = _rename_group_labels(frontend_data)
    return frontend_data
