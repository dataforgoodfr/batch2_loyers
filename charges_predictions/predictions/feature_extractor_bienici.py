import numpy as np
import pandas as pd
import re

class FeatureExtractorBienici(object):
    """
    Extracts features and the target from the dataframe of all ads from bienici.com
    """
    
    # Parameters price, furnished, lift, n_rooms, description, heating, heating_source, gardien, internet
    # allow to chose the features we want to extract
    
    def __init__(self, price=True,
                 surface=True,
                 district=True,
                 furnished=True,
                 lift=True,
                 n_rooms=True,
                 description=False,
                 heating=True,
                 heating_source=True,
                 gardien=True,
                 internet=True):
        
        self.price = price
        self.surface = surface
        self.district = district
        self.furnished = furnished
        self.lift = lift
        self.n_rooms = n_rooms
        self.description = description
        self.heating = heating
        self.heating_source = heating_source
        self.gardien = gardien
        self.internet = internet
        
        self.list_features = []
        
    def set_params():
        pass
    
    def fit(self, X_df):
        """Extract the target and all features"""
        
        # Get the target
        self.target = np.array(X_df["charges"]).astype(float)
        
        # Get all features
        if self.price:
            price = np.asarray(X_df["price"]).astype(float)
            self.list_features.append({'data':price, 'feature_name':'price'})
            
        if self.surface:
            surface = np.asarray(X_df["surface"]).astype(float)
            self.list_features.append({'data':surface, 'feature_name':'surface'})
            
        if self.district:
            # District of Paris ('arrondissement')
            district = np.array(X_df['district'])
            self.list_features.append({'data':district, 'feature_name':'district'})
            
            
        if self.furnished:
            # Is the flat furnished ?
            def furnished_sure(x):
                ret = False
                if x == 'Yes':
                    ret = True
                return ret

            def furnished_from_mining(x):
                ret = False
                if 'meublé' in x and 'non meublé' not in x and 'non-meublé' not in x and 'non meuble' not in x\
                and 'non-meuble' not in x:
                    ret = True
                return ret

            def extract_furnished_feature(X_df):
                # vec_furnished gives the position of ads where it is sure that furnished is true
                vec_furnished_sure = np.asarray(X_df["furnished"].apply(furnished_sure, 1)).astype(int)
                # vec_furnished_minig gives the position of ads where we found that the flat is furnished, thanks to the description
                vec_furnished_mining = np.asarray(X_df["description"].apply(furnished_from_mining, 1)).astype(int)
                
                vec_furnished = vec_furnished_sure + vec_furnished_mining
                vec_furnished = (vec_furnished >= 1).astype(int) # 0/1 format
                return vec_furnished
            
            self.list_features.append({'data':extract_furnished_feature(X_df), 'feature_name':'furnised'})
            
        if self.lift:
            # Is there a lift ?
            def get_lifts(X_df):
                def lift_present_descr(x):
                    lift = False
                    if 'ascenseur' in x and 'sans ascenseur' not in x and 'pas ascenseur' not in x:
                        lift = True
                    elif 'ascenceur' in x and 'sans ascenceur' not in x and 'pas ascenceur' not in x:
                        # ascenceur is misspellt, but is present in the descriptions !
                        lift = True
                    return lift
                def lift_present_sure(x):
                    lift = False
                    if x==1:
                        lift = True
                    return lift

                lifts_descr = np.asarray(X_df["description"].apply(lift_present_descr, 1)).astype(int)
                lifts_sure = np.asarray(X_df["lift"].apply(lift_present_sure, 1))

                lifts = lifts_descr + lifts_sure
                lifts = (lifts >= 1).astype(int)

                return lifts
            
            self.list_features.append({'data':get_lifts(X_df), 'feature_name':'lift'})
            
        if self.n_rooms:
            # Number of rooms
            
            # When the number of rooms is unknown, try to find it in the description.
            # If sill unknown, use the median
            get_non_missing_arg = lambda x: str(x) != 'nan'
            position_known_rooms = np.asarray(X_df["number_rooms"].apply(get_non_missing_arg, 1))

            vec_rooms = np.asarray(X_df["number_rooms"]).astype(int)
            
            median_rooms = X_df["number_rooms"].where(vec_rooms).median()

            for i in range(len(position_known_rooms)):
                if position_known_rooms[i] == False:
                    #print(i)
                    descr = np.asarray(X_df["description"])[i]
                    if 'studio' in descr or 'chambre' in descr.split(' ')[:3]:
                        vec_rooms[i] = 1
                    elif 'f2 ' in descr or '2 pièces' in descr or '2 pieces' in descr \
                    or 'deux pièces' in descr or 'deux pieces' in descr:
                        vec_rooms[i] = 2
                    elif 'f3 ' in descr or '3 pièces' in descr or '3 pieces' in descr\
                    or 'trois pièces' in descr or 'trois pieces' in descr:
                        vec_rooms[i] = 3
                    else:
                        vec_rooms[i] = median_rooms
            vec_rooms = np.array(vec_rooms).astype(int)
            self.list_features.append({'data':vec_rooms, 'feature_name':'nb_rooms'})
            
        if  self.heating:
            # Is the heating individual or collective ?
            
            # First, we get the heating type ('individuel' or 'collective' from the column 'heating')
            def get_coll(system):
                if re.compile("collectif").match(system):
                    return "collective"
                elif 'individuel' in system:
                    return "individual"
                else:
                    return "unknown"
            heating_known = np.asarray(X_df["heating"].astype(str).apply(get_coll, 0))
        
            # Now, we use the description, if this information is still missing
            def update_heating_with_description(heating_known, X_df):
                heating = heating_known.copy()
                descriptions = np.asarray(X_df['description'])
                def get_heating(descr, key_word, descriptions):
                    # The idea is to look if 'collectif' or 'individuel' is close to a key word, in the description
                    descr = descr.replace('.',' ').replace(';',' ').replace(',',' ').replace(':',' ').replace('-', ' ')
                    if key_word in descriptions[i]:
                        descr = descr.replace(key_word, ' ' + key_word + ' ')
                        descr = descr.split(' ')
                        descr = list(filter(lambda a: a != '', descr))
                        index_heating = descr.index(key_word)

                        next_words = ''
                        for j in range(min(6,len(descr)-index_heating)):
                            next_words += descr[index_heating+j]

                        if 'collectif' in next_words or 'collectifs' in next_words:
                            return 'collective'
                        elif 'individuel' in next_words or 'individuels' in next_words or 'ind' in next_words:
                            return'individual'
                    return 'unknown'

                for i in range(len(heating)):
                    if heating[i] == 'unknown':
                        descr = descriptions[i]
                        ret = get_heating(descr, 'chauffage', descriptions)
                        if ret == 'unknown':
                            ret = get_heating(descr, 'chaudière', descriptions)        
                        heating[i] = ret
                return heating

            heating = update_heating_with_description(heating_known, X_df)
            self.list_features.append({'data':heating, 'feature_name':'heating'})
            
        if self.heating_source:
            # What is the source of heating ?
            
            def get_source(system):
                system = system.replace('é', 'e')
                if "electricite" in system or "electrique" in system:
                    return "electricite"
                elif "gaz" in system:
                    return "gaz"
                elif "fuel" in system or "fioul" in system:
                    return "fuel"
                else:
                    return "unknown"

            def get_source_from_description(heating_source_known):
                descriptions = np.asarray(X_df["description"])
                source = heating_source_known.copy()
                for i in range(len(descriptions)):
                    if source[i] == 'unknown':
                        descr = descriptions[i].replace('é', 'e')
                        if "electricite" in descr or "electrique" in descr:
                            source[i] = "electricite"
                        elif "gaz" in descr:
                            source[i] = "gaz"
                        elif "fuel" in descr or "fioul" in descr:
                            source[i] = "fuel"
                return source

            heating_source_known = np.asarray(X_df["heating"].astype(str).apply(get_source, 0))
            heating_source = get_source_from_description(heating_source_known)
            self.list_features.append({'data':heating_source, 'feature_name':'heating_source'})
        
        if self.gardien:
            def find_gardien(x):
                if 'gardien' in x:
                    return True
                else:
                    return False
            gardien = np.asarray(X_df["description"].apply(find_gardien, 0)).astype(int)
            self.list_features.append({'data':gardien, 'feature_name':'gardien'})
            
        
        if self.internet:
            def find_internet(x):
                if 'internet' in x:
                    return True
                else:
                    return False

            internet = np.asarray(X_df["description"].apply(find_internet, 0)).astype(int)
            self.list_features.append({'data':internet, 'feature_name':'internet'})
            
        # We also studied the presence of a garden, but it gave no good result...
            
        if self.description:
            self.list_features.append({'data':np.array(X_df['description']), 'feature_name':'description'})
        
        # Gather all features
        df_features = pd.DataFrame()
        for feature in self.list_features:
            df_features[feature['feature_name']] = feature['data']
        self.features = df_features
        
    def transform(self, X_df):
        """
        Transform the feature to use them in machine learning algorithms
        Returns self.features (X) and self.target (y)
        """
        # Get dummies for categorial features
        if self.district:
            # Get dummies for 'district'
            districts = self.features['district']
            dummies_district = pd.get_dummies(districts).rename(columns=lambda x: 'paris_' + str(x))
            dummies_district = dummies_district.astype(int)
            
            # Replace the feature 'district' by all these new ones
            self.features = self.features.drop(['district'], 1)
            self.features[dummies_district.columns] = dummies_district
            
            # The districts variable are perfectly correlated. We should remove one of them
            self.features = self.features.drop(["paris_1"], 1)
            
        if self.heating:
            # Get dummies for 'heating'
            # A lot of missing values...
            # 3 possible values: 'collective', 'individual', 'unknown' => get dummies
            heating = self.features['heating']
            dummies_heating = pd.get_dummies(heating).rename(columns=lambda x: 'heating_' + str(x))
            dummies_heating = dummies_heating.astype(int)
            
            # Replace the previous feature 'heating' by these new ones.
            # These feature are perfectly correlated. Remove 'heating_unknown'
            self.features[dummies_heating.columns] = dummies_heating
            self.features = self.features.drop(['heating'], 1)
            self.features = self.features.drop(['heating_unknown'], 1)
        
        if self.heating_source:
            # Get dummies for 'heating_source'
            sources = self.features['heating_source']
            dummies_heating_src = pd.get_dummies(sources).rename(columns=lambda x: 'heating_src_' + str(x))
            dummies_heating_src = dummies_heating_src.astype(int)
            
            # Replace the previous feature 'heating_source' by these new ones.
            # These feature are perfectly correlated. Remove 'heating_src_unknown'
            self.features[dummies_heating_src.columns] = dummies_heating_src
            self.features = self.features.drop(['heating_source'], 1)
            self.features = self.features.drop(['heating_src_unknown'], 1)
            
            # We do not normalize the data now
        
        return self.features, self.target