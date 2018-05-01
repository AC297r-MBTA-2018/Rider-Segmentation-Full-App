import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import os, sys
import re
from datetime import datetime

from MBTAriderSegmentation.config import *
from MBTAriderSegmentation.report import ReportGenerator

class CensusFormatter:
    """
    Class to format and to return formatted census data
    """
    # column names used to rename raw census columns
    new_col_names = [
        'zipcode', 'state',
        # Race & Ethnicity
        'race_pop_nb', 'race_wht', 'race_blk', 'race_ntv', 'race_asn',
        'race_isld', 'race_othr', 'race_two', 'race_hisp',
        # Age & Sex
        'as_pop_nb', 'as_f_br0', 'as_f_br1', 'as_f_br2', 'as_f_br3',
        'as_f_br4', 'as_f_br5', 'as_f_br6', 'as_f_br7', 'as_m_br0',
        'as_m_br1', 'as_m_br2', 'as_m_br3', 'as_m_br4', 'as_m_br5',
        'as_m_br6', 'as_m_br7',
        # Household Income in 2016 Inflation-Adjusted Dollars
        'inc_med', 'inc_hh_nb', 'inc_br0', 'inc_br1', 'inc_br2',
        'inc_br3', 'inc_br4', 'inc_br5', 'inc_br6',
        # Education Attainment
        'edu_pop_25_nb', 'edu_nd', 'edu_hs', 'edu_sc', 'edu_bd', 'edu_gd',
        # Poverty
        'pov_fam_nb', 'pov_fam_in_pov',
        # Unemployment
        'emp_pop_16_nb', 'emp_unemployed',
        # Housing units
        'hu_house_units_nb',
        # Household Statistics
        'hstat_hh_nb', 'hstat_fam',
        'hstat_mcf', 'hstat_mcf_ychild', 'hstat_mcf_nchild',
        'hstat_spf', 'hstat_spf_ychild', 'hstat_spf_nchild',
        'hstat_nf', 'hstat_nf_alone', 'hstat_nf_with_ui'
    ]
    # dictionary for census groups and prefixes in the renamed census dataframe
    census_groups = {
        'race': 'race_',
        'agesex': 'as_',
        'income': 'inc_',
        'education': 'edu_',
        'poverty': 'pov_',
        'unemployment': 'emp_',
        'housing_units': 'hu_',
        'household': 'hstat_'
    }

    def __init__(self, raw_census_filepath):
        self.raw_census_filepath = raw_census_filepath
        self.census_in_counts = self.__format_raw_census_in_counts(self.raw_census_filepath)
        self.census_in_percents = self.__convert_to_percents(self.census_in_counts)
        self.census_in_proportions = self.__convert_to_proportions(self.census_in_counts)

    def __format_raw_census_in_counts(self, raw_census_filepath):
        """
        DESCRIPTION:
            Function to unify the raw census data format.
            The raw census represents some columns in counts and others
            in percents. This function converts all data representation
            to counts. Specifically, this function formats data pertaining
            to education, poverty and unemployment.
        INPUT:
            raw_census_filepath: A string of file path to raw census data
        RETURN:
            census: A formaated dataframe where data is represented in counts
        """
        census = pd.read_excel(raw_census_filepath, skiprows=3,
                               names=CensusFormatter.new_col_names,
                               dtype={'Unnamed: 0': str})
        # add Unoccupied Housing Unit = Housing units - Households
        census['hu_occ_hh'] = census['hstat_hh_nb']
        census['hu_unocc'] = census['hu_house_units_nb'] - census['hu_occ_hh']
        census['pov_fam_not_in_pov'] = 100 - census['pov_fam_in_pov']
        census['emp_employed'] = 100 - census['emp_unemployed']

        # convert education, poverty and unemployment to numbers
        edu_cols = [col for col in census.columns if 'edu_' in col]
        pov_cols = [col for col in census.columns if 'pov_' in col]
        emp_cols = [col for col in census.columns if 'emp_' in col]

        # convert education from % to numbers
        for col in edu_cols:
            if '_pop_25' not in col:
                census[col] = (round(census[col].mul(census['edu_pop_25_nb']) / 100)).astype(int)
        # convert poverty from % to numbers
        for col in pov_cols:
            if '_fam' not in col:
                census[col] = (round(census[col].mul(census['pov_fam_nb']) / 100)).astype(int)
        # convert unemployment % to numbers
        for col in emp_cols:
            if '_pop_16' not in col:
                census[col] = (round(census[col].mul(census['emp_pop_16_nb']) / 100)).astype(int)
        return census

    def __convert_to_percents(self, census_in_counts):
        """
        DESCRIPTION:
            Function to convert counts distribution into percentages.
            The normalizing columns (e.g. populations, households and
            family units) plus inc_med (median income) are not converted.
        INPUT:
            census_in_counts: A dataframe where census data are in counts.
                This is the output of __format_raw_census_in_counts().
        RETURN:
            converted: A dataframe where census data are in percentages.
        """
        converted = census_in_counts.copy()
        # loop through each demographics profile group
        for cset, prefix in CensusFormatter.census_groups.items():
            # get the column names corresponding to current group
            cset_cols = [col for col in converted.columns if prefix in col]

            # find the normalizing column
            norm_suffix = '_nb'
            norm_col = [col for col in cset_cols if norm_suffix in col][0]

            # convert each column except the norm_col in current group
            for col in cset_cols:
                # do not normalize norm_col and inc_med (median income)
                if (col is not norm_col and '_med' not in col):
                    # normalize to percentages
                    converted[col] = (converted[col].div(converted[norm_col])).replace({np.nan: 0, np.inf: 0})
        return converted

    def __convert_to_proportions(self, census_in_counts):
        """
        DESCRIPTION:
            Function to convert counts distribution into percentages.
            The normalizing columns (e.g. populations, households and
            family units) plus inc_med (median income) are not converted.
        INPUT:
            census_in_counts: A dataframe where census data are in counts.
                This is the output of __format_raw_census_in_counts().
        RETURN:
            converted: A dataframe where census data are in proportions.
        """
        converted = census_in_counts.copy()
        # loop through each demographics profile group
        for cset, prefix in CensusFormatter.census_groups.items():
            # get the column names corresponding to current group
            cset_cols = [col for col in converted.columns if prefix in col]

            # find the normalizing column
            norm_suffix = '_nb'
            norm_col = [col for col in cset_cols if norm_suffix in col][0]

            # convert each column except the norm_col in current group
            for col in cset_cols:
                # do not normalize norm_col and inc_med (median income)
                if (col is not norm_col and '_med' not in col):
                    # normalize to proportions
                    converted[col] = converted[col].div(converted[norm_col]).replace({np.nan: 0, np.inf: 0})
        return converted

    def to_csv(self, filename, census_type='proportions'):
        """
        DESCRIPTION:
            Function to save census data in either percents or counts
        INPUT:
            filename: A string of file name to save, required
            census_type: A string of which census type to save,
                oprtions=['percents', 'counts', 'proportions'], default = 'proportions'
        RETURN:
            None
        """
        if census_type == 'proportions':
            self.census_in_proportions.to_csv(filename)
        elif census_type == 'percents':
            self.census_in_percents.to_csv(filename)
        elif census_type == 'counts':
            self.census_in_counts.to_csv(filename)
        else:
            raise ValueError('census_type must be either "percents", "counts" or "proportions"')

    def get_census_in_counts(self):
        """
        DESCRIPTION:
            Simple function that returns census_in_count
        INPUT:
            None
        RETURN:
            census_in_count: A dataframe where data is in counts
        """
        return self.census_in_counts

    def get_census_in_percents(self):
        """
        DESCRIPTION:
            Simple function that returns census_in_percent
        INPUT:
            None
        RETURN:
            census_in_percent: A dataframe where data is in percentages
        """
        return self.census_in_percents

    def get_census_in_proportions(self):
        """
        DESCRIPTION:
            Simple function that returns census_in_percent
        INPUT:
            None
        RETURN:
            census_in_percent: A dataframe where data is in properties
        """
        return self.census_in_proportions


class ClusterProfiler:
    # feature groups and expected prefixes in riders
    feat_groups = {
        'cluster': ['cluster_'],
        'temporal': ['hr_'],
        'geographical': ['zipcode_'],
        'ticket_purchase': ['usertype_', 'tariff_', 'servicebrand_']
    }

    demo_groups = {
        'cluster': 'cluster_',
        'race': 'race_',
        'agesex': 'as_',
        'income': 'inc_',
        'education': 'edu_',
        'poverty': 'pov_',
        'unemployment': 'emp_',
        'housing_units': 'hu_',
        'household': 'hstat_'
    }

    def __init__(self, hierarchical=False, w_time=None, start_month='1701', duration=1):
        self.start_month = start_month
        self.duration = duration
        self.hierarchical = hierarchical
        self.census = CensusFormatter(DATA_PATH + INPUT_PATH + "census/MA_census.xlsx").get_census_in_counts()

        if w_time:
            self.w_time = int(w_time)
        else:
            self.w_time = 0

        if hierarchical:
            self.input_path = DATA_PATH + CLUSTER_PATH + 'hierarchical/results/'
        else:
            self.input_path = DATA_PATH + CLUSTER_PATH + 'non_hierarchical/results/'

        self.param_keys = ['hierarchical', 'month', 'duration', 'w_time']

        self.__get_data()

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
                if 'non' not in self.input_path:
                    param_vals = ['True'] + str_split[2:]
                else:
                    param_vals = ['False'] + str_split[2:]
                cached_combo.append(dict(zip(self.param_keys, param_vals)))
        return cached_combo

    def __get_data(self):
        # check if the requested data is in the cache directory ready to go
        cached_combo = self.__get_cached_params_list()
        req_param_vals = [str(self.hierarchical), self.start_month, str(self.duration), str(self.w_time)]
        req_param_dict = dict(zip(self.param_keys, req_param_vals))

        if req_param_dict in cached_combo:
            self.riders = pd.read_csv(self.input_path + CLUSTER_FILE_PREFIX +
                                       req_param_dict['month'] + '_' +
                                       req_param_dict['duration'] + '_' +
                                       req_param_dict['w_time'] +
                                       '.csv', index_col=0)
        else:  # Recluster
            segmentation = Segmentation(start_month=self.start_month, duration=self.duration, w_time=self.w_time)
            segmentation.get_rider_segmentation(hierarchical=self.hierarchical)
            del segmentation
            self.riders = pd.read_csv(self.input_path + CLUSTER_FILE_PREFIX +
                                       req_param_dict['month'] + '_' +
                                       req_param_dict['duration'] + '_' +
                                       req_param_dict['w_time'] +
                                       '.csv', index_col=0)

    def _softmax(self, df):
        exp_df = np.exp(df)
        exp_df['row_sum'] = exp_df.sum(axis=1)
        exp_df = exp_df.iloc[:,:-1].div(exp_df["row_sum"], axis=0)
        return exp_df

    def _summarize_features(self, riders, by_cluster):
        """
        DESCRIPTION:
            Function to summarize, by cluster or overall, features that were used to form the clusters.
            Approach is to turn each feature group (e.g. temporal or geographical patterns) into
            a probabiliy-like distribution. This way we can say, for instance, that the probabiliy
            of cluster 1 taking a trip in hour 3 is 0.002 or that the probability of cluster 2
            taking a trip in zipcode 02138 is 0.005, etc. Since we aim for a probability
            distribution, an important characteristic to fulfill is that the resulting columns
            belonging to a feature set (e.g. the 168 hour columns) add up to 1.
        INPUT:
            riders: A dataframe containing rider-level pattern-of-use features
                used to form clusters plus resulting cluster assignment, required
            by_cluster: A boolean, summarize features by cluster or overall, required
        RETURN:
            cluster_features: A dataframe containing cluster-level pattern-of-use features
                and additional cluster info such as cluster size
        """
        if by_cluster:
            # group by cluster and calculate cluster_size and cluster_avg_num_trips
            temp_df1 = riders.groupby(by=['cluster'])
            # column sums
            temp_df2 = temp_df1.sum()
            temp_df2['cluster_size'] = temp_df1['total_num_trips'].count()
            temp_df2['cluster_avg_num_trips'] = temp_df2['total_num_trips'].div(temp_df2['cluster_size'], axis=0)
            temp_df2 = temp_df2.reset_index()

            max_hr_modes = temp_df1.apply(lambda x: x[['max_wkday_24_1', 'max_wkday_24_2', 'max_wkend_24_1']].mode())
            max_hr_idx = [i for i, x in enumerate(max_hr_modes.index) if x[1] == 0]
            max_hr_modes = max_hr_modes.iloc[max_hr_idx].reset_index().drop(['cluster', 'level_1'], axis=1)

        else:
            temp_df1 = riders.drop(['cluster'], axis=1)
            # column sums
            temp_df2 = (temp_df1.sum().to_frame()).T
            temp_df2['cluster_size'] = len(temp_df1)
            temp_df2['cluster_avg_num_trips'] = temp_df2['total_num_trips'] / temp_df2['cluster_size']
            temp_df2 = temp_df2.reset_index().rename(index=int, columns={'index': 'cluster'})
            max_hr_modes = (temp_df1[['max_wkday_24_1', 'max_wkday_24_2', 'max_wkend_24_1']].mode().loc[0,:].to_frame()).T

        # loop through feature groups
        cluster_features = pd.DataFrame()
        cluster_features['cluster'] = temp_df2['cluster'].astype(int)
        for feature, prefix_list in ClusterProfiler.feat_groups.items():
            for prefix in prefix_list:
                # get column names that belong to the current feature group
                feature_cols = [col for col in temp_df2.columns if prefix in col]
                # normalize if the feature is not 'cluster'
                if feature is 'cluster':
                    cluster_features = pd.concat([cluster_features, temp_df2[feature_cols]], axis=1)
                else:
                    # normalize by row sum of current feature group
                    normalized = temp_df2[feature_cols].copy()
                    normalized.iloc[:, :] = (normalized.iloc[:, :].div(normalized.sum(axis=1), axis=0)).multiply(100)
                    cluster_features = pd.concat([cluster_features, normalized], axis=1)
        # add in the hr in which has the max number of trips
        cluster_features = pd.concat([cluster_features, max_hr_modes], axis=1)
        return cluster_features

    def _summarize_demographics(self, cluster_features):
        """
        DESCRIPTION:
            Function to summarize, by cluster, demographics distribution by its geo distribution.
            The approach is that for each cluster, we take its geo-pattern as a probability
            distribution over zipcodes (i.e. if cluster 1's zipcode_02142 column = 0.002, then
            0.002 is the probability/weight for zipcode 02142), and calcualte expected
            demographics distribution using zipcode probabilities. In other words, we calculate
            E = sum over i of x_i*p(x_i) where x is a vector representing demographics data in
            zipcode i and p(x_i) is the probability of zipcode i.
        INPUT:
            cluster_features: A dataframe containing cluster-level pattern-of-use features.
                This is the resulting dataframe from __get_cluster_features(), required.
        RETURN:
            cluster_demographics: A dataframe containing cluster assignment plus
                expected cluster demographics distribution. The distribution is described in
                number of people. To convert to percentages/proportions use __convert_demo_to_percent().
        """
        # get column names corresponding to geographical distribution
        geo_cols = [col for col in cluster_features.columns if 'zipcode' in col]
        geo_patterns = self._softmax(cluster_features[geo_cols])

        # filter census by the zipcodes present in the data to increase search efficiency
        self.zipcodes = [col.split('_')[-1] for col in geo_patterns.columns]
        census_of_interest = self.census.loc[self.census['zipcode'].isin(self.zipcodes)]

        cluster_demographics = pd.DataFrame()
        # loop through each cluster in geo_patterns
        for cluster, cluster_feats in geo_patterns.iterrows():
            # demographics of current cluster
            cluster_i_demo = pd.DataFrame()
            # loop through each zipcode in current cluster
            for col_name in cluster_feats.index:
                zipcode_i = col_name.split('_')[-1]  # current zipcode
                zipcode_i_prob = cluster_feats[col_name]  # weight of current zipcode
                # demographics of current zipcode
                zipcode_i_demo = census_of_interest[census_of_interest.zipcode == zipcode_i].iloc[:, 2:]
                # multiply weight by the demographics profile
                cluster_i_demo = cluster_i_demo.append(zipcode_i_prob * zipcode_i_demo)
            # cluster i demographics is weighted sum of demographics profile in each zipcode
            cluster_i_demo = cluster_i_demo.sum()
            cluster_demographics = cluster_demographics.append(cluster_i_demo.rename(cluster))

        # round all counts fields (e.g. population, num_households) as integer
        count_suffix = '_nb'
        count_cols = [col for col in cluster_demographics.columns if count_suffix in col]
        cluster_demographics[count_cols] = round(cluster_demographics[count_cols]).astype(int)

        # rename count fields with "cluster" as prefix to facilitate normalizing each individual groups
        cluster_demographics.rename(index=int, columns={"race_pop_nb": "cluster_demo_pop",
                                                        'edu_pop_25_nb': 'cluster_demo_pop_25',
                                                        'emp_pop_16_nb': 'cluster_demo_pop_16',
                                                        'inc_hh_nb': 'cluster_demo_hh',
                                                        'inc_med': 'cluster_demo_med_income',
                                                        'pov_fam_nb': 'cluster_demo_fam',
                                                        'hu_house_units_nb': 'cluster_demo_house_unit'}, inplace=True)
        # drop count columns
        new_count_cols = [col for col in cluster_demographics.columns if count_suffix in col]
        cluster_demographics.drop(new_count_cols, axis=1, inplace=True)

        # loop through feature groups
        normalized_cluster_demographics = pd.DataFrame()
        normalized_cluster_demographics['cluster'] = cluster_features['cluster']
        normalized_cluster_demographics['cluster_id'] = cluster_features['cluster'].astype(int)
        for feature, prefix in ClusterProfiler.demo_groups.items():
            # get column names that belong to the current feature group
            feature_cols = [col for col in cluster_demographics.columns if prefix in col]
            # normalize if the feature is not 'cluster'
            if feature is 'cluster':
                normalized_cluster_demographics = pd.concat([normalized_cluster_demographics, cluster_demographics[feature_cols]], axis=1)
            else:
                # normalize by row sum of current feature group
                normalized = cluster_demographics[feature_cols].copy()
                normalized.iloc[:, :] = (normalized.iloc[:, :].div(normalized.sum(axis=1), axis=0)).multiply(100)
                normalized_cluster_demographics = pd.concat([normalized_cluster_demographics, normalized], axis=1)

        return normalized_cluster_demographics

    def _get_first_2_pca_components(self, features):
        if len(features) > 1:
            X = pd.DataFrame()
            # standardize features for pca
            for col in features.drop(['cluster'], axis=1).columns:
                if features[col].std() == 0:
                    X[col] = 0
                else:
                    X[col] = (features[col] - features[col].mean())/features[col].std()
            pca = PCA(n_components=2, svd_solver='full')
            X_pca = pca.fit_transform(X)
            pca_df = pd.DataFrame(data={'cluster': features['cluster'], 'viz_id': features['cluster'].astype(int),
                                        'viz_pca1': X_pca[:, 0], 'viz_pca2': X_pca[:, 1],
                                        'viz_size': features['cluster_size'], 'viz_grp': features['cluster'] // 100})
        else: # there is only one cluster
            pca_df = pd.DataFrame(data={'cluster': features['cluster'], 'viz_id': features['cluster'].astype(int),
                                        'viz_pca1': 0, 'viz_pca2': 0,
                                        'viz_size': features['cluster_size'], 'viz_grp': 0})
        return pca_df

    def extract_profile(self, algorithm, by_cluster):
        """
        DESCRIPTION:
            Function to extract cluster profile.
        INPUT:
            by_cluster: A boolean indicating whether feature summary should be performed by cluster, required
        RETURN:
            profile: A dataframe with cluster assignment, features and demographics distribution
        """

        cols_to_drop = ['riderID', 'initial_cluster']
        df = self.riders.drop(ALGORITHMS + cols_to_drop, axis=1)
        df['cluster'] = self.riders[algorithm]

        # summarize features
        if by_cluster:
            print("summarizing by cluster features...")
            self.features = self._summarize_features(df, True)
        else:
            print("summarizing overall features...")
            self.features = self._summarize_features(df, False)

        # summarize demographics
        print("summarizing demographics...")
        self.demographics = self._summarize_demographics(self.features)

        # get pca components
        print("getting pcas...")
        pca_df = self._get_first_2_pca_components(self.features)

        # merge dfs
        profile = self.features.merge(self.demographics, on='cluster', how='inner')
        profile = profile.merge(pca_df, on='cluster', how='inner')

        # generating reports
        print("generating reports...")
        cnn_model_filename = DATA_PATH + REPORT_PATH + 'report_cnn.h5'
        profile = ReportGenerator(cnn_model_filename=cnn_model_filename).generate_report(profile)

        print("saving results...")
        self.__save_profile(profile, algorithm, by_cluster)

    def __save_profile(self, profile, algorithm, by_cluster):
        start_month = datetime.strptime(self.start_month, "%y%m").strftime("%Y-%b")

        if self.duration > 1:
            end_month = datetime.strptime(str(int(self.start_month) + self.duration-1), "%y%m").strftime("%Y-%b")
            dest = DATA_PATH + PROFILE_PATH + start_month + '_to_' + end_month + '/'
        else:
            dest = DATA_PATH + PROFILE_PATH + start_month + '/'

        if not os.path.isdir(dest):
            os.makedirs(dest)

        if by_cluster:
            if self.hierarchical:
                profile.to_csv(dest + 'hierarchical_' + PROFILE_FILE_PREFIX  + self.start_month +
                       '_' + str(self.duration) + '_' + str(self.w_time) + '_' + algorithm + '.csv')
            else:
                profile.to_csv(dest + 'non-hierarchical_' + PROFILE_FILE_PREFIX  + self.start_month +
                       '_' + str(self.duration) + '_' + str(self.w_time) + '_' + algorithm + '.csv')

        else:
            profile.to_csv(dest + 'overview_' + PROFILE_FILE_PREFIX  + self.start_month +
                       '_' + str(self.duration) + '.csv')
