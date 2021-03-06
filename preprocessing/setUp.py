#!/usr/bin/env python3

# set up code for twitter dataset
# will return a file cleanData.csv

import numpy as np
import pandas as pd
from sklearn import preprocessing
from textAnalysis_ex import *
import colorsys

def main():
        # load the dataset
        dataset = '/home/markg/Documents/TCD/ML/ML1819--task-107--team-11/dataset/gender-classifier-DFE-791531.csv'
        data = pd.read_csv(dataset, encoding='latin-1')

        # reformat date column
        data['created'] = pd.to_datetime(data['created'])

        # create new columns for year and month % remove original column
        data['year'] = pd.DatetimeIndex(data['created']).year
        data['month'] = pd.DatetimeIndex(data['created']).month
        data = data.drop(['created'], axis=1)

        # drop entries where gender=brand and gender=unknown
        drop_items_idx = data[data['gender'] == 'unknown'].index
        data.drop (index = drop_items_idx, inplace = True)
        drop_items_idx = data[data['gender'] == 'brand'].index
        data.drop (index = drop_items_idx, inplace = True)

        # drop unnecessary columns
        notNeededCols = ['_unit_id', '_golden', '_unit_state', '_trusted_judgments',
         'profileimage','tweet_coord','tweet_id', '_last_judgment_at', 'tweet_created',
         'gender_gold','profile_yn_gold', 'description', 'user_timezone', 'text']
        data= data.loc[:, ~data.columns.str.contains('^Unnamed')]
        data.drop(columns=notNeededCols, inplace=True)

        # drop entries where profile doesn't exist and column profile_yn
        drop_items_idx = data[data['profile_yn'] == 'no'].index
        data.drop (index = drop_items_idx, inplace = True)
        data.drop (columns = ['profile_yn'], inplace = True)

        # drop entries where gender conf < 1  % col gender_conf
        drop_items_idx = data[data['gender:confidence'] < 1].index
        data.drop (index = drop_items_idx, inplace = True)
        data.drop (columns = ['gender:confidence'], inplace = True)
        data.drop (columns = ['profile_yn:confidence'], inplace = True)

        # count the length of letters in name and create column
        data['totalLettersName']=data['name'].str.len()
        data.drop (columns = ['name'], inplace = True)

        # change tweet location to 0 if present, 1 if empty
        data.tweet_location.where(data.tweet_location.isnull(), 1, inplace=True)
        data.tweet_location.replace(np.NaN, 0, inplace=True)

        # change gender to 0=Male, 1=Female
        data['gender_catg']=pd.factorize(data['gender'])[0]
        data.drop (columns = ['gender'], inplace = True)

        # categorize colours
        # data['link_color_catg']=pd.factorize(data['link_color'])[0]
        # data['sidebar_color_catg']=pd.factorize(data['sidebar_color'])[0]
        # data.drop (columns = ['sidebar_color'], inplace = True)
        # data.drop (columns = ['link_color'], inplace = True)

        # # analyize text for sentiment & drop text column
        # text_sent=[]
        # for tweet in data['text']:
        #   text_sent.append(textAnalysis(tweet))
        # data['text_sent']=text_sent
        # data.drop(columns = ['text'], inplace=True)

        # convert linkColor to hsv
        H, S, V = [], [], []
        linkColorList = data['link_color']
        for color in linkColorList:
            try:
                color = list(int(color[i:i+2], 16) for i in (0, 2 ,4))
            except ValueError:
                color = [0, 0, 0]
            # must divide by 255 as co-ordinates are in range 0 to 1
            hsv = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
            # rescale to hsv
            x = round(hsv[0]*360, 1)
            y = round(hsv[1]*100, 1)
            z = round(hsv[2]*100, 1)
            H.append(x)
            S.append(y)
            V.append(z)

        data['link_hue'] = H
        data['link_sat'] = S
        data['link_value'] = V
        data.drop (columns = ['link_color'], inplace = True)

        # convert sidebar to hsv
        H2, S2, V2 = [], [], []
        sidebarColorList = data['sidebar_color']
        for color in sidebarColorList:
            try:
                color = list(int(color[i:i+2], 16) for i in (0, 2 ,4))
            except ValueError:
                color = [0, 0, 0]
            # must divide by 255 as co-ordinates are in range 0 to 1
            hsv = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)

            # rescale to hsv
            x = round(hsv[0]*360, 1)
            y = round(hsv[1]*100, 1)
            z = round(hsv[2]*100, 1)
            H2.append(x)
            S2.append(y)
            V2.append(z)

        data['sidebar_hue'] = H2
        data['sidebar_sat'] = S2
        data['sidebar_value'] = V2
        data.drop (columns = ['sidebar_color'], inplace = True)

        ####### OUTLIER CODE #######################
        l,u = stndrd_Devtn(data['fav_number'],3)
        drop_items_idx = data[(data['fav_number'] > u) | (data['fav_number'] < l)].index
        data.drop (index = drop_items_idx, inplace = True)

        l,u = stndrd_Devtn(data['retweet_count'],3)
        drop_items_idx = data[(data['retweet_count'] > u) | (data['retweet_count'] < l)].index
        data.drop (index = drop_items_idx, inplace = True)

        l,u = stndrd_Devtn(data['tweet_count'],3)
        drop_items_idx = data[(data['tweet_count'] > u) | (data['tweet_count'] < l)].index
        data.drop (index = drop_items_idx, inplace = True)


        # standardize numeric variables (could also consider using robust scaler here)
        numericVariables = ['fav_number', 'tweet_count','retweet_count', 'totalLettersName',
         'year', 'month', 'link_hue', 'link_value', 'link_sat',
         'sidebar_hue', 'sidebar_sat', 'sidebar_value']

        scaler = preprocessing.StandardScaler()
        data[numericVariables] = scaler.fit_transform(data[numericVariables])

        data.to_csv('cleanData.csv')
        data.info()
        print (data.head(5))

if __name__ == '__main__':
  main()
