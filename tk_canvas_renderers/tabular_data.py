import tkinter as tk

class TabularData:
    '''
    Takes data as a list of dicts
    [
        {
            label: required,
            value: optional,
            column: optional,
        },
        ...
    ]
    '''

    LABEL = 'label'
    VALUE = 'value'
    COLUMN = 'column'

    def __init__(
            self,
            data: list,
    ):
        self._data = data
        self._column_frames = None
        self._value_fields = {}

    def setup_ui(self, master):
        self._column_frames = [
            tk.Frame(master=master)
            for _ in list(range(self._get_num_columns()))
        ]

        for column, column_frame in enumerate(self._column_frames):
            column_frame.grid(
                column=column,
                row=0,
                sticky=tk.NW,
            )

        for column in range(self._get_num_columns()):
            for row, label in enumerate(self._get_labels_in_column(column)):
                tk.Label(
                    self._column_frames[column],
                    text=label,
                ).grid(
                    column=0,
                    row=row,
                    sticky=tk.W,
                )
                self._value_fields[label] = tk.Label(
                    self._column_frames[column],
                )
                self._value_fields[label].grid(
                    column=1,
                    row=row,
                    sticky=tk.W,
                )
        self.update_values(data=self._data)

    def _get_column_from_entry(self, entry: dict) -> int:
        if self.__class__.COLUMN in entry:
            return entry[self.__class__.COLUMN]
        return 0

    def _get_value_with_label(self, label: str, data: list) -> str:
        for entry in data:
            if entry[self.__class__.LABEL] == label and self.__class__.VALUE in entry:
                return entry[self.__class__.VALUE]
        return None

    def _get_num_columns(self):
        return max([self._get_column_from_entry(entry) for entry in self._data]) + 1

    def _get_labels_in_column(self, column):
        r = []
        for entry in self._data:
            if self._get_column_from_entry(entry) == column:
                r.append(entry[self.__class__.LABEL])
        return r

    def update_values(self, data):
        for entry in data:
            label = entry[self.__class__.LABEL]
            value = self._get_value_with_label(
                label=label,
                data=data,
            )
            if value is not None:
                self._value_fields[label].config(text=value)

    def run(self):
        master = tk.Tk()
        self.setup_ui(master)
        master.mainloop()
