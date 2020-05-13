# files
import sql

# stdlib
import tkinter as tk
from functools import partial
import os

# 3rd party
import tkcalendar
from pandas import read_sql, DataFrame
from pyodbc import InterfaceError


class RetailerSelector():
    def __init__(self, master, *args, **kwargs):
        self.master = master
        self.retailer_id = tk.IntVar()
        self.retailer_id.set(13)
        self.retailers_label = tk.Label(
            self.master,
            text='Retailers'
        )
        self.retailer_btn_ps4 = tk.Radiobutton(
            self.master,
            text='PlayStation 4',
            variable=self.retailer_id,
            value=13
        )
        self.retailer_btn_xb1 = tk.Radiobutton(
            self.master,
            text='Xbox One',
            variable=self.retailer_id,
            value=16
        )
        self.retailers_label.grid(
            row=0,
            column=1,
            columnspan=2
        )
        self.retailer_btn_ps4.grid(
            row=1,
            column=1,
            padx=5
        )
        self.retailer_btn_xb1.grid(
            row=1,
            column=2,
            padx=(5, 10)
        )


class DateSelector():
    def __init__(self, master, *args, **kwargs):
        self.master = master
        self.startlabel = tk.Label(self.master, text='Start Date')
        self.endlabel = tk.Label(self.master, text='End Date')
        self.startdate = tkcalendar.DateEntry(self.master)
        self.enddate = tkcalendar.DateEntry(self.master)
        self.startdate.config(
            firstweekday='sunday',
            showweeknumbers='false',
            weekendbackground='white',
            weekendforeground='black',
            date_pattern='mm/dd/yy'
        )
        self.enddate.config(
            firstweekday='sunday',
            showweeknumbers='false',
            weekendbackground='white',
            weekendforeground='black',
            date_pattern='mm/dd/yy'
        )
        self.startlabel.grid(
            row=0,
            column=3
        )
        self.endlabel.grid(
            row=0,
            column=4
        )
        self.startdate.grid(
            row=1,
            column=3,
            padx=5)
        self.enddate.grid(
            row=1,
            column=4,
            padx=(5, 10)
        )


class ResultsButton():
    def __init__(self, master, function, *args, **kwargs):
        self.master = master
        self.function = function
        self.run = tk.Button(self.master)
        self.run.config(
            text='Show Campaigns',
            command=self.function
        )
        self.run.grid(
            row=0,
            column=5,
            rowspan=2,
            padx=5
        )


class ExportButton():
    def __init__(self, master, function, *args, **kwargs):
        self.master = master
        self.function = function
        self.save = tk.Button(self.master)
        self.msg = tk.Label(
            self.master,
            text=''
        )
        self.save.config(
            text='Export to CSV',
            command=self.function
        )
        self.save.pack()
        self.msg.pack(pady=5)

    def print_text(self, text, color='black'):
        '''prints confirmation or error text
        '''
        self.clear_text()
        self.msg['text'] = text
        self.msg.config(fg=color)
        self.master.after(
            2000,
            self.clear_text
        )

    def clear_text(self):
        '''clears the message content
        '''
        self.msg['text'] = ''


class ResultsTable():
    def __init__(self, master, function, *args, **kwargs):
        self.master = master
        self.function = function
        self.sort = {
            'Product': 'up',
            'Location': 'down',
            'Start Date': 'down',
            'End Date': 'down'
        }
        self.tree = tk.ttk.Treeview(self.master)
        self.tree['columns'] = (
            'Product',
            'Location',
            'Sub-Location',
            'Start Date',
            'End Date'
        )
        for column in self.tree['columns']:
            if column == 'Sub-Location':
                self.tree.heading(
                    column,
                    text=column
                )
            elif column == 'Location':
                self.tree.heading(
                    column,
                    text=column,
                    command=partial(self.function, column, column2='Sub-Location')
                )
            else:
                self.tree.heading(
                    column,
                    text=column,
                    command=partial(self.function, column)
                )
        self.tree.pack()


class MainApp():
    def __init__(self, master, *args, **kwargs):
        self.master = master
        self.master.geometry('700x400')
        self.master.title('Sponsored Placements Tracker')

        self.topframe = tk.Frame(self.master)
        self.midframe = tk.Frame(self.master)
        self.botframe = tk.Frame(self.master)

        self.retailer_selector = RetailerSelector(self.topframe)
        self.date_selector = DateSelector(self.topframe)
        self.results_button = ResultsButton(
            self.topframe,
            self.show_results
        )
        self.results_table = ResultsTable(
            self.midframe,
            self.sort_df
        )
        self.export_button = ExportButton(
            self.botframe,
            self.save_to_csv
        )

        self.topframe.pack()
        self.midframe.pack()
        self.botframe.pack()

    def get_df(self):
        try:
            self.conn = sql.db_conn()
            self.rid = self.date_selector.retailer_id.get()
            self.start = self.date_selector.startdate.get_date()
            self.end = self.date_selector.enddate.get_date()
            self.q = read_sql(
                sql.promos_sql,
                self.conn,
                params=(
                    self.rid,
                    self.start,
                    self.end,
                    self.start,
                    self.end,
                    self.start,
                    self.end
                )
            )
            self.df = DataFrame(self.q)
        except InterfaceError:
            pass

    def show_results(self):
        '''prints dataframe results to the self.results treeview table
        '''
        try:
            self.i = 1
            self.get_df()
            self.results_table.tree.delete(*self.results_table.tree.get_children())
            for cid, product, loc, subloc, promo_start, promo_end in self.df.values:
                self.results_table.insert(
                    '',
                    'end',
                    text=self.i,
                    values=(
                        f'{product}',
                        f'{loc}',
                        f'{subloc}',
                        f'{promo_start}',
                        f'{promo_end}'
                    )
                )
                self.i += 1
        except AttributeError:
            self.export_button.print_text(
                'Could not retrieve data from connection',
                color='red'
            )

    def sort_df(self, column, column2=''):
        '''
        sorts a self.results column in reversible alphabetical/numerical order
        '''
        if self.df:
            self.results.column = column
            self.results.column2 = column2
            if self.results.column2 == '':
                if self.results.sort[self.results.column] == 'up':
                    self.df.sort_values(
                        self.results.column,
                        inplace=True,
                        ascending=False
                    )
                    for c in self.results.sort:
                        self.results.sort[c] = 'down'
                else:
                    self.df.sort_values(
                        self.results.column,
                        inplace=True
                    )
                    self.results.sort[self.results.column] = 'up'
                    for c in self.sort:
                        if c != self.results.column:
                            self.results.sort[c] = 'down'

            # also sorts sub-location when sorting by location
            else:
                if self.results.sort[self.results.column] == 'up':
                    self.df.sort_values(
                        [self.results.column, self.results.column2],
                        inplace=True,
                        ascending=False
                    )
                    for c in self.sort:
                        self.results.sort[c] = 'down'
                else:
                    self.df.sort_values(
                        [self.results.column, self.results.column2],
                        inplace=True
                    )
                    self.results.sort[self.results.column] = 'up'
                    for c in self.results.sort:
                        if c != self.results.column:
                            self.results.sort[c] = 'down'
            self.show_results(self.df)

    def save_to_csv(self):
        '''
        saves results to CSV file in user's Downloads folder
        '''
        try:
            self.start = self.data_selector.start.strftime('%d-%m-%y')
            self.end = self.data_selector.end.strftime('%d-%m-%y')
            if self.retailer_selector.rid == 13:
                self.filename = f'PlayStation 4 Sponsored Placements {self.start} to {self.end}'
            else:
                self.filename = f'Xbox One Sponsored Placements {self.start} to {self.end}'
            self.downloads_path = f'~/Downloads/{self.filename}.csv'
            self.filepath = os.path.expanduser(self.downloads_path)
            self.df.to_csv(
                self.filepath,
                encoding='utf-8',
                index=False
            )
            self.export_button.print_text('Results saved to Downloads folder')
        except AttributeError:
            self.export_button.print_text(
                'No data to save',
                color='red'
            )


if __name__ == '__main__':
    root = tk.Tk()
    MainApp(root)
    root.mainloop()
