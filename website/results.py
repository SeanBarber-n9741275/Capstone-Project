import pandas as pd
#compare_csv = pd.read_csv("resume.csv")

def get_results(tocompare):
    import pickle
    import yake
    import pandas as pd
    import pyLDAvis
    from pyLDAvis import prepare
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    stemmer = PorterStemmer()
    stop = stopwords.words('english')

    prepared = pickle.load(open('website/model/model.sav', 'rb'))

    cols = list(['Resume_str'])
    tocompare = tocompare[cols]
    tocompare.columns = ['Resume_str']
    #print(tocompare.head())

    custom_kw_extractor = yake.KeywordExtractor(lan="en", n=1, dedupLim=0.9, top=20, features=None)
    keywords = custom_kw_extractor.extract_keywords(tocompare['Resume_str'][0])
    keywords_stemmed = []

    for kw in keywords:
        kw_stemmed = stemmer.stem(kw[0])
        #print(kw)
        keywords_stemmed.append((kw[0], kw_stemmed, kw[1]))

    results = []
    for kw in keywords_stemmed:
        for index, row in prepared.topic_info.iterrows():
            if kw[1] == row['Term']:
                results.append((kw[0], row['Freq']/kw[2]/100000)) #row['Term'], 
    return results

#print(get_results(compare_csv));
