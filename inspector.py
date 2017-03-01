import codecs
from dateutil import parser
from terminaltables import AsciiTable
from collections import defaultdict
from optparse import OptionParser

class time(object):
    def __str__(self):
        return "time"
    # def
# class

class empty(object):
    def __str__(self):
        return "empty"
    # def
# class

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    # try
# def

def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
    # try
# def

def is_datetime(value):
    try:
        parser.parse(value)
        return True
    except:
        return False
    # try
# def

def parse_options():
    parser = OptionParser()

    parser.add_option("-f", "--file",    dest="file",    help="csv file to process", default="")
    parser.add_option("-w", "--where",   dest="where",   help="where cluase to filter out some fields, use simple python code", default="")
    parser.add_option("-c", "--columns", dest="columns", help="comma separated list of column numbers, that you want to see in output", default="")

    options, args = parser.parse_args()
    return options.where, options.columns, options.file
# def

option_where, option_columns, input_file_name = parse_options()
if option_columns:
    option_columns = map(int, filter(lambda x: len(x.strip()) != 0, option_columns.split(',')))
else:
    option_columns = []
# if

if not input_file_name:
    print "Input files is omitted! Use -h to see the right option"
    exit()
# if

LINES_TO_CHECK_UNIQUE = 10000
#---------------#

column_name = []
column_inx_values = defaultdict(set)
column_inx_types = defaultdict(set)
column_inx_capacity = []
column_inx_repeatness = []
column_inx_max_length = []
column_inx_min_length = []

is_unique = []
is_half = []

lines_count = 0

#input_file_name = 'MX_2017-02-08.csv'

with codecs.open(input_file_name, 'r', encoding='utf-8') as fin:
    first = True

    for line in fin:
        column = line.split(',')

        if first:
            first = False
            column_name = map(lambda x: x.strip(), list(column))
            is_unique = [False] * len(column_name)
            is_half = [False] * len(column_name)
            column_inx_capacity = [0.0] * len(column_name)
            column_inx_repeatness = [0] * len(column_name)
            column_inx_max_length = [0] * len(column_name)
            column_inx_min_length = [1000000] * len(column_name)
            continue
        # if

        if lines_count == LINES_TO_CHECK_UNIQUE:
            for inx in range(len(column_name)):
                is_unique[inx] = len(column_inx_values[inx]) == lines_count
                is_half[inx] = len(column_inx_values[inx]) >= int(lines_count / 2)
                column_inx_capacity[inx] = (len(column_inx_values[inx]) * 100.0) / LINES_TO_CHECK_UNIQUE
            # for
        # if

        if option_where:
            if not eval(option_where):
                continue
            # if
        # if

        for inx in range(len(column_name)):
            if not is_unique[inx] and len(column) > inx:
                column[inx] = column[inx].strip()

                if column[inx] in column_inx_values[inx]:
                    column_inx_repeatness[inx] += 1
                # if

                column_inx_values[inx].add(column[inx])
            # if
        # for

        lines_count += 1
    # for
# with

#----------------------------#
# Inspect types
#----------------------------#

for inx in range(len(column_name)):
    for value in column_inx_values[inx]:
        if len(value) < column_inx_min_length[inx]:
            column_inx_min_length[inx] = len(value)
        # if

        if len(value) > column_inx_max_length[inx]:
            column_inx_max_length[inx] = len(value)
        # if

        if len(value):
            if is_float(value):
                if is_int(value):
                    column_inx_types[inx].add(int)
                else:
                    column_inx_types[inx].add(float)
                # if
            else:
                if is_int(value):
                    column_inx_types[inx].add(int)
                # if
            # if

            if is_datetime(value):
                column_inx_types[inx].add(time)
            # if
        else:
            column_inx_types[inx].add(empty)
        # if
    # for
# for

for inx in range(len(column_name)):
   if len(column_inx_types[inx]) == 0:
       column_inx_types[inx].add(str)
   # if

   if not is_unique[inx]:
       column_inx_repeatness[inx] = (column_inx_repeatness[inx] * 100.0) / lines_count
       column_inx_capacity[inx]   = (len(column_inx_values[inx]) * 100.0) / lines_count
   # if
# for

# ================================ #
# Form table and print it out
# ================================ #

table_data = []

# add header
table_data.append(['inx', 'name', 'unique', 'length', 'types', 'values'])

for inx in range(len(column_name)):
    if len(option_columns) and inx not in option_columns:
        continue
    # if

    data = []
    data.append(inx)
    data.append(column_name[inx])
    data.append(is_unique[inx])
    data.append('[' + str(column_inx_min_length[inx]) + ':' + str(column_inx_max_length[inx]) + ']');
    data.append(', '.join(map(lambda x: x.__name__, column_inx_types[inx])))
    
    if len(column_inx_values[inx]) <= 4 and len(column_inx_values[inx]) > 0:
        data.append(', '.join(column_inx_values[inx]))
    elif len(column_inx_values[inx]) == 1:
        data.append("")
    else:
        data.append("<too much>")
    # if

    table_data.append(data)
# for

print AsciiTable(table_data).table
print "LINES COUNT : ", lines_count

