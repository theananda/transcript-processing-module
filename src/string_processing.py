from __future__ import unicode_literals
import re
import string
import sys

PY3 = sys.version_info[0] == 3
if PY3:
    string = str


class StringProcessor(object):
    """
    This class defines method to process strings in the most
    efficient way. Ideally all the methods below use unicode strings
    for both input and output.
    """
    
    def _list_to_string(self,input_list):
        """Convert List to String"""
        return "".join(input_list)

    def _split_lines(self,input_string):
        """Split string line by line to be able to iterate"""
        return iter(input_string.splitlines())

    def _add_new_line(self,input_string):
        """Add newline \n for string input"""
        return f"{input_string}\n"

    def pattern_substitute_two_way(self,mm_text,regex_pattern,start_tag, end_tag):
        """
        Find Specific Pattern and put between two define tags
        Example (filedata,'^ဥက္ကဋ္ဌ။ ။','<speaker>','</speaker>')
        Example (filedata,'မေးခွန်း$','<title>','</title>')
        """
        #Check the input is List
        if type(mm_text) is list:
            temporary_list=[]
            for line in mm_text:
                if re.search(regex_pattern,line) is None:
                    temporary_list.append(line)
                else:
                    temporary_list.append(f"{start_tag}{line}{end_tag}")
            return self._list_to_string(temporary_list)
        #Check the input is String
        #If input is String, Call _split_lines Method and iterate over it
        elif type(mm_text) is str:
            temporary_list=[]
            for line in self._split_lines(mm_text):
                if re.search(regex_pattern,line) is None:
                    temporary_list.append(self._add_new_line(line))
                else:
                    temporary_list.append(self._add_new_line(f"{start_tag}{line}{end_tag}"))
            return self._list_to_string(temporary_list)
        else:
            pass
