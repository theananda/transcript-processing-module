import string
import json
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from myparser import MyParser

from fuzzywuzzy import fuzz

class SimilarityMethods:

    rank = list()
    m = MyParser()

    # Used Syllable_tokenizer from myparser instead
    #def _syllable_tokenizer(self,input_string):
    #    return [x for x in input_string]
        
    def _cosine_sim_vectors(self,vec1,vec2):
        '''Take 2 vectors and return cosine similarity values'''
        vec1 = vec1.reshape(1,-1)
        vec2 = vec2.reshape(1,-1)
        return cosine_similarity(vec1,vec2)[0][0]

    def _array_max(self,input_list):
        '''Take 2 dimensional list and return id of the list'''
        return input_list[np.array(input_list).argmax(axis=0)[1]]
    
    def _check_accuracy_score_cosine(self,input_list):
        if input_list[1]>0.65: #Adjust Accuracy Scores Here
            return input_list
        else:
            input_list[0] = 'UNKNOWN'
            return input_list

    def _check_accuracy_score_levenshtein(self,input_list):
        if input_list[1]>0.95: #Adjust Accuracy Scores Here
            return input_list
        else:
            input_list[0] = 'UNKNOWN'
            return input_list
    

    def cosine_similarity_method(self,keyword,rules_dict):
        '''similarity.cosine_similarity_method('keyword','rule_dictionary')
        return id and score
        '''
        vectorizer = CountVectorizer(tokenizer=self.m.syllable,lowercase=False)
        self.rank.clear()
        for rule in rules_dict:
            X = vectorizer.fit_transform([keyword,rule['name_mm']])
            vectors = X.toarray()
            self.rank.append([rule['id'],self._cosine_sim_vectors(vectors[0],vectors[1])])
        return self._check_accuracy_score_cosine(self._array_max(self.rank))

    def levenshtein_similarity_method(self,keyword,rules_dict):
        '''similarity.levenshtein_similarity_method('keyword','rule_dictionary')
        return id and score
        '''
        self.rank.clear()
        for rule in rules_dict:
            id_score = fuzz.ratio(keyword,rule['name_mm'])/100
            self.rank.append([rule['id'],id_score])
        return self._check_accuracy_score_levenshtein(self._array_max(self.rank))
