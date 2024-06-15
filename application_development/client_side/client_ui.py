import time
import os
import requests
import subprocess
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk


class Home(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self._create_home_widget()

    def _create_home_widget(self):
        self.profile_frame = ttk.Frame(self)
        self.profile_frame.grid(row=0, column=0, sticky=W)
        self.profile_pic = Label(self.profile_frame, bg="Sky Blue", width=10)
        self.profile_pic.grid_propagate(False)
        self.profile_pic.grid(row=0, column=0, rowspan=4, sticky=N + S + W + E)

        self.current_user = Label(self.profile_frame)
        self.current_user.grid(row=0, column=1, padx=3, sticky=W)
        self.status = Label(self.profile_frame)
        self.status.grid(row=1, column=1, padx=3, sticky=W)
        self.time_in = Label(self.profile_frame)
        self.time_in.grid(row=2, column=1, padx=3, sticky=W)
        self.id = Label(self.profile_frame)
        self.id.grid(row=3, column=1, padx=3, sticky=W)
        self.edit = ttk.Button(self.profile_frame, text="Edit Profile",
                               command=lambda: self.upload_profile(self.current_user, self.profile_pic))
        self.edit.grid(row=4, column=0, sticky=W + E, pady=5)

        self.info_frame = ttk.Frame(self)
        self.info_frame.grid(row=2, column=0, columnspan=2, pady=10)
        self.announcement = ttk.LabelFrame(self.info_frame, text="ANNOUNCEMENT", width=Client.AREA["width"] / 2,
                                           height=280)
        self.announcement.grid_propagate(False)
        self.announcement.grid(row=0, column=0, rowspan=2, padx=5)

        self.notification = ttk.LabelFrame(self.info_frame, text="NOTIFICATION", width=Client.AREA["width"] / 2 - 25,
                                           height=135)
        self.notification.grid_propagate(False)
        self.notification.grid(row=0, column=1, sticky=N)

        self.quote = ttk.LabelFrame(self.info_frame, text="QUOTES OF THE DAY", width=Client.AREA["width"] / 2 - 25,
                                    height=135)
        self.quote.grid_propagate(False)
        self.quote.grid(row=1, column=1, sticky=S)

        self.time_frame = ttk.Frame(self)
        self.time_frame.grid(row=0, column=1, sticky=E)
        self.date = Label(self.time_frame, text="Date: " + time.strftime("%d %B %Y "),
                          font=("Times New Roman", 12, "bold"))
        self.date.grid(row=0, column=0)
        self.day = Label(self.time_frame, text=time.strftime("%A"), font=("Times New Roman", 12, "bold"))
        self.day.grid(row=1, column=0)
        self.current_time = Label(self.time_frame, font=("Times New Roman", 12, "bold"))
        self.current_time.grid(row=2, column=0)
        Home.tick_time(self.current_time)

        self.announce_canvas = Canvas(self.announcement, width=415, height=250)
        self.announce_canvas.grid(row=0, column=0)
        self.announce_scroll = Scrollbar(self.announcement, orient=VERTICAL,
                                         command=self.announce_canvas.yview)
        self.announce_scroll.grid(row=0, column=1, sticky=N + S)
        self.announce_canvas.config(yscrollcommand=self.announce_scroll.set)
        self.announce_window = ttk.Frame(self.announce_canvas)
        self.announce_canvas.create_window((0, 0), window=self.announce_window, anchor="nw")

        for i in range(100):
            label = Label(self.announce_window, text=i)
            label.grid(row=i)
            self.announce_window.update()

        self.announce_canvas.config(scrollregion=self.announce_canvas.bbox("all"))

    @staticmethod
    def open_image_directory(label_widget: Label, save_button: ttk.Button, current_user, profile_pic: Label):
        profile_image = filedialog.askopenfilename(filetypes=[("JPEG files", "*.jpg;*.jpeg"), ("PNG files", "*.png")])
        img_name = os.path.basename(profile_image)
        set_profile = Image.open(profile_image)
        set_profile = set_profile.resize((80, 80))
        photo = ImageTk.PhotoImage(set_profile)
        label_widget.config(text=f"{img_name} was selected.")
        save_button.config(command=lambda: Home.save_profile(photo, label_widget, profile_image,
                                                             current_user, profile_pic))
        label_widget.photo = photo

    @staticmethod
    def save_profile(image: ImageTk.PhotoImage, label_widget: Label, file: filedialog, current_user, profile_pic):
        ...
        if not file:
            label_widget.config(text="Select an image file")
        try:
            with open(file, "rb") as f:
                user_data = {
                    'username': current_user.cget("text").replace("Username: ", "")
                }
                file_data = {
                    "file": f
                }

                send_request = requests.post("http://127.0.0.1:5000/client/library/home/edit", files=file_data,
                                             data=user_data)
                if send_request.status_code == 200:
                    label_widget['text'] = send_request.text
                    profile_pic.config(image=image)
                    profile_pic.image = image
                else:
                    label_widget['text'] = send_request.text

        except ConnectionError:
            label_widget['text'] = "Server is offline"
        except requests.exceptions.ConnectionError:
            label_widget['text'] = "Cannot connect to server."
        except requests.exceptions.HTTPError:
            label_widget['text'] = "Invalid Requests."
        except requests.exceptions.RequestException:
            label_widget['text'] = "Invalid Requests."

    def upload_profile(self, current_user: Label, profile_pic: Label):
        tl_profile = Toplevel(self)
        tl_profile.title("Edit Profile")
        tl_profile.lift()
        tl_profile.grab_set()
        upload = ttk.Button(tl_profile, text="Upload an image")
        upload.grid(row=0, column=0)
        save = ttk.Button(tl_profile, text="Save")
        save.grid(row=0, column=1)
        cancel = ttk.Button(tl_profile, text="Cancel", command=lambda: tl_profile.destroy())
        message = Label(tl_profile, text="Select an image file")
        message.grid(row=1, column=0, columnspan=3, pady=10)
        cancel.grid(row=0, column=2)
        upload.config(command=lambda: Home.open_image_directory(message, save, current_user, profile_pic))

    @staticmethod
    def tick_time(widget):
        current_time = time.strftime("%H:%M:%S")
        widget.config(text="Time: " + current_time)
        widget.after(1000, lambda: Home.tick_time(widget))


class Browse(ttk.Frame):
    SEARCH_COLUMNS = ("ID", "Title", "Author", "Subject", "Date Added")
    SEARCH_TAGS = SEARCH_COLUMNS

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self._create_browse_widget()

    def _create_browse_widget(self):
        self.query_frame = ttk.Frame(self)
        self.query_frame.grid(row=0, column=0, sticky=W)
        self.search_label = Label(self.query_frame, text="Search:")
        self.search_label.grid(row=0, column=0)
        self.search = ttk.Entry(self.query_frame, width=30)
        self.search.grid(row=0, column=1, padx=5)
        self.tag = ttk.Combobox(self.query_frame, values=Browse.SEARCH_TAGS, width=15, state="readonly")
        self.tag.set(value=Browse.SEARCH_TAGS[1])
        self.tag.grid(row=0, column=2, padx=5)
        self.search_button = ttk.Button(self.query_frame, text="Confirm")
        self.search_button.grid(row=0, column=3)
        self.search_result = Label(self.query_frame, text="Use a proper tag from dropdown menu when searching.")
        self.search_result.grid(row=0, column=4, padx=25)

        self.file_frame = ttk.Frame(self)
        self.file_frame.grid(row=1, column=0, sticky=W, pady=5)
        self.dir_label = Label(self.file_frame, text="Directory:")
        self.dir_label.grid(row=0, column=0)
        self.dir = ttk.Label(self.file_frame)
        self.dir.grid(row=0, column=1, padx=5)
        self.dir_button = ttk.Button(self.file_frame, text="Set Directory",
                                     command=lambda: self.set_dir(self.master.master.master.username_entry.get()))
        self.dir_button.grid(row=0, column=3)

        self.search_tree = ttk.Treeview(self, show="headings", columns=Browse.SEARCH_COLUMNS, height=15)
        self.search_tree.grid(row=2, column=0)
        self.search_tree.bind("<<TreeviewSelect>>",
                              lambda event: self.record_selected(event, self.master.master.master.username_entry.get()))

        self.search_button.config(command=lambda: Browse.search_book(self.search, self.tag, self.search_result,
                                                                     self.search_tree))

        for index, column in enumerate(Browse.SEARCH_COLUMNS):
            self.search_tree.heading(index, text=column)

        self.search_tree.column(0, width=100, minwidth=200, anchor=CENTER)
        self.search_tree.column(1, width=285, minwidth=350, anchor=CENTER)
        self.search_tree.column(2, width=200, minwidth=300, anchor=CENTER)
        self.search_tree.column(3, width=150, minwidth=250, anchor=CENTER)
        self.search_tree.column(4, width=150, minwidth=250, anchor=CENTER)

        self.tree_scroll = Scrollbar(self, orient=HORIZONTAL, command=self.search_tree.xview)
        self.tree_scroll.grid(row=3, column=0, sticky=W + E)
        self.search_tree.config(xscrollcommand=self.tree_scroll.set)

        """
        Bind the treeview in a way that when the user clicks the result, it will show a toplevel pop-up containing more
        information of the book.
        Toplevel pop-up should appear on the cursor's location and can be drag.
        Information should be:
            1. Title
            2. Author
            3. Subject
            4. ID (from the application database)
            5. ISBN Maybe? 
            6. A cover page or thumbnail if that makes sense and if it is possible.
            7. Librarian notes
            8. A quick preview?? Is that possible?
        While you're at it, add a vertical scrollbar for vertical navigation of the treeview.
        
        """

    def set_dir(self, current_user):
        file_dir = filedialog.askdirectory()
        data = {
            'new_dir': file_dir,
            'current_x': current_user
        }
        if not file_dir:
            return
        try:
            send_request = requests.post("http://127.0.0.1:5000/client/library/browse/setdir", json=data)
            if send_request.status_code == 200:
                response = send_request.json()
                user_dir = response['dir']
                self.dir.config(text=user_dir)

        except ConnectionError:
            print(str(ConnectionError))
        except requests.exceptions.ConnectionError:
            print(str(requests.exceptions.ConnectionError))
        except requests.exceptions.HTTPError:
            print(str(requests.exceptions.HTTPError))
        except requests.exceptions.RequestException:
            print(str(requests))

    def record_selected(self, event, username):
        selected_record = event.widget.item(event.widget.selection(), "values")
        book_title = {
            'title': selected_record
        }
        if not book_title['title']:
            print("Nope")
            return

        try:
            print("Hello")
            send_request = requests.post("http://127.0.0.1:5000/client/library/browse/show", json=book_title)
            if send_request.status_code == 200:
                response = send_request.json()
                print("hello", response)
                return self.record_check(response, username, self.dir)
        except ConnectionError:
            print(str(ConnectionError))
        except requests.exceptions.ConnectionError:
            print(str(requests.exceptions.ConnectionError))
        except requests.exceptions.HTTPError:
            print(str(requests.exceptions.HTTPError))
        except requests.exceptions.RequestException:
            print(str(requests))

    def record_check(self, record, username, f_dir):
        for widget in self.search_tree.winfo_children():  # This would allow to only one Toplevel at a time.
            if isinstance(widget, Toplevel):
                widget.destroy()

        x_pos = self.search_tree.winfo_pointerx()
        y_pos = self.search_tree.winfo_pointery()
        b_id, title, author, subject, date_added, cover = record['record']
        base_directory = "C:\\Users\\admin\\PycharmProjects\\pythonProject\\true\\first\\backend"
        cover_page_path = os.path.join(base_directory, cover)

        pop_up = Toplevel(self.search_tree)
        pop_up.geometry(f"+{x_pos + 20}+{y_pos + 20}")
        pop_up.resizable(False, False)
        photo_image = ImageTk.PhotoImage(file=cover_page_path)
        borrow_button = ttk.Button(pop_up, text="Borrow this",
                                   command=lambda: Browse.borrow_book(title, pop_up, username, f_dir))
        borrow_button.grid(row=0, column=0, sticky=E, pady=5, padx=5)
        """
        Fix the server. This photo_image thing should be in server not in this place. That variable should be included
        in the 'record'.
        """

        record_list = {
            "image": photo_image,
            "ID": b_id,
            "Title": title,
            "Author": author,
            "Subject": subject,
            "Date Added": date_added
        }
        griding = 1
        for ct, r in record_list.items():
            if ct == "image":
                image_label = Label(pop_up, image=r)
                image_label.photo = photo_image
                image_label.grid(row=griding)
            else:
                Label(pop_up, text=f"{ct}: {r}").grid(row=griding, sticky=W)
            griding += 1

        """
        This function should only be executed after sending a request to the server as it needs to show more 
        information to the book. 
        Provide a real book. 
        """

    @staticmethod
    def borrow_book(title, top_level, username, f_dir):
        if not title:
            return
        if not f_dir['text']:
            return messagebox.showwarning("Failed", "Set a desired directory first.")
        try:
            send_request = requests.post(
                f"http://127.0.0.1:5000/client/library/browse/borrow/{title.lower()}/{username}")
            if send_request.status_code == 200:
                file_data = send_request.content
                desired_path = f_dir['text']
                file_path = os.path.join(desired_path, title+".pdf")
                with open(file_path, "wb") as f:
                    f.write(file_data)
                top_level.destroy()
                messagebox.showinfo("Success", "The book was borrowed successfully and was "
                                               "automatically transferred to your station.")
            else:
                messagebox.showwarning("Failed", "The book was already borrowed.")

        except ConnectionError:
            print(str(ConnectionError))
        except requests.exceptions.ConnectionError:
            print(str(requests.exceptions.ConnectionError))
        except requests.exceptions.HTTPError:
            print(str(requests.exceptions.HTTPError))
        except requests.exceptions.RequestException:
            print(str(requests))

    @staticmethod
    def search_book(entry: ttk.Entry, tag: ttk.Combobox, result: Label, tree: ttk.Treeview):
        ...
        search_data = entry.get().upper().strip()
        tag_data = tag.get().capitalize().strip()
        if not search_data:
            print("Search entry is empty")
            return
        search_query = {
            'search': search_data,
            'tag': tag_data
        }
        try:
            send_request = requests.post("http://127.0.0.1:5000/client/library/browse/search", json=search_query)
            if send_request.status_code == 200:
                result.config(text="Result Below")
                result_data = send_request.json()
                """
                Put the data from result_data to the search tree and display all. Add a vertical scrollbar for vertical
                navigation. (Optional)
                """
                """
                This part demonstrate how insertion and deletion works in ttk.Treeview
                
                    for heading in TABLES[table_name]['Columns']:
                        the_table.heading(heading, text=heading.upper())
                        the_table.column(heading, width=100, minwidth=100, anchor="center")
                        the_table['show'] = "headings"
            
                    the_table.delete(*the_table.get_children())
                    for data in TABLES[table_name]['Data']:
                        the_table.insert("", END, values=data)
                """

                tree.delete(*tree.get_children())
                for book in result_data:
                    tree.insert("", END, values=result_data[book])

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


class Station(ttk.Frame):
    COLUMNS = ["Title", "Author", "Subject"]
    DESIRED = ""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self._create_station_widget()

    def _create_station_widget(self):
        self.station_frame = Frame(self)
        self.station_frame.grid(row=0, column=0, sticky=W)
        self.station_label = Label(self.station_frame, text="Station:", font=("Times New Roman", 12, "bold"))
        self.station_label.grid(row=0, column=0)
        self.blank = Label(self.station_frame,
                           font=("Times New Roman", 12, "bold"))
        self.blank.grid(row=0, column=1, padx=5)
        self.set_button = ttk.Button(self.station_frame, text="Set Station", command=self.change_station)
        self.set_button.grid(row=1, column=0)

        self.station_tree = ttk.Treeview(self, columns=Station.COLUMNS, show="headings", height=16)
        self.station_tree.grid(row=1, column=0, pady=10)

        for index, column in enumerate(Station.COLUMNS):
            self.station_tree.heading(index, text=column)

        self.station_tree.column(0, width=385, minwidth=350, anchor=CENTER)
        self.station_tree.column(1, width=250, minwidth=250, anchor=CENTER)
        self.station_tree.column(2, width=250, minwidth=250, anchor=CENTER)

        self.station_tree.bind("<<TreeviewSelect>>", self.record_selected)

        """
        Problem:
            When the user left clicks on a certain row from the treeview, they have an opportunity to right click. 
            Once they do it, a menu should pop where the cursor is located while catching the selected record 
            from the treeview.
            
            In short, it should return False or nothing should happen when right clicking 
                (then choosing a function from the menu) while there is no record selected.
                
            The above code only pops the menu on the cursor's location.
            
        """
    def record_selected(self, event):
        ...
        """
        def record_selected(event):
            selected_item = event.widget.selection()
            selected_record = event.widget.item(selected_item, "values")
            return perform_checking(selected_record, table_name=table_selector.get())
        """
        selected_item = event.widget.selection()
        selected_record = event.widget.item(selected_item, "values")
        return self.process_selected(selected_record)

    def process_selected(self, record):
        if not record:
            return False
        for widget in self.station_tree.winfo_children():  # One instance of Menu at a time
            if isinstance(widget, Menu):
                widget.destroy()
        print(record)
        search_menu = Menu(self.station_tree, tearoff=False)
        search_menu.add_command(label="Read this", command=lambda: Station.read_this(record[0]))
        search_menu.add_separator()
        search_menu.add_command(label="Unborrow this", command=lambda: Station.unborrow_this(record))
        search_menu.tk_popup(self.station_tree.winfo_pointerx()+10, self.station_tree.winfo_pointery()+10)

    @staticmethod
    def read_this(record):
        ...
        print("Desired", Station.DESIRED)
        print("TITLE", record)
        full_path = os.path.join(Station.DESIRED, record+".pdf")
        print(full_path)
        subprocess.run(["start", "", full_path], shell=True)



    @staticmethod
    def unborrow_this(record):
        ...

    def change_station(self):
        ...
        station_form = ttk.Frame(self.station_frame)
        station_form.grid(row=0, column=1, padx=5)
        station_entry = ttk.Entry(station_form, width=15)
        station_entry.grid(row=0, column=0)
        confirm_button = ttk.Button(station_form, text="Confirm",
                                    command=lambda: self.confirm_change(station_entry.get(), station_form))
        confirm_button.grid(row=0, column=1, padx=5)

    def confirm_change(self, station_name, form):
        ...
        if not station_name:
            return
        try:
            new_name = {
                'name': station_name,
                'current': self.master.master.master.username_entry.get()
            }
            send_request = requests.post("http://127.0.0.1:5000/client/library/station/change_station", json=new_name)
            if send_request.status_code == 200:
                self.blank['text'] = send_request.json()['name']
                print(self.blank['text'])
                return form.destroy()
        except:
            ...


class Collab(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._create_collab_widget()

    def _create_collab_widget(self):
        self.friend_list = ttk.LabelFrame(self, text="FRIEND LIST", labelanchor=N, width=200, height=410)
        self.friend_list.grid_propagate(False)
        self.friend_list.grid(row=0, column=0)
        self.friend_list_canvas = Canvas(self.friend_list, width=170, height=380)
        self.friend_list_canvas.grid(row=0, column=0)
        self.friend_list_scroll = Scrollbar(self.friend_list, orient=VERTICAL, command=self.friend_list_canvas.yview)
        self.friend_list_scroll.grid(row=0, column=1, sticky=N + S)
        self.friend_list_canvas.config(yscrollcommand=self.friend_list_scroll.set)
        self.friend_window = ttk.Frame(self.friend_list_canvas)
        self.friend_list_canvas.create_window((0, 0), anchor="nw", window=self.friend_window)

        """for i in range(100):
            placeholder = Label(self.friend_window, text=f"Placeholder: {i}")
            placeholder.grid(row=i)
            self.friend_window.update()

        self.friend_list_canvas.config(scrollregion=self.friend_list_canvas.bbox("all"))"""

        self.conversation = ttk.LabelFrame(self, text="CONVERSATION", labelanchor=N, width=480, height=410)
        self.conversation.grid_propagate(False)
        self.conversation.grid(row=0, column=2, padx=3)
        self.convo_canvas = Canvas(self.conversation, width=450, height=380)
        self.convo_canvas.grid(row=0, column=0)
        self.convo_scroll = Scrollbar(self.conversation, orient=VERTICAL, command=self.convo_canvas.yview)
        self.convo_scroll.grid(row=0, column=1, sticky=N + S)
        self.convo_canvas.config(yscrollcommand=self.convo_scroll.set)
        self.convo_window = ttk.Frame(self.convo_canvas)
        self.convo_canvas.create_window((0, 0), anchor="nw", window=self.convo_window)

        """for i in range(100, 201):
            placeholder = Label(self.convo_window, text=f"Placeholder: {i}")
            placeholder.grid(row=i)
            self.convo_window.update()

        self.convo_canvas.config(scrollregion=self.convo_canvas.bbox("all"))"""

        self.friend_request = ttk.LabelFrame(self, text="FRIEND REQUEST", labelanchor=N, width=200, height=410)
        self.friend_request.grid_propagate(False)
        self.friend_request.grid(row=0, column=4)

        self.req_canvas = Canvas(self.friend_request, width=170, height=380)
        self.req_canvas.grid(row=0, column=0)
        self.req_scroll = Scrollbar(self.friend_request, orient=VERTICAL, command=self.req_canvas.yview)
        self.req_scroll.grid(row=0, column=1, sticky=N + S)
        self.req_canvas.config(yscrollcommand=self.req_scroll.set)
        self.req_window = ttk.Frame(self.req_canvas)
        self.req_canvas.create_window((0, 0), anchor="nw", window=self.req_window)

        """for i in range(201, 301):
            placeholder = Label(self.req_window, text=f"Placeholder: {i}")
            placeholder.grid(row=i)
            self.req_window.update()

        self.req_canvas.config(scrollregion=self.req_canvas.bbox("all"))"""


class Settings(ttk.Frame):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)


class Client(Toplevel):
    TITLE = "Library: Client"
    AREA = {
        "width": 900,
        "height": 450
    }

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.master.withdraw()
        self.style = ttk.Style(self)
        self.title(Client.TITLE)
        self.geometry("{}x{}".format(Client.AREA["width"], Client.AREA["height"]))
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: Client.show_parent(self, self.master))
        self.client_notebook = ttk.Notebook(self, width=Client.AREA["width"], height=Client.AREA["height"])
        self.client_notebook.grid(row=0, column=0)
        self.style.configure('TNotebook.Tab', padding=(10, 3))
        self._create_widgets()

    @staticmethod
    def show_parent(child, parent):
        child.destroy()
        parent.deiconify()

    def _create_widgets(self):
        self.home = Home(self.client_notebook, padding=5)
        self.client_notebook.add(self.home, text="HOME")

        self.browse = Browse(self.client_notebook, padding=5)
        self.client_notebook.add(self.browse, text="BROWSE")

        self.station = Station(self.client_notebook, padding=5)
        self.client_notebook.add(self.station, text="STATION")

        self.collab = Collab(self.client_notebook, padding=5)
        self.client_notebook.add(self.collab, text="COLLAB")

        self.settings = Settings(self.client_notebook, padding=5)
        self.client_notebook.add(self.settings, text="SETTINGS")

        self.client_notebook.select(self.client_notebook.index(0))
        self.client_notebook.bind("<<NotebookTabChanged>>", lambda event: self.tab_select(event,
                                                                                          self.master.username_entry))

    def tab_select(self, event, username_widget):
        valid_tab = ("home", "browse", "station", "collab", "settings")
        ...
        print(self.client_notebook.tab(event.widget.select(), 'text'))
        tab_name = self.client_notebook.tab(event.widget.select(), 'text')
        username = username_widget.get()
        if not username:
            return
        if tab_name.lower() == valid_tab[0]:  # Home Tab
            try:
                user_data = {
                    'username': username
                }
                send_request = requests.post(f"http://127.0.0.1:5000/client/library/{tab_name.lower()}", json=user_data)
                if send_request.status_code == 200:
                    user_data = send_request.json()
                    self.home.current_user.config(text=f"Username: {user_data['username']}")
                    self.home.time_in.config(text=f"Time-in: {user_data['time-in']}")
                    self.home.id.config(text=f"ID: {user_data['id']}")
                    self.home.status.config(text=f"Status: {user_data['status']}")

            except ConnectionError:
                print(str(ConnectionError))
            except requests.exceptions.ConnectionError:
                print(str(requests.exceptions.ConnectionError))
            except requests.exceptions.HTTPError:
                print(str(requests.exceptions.HTTPError))
            except requests.exceptions.RequestException:
                print(str(requests))

        elif tab_name.lower() == valid_tab[1]:  # Browse Tab
            try:
                send_request = requests.post(f"http://127.0.0.1:5000/client/library/{tab_name.lower()}/{username}")
                if send_request.status_code == 200:
                    response = send_request.json()
                    self.browse.dir['text'] = response['dir']
                    Station.DESIRED = response['dir'][0]
            except ConnectionError:
                print(str(ConnectionError))
            except requests.exceptions.ConnectionError:
                print(str(requests.exceptions.ConnectionError))
            except requests.exceptions.HTTPError:
                print(str(requests.exceptions.HTTPError))
            except requests.exceptions.RequestException:
                print(str(requests))

        elif tab_name.lower() == valid_tab[2]:  # Station Tab
            """
            Show the station name of the user. 
            """
            try:
                send_request = requests.post(f"http://127.0.0.1:5000/client/library/{tab_name.lower()}/{username}")
                if send_request.status_code == 200:
                    response = send_request.json()
                    if "dir" not in response:
                        pass
                    else:
                        Station.DESIRED = response['dir']
                    if "station" not in response:
                        self.station.blank['text'] = response['name']
                    else:
                        self.station.blank['text'] = response['station']['name']

                    if 'books' in response:
                        self.station.station_tree.delete(*self.station.station_tree.get_children())
                        for borrowed_book in response['books']:
                            print(borrowed_book)
                            self.station.station_tree.insert("", END, values=borrowed_book)

                    else:
                        pass


            except ConnectionError:
                print(str(ConnectionError))
            except requests.exceptions.ConnectionError:
                print(str(requests.exceptions.ConnectionError))
            except requests.exceptions.HTTPError:
                print(str(requests.exceptions.HTTPError))
            except requests.exceptions.RequestException:
                print(str(requests))

        elif tab_name.lower() == valid_tab[3]:
            try:
                send_request = requests.post(f"http://127.0.0.1:5000/client/library/{tab_name.lower()}")
            except ConnectionError:
                print(str(ConnectionError))
            except requests.exceptions.ConnectionError:
                print(str(requests.exceptions.ConnectionError))
            except requests.exceptions.HTTPError:
                print(str(requests.exceptions.HTTPError))
            except requests.exceptions.RequestException:
                print(str(requests))

        elif tab_name.lower() == valid_tab[4]:
            try:
                send_request = requests.post(f"http://127.0.0.1:5000/client/library/{tab_name.lower()}")
            except ConnectionError:
                print(str(ConnectionError))
            except requests.exceptions.ConnectionError:
                print(str(requests.exceptions.ConnectionError))
            except requests.exceptions.HTTPError:
                print(str(requests.exceptions.HTTPError))
            except requests.exceptions.RequestException:
                print(str(requests))


if __name__ == "__main__":
    root = Tk()
    c = Client(root)
    root.mainloop()
