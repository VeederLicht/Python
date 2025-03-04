"""
    Recursively traverses a directory and renames all files lowercase (thanks Gemini for the initial direction ;-)
"""

import os
import time
import sys

def list_filetypes(directory):

    start = time.time()
    log = open(os.path.join(directory, "./renamelowercase.rep"), 'w') 


    message = "\n===================== renamelowercase.py =====================\n" \
                        + "\n     Processing directory: " + directory +"\n"
    log.write(message)
    print(message)


    for root, _, files in os.walk(directory):
        for filename in files:

            old_filepath = os.path.join(root, filename)
            new_filename = filename.lower()
            new_filepath = os.path.join(root, new_filename)

            if os.path.isfile(old_filepath) and filename != new_filename: #only rename if needed.
                log.write("\n      ...renaming file: ", filename)
                try:
                    os.rename(old_filepath, new_filepath)
                    print(f"\n Renamed '{old_filepath}' to '{new_filepath}'")
                except FileExistsError:
                    print(f"\n Error: File '{new_filepath}' already exists.")
                except Exception as e:
                    print(f"\n An unexpected error occurred: {e}")

                
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