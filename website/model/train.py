#importing libraries
import pandas as pd
import numpy as np
import nltk
import sklearn

# uploading the file from the local drive
resumes = pd.read_csv("Resumes.csv")
#tocompare = pd.read_csv("resume.csv")

print('')
print('')
print('')

def from_csv(csv, switch_format):
    if switch_format == 1:
        cols = list(['ID']+['Category']+['Resume_str'])
        csv = csv[cols]
        csv.columns = ['Applicant_ID', 'Position_Name', 'Job_Description']
        print(resumes.head())
    else: 
        cols = list(['Applicant.ID']+['Position.Name']+['Job.Description'])
        csv = csv[cols]
        csv.columns = ['Applicant_ID', 'Position_Name', 'Job_Description']
        print(resumes.head())

    csv["allfields"] = csv["Applicant_ID"].map(str) + " " + csv["Position_Name"].map(str) + " " + csv["Job_Description"]
    csv['allfields'] = csv['allfields'].str.replace('[^a-zA-Z \n\.]'," ")
    csv['allfields'] = csv['allfields'].str.lower() 
    final_all = csv[['Applicant_ID', 'allfields']]
    final_all = final_all.fillna(" ")
    csv = final_all['allfields']

    #removing stopwords and applying porter stemming
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    stemmer = PorterStemmer()
    stop = stopwords.words('english')
    only_text = csv.apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))
    only_text = only_text.apply(lambda x : filter(None,x.split(" ")))
    only_text = only_text.apply(lambda x : [stemmer.stem(y) for y in x])
    only_text = only_text.apply(lambda x : " ".join(x))
    final_all['Job_Description']= only_text
    print(final_all.head())
    return final_all['Job_Description']

resumes_processed = from_csv(resumes, 1)
#tocompare_processed = from_csv(tocompare, 0)

from sklearn.feature_extraction.text import TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer()
tfidf_applicantid = tfidf_vectorizer.fit_transform((resumes_processed)) #fitting and transforming the vector
print(tfidf_applicantid)

#tfidf_comparison = tfidf_vectorizer.transform((tocompare_processed))
#print(tfidf_comparison)

data_dense = tfidf_applicantid.todense()
print("Sparsicity: ", ((data_dense > 0).sum()/data_dense.size)*100, "%")

import pyLDAvis
def from_sklearn(docs,vect,lda,**kwargs):
    norm = lambda data: pd.DataFrame(data).div(data.sum(1),axis=0).values
    
    vected = vect.fit_transform(docs)
    doc_topic_dists = norm(lda.fit_transform(vected))
    
    prepared = prepare(
                        doc_lengths = docs.str.len(),
                        vocab = vect.get_feature_names(),
                        term_frequency = vected.sum(axis=0).tolist()[0],
                        topic_term_dists = norm(lda.components_),
                        doc_topic_dists = doc_topic_dists,
                        **kwargs)

    return prepared

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from pyLDAvis import prepare
import pickle

lda = LatentDirichletAllocation()

#similarity = cosine_similarity(tfidf_comparison, tfidf_applicantid)
#np.set_printoptions(threshold=np.inf)
#print(similarity)

#count = 0
#sum_no = 0

#new_array = []
#for idx, val in enumerate(similarity[0]):
#    if(similarity[0][idx] != 0.):
#        #print(idx, resumes_processed[idx], val)
#        sum_no += similarity[0][idx]
#        count += 1
#        new_array.append(resumes_processed[idx])

#new_array = pd.Series(new_array)

#print("similarity cosine:")
#print(sum_no/count)

prepared = from_sklearn(resumes_processed,tfidf_vectorizer,lda)

def show_topics(vectorizer, lda_model, n_words):
    keywords = np.array(vectorizer.get_feature_names())
    topic_keywords = []
    for topic_weights in lda_model.components_:
        top_keyword_locs = (-topic_weights).argsort()[:n_words]
        topic_keywords.append(keywords.take(top_keyword_locs))
    return topic_keywords

topic_keywords = show_topics(tfidf_vectorizer, lda, 15)        

# Topic - Keywords Dataframe
df_topic_keywords = pd.DataFrame(topic_keywords)
df_topic_keywords.columns = ['Word '+str(i) for i in range(df_topic_keywords.shape[1])]
df_topic_keywords.index = ['Topic '+str(i) for i in range(df_topic_keywords.shape[0])]
print(df_topic_keywords)

pickle.dump(prepared, open('model.sav', 'wb'))
