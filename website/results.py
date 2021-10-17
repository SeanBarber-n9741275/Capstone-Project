import pandas as pd
#compare_csv = open('static/Sample_Resume2.pdf', 'rb')#pd.read_csv("resume.csv")


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

    from io import StringIO
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFParser

    output_string = StringIO()
    parser = PDFParser(tocompare)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)

    tocompare = output_string.getvalue()
    #print(tocompare)
    
    device.close()

    prepared = pickle.load(open('website/model/model.sav', 'rb'))

    #cols = list(['Resume_str'])
    #tocompare = tocompare[cols]
    #tocompare.columns = ['Resume_str']
    #print(tocompare.head())

    custom_kw_extractor = yake.KeywordExtractor(lan="en", n=2, dedupLim=0.9, top=20, features=None)
    keywords = custom_kw_extractor.extract_keywords(tocompare)
    keywords_stemmed = []

    for kw in keywords:
        kw_stemmed = stemmer.stem(kw[0])
        #print(kw)
        keywords_stemmed.append((kw[0], kw_stemmed, kw[1]))

    results_label = []
    results_values = []
    for kw in keywords_stemmed:
        for index, row in prepared.topic_info.iterrows():
            if row['Term'] in kw[1]:
                results_label.append(kw[0])
                results_values.append(row['Freq']/kw[2]/100000)
                break
    return results_label, results_values

#print(get_results(compare_csv));
