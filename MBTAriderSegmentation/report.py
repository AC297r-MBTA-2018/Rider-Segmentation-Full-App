import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

import keras
from keras.models import Sequential, load_model
from keras.layers import Dense, Conv2D, Flatten, MaxPooling2D, Activation
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split

from MBTAriderSegmentation.config import *

class ReportGenerator():
    def __init__(self, cnn_model_filename, sample_factor=1000, noise_std=0.3):
        self.n_classes = len(RIDER_LABEL_DICT)
        self.cnn_model_filename = cnn_model_filename
        self.sample_factor = sample_factor
        self.noise_std = noise_std

    def get_text(self, row):
        text = 'Cluster {}\'s predicted type of rider is {} .'.format(row['cluster'], RIDER_LABEL_DICT[row['rider_type']])
        text += 'There are {} riders in the cluster, taking on average {} trips. '.format(row['cluster_size'],
                                                                                          round(row['cluster_avg_num_trips'], 2))
        max_wkday_1 = DAY_DICT[row['max_wkday_1']]
        max_wkday_2 = DAY_DICT[row['max_wkday_2']]
        max_wkend_1 = DAY_DICT[row['max_wkend_1']]

        max_wkday_hr1 = str(row['max_wkday_hr1'])+':00'
        max_wkday_hr2 = str(row['max_wkday_hr2'])+':00'
        max_wkend_hr1 = str(row['max_wkend_hr1'])+':00'

        text += 'The top 2 most frequent trip time during weekday is '
        text += '{} {} and {} {}. '.format(max_wkday_1, max_wkday_hr1, max_wkday_2, max_wkday_hr2)
        text += 'The top 1 most frequent trip time during weekend is {} {}. '.format(max_wkend_1, max_wkend_hr1)
        text += 'The top 1 most frequent trip origin is at zipcode {}. '.format(row['max_zip'])
        return text

    def generate_report(self, df):
        # drop the old report
        if 'report' in df.columns:
            df.drop(['report'], axis=1, inplace=True)
        if 'rider_type' in df.columns:
            df.drop(['rider_type'], axis=1, inplace=True)

        df_copy = df.copy()

        hr_cols = ['hr_' + str(i) for i in range(1, 169)]
        X_1D = df_copy[hr_cols].values
        n_clusters = X_1D.shape[0]
        X = np.expand_dims(X_1D.reshape((n_clusters, 7, 24)), axis=-1)

        self.cnn_model = load_model(self.cnn_model_filename)
        if 'manual_label' in df_copy.columns:
            y_onehot = np.eye(len(RIDER_LABEL_DICT))[df_copy['manual_label'].values.astype(int)]
            scores = self.cnn_model.evaluate(X, y_onehot, verbose=1)
            print('Loss (against manual label):', scores[0])
            print('Accuracy (against manual label):', scores[1])

        df_copy['rider_type'] = self.cnn_model.predict_classes(X)

        df_copy['max_wkday_1'] = ((df_copy['max_wkday_24_1']-1)/24).astype(int)
        df_copy['max_wkday_2'] = ((df_copy['max_wkday_24_2']-1)/24).astype(int)
        df_copy['max_wkend_1'] = ((df_copy['max_wkend_24_1']-1)/24).astype(int)

        df_copy['max_wkday_hr1'] = ((df_copy['max_wkday_24_1']-1)%24).astype(int)
        df_copy['max_wkday_hr2'] = ((df_copy['max_wkday_24_2']-1)%24).astype(int)
        df_copy['max_wkend_hr1'] = ((df_copy['max_wkend_24_1']-1)%24).astype(int)

        zip_cols = [col for col in df_copy.columns if 'zipcode_' in col]
        max_zip_indices = np.argmax(df_copy[zip_cols].values, axis=1)
        df_copy['max_zip'] = [zip_cols[idx].split('_')[-1] for idx in max_zip_indices]

        df_copy['report'] = df_copy.apply(lambda row: self.get_text(row), axis=1)

        # save the profile csv with report and newly predicted rider type
        df['rider_type'] = df_copy['rider_type']
        df['report'] = df_copy['report']
        return df
