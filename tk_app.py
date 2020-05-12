# files
import sql

# stdlib
import tkinter as tk
from tkinter import ttk
from functools import partial
import os

# 3rd party
from tkcalendar import DateEntry
from pandas import read_sql, DataFrame


def show_campaigns():
    '''
    runs the promos_sql query and saves pandas dataframe to a global variable,
    displays in treeview
    '''
    global df
    conn = sql.db_conn()
    rid = retailer_id.get()
    start = datepicker_start.get_date()
    end = datepicker_end.get_date()
    q = read_sql(
        sql.promos_sql,
        conn,
        params=(rid, start, end, start, end, start, end)
    )
    df = DataFrame(q)
    # df['End Date'].fillna(value='Ongoing', inplace=True)
    show_results()


def show_results():
    '''
    prints dataframe results to the treeview table
    '''
    i = 1
    tree.delete(*tree.get_children())
    for cid, product, loc, subloc, promo_start, promo_end in df.values:
        tree.insert(
            '',
            'end',
            text=i,
            values=(
                f'{product}',
                f'{loc}',
                f'{subloc}',
                f'{promo_start}',
                f'{promo_end}'
            )
        )
        i += 1


def sort_df(column, column2=''):
    '''
    sorts the specified column in alphabetical/numerical (or reserve) order
    '''
    global df
    if column2 == '':
        if sort[column] == 'up':
            df.sort_values(column, inplace=True, ascending=False)
            for column in sort:
                sort[column] = 'down'
        else:
            df.sort_values(column, inplace=True)
            sort[column] = 'up'
            for other_column in sort:
                if other_column != column:
                    sort[other_column] = 'down'

    # also sorts sub-location when sorting by location
    else:
        if sort[column] == 'up':
            df.sort_values([column, column2], inplace=True, ascending=False)
            for column in sort:
                sort[column] = 'down'
        else:
            df.sort_values([column, column2], inplace=True)
            sort[column] = 'up'
            for other_column in sort:
                if other_column != column:
                    sort[other_column] = 'down'
    show_results()


def save_to_csv():
    '''
    saves results to CSV file in user's Downloads folder
    '''
    global df
    rid = retailer_id.get()
    start = datepicker_start.get_date()
    end = datepicker_end.get_date()
    start = start.strftime('%d-%m-%y')
    end = end.strftime('%d-%m-%y')
    if rid == 13:
        filename = f'PlayStation 4 Sponsored Placements {start} to {end}'
    else:
        filename = f'Xbox One Sponsored Placements {start} to {end}'
    downloads_path = f'~/Downloads/{filename}.csv'
    filepath = os.path.expanduser(downloads_path)
    try:
        df.to_csv(
            filepath,
            encoding='utf-8',
            index=False
        )
        print_text('Results saved to Downloads folder')
    except:
        print_text('No data to save', color='red')


def print_text(text, color='black'):
    '''
    prints confirmation or error text upon exporting to CSV
    '''
    global msg
    clear_text()
    msg['text'] = text
    msg.config(fg=color)
    root.after(2000, clear_text)


def clear_text():
    '''
    clears the export message
    '''
    global msg
    msg['text'] = ''


# global vars to be modified by sort_df for sorting results columns
df = ''
sort = {
    'Product': 'up',
    'Location': 'down',
    'Start Date': 'down',
    'End Date': 'down'
}

# main app window
root = tk.Tk()
root.geometry('700x400')
root.title('Sponsored Placements Tracker')
frame = tk.Frame(root)
frame2 = tk.Frame(root)
frame3 = tk.Frame(root)
frame.pack(pady=(25, 10))
frame2.pack()
frame3.pack(pady=10)

# retailer selecter
retailer_id = tk.IntVar()
retailer_id.set(13)
ps4 = tk.Radiobutton(
    frame,
    text='PlayStation 4',
    variable=retailer_id,
    value=13
)
xb1 = tk.Radiobutton(
    frame,
    text='Xbox One',
    variable=retailer_id,
    value=16
)

# labels
retailers_label = tk.Label(frame, text='Retailers')
start_label = tk.Label(frame, text='Start Date')
end_label = tk.Label(frame, text='End Date')

# start/end date calendars
datepicker_start = DateEntry(frame)
datepicker_start.config(
    firstweekday='sunday',
    showweeknumbers='false',
    weekendbackground='white',
    weekendforeground='black',
    date_pattern='mm/dd/yy'
)
datepicker_end = DateEntry(frame)
datepicker_end.config(
    firstweekday='sunday',
    showweeknumbers='false',
    weekendbackground='white',
    weekendforeground='black',
    date_pattern='mm/dd/yy'
)

# THE BUTTON
run = tk.Button(frame)
run.config(
    text='Show Campaigns',
    command=show_campaigns
)

retailers_label.grid(row=0, column=1, columnspan=2)
ps4.grid(row=1, column=1, padx=5)
xb1.grid(row=1, column=2, padx=(5, 10))
start_label.grid(row=0, column=3)
datepicker_start.grid(row=1, column=3, padx=5)
end_label.grid(row=0, column=4)
datepicker_end.grid(row=1, column=4, padx=(5, 10))
run.grid(row=0, column=5, rowspan=2, padx=5)

# table to show results
tree = ttk.Treeview(frame2)
tree['columns'] = (
    'Product',
    'Location',
    'Sub-Location',
    'Start Date',
    'End Date'
)
for column in tree['columns']:
    if column == 'Sub-Location':
        tree.heading(
            column,
            text=column
        )
    elif column == 'Location':
        tree.heading(
            column,
            text=column,
            command=partial(sort_df, column, column2='Sub-Location')
        )
    else:
        tree.heading(
            column,
            text=column,
            command=partial(sort_df, column)
        )
tree.pack(
    side='left',
    fill='both',
    expand=1)
tree.column('#0', width=50)
tree.column('Location', width=100)
tree.column('Sub-Location', width=100)
tree.column('Start Date', width=75)
tree.column('End Date', width=75)
vsb = ttk.Scrollbar(frame2, orient="vertical", command=tree.yview)
vsb.pack(side='left', fill='both')
tree.config(yscrollcommand=vsb.set)

# export to CSV button
save = tk.Button(frame3)
save.config(
    text='Export to CSV',
    command=save_to_csv
)
save.pack()

# export confirm/error text
msg = tk.Label(frame3, text='')
msg.pack(pady=5)

root.mainloop()
