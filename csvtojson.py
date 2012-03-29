import csv
import json

import dictformater


def csvtojson(filename, clean_func=None, clean_func_dict=None, verbose=False):
    """
    @param    filename           String                            File name to open()

    @param    clean_func         Function pointer                  Optional. If provided, each 'cell' will be processed
                                                                   by this function.

    @param    clean_func_dict    Dictionary of function pointer    Optional. Takes the form of {header: function_pointer},
                                                                   where each 'cell' in the CSV will be used to lookup a
                                                                   function for processing based on said cell's header.

    @param    verbose            Boolean                           Used to print() debug info.
    """
    with open(filename, 'r') as fp:
        reader = csv.DictReader(fp)

        c = 0

        for row in reader:
            if verbose:
                print("csvtojson('{filename}'): Processing line: {l}".format(filename=filename, l=row))

            if c:  # We're using 'c' as a flag for skipping the first row
                row = dictformater.reformat(row, clean_func=clean_func, clean_func_dict=clean_func_dict, verbose=verbose)

            else:
                c = 1

            yield json.dumps(row)


## ---------------------
if __name__ == "__main__":
    for line in csvtojson(filename="input.csv", clean_func=lambda x: x.strip(), verbose=True):
        print line
