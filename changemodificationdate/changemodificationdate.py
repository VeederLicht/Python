"""
Recursively traverses a directory and modifies the creation date of files
based on the first 8 characters of their filenames. (thanks Gemini for the initial direction ;-)
"""

import os
import datetime
import time
import platform
import sys

def modify_creation_date(directory):

    start = time.time()
    log = open(os.path.join(directory, "./changemodificationdate.rep"), 'w') 

    message = "\n===================== changemodificationdate.py =====================\n" \
                        + "\n     Processing directory: " + directory +"\n"
    log.write(message)
    print(message)
    for root, _, files in os.walk(directory):
        for filename in files:
            log.write(f"\n\n  » processing file: {filename}")
            f = filename.replace("-", "")
            f=f.replace("_","")
            f=f.replace(".", "")
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
                    if tmp < 1970:
                        year = 1970
                    elif tmp >= 1970 and tmp <= datetime.date.today().year:
                        year = tmp

            if year == 0:   # no valid year found -> no mutations to the file
                log.write("\n  ...no valid dates found, skipping file.")
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

            message = f"\n  ...year: {year}"  \
                                + f"\n  ...month: {month}" \
                                + f"\n  ...day: {day}" \
                                + f"\n  ...hour: {hour}" \
                                + f"\n  ...minute: {minute}" \
                                + f"\n  ...second: {second}"
            log.write(message)

            try:
                dt = datetime.datetime(year, month, day, hour, minute,second)
                timestamp = time.mktime(dt.timetuple())
                filepath = os.path.join(root, filename)
                if platform.system() == 'Windows':
                    # Windows: Modification and creation times are set together
                    os.utime(filepath, (timestamp, timestamp))

                    # Set creation time directly (Windows specific, requires pywin32 module):
                    try:
                        import win32_setctime
                        win32_setctime.setctime(filepath, timestamp)
                    except ImportError:
                        log.write("\n  ...warning: pywin32 module not found. Creation time may not be set on Windows.")
                    except Exception as e:
                        log.write(f"\n  ...error setting creation time on windows: {e}")
                else:
                    # Unix-like systems (Linux, macOS): Modification and access times are set.
                    os.utime(filepath, (timestamp, timestamp))
                    #setting the birthtime is more complex and system dependent, and often requires root.
            except ValueError:
                log.write(f"\n  ...invalid date format in filename: {filename}")
            except Exception as e:
                log.write(f"\n  ...error processing file {filename}: {e}")

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
