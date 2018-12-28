import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
warnings.filterwarnings('ignore', category=DeprecationWarning)
import numpy as np
from gensim.models import Word2Vec,FastText,KeyedVectors
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
import gensim.downloader as api
from tqdm import tqdm
from os import listdir

class Vectorizer:
    
    def __init__(self,type,pre_trained=False,retrain=False,extend_training=False,params={}):
        self.type = type
        self.pre_trained = pre_trained
        self.params = params
        self.retrain = retrain
        self.extend_training = extend_training

    def word2vec(self):
        if not self.pre_trained:
            if 'word2vec.model' not in listdir('./embeddings') or self.retrain:
                print('\n\tTraining Word2Vec model...')
                model = self.train_w2v()
            elif self.extend_training and 'word2vec.model' in listdir('./embeddings'):
                print('\n\tExtending existing model...')
                model = Word2Vec.load("./embeddings/word2vec.model")
                for i in range(5):
                    model.train(self.data, total_examples=len(self.data), epochs=50)
            else:
                print('\n\tLoading existing model...')
                model = Word2Vec.load("./embeddings/word2vec.model")
        else:
            model = Word2Vec(self.data,**self.params)
        vectorizer = model.wv
        self.vocab_length = len(model.wv.vocab)
        vectors = [
            np.array([vectorizer[word] if word in model else np.zeros(100) for word in tweet]).flatten() for tweet in tqdm(self.data,'Vectorizing')
            ]
        max_len = np.max([len(vector) for vector in vectors])
        self.vectors = [
            np.array(vector.tolist()+[0 for _ in range(max_len-len(vector))]) for vector in tqdm(vectors,'Finalizing')
            ]
        return self.vectors

    def train_w2v(self):
        import logging
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        model = Word2Vec(self.data, sg=1,window=3,size=100,min_count=1,workers=4,iter=500,sample=0.01)
        if self.extend_training:
            model.train(self.data, total_examples=len(self.data), epochs=100)
        model.save("./embeddings/word2vec.model")
        print("Done training w2v model!")
        return model

    def tfidf(self):
        vectorizer = TfidfVectorizer(**self.params)
        untokenized_data =[' '.join(tweet) for tweet in self.data] 
        self.vectors = vectorizer.fit_transform(untokenized_data).toarray()
        return self.vectors
    
    def BoW(self):
        vectorizer = CountVectorizer(**self.params)
        untokenized_data =[' '.join(tweet) for tweet in self.data] 
        self.vectors = vectorizer.fit_transform(untokenized_data).toarray()
        return self.vectors

    def glove(self):
        from os import listdir
        if 'glove-twitter-100.gz' in listdir('./embeddings'):
            print('Loading Glove Embeddings...\t')
            model = KeyedVectors.load_word2vec_format('./embeddings/glove-twitter-100.gz')
        else:
            print('Loading Glove Embeddings...\t')
            model = api.load('glove-twitter-100')
        print("Done.",len(model),'words loaded!')
        vectorizer = model.wv
        vectors = [np.array([vectorizer[word] if word in model else np.zeros(100) for word in tweet]).flatten() for tweet in tqdm(self.data,'Vectorizing')]
        self.vocab_length = len(model.wv.vocab)
        max_len = np.max([len(vector) for vector in vectors])
        self.vectors = [
            np.array(vector.tolist()+[0 for _ in range(max_len-len(vector))]) for vector in tqdm(vectors,'Finalizing')
            ]
        return self.vectors

    def vectorize(self,data):
        self.data = data
        vectorize_call = getattr(self, self.type, None)
        if vectorize_call:
            vectorize_call()
        else:
            raise Exception(str(self.type),'is not an available function')
        return self.vectors
    
    def fit(self,data):
        self.data = data

def shuffle_corpus(sentences):
    import random
    shuffled = list(sentences)
    random.shuffle(shuffled)
    return shuffled


