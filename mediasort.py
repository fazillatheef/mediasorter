import PIL.Image,PIL.ExifTags,os
import ffmpeg
from datetime import datetime
import shutil

DUMMY_MODE = True

check_created_folders = [] #Stop trying to create the directory again and again
check_created_files = [] #To check if sequence number must be incremented
file_read_ct = img_file_read_ct = file_ign_ct = video_file_read_ct = folder_create_ct = file_copied_ct =  0

if DUMMY_MODE:
    print("Running in dummy mode!!!")
#Go thru folder structure
for root, subdirs, files in os.walk('randomfiles'):
    for each_file in files:
        file_read_ct += 1
        info_found = True
        file_name = os.path.join(root,each_file)
        try:
            ext_file = file_name[file_name.rfind('.')+1:].upper()
        except:
            ext_file = ""
        #Find last modified date to use incase no meta data is available
        creation_time = datetime.fromtimestamp(os.path.getmtime(file_name)).strftime("%Y-%m-%d")
        if ext_file in ['MOV','3GP','MP4','MPEG']:
            video_file_read_ct += 1
            vid_dict = ffmpeg.probe(file_name)["streams"]
            # Decided model based on following
            # If there it is MOV format, it is either DSLR or iphone
            # If there is a creation date, it is an Android video
            # If there it is 3GP, then it is an old video
            # Else it is categorized as Other video
            model = 'Other video'
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
            img_file_read_ct += 1
            # Read the meta data from EXIF, if not found model is marked as Unknown
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
            file_ign_ct += 1

        if info_found:
            to_folder_name = f'{creation_time[:4]}-{creation_time[5:7]}'
            to_create_folder = os.path.join('organized',file_type,model,to_folder_name)
            if to_create_folder not in check_created_folders:
                print(f"created folder {to_create_folder}")
                if not DUMMY_MODE:
                    os.makedirs(to_create_folder)
                    folder_create_ct += 1
                check_created_folders.append(to_create_folder)

            for seq in range(1,100000):
                to_file_name = f'{creation_time[:4]}{creation_time[5:7]}{creation_time[8:10]}_{seq:05}.{ext_file.lower()}'
                if to_file_name not in check_created_files:
                    check_created_files.append(to_file_name)
                    break
            if not DUMMY_MODE:
                # copy2 used to copy without changing the modified dates 
                shutil.copy2(file_name,os.path.join(to_create_folder,to_file_name))
                file_copied_ct += 1
            print(f'copied {file_name}-->{os.path.join(to_create_folder,to_file_name)}')

print(f"Files read : {file_read_ct}")
print(f"Images read : {img_file_read_ct}")
print(f"Videos read : {video_file_read_ct}")
print(f"Files ignored : {file_ign_ct}")
print(f"Folders created : {folder_create_ct}")
print(f"Number of folders in list : {len(check_created_folders)}")
print(f"Files copied : {file_copied_ct}")
print(f"Number of files in list : {len(check_created_files)}")
