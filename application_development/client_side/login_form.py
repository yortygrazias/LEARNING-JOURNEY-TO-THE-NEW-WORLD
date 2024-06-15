import requests
from tkinter import *
from tkinter import ttk
from application_development.client_side import client_ui


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

    @staticmethod
    def register_new_user():
        ...
        Register()

    @staticmethod
    def login(parent, message, *user_data_widgets):
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
                cl = client_ui.Client(parent)
                cl.CURRENT_X = usr
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
    login = Login()
    login.mainloop()
