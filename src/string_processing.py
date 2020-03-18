from __future__ import unicode_literals
import re
import string
import sys
from similarity_methods import SimilarityMethods
import pandas as pd
import json

similarity = SimilarityMethods()

class StringProcessor:
    """
    This class defines method to process strings in the most
    efficient way. Ideally all the methods below use unicode strings
    for both input and output.
    """

    _regex_lower_mp = r'^(\u1026\u1038|\u1012\u1031\u102B\u103A|\u1012\u1031\u102B\u1000\u103A\u1010\u102C)(.*?)(\u1019\u1032\u1006\u1014\u1039\u1012\u1014\u101A\u103A\)\u104B \u104B)'
    _regex_upper_mp = r''
    _regex_agency = r'(.*?)(\u101D\u1014\u103A\u1000\u103C\u102E\u1038\u100C\u102C\u1014\)\u104B \u104B)'
    _regex_army = r'.*\(\u1010\u1015\u103A\u1019\u1010\u1031\u102C\u103A\u101E\u102C\u1038\u1000\u102D\u102F\u101A\u103A\u1005\u102C\u1038\u101C\u103E\u101A\u103A\)\u104B \u104B'   

    agency_data = pd.read_csv('Datasets/agency.csv')
    agency_dict = agency_data.to_dict('records')
    agency_rules = json.loads(json.dumps(agency_dict))

    mp_lower_data = pd.read_csv('Datasets/mp_lower.csv')
    mp_lower_dict = mp_lower_data.to_dict('records')
    mp_lower_rules = json.loads(json.dumps(mp_lower_dict))

    mp_upper_data = pd.read_csv('Datasets/mp_lower.csv')
    mp_upper_dict = mp_upper_data.to_dict('records')
    mp_upper_rules = json.loads(json.dumps(mp_upper_dict))

    

    _temporary_list = list()
    
    def _list_to_string(self,input_list):
        """Convert List to String"""
        return "".join(input_list)

    def _split_lines(self,input_string):
        """Split string line by line to be able to iterate"""
        return iter(input_string.splitlines())

    def _add_new_line(self,input_string):
        """Add newline \n for string input"""
        return f"{input_string}\n"
    
    def _mp_agency_tag_constructor(self,input_string,person_type,person_id):
        '''parameters(input_string,person_type,person_id)
            Check input string and return the tags accordingly
        '''
        if person_type == 'mp':
            input_string = input_string.rstrip('။ ။')
            return f"<mp id='{person_id}'>{input_string}</mp>"
        if person_type == 'agency':
            input_string = input_string.rstrip('။ ။')
            return f"<agency id='{person_id}'>{input_string}</agency>"
        elif person_type == 'army':
            input_string = input_string.rstrip('။ ။')
            return f"<mp id='{person_id}'>{input_string}</mp>" 


    def _construct_arguments_for_similarity_matching(self):
        return None


    def pattern_substitute_two_way(self,mm_text,regex_pattern,start_tag, end_tag):
        """
        Find Specific Pattern and put between two define tags
        Example (filedata,'^ဥက္ကဋ္ဌ။ ။','<speech type ='speaker'>','</speech>')
        Example (filedata,'မေးခွန်း$','<title>','</title>')
        """
        #Check the input is List
        if type(mm_text) is list:
            self._temporary_list.clear()
            for line in mm_text:
                if re.search(regex_pattern,line) is None:
                    self._temporary_list.append(line)
                else:
                    self._temporary_list.append(f"{start_tag}{line}{end_tag}")
            return self._list_to_string(self._temporary_list)
        #Check the input is String
        #If input is String, Call _split_lines Method and iterate over it
        elif type(mm_text) is str:
            self._temporary_list.clear()
            for line in self._split_lines(mm_text):
                if re.search(regex_pattern,line) is None:
                    self._temporary_list.append(self._add_new_line(line))
                else:
                    self._temporary_list.append(self._add_new_line(f"{start_tag}{line}{end_tag}"))
            return self._list_to_string(self._temporary_list)
        else:
            pass
    
    def pattern_substitute_with_id(self,mm_text,house,person_type):
        '''parameter(mm_text,regex,house,person_type)
        possible person_type 'army','mp','agency'
        '''
        #if person type = 'agency' search with agency regex and if match is found 
        if person_type == 'agency':
            print('agency')
            for line in self._split_lines(mm_text):
                if re.search(self._regex_agency,line) is None:
                    self._temporary_list.append(self._add_new_line(line))
                else:
                    original_name = re.match(self._regex_agency,line).group(0)  #put the name in the list#
                    person_id = similarity.cosine_similarity_method(original_name,self.agency_rules)
                    print(f'id : {person_id[0]} Match with Accuracy : {person_id[1]:.2f}')
                    line = line.replace(original_name,self._mp_agency_tag_constructor(original_name,person_type,person_id[0]))
                    self._temporary_list.append(self._add_new_line(line))
            return self._list_to_string(self._temporary_list)
        
        elif person_type == 'mp' and house == 'upper':
            print('mp and upper')
            for line in self._split_lines(mm_text):
                if re.search(self._regex_upper_mp,line) is None:
                    self._temporary_list.append(self._add_new_line(line))
                else:
                    original_name = re.match(self._regex_upper_mp,line).group(0)
                    person_id = similarity.levenshtein_similarity_method(original_name,self.mp_upper_rules)
                    print(f'id : {person_id[0]} Match with Accuracy : {person_id[1]}')
                    line = line.replace(original_name,self._mp_agency_tag_constructor(original_name,person_type,person_id[0]))
                    self._temporary_list.append(self._add_new_line(line))
            return self._list_to_string(self._temporary_list)

        elif person_type == 'mp' and house == 'lower':
            print('mp and lower')
            for line in self._split_lines(mm_text):
                if re.search(self._regex_lower_mp,line) is None:
                    self._temporary_list.append(self._add_new_line(line))
                else:
                    original_name = re.match(self._regex_lower_mp,line).group(0)
                    person_id = similarity.levenshtein_similarity_method(original_name,self.mp_lower_rules)
                    print(f'id : {person_id[0]} Match with Accuracy : {person_id[1]}')
                    line = line.replace(original_name,self._mp_agency_tag_constructor(original_name,person_type,person_id[0]))
                    self._temporary_list.append(self._add_new_line(line))
            return self._list_to_string(self._temporary_list)

        elif person_type == 'army':
            for line in self._split_lines(mm_text):
                if re.search(self._regex_army,line) is None:
                    self._temporary_list.append(self._add_new_line(line))
                else:
                    original_name = re.match(self._regex_army,line).group(0)
                    person_id = '000'
                    line = line.replace(original_name,self._mp_agency_tag_constructor(original_name,person_type,person_id))
                    self._temporary_list.append(self._add_new_line(line))
            return self._list_to_string(self._temporary_list)


    def concat_string_with_tags(self,mm_text, start_tag = None, end_tag= None):
        return f"{start_tag}{mm_text}{end_tag}"

