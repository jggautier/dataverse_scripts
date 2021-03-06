# For each dataset listed in dataset_pids.txt, get the basic metadata that lives outside of the metadata blocks

import csv
import json
import glob
import os
from pathlib import Path
from tkinter import filedialog
from tkinter import ttk
from tkinter import *

# Create GUI for getting user input

# Create, title and size the window
window = Tk()
window.title('Get basic dataset metadata')
window.geometry('550x500')  # width x height


# Function called when Browse button is pressed
def retrieve_jsondirectory():
    global jsonDirectory

    # Call the OS's file directory window and store selected object path as a global variable
    jsonDirectory = filedialog.askdirectory()

    # Show user which directory she chose
    label_showChosenDirectory = Label(window, text='You chose: ' + jsonDirectory, anchor='w', foreground='green', wraplength=500, justify='left')
    label_showChosenDirectory.grid(sticky='w', column=0, row=2)


# Function called when Browse button is pressed
def retrieve_csvdirectory():
    global csvDirectory

    # Call the OS's file directory window and store selected object path as a global variable
    csvDirectory = filedialog.askdirectory()

    # Show user which directory she chose
    label_showChosenDirectory = Label(window, text='You chose: ' + csvDirectory, anchor='w', foreground='green', wraplength=500, justify='left')
    label_showChosenDirectory.grid(sticky='w', column=0, row=6)


# Function called when Browse button is pressed
def start():
    window.destroy()


# Create label for button to browse for directory containing JSON files
label_getJSONFiles = Label(window, text='Choose folder containing the JSON files:', anchor='w')
label_getJSONFiles.grid(sticky='w', column=0, row=0, pady=2)

# Create button to browse for directory containing JSON files
button_getJSONFiles = ttk.Button(window, text='Browse', command=lambda: retrieve_jsondirectory())
button_getJSONFiles.grid(sticky='w', column=0, row=1)

# Create empty row in grid to improve spacing between the two fields
window.grid_rowconfigure(3, minsize=25)

# Create label for button to browse for directory to add csv files in
label_tablesDirectory = Label(window, text='Choose folder to store the csv files:', anchor='w')
label_tablesDirectory.grid(sticky='w', column=0, row=4, pady=2)

# Create button to browse for directory containing JSON files
button_tablesDirectory = ttk.Button(window, text='Browse', command=lambda: retrieve_csvdirectory())
button_tablesDirectory.grid(sticky='w', column=0, row=5)

# Create start button
button_Start = ttk.Button(window, text='Start', command=lambda: start())
button_Start.grid(sticky='w', column=0, row=7, pady=40)

# Keep window open until it's closed
mainloop()


def improved_get(_dict, path, default=None):
    for key in path.split('.'):
        try:
            _dict = _dict[key]
        except KeyError:
            return default
    return str(_dict)


# Add path of csv file to filename variable
filename = os.path.join(csvDirectory, 'basic_metadata.csv')

print('Creating CSV file')

with open(filename, mode='w', newline='') as metadatafile:
    metadatafile = csv.writer(metadatafile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    metadatafile.writerow(['datasetVersionId', 'persistentUrl', 'persistent_id', 'datasetPublicationDate', 'versionCreateTime', 'versionState', 'majorVersionNumber', 'minorVersionNumber', 'publisher'])  # Create header row

print('Getting metadata:')
error_files = []

# For each JSON file in a folder
for file in glob.glob(os.path.join(jsonDirectory, '*.json')):

    # Open each file in read mode
    with open(file, 'r') as f1:
        # Copy content to dataset_metadata variable
        dataset_metadata = f1.read()
        # Load content in variable as a json object
        dataset_metadata = json.loads(dataset_metadata)

        # Check if JSON file has "data" key
        if dataset_metadata['status'] == 'OK':
            datasetVersionId = dataset_metadata['data']['datasetVersion']['id']
            persistentUrl = dataset_metadata['data']['persistentUrl']
            datasetPersistentId = improved_get(dataset_metadata, 'data.datasetVersion.datasetPersistentId')
            versionCreateTime = dataset_metadata['data']['datasetVersion']['createTime']
            versionState = dataset_metadata['data']['datasetVersion']['versionState']
            datasetPublicationDate = dataset_metadata['data']['publicationDate']
            majorVersionNumber = improved_get(dataset_metadata, 'data.datasetVersion.versionNumber')
            minorVersionNumber = improved_get(dataset_metadata, 'data.datasetVersion.versionMinorNumber')
            publisher = dataset_metadata['data']['publisher']

            # Write fields to the csv file
            with open(filename, mode='a', newline='') as metadatafile:

                # Convert all characters to utf-8
                def to_utf8(lst):
                    return [unicode(elem).encode('utf-8') for elem in lst]

                metadatafile = csv.writer(metadatafile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                # Write new row
                metadatafile.writerow([datasetVersionId, persistentUrl, datasetPersistentId, datasetPublicationDate, versionCreateTime, versionState, majorVersionNumber, minorVersionNumber, publisher])
            # As a progress indicator, print a dot each time a row is written
            sys.stdout.write('.')
            sys.stdout.flush()

        # If JSON file doens't have "data" key, add file to list of error_files
        else:
            error_files.append(Path(file).name)
print('\n')
if error_files:
    print('\nThe following files may not have metadata:%s' % (error_files))
