import numpy as np
import pandas as pd
import re

class DataCleaningBienici(object):
    """
    This class cleans the data from Bienici adds
    """
    def __init__(self, price_max=np.inf):
        
        self.price_max=price_max
        
    def fit(self, X_df):
        pass
    
    def transform(self, X_df):
        
        # Remove lines with incorrect price
        def get_weird(x):
            return re.compile("[0-9]+\sà").match(x) is None
        position_weird_price = X_df["price"].apply(get_weird, 0)
        X_df = X_df.ix[position_weird_price,:]
        
        # Remove lines where price > price_max
        position_keep = X_df["price"].apply(lambda x: float(x) < self.price_max)
        X_df = X_df.ix[position_keep,:]
        
        # Remove lines refering to the same flat
        # (some ads are often updated on the site => appear several times in the database ; sometimes it seems that
        # two flats are exactly the same (they may be 2 different ones, but we keep only one))
        # Group by description and title (if same description and same title, we consider it is the same ad)
        # COMMENTED, BECAUSE ENWORSES THE SCORE
        #grouped = X_df.groupby(by=['description', 'title'])
        #list_keep = list(X_df.index).copy()
        #for group, sub_df in grouped:
        #    if sub_df.shape[0] > 1:
        #        # Keep only the most recent, ie the ad with the largest index
        #        indexes = sub_df.index # sort in increasing order
        #        np.sort(indexes)
        #        for i in indexes[:-1]:
        #            list_keep.remove(i)
        # Remove redondant lines
        #X_df = X_df.ix[list_keep,:]
        #grouped = None
        
        
        # Remove lines where charges are unknown
        def get_non_missing_arg(x):
            return str(x) != 'nan'
        position_known_charge = X_df["charges"].apply(get_non_missing_arg, 1)
        X_df = X_df.ix[position_known_charge,:]
        
        # Clear the description text
        def clear_description(descr):
            descr = descr.replace("&eacute;", "é")
            descr = descr.replace("&Eacute;", "É")
            descr = descr.replace("&egrave;", "è")
            descr = descr.replace("&Egrave;", "È")
            descr = descr.replace("&sup2;", "²")
            descr = descr.replace("&agrave;", "à")
            descr = descr.replace("&ccedil;", "ç")
            descr = descr.replace("&ucirc;", "û")
            descr = descr.replace("&Ucirc;", "Û")
            descr = descr.replace("&acirc;", "â")
            descr = descr.replace("&Acirc;", "Â")
            descr = descr.replace("&ecirc;", "ê")
            descr = descr.replace("&Ecirc;", "Ê")
            descr = descr.replace("&ocirc;", "ô")
            descr = descr.replace("&Ocirc;", "Ô")
            descr = descr.replace("&icirc;", "î")
            descr = descr.replace("&Icirc;", "Î")
            descr = descr.replace("&nbsp;", " ")
            descr = descr.replace("&euro;", "€")
            descr = descr.replace("&deg;","°")
            descr = descr.replace("�","é")
            descr = descr.replace("<br>"," ")
            descr = descr.replace("</br>"," ")
            descr = descr.replace("<br/>"," ")
            descr = descr.replace("<p>"," ")
            descr = descr.replace("</p>"," ")
            descr = descr.replace("<u>","")
            descr = descr.replace("</u>","")
            descr = descr.replace("<em>","")
            descr = descr.replace("</em>","")
            descr = descr.replace("description html_format --","")
            # All the text lowercase
            descr = str.lower(descr)
            return descr
        X_df['description'] = X_df['description'].apply(clear_description,0)
        
        # Add a column 'district' and Remove lines where district is -1 (district not recognized)
        def get_district(place):
            regex = re.compile("Paris\s[0-9]+").match(place)
            if regex:
                district = regex.group(0)
                district = int(district.replace('Paris',''))
                if district <= 20:
                    return district
                else:
                    return -1
            else:
                if 'Grandes Carrières - Clichy' or 'Jules Joffrin' in place:
                    return 18
                return -1
        district = np.asarray(X_df["place"].apply(get_district, 0))
        X_df['district'] = district
        X_df = X_df.ix[district!=-1,:]        
        
        # Remove the lines where surface not known
        position_known_surface = X_df["surface"].apply(get_non_missing_arg, 1)
        X_df = X_df.ix[position_known_surface,:]
        
        return X_df