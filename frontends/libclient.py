import time
import os
import requests
import subprocess
import socketio
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk


class Home(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        LibClient.sio_connection.on("receive_announcement", self.receive_announcement)
        LibClient.sio_connection.on("receive_notification", self.receive_notif)
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
        self.announcement = ttk.LabelFrame(self.info_frame, text="ANNOUNCEMENT", width=LibClient.AREA["width"] / 2,
                                           height=280)
        self.announcement.grid_propagate(False)
        self.announcement.grid(row=0, column=0, rowspan=2, padx=5)

        self.notification = ttk.LabelFrame(self.info_frame, text="NOTIFICATION", width=LibClient.AREA["width"] / 2 - 25,
                                           height=135)
        self.notification.grid_propagate(False)
        self.notification.grid(row=0, column=1, sticky=N)

        self.quote = ttk.LabelFrame(self.info_frame, text="QUOTES OF THE DAY", width=LibClient.AREA["width"] / 2 - 25,
                                    height=135)
        self.quote.grid_propagate(False)
        self.quote.grid_columnconfigure(0, weight=1)
        self.quote.grid_rowconfigure(0, weight=1)
        self.quote.grid(row=1, column=1, sticky=S)

        self.quote_content = Label(self.quote, text="PSALMS 73:26\n"
                                                    "My flesh and my heart may fail, but God is the strength of "
                                                    "my heart and my portion forever.", wraplength=400)
        self.quote_content.grid(row=0, column=0)

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

        self.announce_canvas = Canvas(self.announcement, width=420, height=250)
        self.announce_canvas.grid(row=0, column=0)
        self.announce_scroll = Scrollbar(self.announcement, orient=VERTICAL,
                                         command=self.announce_canvas.yview)
        self.announce_scroll.grid(row=0, column=1, sticky=N + S)
        self.announce_canvas.config(yscrollcommand=self.announce_scroll.set)
        self.announce_window = ttk.Frame(self.announce_canvas)

        self.announce_canvas.create_window((0, 0), window=self.announce_window, anchor="nw")

        self.notif_canvas = Canvas(self.notification, width=390, height=110)
        self.notif_canvas.grid(row=0, column=0)
        self.notif_scroll = Scrollbar(self.notification, orient=VERTICAL, command=self.notif_canvas.yview)
        self.notif_scroll.grid(row=0, column=1, sticky=N+S, padx=5)
        self.notif_canvas.config(yscrollcommand=self.notif_scroll.set)
        self.notif_window = ttk.Frame(self.notif_canvas, padding=5)
        self.notif_canvas.create_window((0, 0), anchor=N+W, window=self.notif_window)

        self.announcement.bind("<Enter>", lambda event, c=self.announce_canvas: c.bind_all("<MouseWheel>",
                                                                                           lambda e: self.on_scroll(e, c)))
        self.announcement.bind("<Leave>", lambda event, c=self.announce_canvas: c.unbind_all("<MouseWheel>"))
        self.notification.bind("<Enter>", lambda event, c=self.notif_canvas: c.bind_all("<MouseWheel>",
                                                                                        lambda e: self.on_scroll(e, c)))
        self.notification.bind("<Leave>", lambda event, c=self.notif_canvas: c.unbind_all("<MouseWheel>"))


    def on_scroll(self, event, canvas):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def receive_announcement(self, announcement_data):
        ...
        print("I received the announcement")
        number, to_announce, announce_type, announce_tag, date = (
            announcement_data['number'],
            announcement_data['to_announce'],
            announcement_data['announce_type'],
            announcement_data['tag'],
            announcement_data['date'])

        announce_label = ttk.Labelframe(self.announce_window, text=announce_tag)
        announce_label.grid(row=len(self.announce_window.winfo_children()), pady=2, sticky=W)
        announce_text = Label(announce_label, text=to_announce, wraplength=420)
        announce_text.grid(row=0, column=0)
        date_label = Label(self.announce_window, text=date)
        date_label.grid(row=len(self.announce_window.winfo_children()), pady=3)
        announce_separator = ttk.Separator(self.announce_window, orient=HORIZONTAL)
        announce_separator.grid(row=len(self.announce_window.winfo_children()), sticky=W+E, pady=2)
        self.announce_window.update()
        self.announce_canvas.config(scrollregion=self.announce_canvas.bbox("all"))
        self.announce_canvas.yview_moveto(1.0)

    def receive_notif(self, data):
        print("I received a notification")
        notif_title, notif_body, notif_sender = data['title'], data['body'], data['sender']
        notif_label = ttk.Labelframe(self.notif_window, text=notif_title)
        notif_label.grid(row=len(self.notif_window.winfo_children()), sticky=W + E)
        notif_text = Label(notif_label, text=notif_body, wraplength=375)
        notif_text.grid(row=0, column=0)
        notif_separator = ttk.Separator(self.notif_window, orient=HORIZONTAL)
        notif_separator.grid(row=len(self.notif_window.winfo_children()), sticky=W + E, pady=5)
        self.notif_window.update()
        self.notif_canvas.config(scrollregion=self.notif_canvas.bbox("all"))
        self.notif_canvas.yview_moveto(1.0)

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
                                     command=lambda: self.set_dir(LibClient.current_user))
        self.dir_button.grid(row=0, column=3)

        self.search_tree = ttk.Treeview(self, show="headings", columns=Browse.SEARCH_COLUMNS, height=15)
        self.search_tree.grid(row=2, column=0)
        self.search_tree.bind("<<TreeviewSelect>>",
                              lambda event: self.record_selected(event, LibClient.current_user))

        self.search_button.config(command=lambda: Browse.search_book(self.search, self.tag, self.search_result,
                                                                     self.search_tree, event=None))
        self.search.bind("<Return>", lambda event: Browse.search_book(self.search, self.tag, self.search_result,
                                                                      self.search_tree, event))

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
    def search_book(entry: ttk.Entry, tag: ttk.Combobox, result: Label, tree: ttk.Treeview, event=None):
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
                'current': LibClient.current_user
            }
            send_request = requests.post("http://127.0.0.1:5000/client/library/station/change_station", json=new_name)
            if send_request.status_code == 200:
                self.blank['text'] = send_request.json()['name']
                print(self.blank['text'])
                return form.destroy()

        except requests.exceptions.ConnectionError as reC:
            print(reC)


class Collab(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        LibClient.sio_connection.on("receive", self.receive_message)
        LibClient.sio_connection.emit("load_active", LibClient.current_user)
        self.online_users_frames = {}
        self.online_users_windows = {}
        self.online_users_button_list = []
        self._create_collab_widget()

    def _create_collab_widget(self):
        self.active_users_label = ttk.LabelFrame(self, text="ACTIVE USERS", labelanchor=N, width=200, height=410)
        self.active_users_label.grid_propagate(False)
        self.active_users_label.grid(row=0, column=0)
        self.active_list_canvas = Canvas(self.active_users_label, width=170, height=330)
        self.active_list_canvas.grid(row=0, column=0)
        self.active_list_scroll = Scrollbar(self.active_users_label, orient=VERTICAL,
                                            command=self.active_list_canvas.yview)
        self.active_list_scroll.grid(row=0, column=1, sticky=N + S)
        self.active_list_canvas.config(yscrollcommand=self.active_list_scroll.set)
        self.active_list_window = ttk.Frame(self.active_list_canvas, padding=5, relief=RIDGE)
        self.active_list_canvas.create_window((0, 0), anchor="nw", window=self.active_list_window, width=173)

        self.active_search_frame = ttk.Frame(self.active_list_window)
        self.active_search_frame.grid(row=0, column=0)
        self.active_search_text = Label(self.active_search_frame, text="Search:")
        self.active_search_text.grid(row=0, column=0)
        self.active_search = ttk.Entry(self.active_search_frame, width=18)
        self.active_search.grid(row=0, column=1)

        self.active_button_frame = ttk.Frame(self.active_users_label)
        self.active_button_frame.grid(row=1, column=0)
        self.online_users_button = ttk.Button(self.active_button_frame, text="SEE ONLINE USERS",
                                              command=self.see_online_users)
        self.online_users_button.grid(row=1, column=0, sticky=W+E)
        self.study_group_button = ttk.Button(self.active_button_frame, text="CREATE STUDY GROUP")
        self.study_group_button.grid(row=2, column=0)

        self.conversation = ttk.LabelFrame(self, text="CONVERSATION", labelanchor=N, width=480, height=410)
        self.conversation.grid_propagate(False)
        self.conversation.grid(row=0, column=2, padx=3)
        self.convo_canvas = Canvas(self.conversation, width=450, height=360)
        self.convo_canvas.grid(row=0, column=0)

        self.message_frame = ttk.Frame(self.conversation)
        self.message_frame.grid(row=1, column=0)
        self.current_user_label = Label(self.message_frame, text=LibClient.current_user, state=DISABLED)
        self.current_user_label.grid(row=0, column=0)
        self.message_entry = ttk.Entry(self.message_frame, width=20, state=DISABLED)
        self.message_entry.grid(row=0, column=1, padx=5)
        self.send_label_instruction = Label(self.message_frame, text="[ENTER] to SEND", state=DISABLED)
        self.send_label_instruction.grid(row=0, column=2)

        self.convo_scroll = Scrollbar(self.conversation, orient=VERTICAL, command=self.convo_canvas.yview)
        self.convo_scroll.grid(row=0, column=1, sticky=N + S)
        self.convo_canvas.config(yscrollcommand=self.convo_scroll.set)

        self.study_group_label = ttk.LabelFrame(self, text="STUDY GROUP", labelanchor=N, width=200, height=410)
        self.study_group_label.grid_propagate(False)
        self.study_group_label.grid(row=0, column=4)

        self.group_list_canvas = Canvas(self.study_group_label, width=170, height=380)
        self.group_list_canvas.grid(row=0, column=0)
        self.group_list_scroll = Scrollbar(self.study_group_label, orient=VERTICAL,
                                           command=self.group_list_canvas.yview)
        self.group_list_scroll.grid(row=0, column=1, sticky=N + S)
        self.group_list_canvas.config(yscrollcommand=self.group_list_scroll.set)
        self.group_list_window = ttk.Frame(self.group_list_canvas, padding=10)
        self.group_list_canvas.create_window((0, 0), anchor="nw", window=self.group_list_window)

    def receive_message(self, data):
        print()
        message, receiver, room, sender = data['message'], data['receiver'], data['room'], data['sender']
        print(self.online_users_frames)
        print(message, receiver, room, sender)
        """self.online_users_frames[sender] = ttk.Frame(self.convo_canvas, padding=5, relief=RIDGE)
        self.online_users_windows[sender] = self.convo_canvas.create_window(
            (0, 0), anchor=N + W, window=self.online_users_frames[sender], width=453, state=HIDDEN)
        blank_space_c = Label(self.online_users_frames[sender], text=" " * 145)
        blank_space_c.grid(row=0, column=0, columnspan=2)
        convo_separator = ttk.Separator(self.online_users_frames[sender], orient=HORIZONTAL)
        convo_separator.grid(row=0, column=0, columnspan=2, sticky=W + E)"""
        if sender not in self.online_users_frames:
            self.online_users_frames[sender] = ttk.Frame(self.convo_canvas, padding=5, relief=RIDGE)
            self.online_users_windows[sender] = self.convo_canvas.create_window(
                (0, 0), anchor=N + W, window=self.online_users_frames[sender], width=453, state=HIDDEN)
            blank_space_c = Label(self.online_users_frames[sender], text=" " * 145)
            blank_space_c.grid(row=0, column=0, columnspan=2)
            convo_separator = ttk.Separator(self.online_users_frames[sender], orient=HORIZONTAL)
            convo_separator.grid(row=0, column=0, columnspan=2, sticky=W + E)

            sender_frame = self.online_users_frames[sender]
            receiver_label = ttk.LabelFrame(sender_frame, text=f"FROM: [{data['sender']}]\nTO: [{data['receiver']}]",
                                            labelanchor=N + W)
            receiver_label.grid(row=len(sender_frame.winfo_children()), column=0, sticky=W)
            received_message = Label(receiver_label, text=message, wraplength=200, justify=LEFT)
            received_message.grid(row=0, column=0)

            sender_frame.update()
            self.convo_canvas.config(scrollregion=self.convo_canvas.bbox("all"))
            self.convo_canvas.yview_moveto(1.0)

        else:
            sender_frame = self.online_users_frames[sender]
            receiver_label = ttk.LabelFrame(sender_frame, text=f"FROM: [{data['sender']}]\nTO: [{data['receiver']}]",
                                            labelanchor=N + W)
            receiver_label.grid(row=len(sender_frame.winfo_children()), column=0, sticky=W)
            received_message = Label(receiver_label, text=message, wraplength=200, justify=LEFT)
            received_message.grid(row=0, column=0)

            sender_frame.update()
            self.convo_canvas.config(scrollregion=self.convo_canvas.bbox("all"))
            self.convo_canvas.yview_moveto(1.0)

    def send_message(self, event, selected_user):

        message = event.widget.get()
        receiver = selected_user
        room = f"/chat/{receiver}"

        data = {
            'message': message,
            'receiver': receiver,
            'room': room,
            'sender': LibClient.current_user
        }

        LibClient.sio_connection.emit("chat", data)
        sender_frame = self.online_users_frames[selected_user]
        print(selected_user)
        print(sender_frame)

        sender_label = ttk.LabelFrame(sender_frame, text=f"FROM: [{data['sender']}]\nTO: [{data['receiver']}]",
                                      labelanchor=N + E)
        sender_label.grid(row=len(sender_frame.winfo_children()), column=1, sticky=E)
        sent_message = Label(sender_label, text=message, wraplength=200, justify=LEFT)
        sent_message.grid(row=0, column=0)

        sender_frame.update()
        self.convo_canvas.config(scrollregion=self.convo_canvas.bbox("all"))
        self.convo_canvas.yview_moveto(1.0)

        event.widget.delete(0, END)

    """def load_active(self, data):
        ...
        var = StringVar()
        del data[LibClient.current_user]
        if not self.conversation.winfo_children():
            for user in data.keys():
                self.online_users_frames[user] = ttk.Frame(self.convo_canvas, padding=5, relief=RIDGE)
                self.online_users_windows[user] = (
                    self.convo_canvas.create_window((0, 0),
                                                    anchor=N+W,
                                                    window=self.online_users_frames[user],
                                                    state=HIDDEN,
                                                    width=453))
                blank_space_c = Label(self.online_users_frames[user], text=" " * 145)
                blank_space_c.grid(row=0, column=0, columnspan=2)

                convo_separator = ttk.Separator(self.online_users_frames[user], orient=HORIZONTAL)
                convo_separator.grid(row=0, column=0, columnspan=2, sticky=W + E)

                ttk.Radiobutton(self.active_list_window, text=user, variable=var, value=data[user],
                                command=lambda u=user: self.selected_online_user(u)).grid(
                    row=len(self.active_list_window.winfo_children()), sticky=W)

    def selected_online_user(self, selected_user):
        for widget in self.message_frame.winfo_children():
            widget['state'] = NORMAL
        print(selected_user)

        for window in self.online_users_windows.values():
            self.convo_canvas.itemconfig(window, state=HIDDEN)

        self.convo_canvas.itemconfig(self.online_users_windows[selected_user], state=NORMAL)

        self.message_entry.bind("<Return>", lambda event: self.send_message(event, selected_user))"""

    def see_online_users(self):
        for button in self.online_users_button_list:
            if not self.online_users_button_list:
                pass
            button.destroy()
        try:
            send_request = requests.get("http://127.0.0.1:5000/client/library/collab/see/online")
            if send_request.status_code == 200:
                response = send_request.json()
                response.pop(LibClient.current_user)
                var = StringVar()
                for user in response.keys():
                    rdb = ttk.Radiobutton(self.active_list_window, text=user, variable=var, value=response[user],
                                          command=lambda u=user: self.selected_online_user(u))
                    rdb.grid(
                        row=len(self.active_list_window.winfo_children()), sticky=W
                    )
                    self.online_users_button_list.append(rdb)
        except ConnectionError:
            print(str(ConnectionError))
        except requests.exceptions.ConnectionError:
            print(str(requests.exceptions.ConnectionError))
        except requests.exceptions.HTTPError:
            print(str(requests.exceptions.HTTPError))
        except requests.exceptions.RequestException:
            print(str(requests))

    def selected_online_user(self, selected_user):
        ...
        """
        
        Check if the selected_user has already Frame and a Window.
        If not:
            Create a frame and add a window.
            Store it in a dictionary (self.online_user_frame, self.online_user_window)
        If yes:
            Load it.
        """
        self.message_entry.bind("<Return>", lambda event: self.send_message(event, selected_user))

        for widget in self.message_frame.winfo_children():
            widget['state'] = NORMAL
        if selected_user not in self.online_users_frames:
            for window in self.online_users_windows.values():
                self.convo_canvas.itemconfig(window, state=HIDDEN)

            self.online_users_frames[selected_user] = ttk.Frame(self.convo_canvas, padding=5, relief=RIDGE)
            self.online_users_windows[selected_user] = self.convo_canvas.create_window(
                (0, 0), anchor=N+W, window=self.online_users_frames[selected_user], width=453)

            blank_space_c = Label(self.online_users_frames[selected_user], text=" " * 145)
            blank_space_c.grid(row=0, column=0, columnspan=2)

            convo_separator = ttk.Separator(self.online_users_frames[selected_user], orient=HORIZONTAL)
            convo_separator.grid(row=0, column=0, columnspan=2, sticky=W + E)

        else:
            for window in self.online_users_windows.values():
                self.convo_canvas.itemconfig(window, state=HIDDEN)

            self.convo_canvas.itemconfig(self.online_users_windows[selected_user], state=NORMAL)



class Settings(ttk.Frame):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)


class LibClient(Toplevel):
    TITLE = "Library: Client"
    AREA = {
        "width": 900,
        "height": 450
    }
    current_user = None
    sio_connection = None

    def __init__(self, master, current_user, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.current_user = current_user
        LibClient.current_user = self.current_user

        self.socket_io = socketio.Client()
        LibClient.sio_connection = self.socket_io
        self.socket_io.connect("http://127.0.0.1:5000")
        self.socket_io.emit("online", self.current_user)
        self.socket_io.on("load_announcement", self.load_announcement)

        self.master.withdraw()
        self.style = ttk.Style(self)
        self.title(LibClient.TITLE)
        self.geometry("{}x{}".format(LibClient.AREA["width"], LibClient.AREA["height"]))
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: LibClient.show_parent(self, self.master))
        self.client_notebook = ttk.Notebook(self, width=LibClient.AREA["width"], height=LibClient.AREA["height"])
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
                                                                                          self.current_user))

        self.binding_keys = ("<F1>", "<F2>", "<F3>", "<F4>", "<F5>")

        for key in self.binding_keys:
            self.bind(key, lambda event, k=key: self.client_notebook.select(self.binding_keys.index(k)))

    def load_announcement(self, data):
        try:
            if not self.home.announce_window.winfo_children():
                for number, to_announce, a_type, tag, date in data['announcement']:
                    ...
                    lbf = ttk.Labelframe(self.home.announce_window, text=tag)
                    lbf.grid(row=len(self.home.announce_window.winfo_children()), sticky=W + E)
                    lbt = Label(lbf, text=to_announce, wraplength=417, justify=LEFT)
                    lbt.grid(row=0, column=0)
                    date_label = Label(self.home.announce_window, text=f"Date: {date}")
                    date_label.grid(row=len(self.home.announce_window.winfo_children()), sticky=W, pady=2)
                    announce_separator = ttk.Separator(self.home.announce_window, orient=HORIZONTAL)
                    announce_separator.grid(row=len(self.home.announce_window.winfo_children()), sticky=W + E, pady=3)
                    self.home.announce_window.update()
                    self.home.announce_canvas.config(scrollregion=self.home.announce_canvas.bbox("all"))
                    self.home.announce_canvas.yview_moveto(1.0)
        except TclError:
            pass

    def tab_select(self, event, current_user):
        valid_tab = ("home", "browse", "station", "collab", "settings")
        ...
        print(self.client_notebook.tab(event.widget.select(), 'text'))
        tab_name = self.client_notebook.tab(event.widget.select(), 'text')
        if not current_user:
            return
        if tab_name.lower() == valid_tab[0]:  # Home Tab
            try:
                user_data = {
                    'username': current_user
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
                send_request = requests.post(f"http://127.0.0.1:5000/client/library/{tab_name.lower()}/"
                                             f"{self.current_user}")
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
                send_request = requests.post(f"http://127.0.0.1:5000/client/library/{tab_name.lower()}/"
                                             f"{self.current_user}")
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


class Register(Toplevel):
    REGISTER_AREA = {
        "width": 230,
        "height": 320
    }

    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.geometry("{}x{}".format(Register.REGISTER_AREA["width"], Register.REGISTER_AREA["height"]))
        self.resizable(False, False)
        self.grab_set()
        self._create_register_widgets()

    def _create_register_widgets(self):
        ...
        self.register = Label(self, text="REGISTER", font=("Times New Roman", 15, "bold"))
        self.register.grid(row=0, column=0, columnspan=2, pady=10)

        self.first_name_label = Label(self, text="First Name:")
        self.first_name_label.grid(row=1, column=0)
        self.first_name = ttk.Entry(self, width=15)
        self.first_name.grid(row=1, column=1, padx=3, sticky=W + E)

        self.last_name_label = Label(self, text="Last Name:")
        self.last_name_label.grid(row=2, column=0)
        self.last_name = ttk.Entry(self, width=15)
        self.last_name.grid(row=2, column=1, padx=3, pady=5, sticky=W + E)

        self.age_var = StringVar()
        self.age_label = Label(self, text="Age:")
        self.age_label.grid(row=3, column=0)
        self.age = ttk.Combobox(self, values=[str(age) for age in range(16, 60 + 1)], textvariable=self.age_var,
                                width=15)
        self.age.grid(row=3, column=1, padx=3)

        self.gender_var = StringVar()
        self.gender_label = Label(self, text="Gender:")
        self.gender_label.grid(row=4, column=0)
        self.gender_frame = ttk.Frame(self)
        self.gender_frame.grid(row=4, column=1, padx=3, pady=5)
        self.male_gender = ttk.Radiobutton(self.gender_frame, text="Male", value="Male", variable=self.gender_var)
        self.male_gender.grid(row=0, column=0)
        self.female_gender = ttk.Radiobutton(self.gender_frame, text="Female", value="Female", variable=self.gender_var)
        self.female_gender.grid(row=0, column=1)

        self.email_label = Label(self, text="Email:")
        self.email_label.grid(row=5, column=0)
        self.email = ttk.Entry(self, width=15)
        self.email.grid(row=5, column=1, padx=3, sticky=W + E)

        self.tl_username_label = Label(self, text="Username:")
        self.tl_username_label.grid(row=6, column=0)
        self.tl_username = ttk.Entry(self, width=15)
        self.tl_username.grid(row=6, column=1, sticky=W + E, padx=3, pady=5)

        self.tl_password_label = Label(self, text="Password:")
        self.tl_password_label.grid(row=7, column=0)
        self.tl_password = ttk.Entry(self, width=15, show="*")
        self.tl_password.grid(row=7, column=1, sticky=W + E, padx=3)

        self.tl_password_label_2 = Label(self, text="Confirm Password:")
        self.tl_password_label_2.grid(row=8, column=0)
        self.tl_password_2 = ttk.Entry(self, width=15, show="*")
        self.tl_password_2.grid(row=8, column=1, sticky=W + E, padx=3, pady=5)

        self.save_info = ttk.Button(self, text="Save")
        self.save_info.grid(row=9, column=1, sticky=W + E)

        self.tl_message = Label(self, wraplength=200)
        self.tl_message.grid(row=10, column=0, columnspan=2, pady=10)

        widget_with_data = [self.first_name, self.last_name, self.age,
                            self.gender_var, self.email, self.tl_username,
                            self.tl_password, self.tl_password_2]
        self.save_info.config(command=lambda: Register.save_new_user(self.tl_message, *widget_with_data))

    @staticmethod
    def save_new_user(tl_message, *data_to_transfer):
        if any(widget.get() == "" for widget in data_to_transfer):
            return tl_message.config(text="You cannot leave entry(ies) as blank.")
        data_to_save = tuple([widget.get() for widget in data_to_transfer])
        if data_to_save[len(data_to_save) - 1] != data_to_save[len(data_to_save) - 2]:
            return tl_message.config(text="Password do not match")
        try:
            if not isinstance(int(data_to_save[2]), int):
                raise ValueError
        except ValueError:
            return tl_message.config(text="Invalid age")

        # Conversion
        first_name, last_name, age, gender, email, username, password, password2 = data_to_save
        age = int(age)
        info_data = {
            "first_name": first_name,
            "last_name": last_name,
            "age": age,
            "gender": gender,
            "email": email,
            "identifier": None
        }
        user_data = {
            "username": username,
            "passcode": password,
            "tail": ""
        }
        all_data = {
            "user": user_data,
            "info": info_data
        }

        try:
            send_request = requests.post(url="http://127.0.0.1:5000/home/register", json=all_data)
            if send_request.status_code == 201:
                tl_message.config(text=send_request.text)
            elif send_request.status_code == 400:
                tl_message.config(text="Username already exists.")
        except ConnectionError:
            tl_message['text'] = "Cannot connect to server."
        except requests.exceptions.ConnectionError:
            tl_message['text'] = "Cannot connect to server."
        except requests.exceptions.HTTPError:
            tl_message['text'] = "Invalid Requests."
        except requests.exceptions.RequestException:
            tl_message['text'] = "Invalid Requests."


class Login(Tk):
    TITLE = "Login"
    LOGIN_AREA = {
        "width": 200,
        "height": 200
    }

    def __init__(self):
        super().__init__()
        self.title(Login.TITLE)
        self.geometry("{}x{}".format(Login.LOGIN_AREA["width"], Login.LOGIN_AREA["height"]))
        self.resizable(False, False)
        self._create_widget()

    def _create_widget(self):
        ...
        self.login_frame = ttk.Frame(self)
        self.login_frame.place(x=Login.LOGIN_AREA["width"] / 2, y=Login.LOGIN_AREA["height"] / 2 - 10, anchor=CENTER)
        self.login_label = Label(self.login_frame, text="LOGIN", font=("Times New Roman", 15, "bold"))
        self.login_label.grid(row=0, column=0, columnspan=2, pady=10)
        self.username_label = Label(self.login_frame, text="Username:")
        self.username_label.grid(row=1, column=0)
        self.username_entry = ttk.Entry(self.login_frame, width=15)
        self.username_entry.grid(row=1, column=1, padx=3, pady=3)
        self.password_label = Label(self.login_frame, text="Password:")
        self.password_label.grid(row=2, column=0)
        self.password_entry = ttk.Entry(self.login_frame, width=15, show="*")
        self.password_entry.grid(row=2, column=1, padx=3)

        self.confirm_button = ttk.Button(self.login_frame, text="Login")
        self.confirm_button.grid(row=3, column=1, pady=3, sticky=W + E)
        self.register_button = ttk.Button(self.login_frame, text="Register", command=Login.register_new_user)
        self.register_button.grid(row=4, column=1, sticky=W + E)

        self.login_message = Label(self.login_frame, wraplength=180)
        self.login_message.grid(row=5, column=0, columnspan=2, pady=10)

        self.confirm_button.config(command=lambda: Login.login(self, self.login_message, self.username_entry,
                                                               self.password_entry))

        self.bind("<Return>", lambda event: Login.login(self, self.login_message, self.username_entry,
                                                        self.password_entry, event=event))

    @staticmethod
    def register_new_user():
        ...
        Register()

    @staticmethod
    def login(parent, message, *user_data_widgets, event=None):
        ...
        if any(data.get() == "" for data in user_data_widgets):
            return message.config(text="Invalid username or password")
        username, passcode = user_data_widgets
        usr = username.get()
        pw = passcode.get()
        data = {
            "username": usr,
            "passcode": pw
        }
        try:
            send_request = requests.post(url="http://127.0.0.1:5000/home/login", json=data)
            if send_request.status_code == 200:
                # This status code must be changed for 'I don't know' reason.
                message.config(text="Login Success")
                LibClient(parent, data['username'])
                passcode.delete(0, END)
            else:
                message.config(text=send_request.text)
        except ConnectionError:
            message['text'] = "Server is offline"
        except requests.exceptions.ConnectionError:
            message['text'] = "Cannot connect to server."
        except requests.exceptions.HTTPError:
            message['text'] = "Invalid Requests."
        except requests.exceptions.RequestException:
            message['text'] = "Invalid Requests."


if __name__ == "__main__":
    login_ui = Login()
    login_ui.mainloop()
