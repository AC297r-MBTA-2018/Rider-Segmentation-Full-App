from sklearn.decomposition import PCA
from datetime import datetime
import os
import re
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from branca.colormap import linear
import IPython

from MBTAriderSegmentation.config import *
from MBTAriderSegmentation.profile import ClusterProfiler

SMALL_FONT = 12
MEDIUM_FONT = 15
LARGE_FONT = 100

sns.set()
plt.rc('font', size=SMALL_FONT)          # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_FONT)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_FONT)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_FONT)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_FONT)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_FONT)    # legend fontsize
plt.rc('figure', titlesize=LARGE_FONT)  # fontsize of the figure title

class Visualization:
    def __init__(self, start_month='1701', duration=1):
        self.start_month = start_month
        self.duration = duration

        # setting the file path based on start month and duration
        start = datetime.strptime(self.start_month, "%y%m").strftime("%Y-%b")
        if self.duration > 1:
            end = datetime.strptime(str(int(self.start_month) + self.duration-1), "%y%m").strftime("%Y-%b")
            self.input_path = DATA_PATH + PROFILE_PATH + start + '_to_' + end + '/'
            self.output_path = DATA_PATH + VIZ_PATH + start + '_to_' + end + '/'
        else:
            self.input_path = DATA_PATH + PROFILE_PATH + start + '/'
            self.output_path = DATA_PATH + VIZ_PATH + start + '/'

        if not os.path.isdir(self.input_path):
            os.makedirs(self.input_path)

        self.param_keys = ['view', 'month', 'duration', 'w_time', 'algorithm']

    def __split(self, delimiters, string, maxsplit=0):
        """
        Function to split file name for matching cached results
        """
        regexPattern = '|'.join(map(re.escape, delimiters))
        return re.split(regexPattern, string, maxsplit)

    def __get_cached_params_list(self):
        """
        Function to find parameter combinations of cached results
        """
        cached_combo = []
        delimiters = ['_', '.']
        for filename in os.listdir(self.input_path):
            if filename.endswith(".csv"):
                str_split = self.__split(delimiters, filename)[:-1]
                if len(str_split) > 5:
                    param_vals = [str_split[0]] + str_split[3:]
                else:
                    param_vals = [str_split[0]] + str_split[3:5] + ['na', 'na']
                cached_combo.append(dict(zip(self.param_keys, param_vals)))
        return cached_combo

    def __read_csv(self, req_param_dict, by_cluster):
        if by_cluster:
            self.df = pd.read_csv(self.input_path + req_param_dict['view'] + '_' +
                                      PROFILE_FILE_PREFIX +
                                       req_param_dict['month'] + '_' +
                                       req_param_dict['duration'] + '_' +
                                       req_param_dict['w_time'] + '_' +
                                       req_param_dict['algorithm'] +
                                       '.csv', index_col=0)
        else:
            self.df = pd.read_csv(self.input_path + req_param_dict['view'] + '_' +
                                      PROFILE_FILE_PREFIX +
                                       req_param_dict['month'] + '_' +
                                       req_param_dict['duration'] +
                                       '.csv', index_col=0)


    def load_data(self, by_cluster=False, hierarchical=False, w_time=None, algorithm=None):
        # check if the requested data is in the cache directory ready to go
        cached_combo = self.__get_cached_params_list()
        if by_cluster:
            # parse hierarchical request
            if hierarchical:
                self.req_view = 'hierarchical'
            else:
                self.req_view = 'non-hierarchical'

            # parse w_time request
            if not w_time:
                self.req_w_time = str(0)
            else:
                self.req_w_time = str(w_time)

            # parse algo request
            if not algorithm:
                self.req_algo = 'kmeans'
            else:
                self.req_algo = algorithm

        else:
            self.req_view = 'overview'
            self.req_w_time = 'na'
            self.req_algo = 'na'

        req_param_vals = [self.req_view, self.start_month, str(self.duration), self.req_w_time, self.req_algo]
        req_param_dict = dict(zip(self.param_keys, req_param_vals))

        # check if request params are cached in profiler
        if req_param_dict in cached_combo:
            self.__read_csv(req_param_dict, by_cluster)
        else:  # Get the cluster profile again
            profiler = ClusterProfiler(hierarchical=hierarchical, w_time=w_time, start_month=self.start_month, duration=self.duration)
            profiler.extract_profile(algorithm=algorithm, by_cluster=by_cluster)
            del profiler
            self.__read_csv(req_param_dict, by_cluster)


    def visualize_clusters_2d(self):
        fig, ax = plt.subplots(1, 1, figsize=(10, 7))
        for grp in self.df.viz_grp.unique():
            if grp == 1:
                grp_label = '<= 20 Trips/Month'
            else:
                grp_label = '> 20 Trips/Month'
            ax.scatter(x=self.df[self.df.viz_grp == grp].viz_pca1,
                       y=self.df[self.df.viz_grp == grp].viz_pca2,
                       s=self.df[self.df.viz_grp == grp].viz_size/100,
                       label='{} Groups'.format(grp_label),
                       alpha=0.5)
        ax.set_xlabel('PCA Component 1')
        ax.set_ylabel('PCA Component 2')
        ax.set_title('Clusters visualized on PCA axes')

        lgnd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        # change the marker size manually for both lines
        for handle in lgnd.legendHandles:
            handle._sizes = [300]
        plt.show()

    def plot_cluster_hourly_pattern(self, cluster):
        time_feats = [col for col in self.df.columns if 'hr_' in col]
        heatmap_matrix = self.df.loc[self.df['cluster'] == cluster, time_feats].values.reshape(7, 24)
        fig, ax = plt.subplots(1, 1, figsize = (18, 4))
        ax.set_title('{} - cluster {}'.format(self.req_algo, cluster))
        ax.set_xlabel('Hours in the day')
        ax.set_ylabel('Day of week')
        sns.heatmap(heatmap_matrix,
                    yticklabels=['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'],
                    cmap="YlGnBu", ax=ax)
        plt.show()

    def plot_all_hourly_patterns(self):
        for i, cluster in self.df.iterrows():
            self.plot_cluster_hourly_pattern(cluster.cluster)

    def plot_cluster_geo_pattern(self, cluster):
        geo_cols = [col for col in self.df.columns if 'zipcode' in col]
        zipcodes = [z.split('_')[-1] for z in geo_cols]
        geo_json_data = json.load(open(DATA_PATH + INPUT_PATH + 'geojson/ma_massachusetts_zip_codes_geo.min.json'))
        filtered_geo_json = [d for d in geo_json_data['features'] if d['properties']['ZCTA5CE10'] in zipcodes]
        geo_json_data['features'] = filtered_geo_json

        data = self.df.loc[self.df['cluster']==cluster, geo_cols].T
        data['zipcodes'] = zipcodes
        # rename columns and check if geopattern is successfully extracted
        try:
            data.columns = ["geopattern", "zipcodes"]
        except ValueError:
            raise ValueError("Check cluster ID. The unique cluster IDs are {}".format(self.df['cluster'].unique()))

        colormap = linear.YlGnBu.scale(data.geopattern.min(), data.geopattern.max())
        data_dict = data.set_index('zipcodes')['geopattern']


        # initialize map
        m = folium.Map([42.34, -71.1], zoom_start=9.5)

        # plot geo data
        folium.GeoJson(
            geo_json_data,
            style_function=lambda feature: {
                'fillColor': colormap(data_dict[feature['properties']['ZCTA5CE10']]),
                'color': 'black',
                'weight': 1,
                'dashArray': '5, 5',
                'fillOpacity': 0.9,
            }
        ).add_to(m)

        # add colormap and legend
        colormap.caption = 'Trip Origin Density (%)'
        colormap.add_to(m)

        # save visualization
        output_filename = 'GEO-chart' + '_' + self.req_view + '_' + self.start_month + '_' + str(self.duration) + '_' + self.req_w_time + '_' + self.req_algo + '_cluster'+ str(cluster) + '.html'
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)
        m.save(os.path.join(self.output_path + output_filename))

        # display
        url = self.output_path + output_filename
        return url

    def __single_feature_viz(self, feature, title, ylabel, xlabel):
        '''
        Single-bar plot visualization of cluster_feat VS. cluster #
        cluster_feat: ['cluster_size', 'cluster_avg_num_trips']
        '''
        ax = self.df.set_index('cluster')[[feature]].plot(kind='bar', rot=0,
                                                                  title=title,
                                                                  figsize=(10, 7), colormap=COLORMAP)
        ax.legend_.remove()
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        plt.show()

    def plot_cluster_size(self):
        if self.req_view == 'overview':
            title = 'Overview \n Number of Riders'
            xlabel = 'overview'
        else:
            title = self.req_view.upper() + '\nCluster Size'
            xlabel = 'Cluster ID'
        self.__single_feature_viz('cluster_size', title=title, ylabel='Number of riders', xlabel=xlabel)

    def plot_avg_num_trips(self):
        if self.req_view == 'overview':
            title = 'Overview \n Average # of Trips'
            xlabel = 'Overview'
        else:
            title = self.req_view.upper() + '\nAverage # of Trips'
            xlabel = 'Cluster ID'
        self.__single_feature_viz('cluster_avg_num_trips', title=title, ylabel='Avg # of Trips', xlabel=xlabel)

    def __group_feature_viz(self, grp_key, stacked, title, ylabel, xlabel):
        '''
        Multi-bar plot visualization of cluster_feat VS. cluster #
        cluster_feat_key: String, in ['servicebrand', 'usertype', 'tariff',
                                        'race', 'emp', 'edu', 'inc']
        stacked: boolean, default = True for stacked bar plot; False for side-by-side bar plot
        '''
        key = grp_key + '_'
        feat_grps = [col for col in self.df.columns if key in col]
        ax = self.df.set_index('cluster')[feat_grps].plot(kind='bar', rot=0, stacked=stacked,
                                                             title=title,
                                                             legend=False, figsize=(10, 7), colormap=COLORMAP)
        ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        plt.show()

    def plot_demographics(self, grp, stacked=True):
        """
        grp: ['race', 'emp', 'edu', 'inc']
        """
        if grp not in ['race', 'emp', 'edu', 'inc']:
            raise ValueError("Not a type of ticket purchasing field. Options=['race', 'emp', 'edu', 'inc']")

        if self.req_view == 'overview':
            title_dict = {
                'race': 'Overview \n Race',
                'emp': 'Overview \n Unemployment',
                'edu': 'Overview \n Education',
                'inc': 'Overview \n Income'
            }
            xlabel='Overview'
        else:
            title_dict = {
                'race': self.req_view.upper() + '\n Race',
                'emp': self.req_view.upper() + '\n Unemployment',
                'edu': self.req_view.upper() + '\n Education',
                'inc': self.req_view.upper() + '\n Income'
            }
            xlabel='Cluster ID'

        self.__group_feature_viz(grp, stacked=stacked, title=title_dict[grp], ylabel='% Rider', xlabel=xlabel)

    def plot_ticket_purchasing_patterns(self, grp, stacked=True):
        """
        grp: ['servicebrand', 'usertype', 'tariff']
        """
        if grp not in ['servicebrand', 'usertype', 'tariff']:
            raise ValueError("Not a type of ticket purchasing field. Options=['servicebrand', 'usertype', 'tariff']")

        if self.req_view == 'overview':
            title_dict = {
                'servicebrand': 'Overview \n Servicebrand',
                'usertype': 'Overview \n User Type',
                'tariff': 'Overview \n Tariff Type'
            }
            xlabel='Overview'
        else:
            title_dict = {
                'servicebrand': self.req_view.upper() + '\n Servicebrand',
                'usertype': self.req_view.upper() + '\n User Type',
                'tariff': self.req_view.upper() + '\n Tariff Type'
            }
            xlabel='Cluster ID'

        self.__group_feature_viz(grp, stacked=stacked, title=title_dict[grp], ylabel='% Rider', xlabel=xlabel)
