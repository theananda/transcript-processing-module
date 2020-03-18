from string_processing import StringProcessor
from normalization import normalizer
from line_break_normalization import line_break_normalizer
from digitization import digitizer
from similarity_methods import SimilarityMethods
import re
import argparse


parser = argparse.ArgumentParser(description='Python Module to Convert Parliamentary Transcripts to Structured XML Files')
parser.add_argument('--path', type=str, required=True, help='Input dir for PDF Files')
parser.add_argument('--house', type=str, required=True, help="specify the house Lower, Upper, Supreme or None")

args = parser.parse_args()



#to work on parameter provided by user
input_file_path = args.path

if args.house == 'lower':
    house = 'lower'
elif args.house == 'upper':
    house = 'upper'
elif args.house == 'union':
    house = 'union'
elif args.house == None:
    house = None

def house_mm(house):
    if house is 'lower':
        return 'ပြည်သူ့လွှတ်တော်'
    elif house is 'upper':
        return 'အမျိုးသားလွှတ်တော်'
    elif house is 'union':
        return 'ပြည်ထောင်စုလွှတ်တာတော်'
    else:
        return 'UNKNOWN'

dz = digitizer(input_file_path,house=house)
sp = StringProcessor()
nz = normalizer()
lbn = line_break_normalizer()
similarity = SimilarityMethods()

def wire_frame_constructor(file,house,house_mm,start=False,end=False):
    if start:
        return f"<doc>\n<docinfo>\n<docno>{file.stem}.xml</docno>\n<pdf>{file.stem}.pdf</pdf>\n<term value='{file.stem[0:2]}'>ဒုတိယအကြိမ်</term>\n<session value='{file.stem[3:5]}' />\n<sittingday value='{file.stem[6:8]}' />\n<legislature value='{house}'>{house_mm}</legislature>\n<title>"
    elif end:
        return f"</postface>\n</transcript>\n</doc>"

def ends_with(input_string):
    sentence_end = ["။",")","ခြင်း","မေးခွန်း"]
    for se in sentence_end:
        if input_string.endswith(se):
            return input_string
    else: return re.sub('\n+',input_string)

def main():
    print(f"House is {dz.house}")
    # dz.convert_everything() #Digitize pdf
    input("Clean up text files and Press enter to continue...")
    for file in dz.output_path.rglob('*.txt'):
        print(file.as_posix())
        with open(file.as_posix(), 'r',encoding='UTF-8') as in_file :
            filedata = in_file.read()
            filedata = nz.all_normalizations(filedata)
            filedata = lbn.clean_page_brakes_and_time(filedata)
            filedata = lbn.normalize(filedata)
            filedata = nz.all_normalizations(filedata)
            filedata = lbn.clean_brackets(filedata)
            filedata = sp.concat_string_with_tags(filedata,wire_frame_constructor(file,house,house_mm(house),start=True),wire_frame_constructor(file,house,house_mm(house),end=True))
            filedata = re.sub('\n+','\n',filedata)
            filedata = re.sub('နေ့မှတ်တမ်း(\n| )','နေ့မှတ်တမ်း</title>\n<date>',filedata)
            filedata = re.sub('နေ့\)? ?\n?နေပြည်တော်','နေ့</date>\n</docinfo>\n<transcript>\n<preface>\n<p>နေပြည်တော်',filedata)
            filedata = re.sub("\n+ဖြေကြားချက်\n+","",filedata)
            #ADD Junk Detector Here
            filedata = lbn.line_break_normalize(filedata)
            filedata = sp.pattern_substitute_two_way(filedata,'ခြင်း$',"<title>","</title>")
            filedata = sp.pattern_substitute_two_way(filedata,'မေးခွန်း$',"<title>","</title>")
            filedata = lbn.merge_remaining_line_breaks(filedata)
            filedata = re.sub('<t','\n<t',filedata)
            filedata = re.sub('\n+','\n',filedata)
            ###
            filedata = sp.pattern_substitute_two_way(filedata,'ဥက္ကဋ္ဌ။ ။',"<speech type='speaker'>","</speech>")
            filedata = re.sub("ဥက္ကဋ္ဌ။ ။","",filedata)
            filedata = sp.pattern_substitute_two_way(filedata,'အခမ်းအနားမှူး။ ။',"<speech type='mc'>","</speech>")
            filedata = re.sub("အခမ်းအနားမှူး။ ။","",filedata)
            filedata = sp.pattern_substitute_with_id(filedata,house,'army')
            filedata = sp.pattern_substitute_with_id(filedata,house,'mp')
            filedata = sp.pattern_substitute_with_id(filedata,house,'agency')
            print('All Finish Writing XML')
        with open(file.parent.joinpath(f"{file.stem}.xml"), 'w',encoding='UTF-8') as out_file :
             out_file.write(filedata)

if __name__ == '__main__':
    main()