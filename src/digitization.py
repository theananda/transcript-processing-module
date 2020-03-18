
#For PDF PNG Conversion and Cropping
import pathlib
import os
import tempfile
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image

#For OCR
import httplib2
import io
import shutil #To Cleanup Files
## Google Auth and IO
from apiclient import discovery
from apiclient import http
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

upload = http.MediaFileUpload
download = http.MediaIoBaseDownload

#Variables for ocr method
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = './Credentials/client_id.json'
APPLICATION_NAME = 'Python OCR'


class digitizer:

    def __init__(self,input_path,house=None):
        self.input_path = pathlib.Path(input_path)
        self.temp_path = pathlib.Path(f"{input_path}/ocr_temp/")
        self.output_path = pathlib.Path(f"{input_path}/output/")
        self.house = house

    def _consistant_path(self,file_path):
        if file_path.endswith('/'):
            return file_path
        else:
            return f"{file_path}/"

    def png_convert(self,input_file_path,output_file_path):
        '''
        Convert PDF to PNG
        png_convert('1.pdf','.')
        '''
        with tempfile.TemporaryDirectory():
            convert_from_path(input_file_path, output_folder=output_file_path,fmt='png',dpi='300')
    
    def _cropper(self,file_path):
        '''
        Crop image accordingly
        Eg. crop lower house transcripts
        cropper('1.png','lower')
        '''
        ## To add National Assembley
        im = Image.open(file_path)
        width, height = im.size
        print(width,height)
        
        if self.house is None:
            left = 0
            top = 0
            return im.crop((left, top, width, height))
        
        elif self.house is 'lower':
            ## Tuned coordinates for Lower House
            left = 50
            top = 270
            height -= 315
            return im.crop((left, top, width, height))
        
        elif self.house is 'upper':
            ## Tuned coordinates for Upper House
            left = 50
            top = 270
            height -= 200
            return im.crop((left, top, width, height))

    def _crop_recursively(self,file_path):
        for file in pathlib.Path(file_path).rglob('*.png'):
            self._cropper(file).save(file)

    def text_concat(self,input_path,output_path,file_name):
        '''
        Concat all the files in the input path recursively and put output file in the output path
        text_concat('./text_files','./output','concated')
        ./output/concated.txt
        '''
        ext = '.txt'
        final_output = f"{self._consistant_path(output_path)}{file_name}{ext}"
        print("Combining text file")
        path = pathlib.Path(input_path)
        with open(final_output, 'w') as outfile:
            for p in sorted(path.rglob('*.txt')):
                with open(p) as infile:
                    outfile.write(infile.read())
    
    def temp_clean_up(self,input_path,output_path):
        '''
        Remove directory tree
        Same as shell cmd "rm -fr ./dir_name" 
        '''
        print("Cleaning Temp Files")
        shutil.rmtree(input_path, ignore_errors=True)
        shutil.rmtree(output_path, ignore_errors=True)
    
    def _get_credentials(self):
        credential_path = os.path.join("./Credentials", 'google-ocr-credential.json')
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            print(f'The credential is stored in {credential_path}' )
        return credentials

    def goolge_ocr(self,img_file,txt_file):
        '''
        Take image file as input and output text file
        CONVERT 1.png to 1.txt
        google_ocr('1.png','1.txt')
        '''
        
        credentials = self._get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v3', http=http)
        
        mime = 'application/vnd.google-apps.document'
        res = service.files().create(
        body={
            'name': img_file,
            'mimeType': mime
        },
        media_body=upload(img_file, mimetype=mime, resumable=True)
        ).execute()

        downloader = download(
        io.FileIO(txt_file, 'wb'),
        service.files().export_media(fileId=res['id'], mimeType="text/plain")
        )
        done = False
        while done is False:
            done = downloader.next_chunk()

        service.files().delete(fileId=res['id']).execute()

    def create_temp_files_and_convert_png(self):
        '''
        Method to create temp directories and converted png files
        '''
        ##CREATE DIRECTORIES NEED TO Refactor
        
        ## Create Temp Directory Call ocr_temp first
        print(f"Creating Temp Directory {self.temp_path}")
        try:
            self.temp_path.mkdir()
        except FileExistsError:
            print("Directory Already Exist")
        else:
            print("Successfully Created Temp Directory")
        
        ## Create Output Directory
        print(f"Creating output Directory {self.output_path}")
        try:
            self.output_path.mkdir()
        except FileExistsError:
            print("Directory Already Exist")
        else:
            print("Successfully Created output Directory")

        #Iterate through Input Directory
        for p in self.input_path.rglob('*.pdf'):
            print(f"Processing {p.absolute()}")
            print (f"Creating Directory - {p.stem}")

            #Create sub directory with file name in Temp Directory
            temp_extraction_path = pathlib.Path(f"{self.temp_path}/{p.stem}")
            try:
                temp_extraction_path.mkdir()
            except FileExistsError:
                print("Directory Already Exist")
            else:
                print(f"Successfully Created the directory {p.stem}")
        
            print(f"Extracting PDF file to ---- {temp_extraction_path}")

            self.png_convert(p,temp_extraction_path)

            print('Conversion to PNG finished')

    def crop_all_files(self):
        '''
        Method to crop all files recursively
        '''
        #Crop Everything before OCRing to avoid cropping again and again in case if there's an error in ocring
        for dir in self.temp_path.iterdir():
            print(f"Cropping {dir.stem}")
            self._crop_recursively(dir)

    def ocr_all_files(self):
        for dir in self.temp_path.iterdir():
            temp_in_output_path = pathlib.Path(f"{self._consistant_path(self.output_path.as_posix())}{dir.stem}")
            
            print(f"Creating Directory inside Output Directory {temp_in_output_path}")
            try:
                temp_in_output_path.mkdir()
            except FileExistsError:
                print("Directory Already Exist")
            else:
                print("Successfully Created output Directory")
            
            print("Pushing files to google drive")
            for png in dir.rglob('*.png'):
                out_file = f"{temp_in_output_path.as_posix()}/{png.stem}.txt"
                self.goolge_ocr(png.as_posix(),out_file)
                print(f"{png} Finished")
            self.text_concat(temp_in_output_path,self.output_path.as_posix(),f"{dir.stem}")
            self.temp_clean_up(temp_in_output_path,f"{self._consistant_path(self.temp_path.as_posix())}{dir.stem}")
        self.temp_clean_up(self.temp_path,None)
    
    def convert_everything(self):
        self.create_temp_files_and_convert_png()
        input("Clean up images and Press enter to continue...")
        if self.house is not None:
            print(f'House is set to {self.house}')
            self.crop_all_files()
            self.ocr_all_files()
        elif self.house is None:
            print('House is not specified. Cropping is skipped')
            self.ocr_all_files()

    





    
    
# dz = digitizer(input_file_path)
# dz.create_temp_files_and_convert_png()