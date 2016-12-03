import pandas as pd
import os

file_path = os.path.dirname(os.path.abspath(__file__))
refs_path = os.path.join(file_path, 'refs_beta.csv')

def makerefs(refs_path):
    refs = pd.read_csv(refs_path)
    refs['piece'] = refs['piece'].str[0]
    m = {'Meublée':True, 'Non meublée':False}
    refs['type'] = refs['type'].map(m)
    d = {'avant 1946' : 0, 
         '1946-1970': 1946,
         '1971-1990': 1971,
         'après 1990': 1990}
    t = {'avant 1946' : 1946, 
         '1946-1970': 1970,
         '1971-1990': 1990,
         'après 1990': 9999}
    refs['min_year'] = refs['epoque'].map(d)
    refs['max_year'] = refs['epoque'].map(t)
    refs = refs.drop('epoque', axis=1)
    refs.to_csv('refs_beta.csv', index=False)

def get_refs(refs_path, year=2016):
    df = pd.read_csv(refs_path)
    vals = df.ix[(df['nameZone'] == quartier) &
                 (df['type'] == furn) &
                 (df['piece'] == room) &
                 (df['min_year'] < constr) &
                 (df['max_year'] > constr) &
                 (df['annee'] == year)].squeeze()
    return vals[['ref', 'refmin', 'refmaj']].to_dict()


if __name__ == '__main__':
    getrefs(refs_path)