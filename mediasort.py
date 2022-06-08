import PIL.Image,PIL.ExifTags,os
import ffmpeg
from pprint import pprint# can be removed once complete
from datetime import datetime
import shutil

check_created_folders = []
check_created_files = []

for root, subdirs, files in os.walk('randomfiles'):
    print(root,subdirs,files)
    for each_file in files:
        info_found = True
        file_name = os.path.join(root,each_file)
        print(f"\n{file_name}")
        try:
            ext_file = file_name[file_name.rfind('.')+1:].upper()
        except:
            ext_file = ""
        creation_time = datetime.fromtimestamp(os.path.getmtime(file_name)).strftime("%Y-%m-%d")
        if ext_file in ['MOV','3GP','MP4','MPEG']:
            vid_dict = ffmpeg.probe(file_name)["streams"]
            model = 'Other video'
            #pprint(vid_dict)
            try:
                creation_time = vid_dict[0]['tags']['creation_time']
                model = 'Android video'
            except:
                pass
            
            if ext_file =='MOV':
                model = 'Iphone_DSLR video'
            elif ext_file =='3GP':
                model ='Old video'
            
            file_type = "videos"

        elif ext_file in ['JPG','PNG','JPEG','HEIC']:
            img = PIL.Image.open(file_name)
            img_dict = img._getexif()
            try:
                exif = {
                    PIL.ExifTags.TAGS[k]: v
                    for k, v in img._getexif().items()
                    if k in PIL.ExifTags.TAGS
                }
                try:
                    model = exif['Model']
                except:
                    model = "Unknown"
                
                try:
                    creation_time = exif['DateTimeOriginal']
                except:
                    pass
            except:
                model = "Unknown"
            file_type = "images"
        else:
            print(f"Unknown format {ext_file}")
            info_found = False

        if info_found:
            #print(model)
            #print(creation_time)
            to_folder_name = f'{creation_time[:4]}-{creation_time[5:7]}'
            #print(to_folder_name)
            to_create_folder = os.path.join('organized',file_type,model,to_folder_name)
            if to_create_folder not in check_created_folders:
                print(f"create {to_create_folder}")
                os.makedirs(to_create_folder)
                check_created_folders.append(to_create_folder)

            for seq in range(1,100000):
                to_file_name = f'{creation_time[:4]}{creation_time[5:7]}{creation_time[8:10]}_{seq:05}.{ext_file.lower()}'
                if to_file_name not in check_created_files:
                    check_created_files.append(to_file_name)
                    break

            shutil.copy2(file_name,os.path.join(to_create_folder,to_file_name))
            print(f'{file_name}-->{os.path.join(to_create_folder,to_file_name)}')
            
                
