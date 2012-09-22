# -*- coding: utf-8 -*-
""" Functions to write to and read from csv files """

from CONSTANT_VARIABLES import DEBUG_ON
import csv

def append_to_spreadsheet(csv_string, csv_path, identifiers_in_csv, rows_to_add, unique_identifiers=True):    
    ''' Appends to the spreadsheet the rows in rows_to_add not already in the spreadsheet 
    @param unique_identifiers: True if no two rows should be allowed 
    to have the same value in the identifier column, False otherwise'''
    if DEBUG_ON:
        print "Debug turned on, so not appending data to csv of "+csv_string
        return
    
    print "Updating the csv file of "+csv_string+"..."
    csv_writer = csv.writer(open(csv_path, 'a'), quoting=csv.QUOTE_MINIMAL)    
    for row in rows_to_add:
        try:
            identifier = row[0]
            if unique_identifiers and identifier in identifiers_in_csv:
                continue # already in spreadsheet
            csv_writer.writerow(row)    
        except Exception as e:
            print "Problem with row "+str(row), e
            continue
        
def query_csv_for_rows(csv_path):  
    rows = []
    row_num = 0
    for row in csv.reader(open(csv_path)):
        try:
            if row_num!=0: # row 0 is header
                rows.append(row)
            row_num = row_num+1    
        except:
            continue # just ignore a problematic row
    return rows

def query_csv_for_rows_with_value(csv_path, identifier_header, value_col_header, value_to_match):
    ''' 
    Returns a list of identifiers that correspond to the rows 
    that have the given cell value for the given column.
    
    @param identifier_header: the header of the column 
           that contains the identifiers of this csv
    @param value_col_header: the header of the column in which 
           we want to search for cells having the given value_to_match
    @param value_to_match: the value to search for in cells 
           in value_col_header column
    '''
    matching_row_ids = []
    row_num = 0
    for row in csv.reader(open(csv_path)):
        try:
            if row_num==0: #header
                identifier_column_index = row.index(identifier_header)
                query_column_index = row.index(value_col_header)
                row_num = row_num+1
                continue
                
            if value_to_match==row[query_column_index]:
                matching_row_ids.append(row[identifier_column_index])
            row_num = row_num+1    
        except:
            continue # just ignore a problematic row
    return matching_row_ids

def load_or_initialize_csv(csv_path, csv_string, headers, identifiers_header):
    print "Loading CSV file of "+csv_string+"..."
    try:
        identifiers = get_all_column_values(csv_path, identifiers_header)
    except Exception:
        # Spread sheet needs to be created and its header column written
        print "CSV file of "+csv_string+" not yet created. Creating now and writing column headers..."
        __initialize_csv__(csv_path, headers)
        identifiers = []
    return identifiers

def get_all_column_values(csv_path, column_header):
    read_spreadsheet = open(csv_path)
    dicts = csv.DictReader(read_spreadsheet)
    identifiers = [d[column_header] for d in dicts]
    return identifiers

def __initialize_csv__(csv_path, headers):
    if DEBUG_ON:
        print "Debug turned on, so not creating csv file"
        return
    csv_writer = csv.writer(open(csv_path, 'wb'))
    csv_writer.writerow(headers)
