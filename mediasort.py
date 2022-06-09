import PIL.Image,PIL.ExifTags,os
import ffmpeg
from datetime import datetime
import shutil
import argparse
import sys

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("path", help="Give the path where images are not sorted")
arg_parser.add_argument("--commit",action="store_true",default=False,help="Without commit the program wont action any file operations")
arg_parser.add_argument("--out",default="organized",help="Optional path where the files/folders will be created")
arg_parser.add_argument("--log",default="media-sort.log",help="Log file to show where the files will be copied")
arg_parser.add_argument("--smlog",default="small-files.log",help="List of small files")
args = arg_parser.parse_args()

check_created_folders = [] #Stop trying to create the directory again and again
check_created_files = [] #To check if sequence number must be incremented
file_read_ct = img_file_read_ct = file_ign_ct = video_file_read_ct = folder_create_ct = file_copied_ct = file_small_ct= total_file_size= copy_file_size= 0
exclude=['.dtrash']

class logfile:
    def __init__(self,file_name):
        self.log_file = open(file_name,"w")
    def print(self,txt):
        self.log_file.writelines(f"{txt}\n")
    def __del__(self):
        self.log_file.close()

log = logfile(args.log)
smlog = logfile(args.smlog)

if not args.commit:
    print("Running in dummy mode!!!")
#Go thru folder structure
for root, subdirs, files in os.walk(args.path,topdown=True):
    subdirs[:] = [d for d in subdirs if d not in exclude]
    for each_file in files:
        file_read_ct += 1
        sys.stdout.write('\r')
        sys.stdout.write(f'{file_read_ct} files read')
        info_found = True
        file_name = os.path.join(root,each_file)
        try:
            ext_file = file_name[file_name.rfind('.')+1:].upper()
        except:
            ext_file = ""
        #Find last modified date to use incase no meta data is available
        creation_time = datetime.fromtimestamp(os.path.getmtime(file_name)).strftime("%Y-%m-%d")
        file_size = os.path.getsize(file_name)
        total_file_size += file_size
        if ext_file in ['DB','AAE','DTRASHINFO','MP3','TTF']:
            info_found = False
            file_ign_ct += 1            
        elif ext_file in ['MOV','3GP','MP4','MPEG','AVI']:
            copy_file_size += file_size
            video_file_read_ct += 1

            # Decided model based on following
            # If there it is MOV format, it is either DSLR or iphone
            # If there is a creation date, it is an Android video
            # If there it is 3GP, then it is an old video
            # Else it is categorized as Other video
            model = 'Other video'
            try:
                vid_dict = ffmpeg.probe(file_name)["streams"]
                creation_time = vid_dict[0]['tags']['creation_time']
                model = 'Android video'
            except:
                pass
            
            if ext_file =='MOV':
                model = 'Iphone_DSLR video'
            elif ext_file =='3GP':
                model ='Old video'
            
            file_type = "videos"

        elif ext_file in ['JPG','PNG','JPEG','HEIC','BMP','SVG','TIF']:
            copy_file_size += file_size
            img_file_read_ct += 1
            # Read the meta data from EXIF, if not found model is marked as Unknown
            try:
                img = PIL.Image.open(file_name)
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
            if file_size < 100*1024:
                file_small_ct += 1
                smlog.print(file_name)
                file_type = "small-images"
            else:
                file_type = "images"
        else:
            print(f"\nUnknown format {ext_file}")
            info_found = False
            file_ign_ct += 1

        if info_found:
            to_folder_name = f'{creation_time[:4]}-{creation_time[5:7]}'
            to_create_folder = os.path.join(args.out,file_type,model,to_folder_name)
            if to_create_folder not in check_created_folders:
                log.print(f"created folder {to_create_folder}")
                if args.commit:
                    os.makedirs(to_create_folder)
                    folder_create_ct += 1
                check_created_folders.append(to_create_folder)

            for seq in range(1,100000):
                to_file_name = f'{creation_time[:4]}{creation_time[5:7]}{creation_time[8:10]}_{seq:05}.{ext_file.lower()}'
                if to_file_name not in check_created_files:
                    check_created_files.append(to_file_name)
                    break
            if args.commit:
                # copy2 used to copy without changing the modified dates 
                shutil.copy2(file_name,os.path.join(to_create_folder,to_file_name))
                file_copied_ct += 1
            log.print(f'copied {file_name}-->{os.path.join(to_create_folder,to_file_name)}')

print(f"\nFiles read : {file_read_ct}")
print(f"\tTotal file size to copy : {total_file_size/(1024*1024*1024):.2f} GB")
print(f"\tImages read : {img_file_read_ct}")
print(f"\t\tSmall images : {file_small_ct}")
print(f"\tVideos read : {video_file_read_ct}")
print(f"Files ignored : {file_ign_ct}")
print(f"Folders created : {folder_create_ct}")
print(f"\tNumber of folders in list : {len(check_created_folders)}")
print(f"Files copied : {file_copied_ct}")
print(f"\tFile size copied : {copy_file_size/(1024*1024*1024):.2f} GB")
print(f"\tNumber of files in list : {len(check_created_files)}")
