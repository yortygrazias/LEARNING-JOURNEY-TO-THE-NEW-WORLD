import os
import requests
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

import socketio


# Yorty Grazia here!!

class Tooltip:

    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.tooltip_window = None
        self.tooltip_label = None

    def show_tooltip(self, event):
        if event.widget:
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 20
            y += self.widget.winfo_rooty() + 20
            self.tooltip_window = Toplevel(self.widget)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.geometry(f"+{x}+{y}")
            self.tooltip_label = Label(self.tooltip_window, text=self.text, bg="white")
            self.tooltip_label.pack()

    def hide_tooltip(self, event):
        if event.widget:
            if self.tooltip_window:
                self.tooltip_window.destroy()


class FunctionContent(ttk.Frame):
    @classmethod
    def get_width(cls):
        return ServerUI.WIDTH

    @classmethod
    def get_height(cls):
        return ServerUI.HEIGHT

    def __init__(self, master, padding_int=7) -> None:
        super().__init__(master, padding=padding_int)
        self._create_function_widget()

    def _create_function_widget(self):
        self.function_frame = ttk.Frame(self)
        self.function_frame.grid(row=0, column=0)
        self.book_keeping_label = ttk.Labelframe(self.function_frame,
                                                 text="BOOK KEEPING",
                                                 labelanchor=N,
                                                 width=FunctionContent.get_width() / 3,
                                                 height=FunctionContent.get_height() / 3,
                                                 padding=5)
        self.book_keeping_label.grid_propagate(False)
        self.book_keeping_label.grid_columnconfigure(0, weight=1)
        self.book_keeping_label.grid(row=0, column=0, sticky=W)
        for i in range(0, 4):
            self.book_keeping_label.grid_rowconfigure(i, weight=1)

        self.add_book_button = ttk.Button(
            self.book_keeping_label,
            text="ADD BOOK",
            command=lambda: self.invoke_function(add=True))
        self.add_book_button.grid(row=0, column=0, sticky=W + E)
        self.delete_book_button = ttk.Button(
            self.book_keeping_label,
            text="DELETE BOOK",
            command=lambda: self.invoke_function(delete=True))
        self.delete_book_button.grid(row=1, column=0, pady=5, sticky=W + E)
        self.update_book_button = ttk.Button(
            self.book_keeping_label,
            text="UPDATE BOOK",
            command=lambda: self.invoke_function(update=True))
        self.update_book_button.grid(row=2, column=0, sticky=W + E)
        self.announce_button = ttk.Button(
            self.book_keeping_label,
            text="ANNOUNCE",
            command=lambda: self.invoke_function(announce=True))
        self.announce_button.grid(row=3, column=0, pady=5, sticky=W + E)

        self.manager_labelframe = ttk.Labelframe(self.function_frame,
                                                 text="",
                                                 width=FunctionContent.get_width() - 185)
        self.manager_labelframe.grid_propagate(False)
        self.manager_labelframe.grid(row=0, column=1, sticky=N + S, padx=5)

        self.add_button_widget = FunctionContent.AddButtonWidget(
            self.manager_labelframe)
        self.delete_button_widget = FunctionContent.DeleteButtonWidget(
            self.manager_labelframe)
        self.update_button_widget = FunctionContent.UpdateButtonWidget(
            self.manager_labelframe)
        self.announce_button_widget = FunctionContent.AnnouncementButtonWidget(
            self.manager_labelframe)
        self.button_list = [
            self.add_button_widget, self.delete_button_widget,
            self.update_button_widget, self.announce_button_widget
        ]

        self.manage_request_label = Label(self,
                                          text="MANAGE REQUESTS",
                                          font=("Times New Roman", 12, "bold"))
        self.manage_request_label.grid(row=1, column=0, pady=5, sticky=W)
        self.request_field_frame = ttk.Frame(self)
        self.request_field_frame.grid(row=2, column=0)
        self.request_canvas = Canvas(self.request_field_frame,
                                     width=FunctionContent.get_width() - 35,
                                     height=FunctionContent.get_height() - 250)
        self.request_canvas.grid(row=0, column=0, sticky=W + E)
        self.request_scroll = Scrollbar(self.request_field_frame,
                                        orient=VERTICAL,
                                        command=self.request_canvas.yview)
        self.request_scroll.grid(row=0, column=1, sticky=N + S)
        self.request_canvas.configure(yscrollcommand=self.request_scroll.set)
        self.field_frame = ttk.Frame(self.request_canvas)
        self.request_canvas.create_window((0, 0),
                                          window=self.field_frame,
                                          anchor="nw")
        self.request_canvas.bind_all("<MouseWheel>", self.on_scroll)

        for i in range(20):
            self.request_widget = FunctionContent.RequestsWidget(
                self.field_frame, "Deletion Request")
            self.request_widget.grid(row=i, sticky=W)
            self.field_frame.update_idletasks()
        self.request_canvas.configure(scrollregion=self.request_canvas.bbox(ALL))

    def on_scroll(self, event):
        direction = 1 if event.delta < 0 else -1
        self.request_canvas.yview_scroll(direction, "units")

    def invoke_function(self,
                        add=False,
                        delete=False,
                        update=False,
                        announce=False):
        for button in self.button_list:
            button.grid_forget()
            self.manager_labelframe["text"] = ""
        if add:
            self.add_button_widget.grid(row=0, column=0, sticky=W + E)
            self.manager_labelframe["text"] = self.add_book_button["text"]
        elif delete:
            self.delete_button_widget.grid(row=0, column=0, sticky=W + E)
            self.manager_labelframe["text"] = self.delete_book_button["text"]
        elif update:
            self.update_button_widget.grid(row=0, column=0, sticky=W + E)
            self.manager_labelframe["text"] = self.update_book_button["text"]
        elif announce:
            self.announce_button_widget.grid(row=0, column=0, sticky=W + E)
            self.manager_labelframe["text"] = self.announce_button["text"]

    class AddButtonWidget(ttk.Frame):
        SUBJECTS = ["Math", "Science", "Literature", "History", "Engineering"]

        def __init__(self, master, padding_int=7):
            super().__init__(master, padding=padding_int)
            self._create_add_button_widget()

        def _create_add_button_widget(self):
            self.input_add_frame = ttk.Frame(self)
            self.input_add_frame.grid(row=0, column=0)
            self.book_title = Label(self.input_add_frame, text="Title:")
            self.book_title.grid(row=0, column=0, sticky=E, padx=3)
            self.book_title_entry = ttk.Entry(self.input_add_frame, width=15)
            self.book_title_entry.grid(row=0,
                                       column=1,
                                       padx=3,
                                       sticky=W + E,
                                       columnspan=2)
            self.book_author = Label(self.input_add_frame, text="Author:")
            self.book_author.grid(row=1, column=0, pady=5, sticky=E)
            self.book_author_entry = ttk.Entry(self.input_add_frame, width=15)
            self.book_author_entry.grid(row=1,
                                        column=1,
                                        padx=3,
                                        sticky=W + E,
                                        columnspan=2)
            self.cover = Label(self.input_add_frame, text="Cover Page")
            self.cover.grid(row=2, column=0)
            self.cover_button = ttk.Button(self.input_add_frame, text="Cover Page:")
            self.cover_button.grid(row=2, column=1, sticky=W+E, columnspan=2, padx=3)
            self.subject = Label(self.input_add_frame, text="Subject:")
            self.subject.grid(row=3, column=0, padx=3, sticky=E, pady=5)
            self.subject_entry = ttk.Combobox(
                self.input_add_frame,
                width=15,
                values=FunctionContent.AddButtonWidget.SUBJECTS, state="readonly")
            self.subject_entry.set("Select Subject")
            self.subject_entry.grid(row=3,
                                    column=1,
                                    padx=3,
                                    sticky=W + E,
                                    columnspan=2)
            self.book_file = Label(self.input_add_frame, text="File:")
            self.book_file.grid(row=4, column=0, padx=3, sticky=E)
            self.book_file_entry_button = ttk.Button(self.input_add_frame,
                                                     text="Select File")
            self.book_file_entry_button.grid(row=4,
                                             column=1,
                                             padx=3,
                                             sticky=W)
            self.save_add = ttk.Button(self.input_add_frame, text="Save")
            self.save_add.grid(row=4, column=2)
            self.result_frame = ttk.Frame(self)
            self.result_frame.grid(row=1, column=0, padx=3)
            self.result = Label(self.result_frame)
            self.cover_button.config(command=self.add_cover_page)
            self.book_file_entry_button.config(command=lambda: FunctionContent.AddButtonWidget.open_file_directory(
                self.result, self.save_add, self.book_title_entry, self.book_author_entry, self.subject_entry))

        def add_cover_page(self):
            ...
            cover_page_path = filedialog.askopenfilename(filetypes=[("JPEG", "*.jpg; *.jpeg")])
            try:
                with open(cover_page_path, "rb") as f:
                    cover_page_file = f.read()
                    return self.book_file_entry_button.config(
                        command=lambda: FunctionContent.AddButtonWidget.open_file_directory(self.result,
                                                                                            self.save_add,
                                                                                            self.book_title_entry,
                                                                                            self.book_author_entry,
                                                                                            self.subject_entry,
                                                                                            cover=cover_page_file))
            except FileNotFoundError:
                return

        @staticmethod
        def select_file(widget):
            file_path = filedialog.askopenfilename()
            if not file_path:
                return None, None, None
            file_name = os.path.basename(file_path)
            try:
                with open(file_path, "rb") as f:
                    file_bin = f.read()
            except FileNotFoundError:
                return None, None, None

            if widget.winfo_ismapped():
                widget.grid_forget()
            widget.grid(row=0, column=0)
            widget.config(text=f"{file_name} was selected.")
            return file_bin

        @staticmethod
        def open_file_directory(*widgets, cover=""):
            ...
            result_widget, save_widget, title_widget, author_widget, subject_widget = widgets
            if not title_widget.get() or not author_widget.get():
                return result_widget.config(text="Do not leave entry(ies) as blank")
            file_bin = FunctionContent.AddButtonWidget.select_file(result_widget)
            book_data = {
                "cover": cover,
                "title": title_widget.get(),
                "author": author_widget.get(),
                "subject": subject_widget.get(),
                "file_bin": file_bin
            }
            save_widget.config(command=lambda: FunctionContent.AddButtonWidget.add_book(**book_data,
                                                                                        result=result_widget))

        @staticmethod
        def add_book(cover, title, author, subject, file_bin, result):
            ...
            book_data = {
                "title": title.upper(),
                "author": author.upper(),
                "subject": subject.capitalize(),
            }
            book_file = {
                'file': file_bin,
                'cover': cover
            }
            ServerUI.SIO_CONNECTION.emit("announce_add", book_data)
            try:
                send_request = requests.post("http://127.0.0.1:5000/server/library/function/add", data=book_data,
                                             files=book_file)
                if send_request.status_code == 200:
                    ...
                    result.config(text=send_request.text)
                else:
                    result.config(text=send_request.text)
            except ConnectionError:
                print(str(ConnectionError))
            except requests.exceptions.ConnectionError:
                print(str(requests.exceptions.ConnectionError))
            except requests.exceptions.HTTPError:
                print(str(requests.exceptions.HTTPError))
            except requests.exceptions.RequestException:
                print(str(requests))

    class DeleteButtonWidget(ttk.Frame):

        def __init__(self, master, padding_int=7):
            super().__init__(master, padding=padding_int)
            self._create_delete_button_widget()

        def _create_delete_button_widget(self):
            self.input_del_frame = ttk.Frame(self)
            self.input_del_frame.grid(row=0, column=0, sticky=W)
            self.book_title_del = Label(self.input_del_frame, text="Title:")
            self.book_title_del.grid(row=0, column=0, sticky=E)
            self.book_title_entry_del = ttk.Entry(self.input_del_frame, width=15)
            self.book_title_entry_del.grid(row=0,
                                           column=1,
                                           padx=3,
                                           sticky=W + E,
                                           columnspan=2)
            self.book_author_del = Label(self.input_del_frame, text="Author:")
            self.book_author_del.grid(row=1, column=0, sticky=E, pady=3)
            self.book_author_entry_del = ttk.Entry(self.input_del_frame, width=15)
            self.book_author_entry_del.grid(row=1,
                                            column=1,
                                            padx=3,
                                            sticky=W + E,
                                            columnspan=2)

            self.cancel_button = ttk.Button(self.input_del_frame, text="Cancel")
            self.cancel_button.grid(row=2, column=1, padx=3)
            self.delete_button = ttk.Button(self.input_del_frame,
                                            text="Delete",
                                            command=self.delete_book)
            self.delete_button.grid(row=2, column=2)
            self.result_del_frame = ttk.Frame(self)
            self.result_del_frame.grid(row=2, column=0)
            self.result_del = Label(
                self.result_del_frame,
                text="Title do not match with the author. Deletion was canceled.",
                wraplength=200,
                justify="left")

        def delete_book(self):
            if self.result_del.winfo_ismapped():
                self.result_del.grid_forget()
            else:
                self.result_del.grid(row=0, column=0, pady=3)

    class UpdateButtonWidget(ttk.Frame):

        def __init__(self, master, padding_int=7):
            super().__init__(master, padding=padding_int)
            self._create_update_button_widget()

        def _create_update_button_widget(self):
            self.book_title_up = Label(self, text="Title:")
            self.book_title_up.grid(row=0, column=0, sticky=E)
            self.book_title_entry_up = ttk.Entry(self, width=15)
            self.book_title_entry_up.grid(row=0,
                                          column=1,
                                          padx=3,
                                          sticky=W + E,
                                          columnspan=2)

            self.book_author_up = Label(self, text="Author:")
            self.book_author_up.grid(row=1, column=0, pady=3)
            self.book_author_up_entry = ttk.Entry(
                self,
                width=15,
            )
            self.book_author_up_entry.grid(row=1,
                                           column=1,
                                           padx=3,
                                           sticky=W + E,
                                           columnspan=2)
            self.book_author_up_entry.insert(0, "Optional")
            self.cancel_up = ttk.Button(self, text="Cancel")
            self.cancel_up.grid(row=2, column=1)
            self.next = ttk.Button(self, text="Next")
            self.next.grid(row=2, column=2)
            self.set_tip = Tooltip(self.next, "This will open a treeview.")

    class AnnouncementButtonWidget(ttk.Frame):
        PREMADE = [
            "Announce an addition", "Announce a deletion", "Announce an update"
        ]

        def __init__(self, master, padding_int=7):
            super().__init__(master, padding=padding_int)
            self._create_announce_button_widget()

        def _create_announce_button_widget(self):
            self.auto_var = StringVar()
            self.auto_radio = ttk.Radiobutton(
                self,
                variable=self.auto_var,
                text="Auto",
                command=lambda: self.auto_announce(self.premade.get()))
            self.auto_radio.grid(row=0, column=0)
            self.premade = ttk.Combobox(
                self,
                values=FunctionContent.AnnouncementButtonWidget.PREMADE,
                width=15,
                state=DISABLED)
            self.premade.set("Announcement")
            self.premade.grid(row=0, column=1, padx=5)
            self.confirm_ann = ttk.Button(self, text="Confirm", state=DISABLED)
            self.confirm_ann.grid(row=0, column=2)
            self.announce_text = Text(self, width=30, height=5)
            self.announce_text.grid(row=1,
                                    column=0,
                                    columnspan=3,
                                    pady=5,
                                    sticky=W + E)

        def auto_announce(self, announce_type: str):
            self.premade["state"] = NORMAL
            self.confirm_ann["state"] = NORMAL

    class RequestsWidget(ttk.Frame):
        REQUEST_TYPES = ["Addition Request", "Deletion Request", "Update Request"]
        ADD_STR = f"""Requester: {'None'}\nRequest Type: {'None'}\nTitle: {'None'}\nAuthor: {'None'}\nRemarks: {'None'}
"""

        @classmethod
        def get_width(cls):
            return ServerUI.WIDTH

        @classmethod
        def get_height(cls):
            return ServerUI.HEIGHT

        def __init__(self, master, request_type: str, padding_int=7):
            super().__init__(master, padding=padding_int)
            self.master = master
            self.request_type = request_type
            self._create_requests_widget()

        def _create_requests_widget(self):
            if (self.request_type == FunctionContent.RequestsWidget.REQUEST_TYPES[0] or
                    self.request_type == FunctionContent.RequestsWidget.REQUEST_TYPES[1] or
                    self.request_type == FunctionContent.RequestsWidget.REQUEST_TYPES[2]):

                self.request_label = ttk.Labelframe(
                    self,
                    text=self.request_type,
                    width=FunctionContent.RequestsWidget.get_width() - 50,
                    height=FunctionContent.RequestsWidget.get_height() - 450,
                    padding=5)
                self.request_content_label = Label(
                    self.request_label,
                    text=FunctionContent.RequestsWidget.ADD_STR,
                    wraplength=435,
                    justify="left")
                self.request_content_label.grid(row=0, column=0)
                self.request_label.grid_propagate(False)
                self.request_label.grid(row=0, column=0)


class LogContent(ttk.Frame):
    BASIC_HEADINGS = ["Username", "UNIQUE ID", "Station", "Time-in", "Time-out"]

    @classmethod
    def get_width(cls):
        return ServerUI.WIDTH

    @classmethod
    def get_height(cls):
        return ServerUI.HEIGHT

    def __init__(self, master, padding_int=5) -> None:
        super().__init__(master, padding=padding_int)
        self._create_log_widgets()

    def _create_log_widgets(self) -> None:
        self.details_button = ttk.Button(self, text=" More Details", command=self.show_details)
        self.details_tip = Tooltip(self.details_button, "Shows more details of the log in expanded table.")
        self.details_button.grid(row=0, column=0, sticky=E)

        self.log_tree = ttk.Treeview(self,
                                     columns=LogContent.BASIC_HEADINGS,
                                     show="headings",
                                     height=15)
        self.log_tree.grid(row=1, column=0, pady=5, sticky=W + E, columnspan=2)
        self.log_scroll = Scrollbar(self, orient="horizontal", command=self.log_tree.xview)
        self.log_tree.config(xscrollcommand=self.log_scroll.set)
        self.log_scroll.grid(row=2, column=0, sticky=W + E)
        for index in range(len(LogContent.BASIC_HEADINGS)):
            self.log_tree.heading(LogContent.BASIC_HEADINGS[index],
                                  text=LogContent.BASIC_HEADINGS[index])
            self.log_tree.column(LogContent.BASIC_HEADINGS[index],
                                 width=90,
                                 minwidth=200)
        self.log_canvas = Canvas(self, width=LogContent.get_width() - 30, height=LogContent.get_height() - 395)
        self.log_canvas.grid(row=3, column=0)
        self.log_frame = ttk.Frame(self.log_canvas)
        self.log_v_scroll = Scrollbar(self, command=self.log_canvas.yview, orient=VERTICAL)
        self.log_v_scroll.grid(row=3, column=1, sticky=N + S)
        self.log_canvas.config(yscrollcommand=self.log_v_scroll.set)
        self.log_canvas.create_window((0, 0), anchor="nw", window=self.log_frame)
        self.history_label = ttk.Labelframe(self.log_frame,
                                            text="HISTORY",
                                            width=LogContent.get_width() - 35,
                                            height=LogContent.get_height() / 8,
                                            padding=5)
        self.history_label.grid_propagate(False)
        self.history_label.grid(row=3, column=0, sticky=W)

        self.history_content = Label(self.history_label, text="THIS IS A TEST IF THE HISTORY LABEL FRAME WORKS. THIS "
                                                              "WAS PURPOSELY A LONG TEXT TO SEE IF THE TEXT FILLED THE"
                                                              "LABEL FRAME AND IS VISIBLE",
                                     wraplength=LogContent.get_width() - 45)

        """
        for i in range(100):
            self.log_canvas.update_idletasks()
        self.log_canvas.config(scrollregion=self.log_canvas.bbox("all"))
        """
        self.history_content.grid(row=0, column=0)

    def show_details(self):
        ...


# FINISHED
class MainContent(ttk.Frame):

    def __init__(self, master, padding_int=5) -> None:
        super().__init__(master, padding=padding_int)
        self.master = master
        self._create_main_widgets()

    def _create_main_widgets(self):
        self.notif_canvas = Canvas(self, width=ServerUI.WIDTH - 30, height=ServerUI.HEIGHT - 20)
        self.notif_canvas.grid(row=0, column=0)
        self.canvas_frame = ttk.Frame(self.notif_canvas)
        self.notif_canvas.create_window((0, 0), anchor="nw", window=self.canvas_frame)
        self.notif_bar = Scrollbar(self, orient=VERTICAL, command=self.notif_canvas.yview)
        self.notif_canvas.config(yscrollcommand=self.notif_bar.set)
        self.notif_bar.grid(row=0, column=1, sticky=N + S)
        self.test_frame = Frame(self.canvas_frame)
        self.test_frame.grid(row=0)
        self.notif_label = ttk.Labelframe(self.test_frame,
                                          text=f"Notifications",
                                          width=ServerUI.WIDTH - 35,
                                          height=75,
                                          padding=5)
        self.notif_label.grid_propagate(False)
        self.notif_label.grid(row=0, column=0)

        self.button_frame = ttk.Frame(self.test_frame)
        self.button_frame.grid(row=1, column=0, sticky=E)
        self.yap_button = ttk.Button(self.button_frame, text="Read more Dev's yap")
        self.yap_button.grid(row=0, column=0, pady=2)
        self.manage_button = ttk.Button(self.button_frame, text="Manage")
        self.manage_button.grid(row=0, column=1)

        self.notif_divider = ttk.Separator(self.test_frame, orient="horizontal")
        self.notif_divider.grid(row=2, column=0, sticky=W + E, pady=5)

        """
        for i in range(100):
            self.canvas_frame.update_idletasks()
        self.notif_canvas.config(scrollregion=self.notif_canvas.bbox("all"))
        """


class ServerUI(Tk):
    WIDTH = 500
    HEIGHT = 600
    TITLE = "LIBRARY SERVER"

    SIO_CONNECTION = None

    def __init__(self) -> None:
        super().__init__()
        self.title(ServerUI.TITLE)
        self.server_notebook = ttk.Notebook(self,
                                            width=ServerUI.WIDTH,
                                            height=ServerUI.HEIGHT)
        self.server_notebook.grid(row=0, column=0)
        self.resizable(False, False)
        self.socket_io = socketio.Client()
        self.socket_io.connect("http://127.0.0.1:5000")
        ServerUI.SIO_CONNECTION = self.socket_io

        self._create_server_widgets()

    def _create_server_widgets(self):
        self.main_content = MainContent(self.server_notebook)
        self.main_content.manage_button["command"] = self.change_tab
        self.main_content.grid(row=0, column=0)
        self.server_notebook.add(self.main_content, text="MAIN")

        self.log_content = LogContent(self.server_notebook)
        self.log_content.grid(row=0, column=0)
        self.server_notebook.add(self.log_content, text="LOG")

        self.function_content = FunctionContent(self.server_notebook)
        self.function_content.grid(row=0, column=0)
        self.server_notebook.add(self.function_content, text="FUNCTION")

    def change_tab(self):
        return self.server_notebook.select(self.function_content)


if __name__ == "__main__":
    s = ServerUI()
    s.mainloop()
