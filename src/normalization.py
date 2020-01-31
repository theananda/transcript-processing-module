from __future__ import unicode_literals
import re
import string
import sys
import json

PY3 = sys.version_info[0] == 3
if PY3:
    string = str

class normalizer:

 #ADD irrggular space possibilities in the follwing dict
    _irregular_space_dict = '''[{"from": "ကြေ ?ညာ ?ပါ ?တယ် ?။","to":"ကြေညာပါတယ်။"},
        {"from":"စ ?တင် ?ဆောင် ?ရွက် ?ပါ ?မယ် ?။","to":"စတင်ဆောင်ရွက်ပါမယ်။"},
        {"from":"မေး ?မြန်း ?ဖို့ ?ဖြစ် ?ပါ ?တယ် ?။","to":"မေးမြန်းဖို့ဖြစ်ပါတယ်။"},
        {"from":"ဆွေး ?နွေး ?ဖို့ ?ဖြစ် ?ပါ ?တယ် ?။","to":"ဆွေးနွေးဖို့ဖြစ်ပါတယ်။"},
        {"from":"ဖြေ ?ကြား ?ရန် ?ဖြစ် ?ပါ ?တယ် ?။","to":"ဖြေကြားရန် ဖြစ်ပါတယ်။"},        
        {"from":"ဖြစ် ?ပါ ?တယ် ?။","to":"ဖြစ်ပါတယ်။"},
        {"from":"အ ?တည် ?ပြု ?ပါ ?သည် ?။","to":"အတည်ပြုပါသည်။"},
        {"from":" ?။ ။ ?","to":"။ ။"},
        {"from":" ?၊ ။ ?","to":"။ ။"},
        {"from":"မေး ?မြန်း ?ခြင်း ?","to":"မေးမြန်းခြင်း"},
        {"from":"မှတ် ?တမ်း ?တင် ?ခြင်း ?","to":"မှတ်တမ်းတင်ခြင်း"},
        {"from":"ဆွေး ?နွေး ?ခြင်း ?","to":"ဆွေးနွေးခြင်း"},
        {"from":"အ ?ဆို ?တင် ?သွင်း ?ခြင်း ?","to":"အဆိုတင်သွင်းခြင်း"},
        {"from":"အ ?ဆုံး ?အ ?ဖြတ် ?ရ ?ယူ ?ခြင်း ?","to":"အဆုံးအဖြတ်ရယူခြင်း"},
        {"from":"သည့် ?မေး ?ခွန်း","to":"သည့်မေးခွန်း"},
        {"from":"။ ။$","to":"။"}
        ]'''

#ADD common Normalization rules in the following dict
#Used Normalization Rules Myanmar Language Tools by MOA
#https://github.com/MyanmarOnlineAdvertising/myanmar_language_tools
    _common_normazilation_dict = '''[{ "from": "([\u102B-\u1035]+)([\u103B-\u103E]+)", "to": "\\\\2\\\\1" }, 
        { "from": "([\u102D\u102E\u1032]{0,})([\u103B-\u103E]{0,})([\u102F\u1030]{0,})([\u1036\u1037\u1038]{0,})([\u102D\u102E\u1032]{0,})", "to": "\\\\2\\\\1\\\\5\\\\3\\\\4" }, 
        { "from": "(^|[^\u1000-\u1021\u103B-\u103E])(\u1031)([\u1000-\u1021])((?:\u1039[\u1000-\u1021])?)([\u103B-\u103E]{0,})", "to": "\\\\1\\\\3\\\\4\\\\5\\\\2" }, 
        { "from": "\u1037\u102C", "to": "\u102C\u1037" }, 
        { "from": "\u103A\u1037", "to": "\u1037\u103A" }, 
        { "from": "\u1036\u102F", "to": "\u102F\u1036" }, 
        { "from": "[\u200B\u200C\u202C\u00A0]", "to": "" }, 
        { "from": "\u103E\u103B", "to": "\u103B\u103E" }, 
        { "from": "([\u102B-\u103E])\\\\1+", "to": "\\\\1" }, 
        { "from": "(\u103D\u103E)+", "to": "\u103D\u103E" }, 
        { "from": "(\u102F\u1036)+", "to": "\u102F\u1036" }, 
        { "from": "(\u102D\u102F)+", "to": "\u102D\u102F" }, 
        { "from": "([\u102D\u102E])\u1030", "to": "\\\\1\u102F" }, 
        { "from": "([\u1000-\u1021])(\u1036)(\u103D)(\u1037)", "to": "\\\\1\\\\3\\\\2\\\\4" }, 
        { "from": "([\u1000-\u1021])(\u102D)(\u1039)([\u1000-\u1021])", "to": "\\\\1\\\\3\\\\4\\\\2" }, 
        { "from": "([\u1000-\u1021])(\u1036)(\u103E)", "to": "\\\\1\\\\3\\\\2" }, 
        { "from": "(\u1047)(?=[\u1000-\u101C\u101E-\u102A\u102C\u102E-\u103F\u104C-\u109F\u0020])", "to": "\u101B" }, 
        { "from": "\u1031\u1047", "to": "\u1031\u101B" }, 
        { "from": "\u1037\u102F", "to": "\u102F\u1037" }, 
        { "from": "\u1036\u103D", "to": "\u103D\u1036" }, 
        { "from": "(\u1004)(\u1031)(\u103A)(\u1039)([\u1000-\u1021])", "to": "\\\\1\\\\3\\\\4\\\\5\\\\2" }, 
        { "from": "(\u102D)(\u103A)+", "to": "\\\\1" }, 
        { "from": "\u1025\u103A", "to": "\u1009\u103A" }, 
        { "from": "([\u1000-\u1021])(\u1031)(\u103D)", "to": "\\\\1\\\\3\\\\2" }, 
        { "from": "([\u1000-\u1021])(\u1031)(\u103E)(\u103B)", "to": "\\\\1\\\\3\\\\4\\\\2" },
        { "from": "(\u1009|\u1025)\u1000\u1039\u1000(\u100C|\u1020)", "to": "\u1025\u1000\u1039\u1000\u100B\u1039\u100C"}]'''

#ADD common Misspelled words Normalization rules in the following dict
    _misspelled_word_dict= '''[{"from": "ဥက္ကဌ","to":"ဥက္ကဋ္ဌ"},    
        {"from":"ဥကဌ","to":"ဥက္ကဋ္ဌ"},
        {"from":"ဥကဠ","to":"ဥက္ကဋ္ဌ"},
        {"from":"ဥကဋ","to":"ဥက္ကဋ္ဌ"},
        {"from":"ဥက္ကဋ။","to":"ဥက္ကဋ္ဌ။"}
        ]'''
        
        
    
    def whitespace_cleaner(self,input_string):
        """Clean white space related problems"""
        input_string = input_string.strip()#Remove leading and trailing whitespace
        input_string = re.sub('^ +','',input_string)#Strip method is not enough
        input_string = re.sub(' +$','',input_string)
        input_string = re.sub(' +', ' ',input_string)#Remove Consecutive whitespace
        input_string = re.sub('\ufeff', '',input_string)#Strip invisible whitespace
        input_string = re.sub('\u200b', '',input_string)#Strip invisible whitespace
        input_string = re.sub('\n ','\n',input_string)
        input_string = re.sub(' \n','\n',input_string)

        return input_string
    

    def mm_normalize(self,input_string=None):
        """
        Normalize Zawgyi Unicode Conversion Irregularties and Other Burmese writing norms Anomelies
        """
        rules = json.loads(self._common_normazilation_dict)
        for rule in rules:
            input_string = re.sub(rule["from"], rule["to"], input_string)
        return input_string
    
    def irregular_space_normalizer(self,input_string=None):
        """
        Normalize irregular spaces like 'ဖြစ်ပါ တယ်' to 'ဖြစ်ပါတယ်'
        """
        rules = json.loads(self._irregular_space_dict)
        for rule in rules:
            input_string = re.sub(rule["from"], rule["to"], input_string)
        return input_string

    def misspelled_word_normalizer(self,input_string=None):
        """
        Normalize misspelled words like 'ဥကဌ' to 'ဥက္ကဋ္ဌ'
        """
        rules = json.loads(self._misspelled_word_dict)
        for rule in rules:
            input_string = re.sub(rule["from"], rule["to"], input_string)
        return input_string

    def wa_zero_normalizer(self,input_string=None):
        """
        Normalize Wa Lone 'ဝ' and Zero '၀'
        Python 3 port version of wa zero fixer from Myanmar Language Tools by MOA
        https://github.com/MyanmarOnlineAdvertising/myanmar_language_tools
        """
        ## convert everything into wa first
        input_string = re.sub(u"\u1040", u"\u101D", input_string)

        # 1. checking digit in front of wa, followed by either , or space
        # 2. checking if the dot or comma is in front of a zero
        # 3. checking if a zero is in front of dot or comma
        # 4. checking if a space followed by wa that is followed by a digit
        # 5. checking if the wa at the start of the sentence followed by a digit
        matches = re.finditer(r"([\u1041-\u1049]+\.?[\u101D\u0020,]+|[\.,]\u101D+|\u101D+[\.,]\u101D?|\u0020\u101D+[\u1041-\u1049]+|^\u101D[\u1000-\u104F])", input_string)
        for match in matches:
            matched_string = match.group()
            matched_string = re.sub(u"\u101D", u"\u1040", matched_string)
            pos = match.start()

            ## convert string into list to do replacing
            s = list(input_string)
            s[pos: pos + len(matched_string)] = matched_string
            input_string = "".join(s)
        return input_string

    def all_normalizations(self,input_string=None):
        input_string = self.irregular_space_normalizer(input_string)
        input_string = self.misspelled_word_normalizer(input_string)
        input_string = self.mm_normalize(input_string)
        input_string = self.whitespace_cleaner(input_string)
        input_string = self.wa_zero_normalizer(input_string)
        return input_string