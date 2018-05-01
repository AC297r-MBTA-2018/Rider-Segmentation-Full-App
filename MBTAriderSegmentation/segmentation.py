# numpy == 1.14.0
# python 3.6
import pandas as pd
import numpy as np
import json
import sys, os
import time
from copy import deepcopy
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics import calinski_harabaz_score

from MBTAriderSegmentation.config import *

class Segmentation:
    """
    """
    def __init__(self, w_time=None, start_month='1701', duration=1, random_state=RANDOM_STATE, max_iter=MAX_ITER, tol=TOL):
        self.random_state = random_state
        self.max_iter = max_iter
        self.tol = tol

        self.start_month = start_month
        self.duration = duration
        self.w_time_choice = w_time

        self.__get_data()
        self.__standardize_features()
        self.__normalize_features()

        # number of riders
        self.N_riders = len(self.df)

        # feature groups
        self.time_feats = [e for e in self.df.columns if 'hr_' in e] + ['max_wkday_24_1', 'max_wkday_24_2', 'max_wkend_24_1', 'flex_wkday_24', 'flex_wkend_24']
        self.geo_feats = [e for e in self.df.columns if 'zipcode_' in e]
        self.purchase_feats = [e for e in self.df.columns if 'tariff_' in e] + [e for e in self.df.columns if 'usertype_' in e] + [e for e in self.df.columns if 'servicebrand_' in e]
        self.weekday_vs_weekend_feats = ['weekday', 'weekend']

        # for non hierarchical model
        self.features = self.time_feats + self.geo_feats + self.purchase_feats

        # for hierarchical model
        # features used in the initial round of clustering
        self.features_layer_1 = self.purchase_feats + self.weekday_vs_weekend_feats

        # features used in the final round of clustering
        self.features_layer_2 = self.time_feats + self.geo_feats

        # weights for tuning the relative importance of temporal(time) and geographical(location) patterns
        # normalized by number of columns to get equal weighting
        self.w_time = 100/len(self.time_feats)
        self.w_geo = 100/len(self.geo_feats)
        self.w_purchase = 100/len(self.purchase_feats) # weight for purchase patterns
        self.w_week = 100/len(self.weekday_vs_weekend_feats) # weight for weekend/weekday columns


    ###############################################
    # Helper function for init constructor
    ###############################################
    def __get_data(self):
        try:
            self.df = pd.read_csv(DATA_PATH + FEATURE_PATH + FEATURE_FILE_PREFIX + self.start_month +
                                  '_' + str(self.duration) + '.csv', sep=',', dtype={'riderID': str}, index_col=0)
        except: # if features in that month are not cached
            new_df = FeatureExtractor(start_month=self.start_month, duration=self.duration).extract_features()
            del new_df
            self.df = pd.read_csv(DATA_PATH + FEATURE_PATH + FEATURE_FILE_PREFIX + self.start_month +
                                  '_' + str(self.duration) + '.csv', sep=',', dtype={'riderID': str}, index_col=0)

    def __standardize_features(self):
        # standardize features (only the columns with > 0 standard deviation)
        self.X = self.df.drop(['riderID', 'group_by_frequency'], axis=1)
        self.X_stand = pd.DataFrame()
        for col in self.X.columns:
            if self.X[col].std() == 0:
                self.X_stand[col] = 0
            else:
                self.X_stand[col] = (self.X[col] - self.X[col].mean()) / self.X[col].std()

    def __normalize_features(self):
        # minmax normalization (only the columns with col_max - col_min > 0)
        self.X_norm = pd.DataFrame()
        for col in self.X.columns:
            col_min = self.X[col].min()
            col_max = self.X[col].max()

            if self.X[col].max() - self.X[col].min() == 0:
                self.X_norm[col] = 0
            else:
                self.X_norm[col] = (self.X[col] - self.X[col].min()) / (self.X[col].max() - self.X[col].min())

    ###############################################
    # Helper function for segmentation
    ###############################################
    def __apply_clustering_algorithm(self, features, model, n_clusters_list=[2, 3, 4, 5]):
        cluster_labels_list = []
        cluster_scores = []

        for i, n_clust in enumerate(n_clusters_list):
            # calculate label and scores for the current set of labels
            if isinstance(model, LatentDirichletAllocation):
                model.set_params(n_components=n_clust)
                proba = model.fit_transform(features)
                cluster_labels = np.argmax(proba, axis=1)
            elif isinstance(model, KMeans):
                model.set_params(n_clusters=n_clust)
                cluster_labels = model.fit_predict(features)
            else:
                print("Algorithm not implemented")
                pass
            try:
                score = self.__get_cluster_score(features, cluster_labels)
            except:
                score = 0
            # append cluster result to list
            cluster_labels_list.append(cluster_labels)
            cluster_scores.append(score)
            print("finished fitting {}/{} models".format(i+1, len(n_clusters_list)), end='\r')
            sys.stdout.flush()
        # find the number of clusters and labels that gave the highest score
        cluster_result = cluster_labels_list[np.argmax(cluster_scores)]
        return cluster_result

    def __get_cluster_score(self, features, cluster_labels):
        score = calinski_harabaz_score(features, cluster_labels)
        return score

    def __initial_rider_segmentation(self, hierarchical=False):
        '''
        Function to perform initial rider segmentation
            If sequential is True, perform Kmeans
            Otherwise, simply rename "group_by_frequency" to "initial_cluster"
        '''
        # assign initial cluster based trip frequency
        print("assigning initial clusters")
        self.df.rename(columns={"group_by_frequency": "initial_cluster"}, inplace=True)

        if hierarchical:
            # perform KMeans on unique clusters
            unique_clusters = set(self.df['initial_cluster'].unique())

            features_to_cluster = self.X_stand.copy().loc[:, self.features_layer_1]

            # apply weights
            features_to_cluster[self.purchase_feats] = features_to_cluster[self.purchase_feats] * self.w_purchase
            features_to_cluster[self.weekday_vs_weekend_feats] = features_to_cluster[self.weekday_vs_weekend_feats] * self.w_week

            # perform K means clustering on the frequent riders (initial cluster = 1 or 2)
            kmeans = KMeans(random_state=self.random_state, max_iter=self.max_iter, tol=self.tol, n_jobs=-1)
            print("K means for initial clustering in hierarchical model")

             # loop through unique_clusters and find within-cluster clusters
            for cluster in unique_clusters:
                # find riders belonging to the current cluster
                current_X = features_to_cluster.loc[self.df['initial_cluster'] == cluster]
                new_initial_cluster = self.__apply_clustering_algorithm(current_X, kmeans, n_clusters_list=[2, 3])

                # update initial cluster assignment
                self.df.loc[self.df['initial_cluster']==cluster, 'initial_cluster'] = (np.array(new_initial_cluster) + (cluster * 10)).astype(int)
                del current_X
                del new_initial_cluster
            del features_to_cluster
        else:
            self.df['initial_cluster'][self.df['initial_cluster'] == 1] = 10
            self.df['initial_cluster'][self.df['initial_cluster'] == 2] = 20


    def __final_rider_segmentation(self, model, features, n_clusters_list=[2, 3, 4, 5], hierarchical=False):
        df = features.copy()
        # add a column
        df['final_cluster'] = np.nan
        df['initial_cluster'] = np.array(self.df['initial_cluster'])

        unique_clusters = set(df['initial_cluster'].unique())
        print(unique_clusters)
        features_to_cluster = None

        if hierarchical:
            if self.w_time_choice:
                self.w_time = self.w_time * self.w_time_choice
                self.w_geo_choice = (100 - self.w_time_choice)
                self.w_geo = self.w_geo * self.w_geo_choice
            else:
                self.w_geo_choice = None

            features_to_cluster = df[self.features_layer_2]

            # apply weights
            features_to_cluster[self.time_feats] = features_to_cluster[self.time_feats] * self.w_time
            features_to_cluster[self.geo_feats] = features_to_cluster[self.geo_feats] * self.w_geo
        else:
            # update weights
            if self.w_time_choice:
                self.w_time = self.w_time * self.w_time_choice
                self.w_geo_choice = (100 - self.w_time_choice)/2
                self.w_pur_choice = self.w_geo_choice
                self.w_geo = self.w_geo * self.w_geo_choice
                self.w_purchase = self.w_purchase * self.w_pur_choice
            else:
                self.w_geo_choice = None

            features_to_cluster = df[self.features]
            # apply weights
            features_to_cluster[self.purchase_feats] = features_to_cluster[self.purchase_feats] * self.w_purchase
            features_to_cluster[self.time_feats] = features_to_cluster[self.time_feats] * self.w_time
            features_to_cluster[self.geo_feats] = features_to_cluster[self.geo_feats] * self.w_geo

        # loop through unique_clusters and find within-cluster clusters
        for cluster in unique_clusters:
            # find riders belonging to the current cluster
            current_X = features_to_cluster.loc[df['initial_cluster'] == cluster]
            final_clusters = self.__apply_clustering_algorithm(current_X, model, n_clusters_list=n_clusters_list)

            # update initial cluster assignment
            df.loc[df['initial_cluster']==cluster, 'final_cluster'] = (np.array(final_clusters) + (cluster * 10)).astype(int)
        results = df['final_cluster']

        del df
        del features_to_cluster

        return results

    def get_rider_segmentation(self, hierarchical=False):
        if hierarchical:
            n_clusters_list = [2, 3, 4]
        else:
            n_clusters_list = [i for i in range(2, 9)]
        self.scores = {}
        # perform initial segmentation
        print("performing initial segmentation...")
        self.__initial_rider_segmentation(hierarchical=hierarchical)

        # perform K means
        print("performing KMeans...")
        kmeans = KMeans(random_state=self.random_state, max_iter=self.max_iter, tol=self.tol, n_jobs=-1)
        self.df['kmeans'] = self.__final_rider_segmentation(kmeans, self.X_stand, n_clusters_list=n_clusters_list, hierarchical=hierarchical)
        print(self.df['kmeans'].unique())
        self.scores['kmeans'] = self.__get_cluster_score(self.X_stand, self.df['kmeans'])
        del kmeans

        # perform LDA
        print("performing LDA...")
        lda = LatentDirichletAllocation(random_state=self.random_state, n_jobs=-1)
        self.df['lda'] = self.__final_rider_segmentation(lda, self.X_norm, n_clusters_list=n_clusters_list, hierarchical=hierarchical)
        print(self.df['lda'].unique())
        self.scores['lda'] = self.__get_cluster_score(self.X_norm, self.df['lda'])
        del lda

        print("saving results...")
        if hierarchical:
            # save results in subdirectories
            dest = DATA_PATH + CLUSTER_PATH + 'hierarchical/'
            if not os.path.isdir(dest):
                os.makedirs(dest)
        else:
            # save results in a subdirectory
            dest = DATA_PATH + CLUSTER_PATH + 'non_hierarchical/'
            if not os.path.isdir(dest):
                os.makedirs(dest)


        if not os.path.isdir(dest+'results/'):
                os.makedirs(dest+'results/')

        if not os.path.isdir(dest+'scores/'):
            os.makedirs(dest+'scores/')

        if self.w_time_choice:
            self.df.to_csv(dest + 'results/'+ CLUSTER_FILE_PREFIX + self.start_month +
                       '_' + str(self.duration) + '_' + str(self.w_time_choice) + '.csv')
            scores_json = json.dumps(self.scores)
            f = open(dest + 'scores/' + CLUSTER_FILE_PREFIX + self.start_month +
                    '_' + str(self.duration) + '_' + str(self.w_time_choice) + '.json',"w")
            f.write(scores_json)
            f.close()
        else:
            self.df.to_csv(dest + 'results/'+ CLUSTER_FILE_PREFIX + self.start_month + '_' + str(self.duration)
                           + '_0' + '.csv')
            scores_json = json.dumps(self.scores)
            f = open(dest + 'scores/' + CLUSTER_FILE_PREFIX + self.start_month + '_' + str(self.duration)  +
                     '_0' + '.json',"w")
            f.write(scores_json)
            f.close()
