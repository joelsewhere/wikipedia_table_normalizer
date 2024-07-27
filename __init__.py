def set_rowspan(column, row_index, column_index, dataset):
    # Does the column have a rowspan attribute?
    if rowspan := int(column.attrs.get('rowspan', 0)):

        # Loop over rows between current_row and current_row + rowspan
        for rspan_idx in range(row_index, row_index + rowspan):
            
            # Keeping column-index consistent, set the value for each row
            dataset[rspan_idx][column_index] = column

        # Indicate a rowspan was found
        return True

    # No rowspan was found
    return False

def set_colspan(column, row_index, column_index, dataset):
    # Does the column have a colspan attribute?
    if colspan := column.attrs.get('colspan'):

        # Loop over columns between current_col and current_col + colspan
        for cspan_idx in range(column_index, column_index + int(colspan)):
            
            # Check if value also has a rowspan. If yes, set the value
            # for the column and row
            if not set_rowspan(column, row_index, cspan_idx, dataset):
                
                # If no rowspan, keep row index consistent
                # and set the value for each column
                dataset[row_index][cspan_idx] = column

        # colspan attribute was found
        return True

    # No colspan attribute was found
    return False

def normalize_wiki_table(table, include_tr=False):

    # Collect table row objects
    rows = table.find_all('tr')
    
    # The headers (th) are stored
    # in the first table-row
    headers = rows[0]

    # The data-rows are all other
    # rows of the table
    table_rows = rows[1:]

    # Using the table headers
    # calculate the number of columns
    max_cols = 0
    for header in headers.find_all('th'):
            max_cols += int(header.attrs.get('colspan', 1))
    
    # In some cases, data is stored inside the table-row
    # html object. A common example is when a row is highlighted
    # to indicate the winner amongst a list of award nominees
    # In those cases,  `include_tr` can be set to True
    # which will add a new column to the table containing
    # the table-row object
    if include_tr:
        max_cols += 1

    # # Identify the maximum column length
    # if not max_cols:
    #     max_cols = max([len(row.find_all('td')) for row in table_rows])

    # Create empty dataset with the maximum length for each row
    # and the same number of rows as the existing table
    normalized_table = [[None for x in range(max_cols)] for row in table_rows]

    # Loop over each row
    for r_idx, row in enumerate(table_rows):

        # Isolate the row's raw column data
        columns = row.find_all('td')

        # Calculate the number of columns
        # in the isolated column
        column_num = len(columns)

        # Loop over the normalized column indices
        for c_idx in range(max_cols):

            # If the value at the normalized column index 
            # has already been set by a previous rowspan or column span
            # we do not need to set the value at the normalized column index
            if normalized_table[r_idx][c_idx] == None:
    
                # Isolate the individual column's data
                try:
                    column = columns[c_idx]

                except:
                    
                    break

                # Set values across rowspan and colspans
                rowspan = set_rowspan(column, r_idx, c_idx, normalized_table)
                colspan = set_colspan(column, r_idx, c_idx, normalized_table)

                # If no row or colspan, set the value
                if not any([rowspan, colspan]):
                    normalized_table[r_idx][c_idx] = column

            # If the current column index has surpassed the number of
            # columns in the raw data, the row should be fully imputed
            elif c_idx < column_num:
                
                # Isolate the raw column value
                column = columns[c_idx]

                # If the row value was already set
                # at the normalized column index, there is still data at 
                # the raw column index, but it has to be set
                # at the next unimputed value of the normalized row.
                for next_idx in range(c_idx, max_cols):
                    if normalized_table[r_idx][next_idx] == None:
                        normalized_table[r_idx][next_idx] = column
                        break
                
                # If the current column value is a col or rowspan,
                # iterate over columns/rows and set
                try:
                    set_colspan(column, r_idx, next_idx, normalized_table)
                    set_rowspan(column, r_idx, next_idx, normalized_table)
                except:
                    break

        if include_tr:
            normalized_table[r_idx][-1] = row

    return normalized_table