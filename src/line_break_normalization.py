from __future__ import unicode_literals
import re
import string
import sys
import json
import normalization

possible_sentence_end_list = ['>$','မေးခွန်း$','ခြင်း$','။$','\)$']

class line_break_normalizer:
    def _add_new_line(self,input_string):
        """Add newline \n for string input"""
        return f"{input_string}\n"

    def _list_to_string(self,input_list):
        """Convert List to String"""
        return "".join(input_list)

    def clean_page_brakes_and_time(self,input_string=None):
        input_string = re.sub("အချိန်၊? ?..(:|း)?..။?","", input_string)
        input_string = re.sub("__+","", input_string)
        input_string = re.sub("\n\w{1,3}\n","\n", input_string)#Small junks like 
        input_string = re.sub("။ ။$","။", input_string)
        input_string = re.sub("။ ။\n","။\n", input_string)
        input_string = re.sub("\n+ဖြေကြားချက်\n+","",input_string) 
        return input_string
      
    def normalize(self,input_string=None):
        #Break All possible Sentence first
        input_string = re.sub("ဥက္ကဋ္ဌ။ ။","\nဥက္ကဋ္ဌ။ ။", input_string)
        input_string = re.sub("အခမ်းအနားမှူး။ ။","\nအခမ်းအနားမှူး။ ။", input_string)
        input_string = re.sub(r"\(ဩဘာသံများ\)","(ဩဘာသံများ)\n", input_string)
        input_string = re.sub("။ ။$","။", input_string)
        input_string = re.sub(r"\[","\n[", input_string)
        input_string = re.sub(r"\]","]\n", input_string)
        input_string = re.sub("။", "။\n", input_string)
        input_string = re.sub("။\n ။\n","။ ။", input_string)
        input_string = re.sub("။ ?\n ?\(","။ (", input_string)

        return input_string

    def clean_brackets(self,input_string=None):
        input_string = re.sub(r"\[ ?","",input_string) #Del [
        input_string = re.sub(r" ?\]","",input_string) #Del ]
        input_string = re.sub(r"\( ?","(",input_string) #Change ( a to (a
        input_string = re.sub(r" ?\)",")",input_string) #Change a ) to a)
        input_string = re.sub(r"^၊ ?","",input_string)
        input_string = re.sub(r"ခွန်း ?၊$","ခွန်း",input_string)
        input_string = re.sub(r"ခြင်း ?၊$","ခြင်း",input_string)
        return input_string


    def check_sentence_end(self,input_string=None):
        '''Check the string is end with possible ending characters'''
        for item in possible_sentence_end_list:
            if re.search(item,input_string) is not None:
                return False
                break
        return True

    def line_break_normalize(self,input_string=None):
        temporary_list=[]
        input_list = input_string.split('\n') #Change to List to be able to iterate and pop
        for line in input_list:
            if self.check_sentence_end(line) is False:
                temporary_list.append(self._add_new_line(line))
            elif self.check_sentence_end(line) is True:
                temporary_list.append(self._add_new_line(f"{input_list[input_list.index(line)]} {input_list[input_list.index(line)+1]}"))
                input_list.pop(input_list.index(line)+1)
        return self._list_to_string(temporary_list)
    
    def merge_remaining_line_breaks(self,input_string=None):
        '''I DON'T KNOW WHAT THE FUCK I DID'''
        temporary_list=[]
        input_list = input_string.split('\n') #Change to List to be able to iterate and pop
        i = 1
        for idx,line in enumerate(input_list):
            if line.find('။ ။') != -1:
                temporary_list.append(f"\n{line}")
            elif line.find("။ ။") == -1:
                if line.find('<') != -1: #These are tags
                    temporary_list.append(f"{line}\n")
                elif line.find('<') == -1:
                    print(idx)
                    tmp_str = temporary_list[idx-i]
                    temporary_list.pop(idx-i)
                    temporary_list.insert(idx-1, f"{tmp_str} {input_list[idx]}")
                    i+=1
        return self._list_to_string(temporary_list)
