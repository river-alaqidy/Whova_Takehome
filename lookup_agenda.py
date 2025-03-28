#!/usr/bin/env python3

import sys
from db_table import db_table
from import_agenda import agenda_schema, agenda_name, sub_sessions_schema, sub_name

def format_row(row, column_widths, columns):
    # when printing rows formate to fit in column width
    formatted_values = []
    for col in columns:
        value = truncate(row.get(col, "")) # values can sometimes be empty
        formatted_values.append(value.ljust(column_widths[col]))  # make sure text is left justified for display
    return " | ".join(formatted_values) # separate columsn with |

def truncate(value, max_length=20):
    # some column cells are too long to be formatted nicely, so if value exceeds 20 chars then replace rest of value with "..."
    value = str(value) # prevents int errors when passing in ids
    if len(value) <= max_length:
        return value
    else:
        return value[:max_length] + "..."

def print_results(output):

    # get column headers
    columns = list(agenda_schema.keys())
    column_widths = {}
    # for formatting columns for outputting, will have mimimum 10 spacing
    for col in columns:
        column_widths[col] = max(len(col), 10)

    # Adjust column widths based on actual data
    for row in output.values():
        # subsession of parent sessions are stored as lists in dict
        if isinstance(row, list):  
            for sub_row in row:
                for col in columns:
                    column_widths[col] = max(column_widths[col], len(truncate(str(sub_row.get(col, ""))))) # output can be too long sometimes
        else:
            # regular session rows
            for col in columns:
                column_widths[col] = max(column_widths[col], len(truncate(str(row.get(col, "")))))

    # print result header
    header_row = " | ".join(col.ljust(column_widths[col]) for col in columns)
    print(header_row)
    print("-" * len(header_row))  # separate headers from data

    # print data search results
    for key, row in output.items():
        # subsessions are lists in dict
        if isinstance(row, list):  
            for sub_row in row:
                print(format_row(sub_row, column_widths, columns))
        else:
            # regular session results
            print(format_row(row, column_widths, columns))

def lookup(column, value, agenda_table, sub_table):
    output = {}

    # speaker column search is a special case
    if column == "speaker":
        # get all rows from table
        results = agenda_table.select()

        # for each row see if desired speaker is listed
        for row in results:
            # speaker column is string with ; delimiters
            speakers = []
            for speaker in row['speaker'].strip().split(';'):
                speakers.append(speaker.strip())

            # add matching speaker value to eventual output
            if value.strip() in speakers:
                key = row['id']
                output[key] = row
                sub_sessions = sub_table.select(where={"parent_session_id": row['id']})
                for i in range(len(sub_sessions)):
                    sub = agenda_table.select(where={"id": row['id'] + i + 1})
                    key = row['id'] + i + 1
                    output[key] = sub
        print_results(output)
                
    # for all other search cases besides speakers
    else:
        # get results with matching desired column
        results = agenda_table.select(where={column: value})
        for row in results:
            key = row['id']
            output[key] = row
            sub_sessions = sub_table.select(where={"parent_session_id": row['id']})
            for i in range(len(sub_sessions)):
                sub = agenda_table.select(where={"id": row['id'] + i + 1})
                key = row['id'] + i + 1
                output[key] = sub
        print_results(output)

# script is run as ./lookup_agenda.py column value
if __name__ == "__main__":
    if len(sys.argv) == 3:
        column = sys.argv[1]
        value = sys.argv[2]
        # connect to tables in db, should already have been made from running import_agenda script
        agenda_table = db_table(agenda_name, agenda_schema)
        sub_table = db_table(sub_name, sub_sessions_schema)
        lookup(column, value, agenda_table, sub_table)
    else:
        print("Usage: ./lookup_agenda.py column value, where if value is more than 1 word/string use quotes around it. => ./lookup_agenda.py location 'Coral Lounge'")
