#!/usr/bin/env python3

import sys
import xlrd
from db_table import db_table

# according to readme schema will always have this format when including all columns
agenda_schema = {
    "date": "TEXT",
    "time_start": "TEXT",
    "time_end": "TEXT",
    "session": "TEXT",
    "title": "TEXT",
    "location": "TEXT",
    "description": "TEXT",
    "speaker": "TEXT",
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT", # added for foreign key relationship with sub sessions
}

sub_sessions_schema = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "parent_session_id": "INTEGER",  # Foreign key linking to the main session
}

# tables need names
agenda_name = "Agenda"
sub_name = "Subsessions"

def parse_sub_content(agenda_table, sub_table):
    # get all rows in table
    rows = agenda_table.select()
    
    # find subsession rows and link them to their parents in sub table
    parent_id = 0
    for row in rows:
        # assumes that first row will always be Session not Sub
        if row['session'].strip() == "Sub":
            sub_table.insert({"parent_session_id": parent_id})
        else:
            parent_id = row['id']

            
def parse_agenda_content(sheet, agenda_table):
    # row with column names is at line 14 in file, data begins at line 15
    name_row = 14
    # row info that will be inserted
    row_data = {}
    # used to iterate through columns in table to match to schema
    col_names = list(agenda_schema.keys())

    # iterate each column in each row in file sheet
    for i in range(name_row + 1, sheet.nrows):
        for j in range(len(sheet.row(i))):
            cell = str(sheet.cell_value(rowx=i, colx=j))
            # fix issues with passing in cells with special chars for sql (ex. "-")
            row_data[f'"{col_names[j]}"'] = str(cell).replace("'", "''").strip()
        # new row for table
        agenda_table.insert(row_data)

def make_tables(file):
    # select the sheet with the table data
    book = xlrd.open_workbook(file)
    sheet = book.sheet_by_index(0)

    # name agenda data table and pass in schema
    agenda_table = db_table(agenda_name, agenda_schema)

    # subsession table for linking to parent sessions
    sub_table = db_table(sub_name, sub_sessions_schema)

    # populate tables with excel file content
    parse_agenda_content(sheet, agenda_table)
    parse_sub_content(agenda_table, sub_table)

# script is run as ./import_agenda.py agenda.xls
if __name__ == "__main__":
    if len(sys.argv) == 2:
        file = sys.argv[1]
        make_tables(file)
    else:
        print("Usage: ./import_agenda agenda.xls")
