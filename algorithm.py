#importing libraries
import pandas as pd
import numpy as np
import nltk
import sklearn

# uploading the file from the local drive
resumes = pd.read_csv("Experience.csv")
tocompare = pd.read_csv("resume.csv")

print('')
print('')
print('')

def from_csv(csv):
    cols = list(['Applicant.ID']+['Position.Name']+['Job.Description'])
    csv = csv[cols]
    csv.columns = ['Applicant_ID', 'Position_Name', 'Job_Description']
    print(resumes.head())

    csv["allfields"] = csv["Applicant_ID"].map(str) + " " + csv["Position_Name"].map(str) + " " + csv["Job_Description"]
    csv['allfields'] = csv['allfields'].str.replace('[^a-zA-Z \n\.]'," ")
    csv['allfields'] = csv['allfields'].str.lower() 
    final_all = csv[['Applicant_ID', 'allfields']]
    final_all = final_all.fillna(" ")
    cvs = final_all['allfields']

    #removing stopwords and applying porter stemming
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    stemmer = PorterStemmer()
    stop = stopwords.words('english')
    only_text = cvs.apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))
    only_text = only_text.apply(lambda x : filter(None,x.split(" ")))
    only_text = only_text.apply(lambda x : [stemmer.stem(y) for y in x])
    only_text = only_text.apply(lambda x : " ".join(x))
    final_all['Job_Description']= only_text
    print(final_all.head())
    return final_all['Job_Description']

resumes_processed = from_csv(resumes)
tocompare_processed = from_csv(tocompare)

from sklearn.feature_extraction.text import TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer()
tfidf_applicantid = tfidf_vectorizer.fit_transform((resumes_processed)) #fitting and transforming the vector
print(tfidf_applicantid)

tfidf_comparison = tfidf_vectorizer.transform((tocompare_processed))
print(tfidf_comparison)

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

lda = LatentDirichletAllocation()

similarity = cosine_similarity(tfidf_comparison, tfidf_applicantid)
np.set_printoptions(threshold=np.inf)
print(similarity)

count = 0
sum_no = 0

new_array = []
for idx, val in enumerate(similarity[0]):
    if(similarity[0][idx] != 0.):
        #print(idx, resumes_processed[idx], val)
        sum_no += similarity[0][idx]
        count += 1
        new_array.append(resumes_processed[idx])

new_array = pd.Series(new_array)

print("similarity cosine:")
print(sum_no/count)

prepared = from_sklearn(new_array,tfidf_vectorizer,lda)
pyLDAvis.show(prepared)
