from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
# from nltk.corpus import stopwords
import pickle





# Init Objects
tokenizer = RegexpTokenizer(r'\w+')
# en_stopwords = set(stopwords.words('english'))
# en_stopwords = en_stopwords - {'is','of','are'}
# pickle_out = open('stopwords.pickle','wb')
# pickle.dump(en_stopwords,pickle_out)
# pickle_out.close()
pickle_in = open('stopwords.pickle','rb')
en_stopwords = pickle.load(pickle_in)
pickle_in.close()
# print(type(en_stopwords))
ps = PorterStemmer()




def getClearReview(review):
    
    review = review.lower()
    review = review.replace("<br /><br />"," ")
    
    #Tokenize
    tokens = tokenizer.tokenize(review)
    new_tokens = [token for token in tokens if token not in en_stopwords]
    # stemmed_tokens = [ps.stem(token) for token in new_tokens]
    cleaned_review = ' '.join(new_tokens)
    
    return cleaned_review
    



