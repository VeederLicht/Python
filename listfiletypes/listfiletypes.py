"""
    Recursively traverses a directory and lists and counts all filetypes in these directories (thanks Gemini for the initial direction ;-)
    """

import os
import time
import sys

def list_filetypes(directory):

    start = time.time()
    log = open(os.path.join(directory, "./listfiletypes.rep"), 'w') 


    message = "\n===================== listfiletypes.py =====================\n" \
                        + "\n     Processing directory: " + directory +"\n"
    log.write(message)
    print(message)

    ext_dict = {}
    i = 0

    for root, _, files in os.walk(directory):
        for filename in files:
            i += 1
            try:
                ext =  os.path.splitext(filename)[1] #os.path.splitext returns a tuple (filename without extension, extension)
            except IndexError: # catches errors that might occur if the filename is empty.
                print(f"Error, file extension could not be identified of file: {filename}")
                continue
            
            if ext in ext_dict:
                ext_dict [ext] += 1
            else:
                ext_dict [ext] = 1


    message = f"\n\n  Script finished, scanned {i} files and found these extensions:"
    for ftype in ext_dict:
        message = message + f"\n   .......... {ftype}: {ext_dict[ftype]}"
    
    log.write(message)
    print(message)

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
            list_filetypes(target_directory)