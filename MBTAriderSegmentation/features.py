import numpy as np
import pandas as pd
import os, sys

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(os.path.abspath(__file__))
from MBTAriderSegmentation.config import *

class DataLoader:
    """
    NOTE:
        missing values in fareprod are filled with 'N/A' string
    This class merges afc_odx, fareprod, and stops data for feature extraction in the next step.
    	It is wrapped in Class FeatureExtractor. 
    """
    def __init__(self, start_month, duration):
        # initialize attributes
        self.start_month = start_month
        self.duration = duration
        self.afc_odx_fields = ['deviceclassid', 'trxtime',
                               'tickettypeid', 'card',
                               'origin', 'movementtype']
        self.fp_fields = ['tariff', 'servicebrand', 'usertype',
                          'tickettypeid', 'zonecr']
        self.stops_fields = ['stop_id', 'zipcode']

        # reading in fareprod
        self.fareprod = pd.read_csv(DATA_PATH + INPUT_PATH + 'fareprod/fareprod_ttj.csv',
                                    sep=';', usecols=self.fp_fields).fillna('N/A')

        # reading in stops
        self.stops = pd.read_csv(DATA_PATH + INPUT_PATH + 'stops/stops_withzip.csv',
                                 sep=',', usecols=self.stops_fields, dtype={'zipcode': str})

        self.station_deviceclassid = [411, 412, 441, 442, 443, 501, 503]
        self.validation_movementtype = [7, 20]

    def load(self):
    	"""
    	INPUT:
    		None
    	OUTPUT:
    		self.df: a df merged with afd_odx, stops and fareprod for feature extraction in the next step
    	"""
        self.df = pd.DataFrame()
        parse_dates = ['trxtime']

        # read in specified months of afc_odx data
        for dt in range(self.duration):
            file_key = str(int(self.start_month) + dt)
            try:
                new_df = pd.read_csv(DATA_PATH + INPUT_PATH + 'afc_odx/afc_odx_' +
                                     file_key + '.csv', sep=',', usecols=self.afc_odx_fields, dtype={'origin': str, 'card': str}, parse_dates=parse_dates)
                self.df = self.df.append(new_df)
            except FileNotFoundError:
                raise ValueError('File not found, check parameter values')

        # filter out transactions with no origin data
        self.df = self.df[-self.df['origin'].isnull()]

        # filter out station entries
        self.df = self.df[(self.df['deviceclassid'].isin(self.station_deviceclassid)) & (self.df['movementtype'].isin(self.validation_movementtype))]

        # merge afc_odx, stops and fareprod
        self.df = pd.merge(self.df, self.stops, how='inner', left_on=['origin'], right_on=['stop_id'])
        self.df = pd.merge(self.df, self.fareprod, how='inner', on='tickettypeid')

        # drop unnecessary columns
        self.df.drop(['deviceclassid', 'tickettypeid', 'origin', 'movementtype', 'stop_id'], axis=1, inplace=True)

        self.df = self.df.rename(columns={'card': 'riderID'})
        return self.df

class FeatureExtractor:
    """
    This class does the following things:
    1. Extract temporal, geographical, and ticket purchasing features
    2. Label riders by their total number of trips, and whether they use commuter rail expect for zone 1a
    The second step is for further filtering in segmentaion model.
    """
    def __init__(self, start_month='1701', duration=1):
        print("Loading data...", end="\r")
        sys.stdout.flush()
        self.df_transaction = DataLoader(start_month=start_month, duration=duration).load()
        self.purchase_features = ['tariff', 'usertype', 'servicebrand', 'zonecr']
        self.start_month = start_month
        self.duration = duration

    def _extract_temporal_patterns(self):
        """
        Function to extract rider level temporal patterns
        INTPUT:
        	None
        OUTPUT:
        	df_rider_temporal_count: a df of rider level temporal patterns
        """
        # extract hour and day of week
        self.df_transaction['hour'] = self.df_transaction['trxtime'].apply(lambda x: x.hour)
        self.df_transaction['day_of_week'] = self.df_transaction['trxtime'].apply(lambda x: x.dayofweek)  # monday=0, sunday=6

        # counting daily pattern by rider ID
        groups = self.df_transaction.groupby(['riderID', 'day_of_week', 'hour']).agg(['count']).iloc[:, 0]
        df_group = pd.DataFrame(groups).reset_index()
        df_group.columns = ['riderID', 'day_of_week', 'hour', 'count']

        rider_id = self.df_transaction['riderID'].unique()
        N = len(rider_id)
        # construct key dataframe to merge with grouped df
        # this key_df makes sure that each rider has 168 hours
        day_id = np.array([x for x in range(0, 7)])
        day = [x for x in np.repeat(day_id, [24], axis=0)] * N
        hour = [x for x in range(0, 24)] * 7 * N
        hr_col_names = [i for i in range(1, 169)] * N
        riders = [x for x in np.repeat(rider_id, [168], axis=0)]
        key_df = pd.DataFrame(data={'riderID': riders, 'day_of_week': day, 'hour': hour, 'hr_col_names': hr_col_names})

        # left join key_df and group_df to make sure all riders have 168 hours
        # the nan's represent where the rider in df_group has no count information in that hour
        join_df = pd.merge(key_df, df_group, how='left', on=['riderID', 'day_of_week', 'hour']).replace({np.nan: 0})
        df_rider_temporal_count = join_df.pivot(index='riderID', columns='hr_col_names', values='count').reset_index()
        df_rider_temporal_count.reset_index(drop=True, inplace=True)

        # add hr_ prefix to temporal pattern
        new_col_names = [(0, 'riderID')]
        hr_col_names = [(i, 'hr_' + str(i)) for i in df_rider_temporal_count.iloc[:, 1:].columns.values]
        new_col_names.extend(hr_col_names)
        df_rider_temporal_count.rename(columns=dict(new_col_names), inplace=True)

        # add weekend vs weekday count/proportion for higher level features
        weekday_col_names = ['hr_' + str(i) for i in range(1, 121)]
        weekend_col_names = ['hr_' + str(i) for i in range(121, 169)]

        df_rider_temporal_count['weekday'] = df_rider_temporal_count[weekday_col_names].sum(axis=1)
        df_rider_temporal_count['weekend'] = df_rider_temporal_count[weekend_col_names].sum(axis=1)

        # collapse 168 hourly pattern into 24 hr weekend and 24 hr weekday (48 total) + 2 hour max
        wkday_24_hr_col_names = ['wkday_24_' + str(i) for i in range(1, 25)]
        wkend_24_hr_col_names = ['wkend_24_' + str(i) for i in range(1, 25)]

        weekday = np.array(df_rider_temporal_count[weekday_col_names])
        weekday = weekday.reshape((len(weekday), 5, 24)).sum(axis=1)
        weekday = pd.DataFrame(weekday, columns=wkday_24_hr_col_names)

        weekend = np.array(df_rider_temporal_count[weekend_col_names])
        weekend = weekend.reshape((len(weekend), 2, 24)).sum(axis=1)
        weekend = pd.DataFrame(weekend, columns=wkend_24_hr_col_names)

        hr_col_names = ['hr_' + str(i) for i in range(1, 169)]
        df_rider_temporal_count = pd.concat([df_rider_temporal_count, weekday, weekend], axis=1)
        df_rider_temporal_count['hr_row_sum'] = df_rider_temporal_count[hr_col_names].iloc[:, :].sum(axis=1)

        df_rider_temporal_count['flex_wkday_24'] = weekday.max(axis=1).div(df_rider_temporal_count['hr_row_sum'])
        df_rider_temporal_count['flex_wkend_24'] = weekend.max(axis=1).div(df_rider_temporal_count['hr_row_sum'])

        # get the top 2 frequency hr in weekday
        wkday_rank = weekday.apply(np.argsort, axis=1)
        ranked_wkday_cols = weekday.columns.to_series()[wkday_rank.values[:,::-1][:,:2]]

        df_rider_temporal_count['max_wkday_24_1'] = pd.DataFrame(ranked_wkday_cols[:, 0])[0].apply(lambda x: str(x).split('_')[-1])
        df_rider_temporal_count['max_wkday_24_2'] = pd.DataFrame(ranked_wkday_cols[:, 1])[0].apply(lambda x: str(x).split('_')[-1])
        df_rider_temporal_count['max_wkend_24_1'] = weekend.idxmax(axis=1).apply(lambda x: x.split('_')[-1])

        return df_rider_temporal_count

    def _extract_geographical_patterns(self):
        """
        Function to extract rider level geographical patterns
        INPUT:
        	None
        OUTPUT:
        	df_rider_geo_count: a df of rider level grographical patterns
        """
        # take onehot encoding of zipcodes
        onehot = pd.get_dummies(self.df_transaction['zipcode'], prefix='zipcode')
        rider_id = pd.DataFrame(data={'riderID': self.df_transaction['riderID']})
        frames = [rider_id, onehot]
        df_onehot = pd.concat(frames, axis=1)

        # count zipcodes
        df_rider_geo_count = df_onehot.groupby(['riderID'])[list(onehot.columns.values)].sum().reset_index()
        df_rider_geo_count['geo_row_sum'] = df_rider_geo_count.iloc[:, 1:].sum(axis=1)

        return df_rider_geo_count

    def _get_one_purchase_feature(self, feature):
        """
        Function to extract one purchasing feature
        INPUT:
        	feature: an item in self.purchase_features list
        OUTPUT:
        	df_onehot_count: a df of one purchasing feature
        """
        # take onehot encoding of the purchasing feature columns
        onehot = pd.get_dummies(self.df_transaction[feature], prefix=feature)
        rider_id = pd.DataFrame(data={'riderID': self.df_transaction['riderID']})
        frames = [rider_id, onehot]
        df_onehot = pd.concat(frames, axis=1)

        # count purchasing features
        df_onehot_count = df_onehot.groupby(['riderID'])[list(onehot.columns.values)].sum().reset_index()

        return df_onehot_count

    def _extract_ticket_purchasing_patterns(self):
        """
        Function to combine a list of rider level purchasing features
        INPUT:
        	None
        OUTPUT:
        	df_purchase_count: a df of rider level purchasing features
        """
        list_df_purchase_count = []

        for feature in self.purchase_features:
            feature_count = self._get_one_purchase_feature(feature)
            list_df_purchase_count.append(feature_count.drop(['riderID'], axis=1))
        df_purchase_count = pd.concat(list_df_purchase_count, axis=1)

        # append the riderID columns
        df_purchase_count.insert(0, 'riderID', feature_count['riderID'])

        return df_purchase_count

    def _label_rider_by_trip_frequency(self, rider):
        """
        Function to label riders by their total number of trips
        INPUT:
            rider: a row in the riders dataframe
        RETURN:
            label: a string
        """
        if rider['total_num_trips'] <= 5*self.duration:
            label = 0
        elif rider['total_num_trips'] <= 20*self.duration:
            label = 1
        elif rider['total_num_trips'] > 20*self.duration:
            label = 2
        else:
            label = -1
        return label

    def _label_commuter_rail_rider(self, rider):
        """
        Function to label riders as either commuter rail rider or others
        INPUT:
            rider: a row in the riders dataframe
        RETURN:
            label: a string, 'CR except zone 1A' or 'others'
        """
        if (rider['servicebrand_Commuter Rail'] > 0) and (rider['zonecr_1a'] == 0):
            label = 'CR except zone 1A'
        else:
            label = 'others'
        return label

    def extract_features(self):
        # extract time, geo and purchasing patterns
        print('Extracting temporal patterns...', end='\r')
        self.temporal_patterns = self._extract_temporal_patterns()
        sys.stdout.flush()
        print('Extracting geographical patterns...', end='\r')
        self.geographical_patterns = self._extract_geographical_patterns()
        sys.stdout.flush()
        print('Extracting purchasing patterns...', end='\r')
        self.purchasing_patterns = self._extract_ticket_purchasing_patterns()
        sys.stdout.flush()

        # merge all extracted patterns into one featues DataFrame
        self.df_rider_features = pd.merge(self.temporal_patterns, self.geographical_patterns, how='inner', on='riderID')
        self.df_rider_features = pd.merge(self.df_rider_features, self.purchasing_patterns, how='inner', on='riderID')

        # check if 'hr_row_sum' == 'geo_row_sum', they both represent total number of trips
        # if they are equal, drop one of them and rename the other to 'total_num_trips'
        if (self.df_rider_features['hr_row_sum'] == self.df_rider_features['geo_row_sum']).all():
            self.df_rider_features.drop(['hr_row_sum'], axis=1, inplace=True)
            self.df_rider_features.rename(index=str, columns={'geo_row_sum': 'total_num_trips'}, inplace=True)

        # drop infrequent riders
        self.df_rider_features = self.df_rider_features[self.df_rider_features['total_num_trips'] > 5*self.duration]


        print('Labeling riders...', end='\r')

        # label riders based on whether they have commuter rail pass
        self.df_rider_features['group_commuter_rail'] = self.df_rider_features.apply(self._label_commuter_rail_rider, axis=1)
        # drop CR riders
        self.df_rider_features = self.df_rider_features[self.df_rider_features['group_commuter_rail']!='CR except zone 1A']
        self.df_rider_features.drop(['group_commuter_rail'], axis=1, inplace=True)

        # label riders based on their usage frequency
        self.df_rider_features['group_by_frequency'] = self.df_rider_features.apply(self._label_rider_by_trip_frequency, axis=1)
        self.df_rider_features = self.df_rider_features[self.df_rider_features['group_by_frequency'].isin([1,2])]

        # drop zonecr columns (not useful)
        zonecr_cols = [col for col in self.df_rider_features.columns if 'zonecr_' in col]
        self.df_rider_features.drop(zonecr_cols, axis=1, inplace=True)


        sys.stdout.flush()
        print('Saving features..............')
        # save extracted features to cached_features directory
        self.df_rider_features.to_csv(DATA_PATH + FEATURE_PATH + FEATURE_FILE_PREFIX +
                                      self.start_month + '_' + str(self.duration) + '.csv')

        return self.df_rider_features
    # print(DATA_PATH)
    # print(os.path.dirname(os.path.abspath(__file__)))
    # print(os.path.abspath(__file__))
    # # df = pd.read_csv(os.path.dirname(os.path.abspath(__file__))+'/data/cached_profiles/2017-Oct/overview_cluster_profiles_1710_1.csv')
    # df = pd.read_csv('/data/cached_profiles/2017-Oct/overview_cluster_profiles_1710_1.csv')
