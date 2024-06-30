import os
import re
from xml.dom import minidom

def get_run_date(run_dir):
    first_underscore_index = run_dir.find('_') 
    second_underscore_index = run_dir.find('_', first_underscore_index + 1)
    date_str = run_dir[first_underscore_index + 1:second_underscore_index]
    return date_str[4:6] + '-' + date_str[6:8] + '-' + date_str[0:4]

def get_drive_inventory(drive_letter, drive_id):

    # enter drive
    os.chdir(drive_letter + ':')

    # compile into records data about each movie stored on hard drive
    records = []
    for drive_dir in os.listdir(drive_letter + ':'):

        # for each directory containing a run
        if (drive_dir.startswith("r64140") or drive_dir.startswith("r54336U")):

            # enter run directory, collect data
            os.chdir(drive_dir)
            run_date = get_run_date(drive_dir)
            run_id = drive_dir

            for sub_dir in os.listdir():

                # for each sub directory containing a movie
                if (re.compile('^[1-8]_[A-H]0[1-9]$').match(sub_dir)):

                    # enter movie directory, collect data
                    os.chdir(sub_dir)
                    cell_id = sub_dir

                    sample_name = ''
                    movie_id = ''
                    biosample_name = ''
                    subreads_file_size = None
                    for filename in os.listdir():

                        if (re.compile('.+subreads.bam$').match(filename)):

                            # collect subreads file data
                            movie_id = filename[:filename.find('.')]
                            subreads_file_size = os.path.getsize(filename)

                        elif(re.compile('.+subreadset.xml').match(filename)):

                            # collect sample name                            
                            file = minidom.parse(filename)
                            subreadset_element = file.getElementsByTagName('pbds:SubreadSet')
                            sample_name = subreadset_element[0].getAttribute('Name')

                            # collect bio sample name (absent from older data?)
                            biosample_elements = file.getElementsByTagName('BioSample')
                            if len(biosample_elements) != 0:
                                biosample_name = ', '.join(element.getAttribute('Name') for element in biosample_elements)
                    
                    if movie_id != '':

                        # add a new record for this movie
                        records.append(', '.join(
                            [run_date, run_id,
                            cell_id, movie_id,
                            sample_name,
                            biosample_name, drive_id,
                            str(subreads_file_size)]
                        ))
                    else: print('\n *** Expected movie data in ' + os.getcwd() + ', found none. ***\n')

                    # return to run directory, continue looping through sub directories of run dir
                    os.chdir('..')
            
            # return to root directory, continue looping through run dirs
            os.chdir('..')
    return records

# prompt user to indicate which drive to inventory
input_str = input("Please enter the letter of a drive to be inventoried: ")

while 1:

    # validate user specification of drive
    while len(input_str) != 1 or not input_str.isalpha or not os.path.isdir(input_str + ':'): 
        input_str = input("No such drive! Please enter the letter of a drive: ")

    # prompt user to provide the id number of the drive
    drive_id = 'HD' + input('What is this drive\'s ID number? ')

    # print inventory of drive
    for record in get_drive_inventory(input_str, drive_id):
        print(record)

    # provide opportunity either to inventory another drive or to exit
    input_str = input('\nEnter the letter of another drive to inventory, or press enter to exit this script: ')
    if input_str == '':
        break
