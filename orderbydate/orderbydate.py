"""
Script to order files with dates in their names (yyyymm...) into subsequent directories
"""

import os
import sys
import shutil

def main_func (path='/home/user'):
   
    if len(sys.argv) != 5:
        print("Error, not enough arguments passed. Usage: orderbydate [sourcedir] [destinationdir] [exceptionsdir] [validyears]")
        sys.exit(1)  # Exit with error status 1

    sdir = sys.argv[1]
    ddir = sys.argv[2]
    edir = sys.argv[3]
    vy_start = sys.argv[4][:4]
    vy_end = sys.argv[4][5:]

# PRECHECKS
    if not os.path.exists(sdir):
        print("Error, source folder does not exist: ", sdir)
        sys.exit(2)  # Exit with error status 1
    if not os.path.exists(ddir):
        print("Error, destination folder does not exist: ", ddir)
        sys.exit(2)  # Exit with error status 1
    if not os.path.exists(edir):
        print("Error, exceptions folder does not exist: ", edir)
        sys.exit(2)  # Exit with error status 1
    if len(sys.argv[4])!=9 or not vy_start.isdigit() or not vy_end.isdigit() or vy_end<vy_start:
        print("Error, use correct validyear format (eg. 1990-2011)")
        sys.exit(2)  # Exit with error status 1


# LETS GO
    header = "=================== orderbydate.py ===================" \
        + "\n  Source directory:  " + sdir \
        + "\n  Destination directory:  " + ddir \
        + "\n  Exceptions directory:  " + edir \
        + "\n  Valid years start:  " + vy_start \
        + "\n  Valid years end:  " + vy_end
    print(header)
    nfulldated = 0
    npartdated = 0
    nexcept = 0

    with open(os.path.join(ddir, "./orderbydate.rep"), 'w') as f:  # Open the file in write mode ('w')
        f.write(header + '\n\n')  # Write the logmessage
        for root, _, files in os.walk(sdir):
            for fname in files:
                fyear = fname[:4]
                fmonth = fname[4:6]
                if fyear.isdigit():
                    if int(fyear) >= int(vy_start) and int(fyear)<=int(vy_end):
                        movedir = os.path.join(ddir, fyear)
                        if fmonth.isdigit() and int(fmonth) > 0 and int(fmonth) < 13:
                            nfulldated+=1
                            movedir = os.path.join(movedir, fmonth)
                        else:
                            npartdated+=1
                            f.write(f"  Invalid month for file: {fname}\n")
                    else:
                        f.write(f"  File year is outside of selected valid range: {fname}\n")
                        nexcept+=1
                        movedir = edir
                else:
                    nexcept+=1
                    movedir = edir

                try:
                    if not os.path.exists(movedir):
                        os.makedirs(movedir) #create destination if it doesn't exist.
                except FileNotFoundError:
                    print(f"Error: Source path '{movedir}' not found.")
                except PermissionError:
                    print(f"Error: Permission denied to access '{movedir}'.")
                except OSError as e:
                    print(f"An OS error occured: {e}")

                try:
                    movefile=os.path.join(root, fname)
                    shutil.move(movefile, os.path.join(movedir, fname))
                    message = "File [" + movefile + "] moved to " + movedir
                    f.write(message + '\n\n')  # Write the logmessage
                except shutil.Error as e:
                    print(f"Error moving '{movefile}': {e}")
                except PermissionError as e:
                    print(f"Permissions error moving '{movefile}': {e}")
                except OSError as e:
                    print(f"OS error moving '{movefile}': {e}")


        footer = "\n  Total number of files moved:  " + str(nfulldated+npartdated+nexcept) \
            + "\n  ...fully dated:  " + str(nfulldated) \
            + "\n  ...partially dated files:  " + str(npartdated) \
            + "\n  ...exception files:  " + str(nexcept) \
            + "\n======================================================"
        print(footer)
        f.write('\n\n\n' + message)  # Write the final logmessage


if __name__ == "__main__":
    main_func ()
    sys.exit(0)
