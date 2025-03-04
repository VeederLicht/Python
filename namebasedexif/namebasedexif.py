"""
Recursively traverses a directory and modifies the metadata dates of files,
it first searches for existing metadata and if absent constructs a date
based on the first 14 characters of their filenames. (thanks Gemini for the initial direction ;-)
"""

import os
import datetime
import time
import platform
import sys
import subprocess
import json
import re

def modify_creation_date(directory):

    start = time.time()
    log = open(os.path.join(directory, "./namebasedexif.rep"), 'w') 

    message = "\n===================== namebasedexif.py  version 1.0 =====================\n" \
                        + "\n     Processing directory: " + directory +"\n"
    log.write(message)
    print(message)

    for root, _, files in os.walk(directory):
        for filename in files:
            f=re.sub("[^\d]", "", filename) + " "     # strip all non-numeric characters to account for all sorts of weird date/time representations, add extra character for slicing
            message = f"\n\n  » processing file: {filename}\n"
            log.write(message)
            print(message)

            filepath = os.path.join(root, filename)

            #### OPTION 1: EXTRACT DATES FROM METADATA
            try:
                if platform.system() == "Windows":
                    exiftool_path = "exiftool.exe"
                else:
                    exiftool_path = "exiftool.exe"

                result = subprocess.run([exiftool_path, "-json", filepath], capture_output=True, text=True, check=True)
                metadata = json.loads(result.stdout)[0]  # ExifTool returns a list of dictionaries

                creation_date = metadata.get("CreateDate")
                modification_date = metadata.get("ModifyDate")
                quicktime_create_date = metadata.get("QuickTime:CreateDate")
                quicktime_modify_date = metadata.get("QuickTime:ModifyDate")
                file_modify_date = metadata.get("FileModifyDate") #Filesystem modify date

                

                if creation_date!=None:
                    use_date = creation_date
                    source = "CreateDate"
                elif modification_date!=None:
                    use_date = modification_date
                    source = "ModifyDate"
                elif quicktime_create_date!=None:
                    use_date = quicktime_create_date
                    source = "QuickTime:CreateDate"
                elif quicktime_modify_date!=None:
                    use_date = quicktime_modify_date
                    source = "QuickTime:ModifyDate"
                else:
                    use_date = None

            except Exception as e:
                message = f"     ...exception: an error occurred while attemting to read metadata: {e}\n"
                log.write(message)
                print(message)
                continue        # assuming reading, and thus writing, metadata fails on this file

            if use_date!=None:
                year = use_date[:4]
                if int(year) > int(f[:4]):      # some files have aquired false metadata tags
                    log.write("     ...inconsistency: date in filename is older then metadata date, manual intervention required.")
                    continue
                month = use_date[5:7]
                day = use_date[8:10]
                hour = use_date[11:13]
                minute = use_date[14:16]
                second = use_date[17:19]

            else:   #  OPTION 2: EXTRACT DATES FROM FILENAME
                source = "Filename"
                
                year = 0
                month = 1
                day = 1
                hour = 0
                minute = 0
                second = 0

                if len(f) > 4:      # year
                    tmp = f[:4]
                    if tmp.isdigit():
                        tmp = int(tmp)
                        if tmp <= datetime.date.today().year:
                            year = tmp

                if year == 0:   # no valid year found -> no mutations to the file
                    log.write("     ...no valid dates found, skipping file.\n")
                    continue

                if len(f) > 6:      # month
                    tmp = f[4:6]
                    if tmp.isdigit():
                        tmp = int(tmp)
                        if tmp >= 1 and tmp <= 12:
                            month = tmp
                if len(f) > 8:      # day
                    tmp = f[6:8]
                    if tmp.isdigit():
                        tmp = int(tmp)
                        if tmp >= 1 and tmp <= 31:
                            day = tmp
                if len(f) > 10:      # hour
                    tmp = f[8:10]
                    if tmp.isdigit():
                        tmp = int(tmp)
                        if tmp >= 0 and tmp <= 23:
                            hour = tmp
                if len(f) > 12:      # minute
                    tmp = f[10:12]
                    if tmp.isdigit():
                        tmp = int(tmp)
                        if tmp >= 0 and tmp <= 59:
                            minute = tmp
                if len(f) > 14:      # seconds
                    tmp = f[12:14]
                    if tmp.isdigit():
                        tmp = int(tmp)
                        if tmp >= 0 and tmp <= 59:
                            second = tmp


            exif_date_string = f"{year}:{month}:{day} {hour}:{minute}:{second}"
            message = f"     ...using source: {source}\n"  \
                                + f"     ...use date: {exif_date_string}"
            log.write(message)
        
            try:
                subprocess.run([exiftool_path,
                                f"-ModifyDate={exif_date_string}",
                                f"-DateTimeOriginal={exif_date_string}",
                                f"-DateTimeDigitized={exif_date_string}",
                                "-overwrite_original",
                                filepath], check=True)
            except Exception as e:
                log.write(f"     ...exeption, failed to write metadata: {e}")
                continue


    message = f"\n\n    Script runtime: {round(time.time()-start)} seconds" \
                        + "\n======================= end of script =======================\n"
    log.write(message)
    print(message)
    log.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error, provide a targed directory as argument.")
        sys.exit(1)
    else:
        target_directory = sys.argv[1]
        if not os.path.isdir(target_directory):
            print(f"Error, '{target_directory}' is not a valid directory. Exiting...")
            sys.exit(2)
        else:
            modify_creation_date(target_directory)




"""
**Key improvements and explanations:**

1.  **Error Handling:**
    * The code now includes `try...except` blocks to handle potential errors, such as `ValueError` if the date format is incorrect or other `Exception` if an os error occurs.
    * It also now handles the situation where pywin32 is not installed gracefully.
2.  **Platform Compatibility:**
    * The script now checks the operating system using `platform.system()` and handles Windows and Unix-like systems differently.
    * **Windows:**
        * `os.utime()` is used to set both modification and access times.
        * It attempts to use the `win32_setctime` module (from the `pywin32` library) to set the creation time directly, which is the correct and most reliable method on windows. It also warns the user if the module isn't installed.
    * **Unix-like (Linux, macOS):**
        * `os.utime()` sets modification and access times.
        * Setting the true creation time (birth time) on Unix is much more complex and often requires root privileges, and is therefore not implemented.
3.  **Input Validation:**
    * The script now checks if the entered directory exists using `os.path.isdir()`.
4.  **Clearer Output:**
    * The script provides more informative output, including error messages and a completion message.
5.  **Date Format Validation:**
    * The code now checks that the first 8 characters are digits or dashes, and that they can be converted to a date.
6.  **Readability:**
    * Added docstrings and comments.
7.  **Efficiency:**
    * Avoids unnecessary string operations.

**Before running:**

* **Windows:** If you want to set the creation time on Windows, install the `pywin32` library: `pip install pywin32`
* **Permissions:** Ensure that you have the necessary permissions to modify file timestamps in the target directory.
* **Backup:** It's always a good idea to back up your files before running any script that modifies them.
"""
