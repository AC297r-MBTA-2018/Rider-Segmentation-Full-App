import numpy as np
import pandas as pd
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
        text = 'The predicted type of rider for cluster {} is {}. '.format(row['cluster'], RIDER_LABEL_DICT[row['rider_type']])
        text += 'There are {} riders in the cluster, taking on average {} trips. '.format(row['cluster_size'],
                                                                                          round(row['cluster_avg_num_trips'], 2))
        max_wkday_hr1 = str(row['max_wkday_24_1']-1)+':00-' + str(row['max_wkday_24_1'])+':00'
        max_wkday_hr2 = str(row['max_wkday_24_2']-1)+':00-' + str(row['max_wkday_24_2'])+':00'
        max_wkend_hr1 = str(row['max_wkend_24_1']-1)+':00-' + str(row['max_wkend_24_1'])+':00'

        text += 'These riders take most trips during {} and {} on weekdays, '.format(max_wkday_hr1, max_wkday_hr2)
        text += 'and during {} on weekends. '.format(max_wkend_hr1)
        text += 'The most frequent trip origin is in zipcode {}. '.format(row['max_zip'])
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

        zip_cols = [col for col in df_copy.columns if 'zipcode_' in col]
        max_zip_indices = np.argmax(df_copy[zip_cols].values, axis=1)
        df_copy['max_zip'] = [zip_cols[idx].split('_')[-1] for idx in max_zip_indices]

        df_copy['report'] = df_copy.apply(lambda row: self.get_text(row), axis=1)

        # save the profile csv with report and newly predicted rider type
        df['rider_type'] = df_copy['rider_type']
        df['report'] = df_copy['report']
        return df
