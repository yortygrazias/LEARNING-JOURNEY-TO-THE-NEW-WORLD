import time
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory, send_file
from first.backend.data_manager import Model
from flask_socketio import SocketIO, join_room, leave_room


app = Flask(__name__)
app.secret_key = "This is my secret key. Who knows?"
sock_io = SocketIO(app)

online_users = {}


@app.route("/home/register/", methods=["GET", "POST"])
def register():
    requested = request.json
    with Model() as m:
        ...
        if m.find_this("USERNAME", "Users", "USERNAME", requested["user"]["username"]):
            return "Username already exists", 400
        hash_pass, tail = m.hash_this(requested["user"]["passcode"])
        requested["user"]["passcode"] = hash_pass
        requested["user"]["tail"] = tail
        username = requested["user"]["username"]
        requested["info"]["identifier"] = username
        m.create_user_account(**requested["user"])
        m.store_info(**requested["info"])
        return "Account created Successfully", 201


@app.route("/home/login", methods=["GET", "POST"])
def login():
    user_data = request.json
    with Model() as m:
        if m.verify_user(**user_data):
            return "Login Success", 200
        return "Invalid username or password", 400


@sock_io.on("online")
def online(data):
    online_users[str(data)] = data
    print(online_users)
    join_room(f"/chat/{data}")


@app.route("/client/library/home/edit", methods=["GET", "POST", "PUT"])
def edit():
    user_data = request.form
    file_data = request.files
    if 'file' not in file_data:
        return "No attachment", 401
    user_dir = os.path.join("uploads", "user", user_data['username'])
    os.makedirs(user_dir, exist_ok=True)
    actual_file = file_data['file']
    ex = os.path.splitext(actual_file.filename)[1]
    uq = f"{uuid.uuid4().hex}{ex}"
    target = os.path.join(user_dir, uq)
    with open(target, "wb") as f:
        if f.write(actual_file.read()):
            return "Upload success", 200
        return "Upload Failed", 500


@app.route("/client/library/home", methods=["GET", "POST", "PUT"])
def home():
    user_data = request.json
    with Model() as m:
        uid = m.find_this("ID", "Users", "USERNAME", user_data['username'])[0]
        announcements = m.retrieve("Announcement")
        if uid and announcements:
            id_ = uid
            status = "Online"
            time_in = time.strftime("%H:%M")
            data = {
                'username': user_data['username'],
                'status': status,
                'time-in': time_in,
                'id': id_
            }
            announcement = {
                'announcement': announcements
            }
            sock_io.emit("load_announcement", announcement)
            return jsonify(data), 200
        else:
            return "What the hell?", 401


@app.route("/client/library/browse/<user>", methods=["GET", "POST", "PUT"])
def browse(user):
    with Model() as m:
        find_dir = m.find_this("DIR", "Directory", "USER", user)
        if find_dir:
            user_dir = {
                'dir': find_dir
            }
            return jsonify(user_dir), 200
        return "Invalid something", 400


@app.route("/client/library/browse/show", methods=["GET", "POST", "PUT"])
def show():
    book_data = request.json  # This is always have 'title' as key
    print("hello", book_data)
    with Model() as m:
        record = m.query(['BOOK_ID', "TITLE", "AUTHOR", "SUBJECT", "DATE_ADDED", "COVER"], "Books",
                         "TITLE", book_data['title'][1])[0]
        print("HOY", record)
        response = {
            'record': record
        }
        print(response['record'])
        return jsonify(response)


@app.route("/client/library/browse/setdir", methods=["GET", "POST", "PUT"])
def set_dir():
    new_dir = request.json
    if not new_dir['new_dir'] or not new_dir['current_x']:
        return "Invalid Request", 400
    with Model() as m:
        set_new_dir = m.store_dir(**new_dir)
        if set_new_dir:
            user_dir = m.find_this("DIR", "Directory", "USER", new_dir['current_x'])
            if user_dir:
                data = {
                    'dir': user_dir[0]
                }
                return jsonify(data), 200
        return "No directory was selected", 400


@app.route("/client/library/browse/borrow/<title>/<username>", methods=["GET", "POST", "PUT"])
def borrow(title, username):
    ...
    if not title or not username:
        return "Suspicious", 400
    title = title.upper()

    """
    When you get the 'title' of the book, use this data to store a user preference. 
    This rises a question:
        Who borrowed the book?
    Because in the database. There is function 'store_book' that needs two arguments user, book_borrowed --> a 'title' 
        of the book they borrow.
    User here is unknown and should be provided by the frontend.
    """
    """
    The problem above was solved.
    """
    print(username)
    print(title)
    with Model() as m:
        file = m.query(["FILE_NAME", "PATH"], "Books", "Title", title)[0]
        print(file)
        file_name, path = file
        print("Name:", file_name, "Path:", path)
        store_book = m.store_book(username, title)
        if store_book:
            return send_file(path, as_attachment=True), 200
        return "Books already borrowed", 400


@app.route("/client/library/browse/search", methods=["GET", "POST", "PUT"])
def search():
    search_data = request.json
    if "search" not in search_data:
        return "Wrong key bro", 400
    if not search_data['search']:
        return "Bruuuuuhh?", 400
    search_input, tag = search_data.values()
    search_input = search_input.strip()
    tag = tag.strip()
    print(search_input, tag)
    with Model() as m:
        ...
        if tag == "Subject":
            search_input = search_input.capitalize()
        search_result = m.query(["BOOK_ID", "TITLE", "AUTHOR", "SUBJECT", "DATE_ADDED"], "Books",
                                tag, search_input)
        print(search_result)
        if not search_result:
            return "No result: Either search do not exists or search query and tag do not match", 400

        list_of_books = {}
        for index, book in enumerate(search_result):
            list_of_books[f"book{index+1}"] = book
        print(f"List of book: {list_of_books}")
        print(len(list_of_books))
        return jsonify(list_of_books)


@app.route("/client/library/station/<user>", methods=["GET", "POST", "PUT"])
def station(user):
    with Model() as m:
        pref = m.find_this('Station', 'Preference', 'USER', user)
        if not pref:
            station_name = {
                'name': user + " Station"
            }
            return jsonify(station_name)
        station_name = {
            'name': pref[0]
        }
        books_borrowed = [item[0] for item in m.query(['BOOKS'], "BORROWED", "USER", user)]
        book_data = []
        for data in books_borrowed:
            book_data += m.query(['TITLE', 'AUTHOR', 'SUBJECT'], "Books", 'TITLE', data)

        desired_dir = m.find_this("DIR", "Directory", "USER", user)[0]
        station_data = {
            'station': station_name,
            'books': book_data,
            'dir': desired_dir
        }
        return jsonify(station_data), 200


@app.route("/client/library/station/change_station", methods=["GET", "POST", "PUT"])
def change_station():
    name = request.json
    with Model() as m:
        store_pref = m.store_pref(name['name'], name['current'])
        # name --> new name for the station, current --> current user
        if store_pref:
            new_station = {
                'name': name['name']
            }
            return jsonify(new_station), 200
        return "Change Failed", 400


@app.route("/client/library/station/read/<title>", methods=["GET", "POST", "PUT"])
def read(title):
    with Model() as m:
        book_path = m.find_this("PATH", "Books", "TITLE", title)
        if book_path:
            directory = os.path.dirname(book_path[0])
            file = os.path.basename(book_path[0])
            return send_from_directory(directory, file)
        return "No file to read", 400


@app.route("/client/library/collab/see/online", methods=["GET", "POST", "PUT"])
def see_online():
    return jsonify(online_users), 200



@sock_io.on("load_active")
def load_active(data):
    room = f"/chat/{data}"
    sock_io.emit("load_active", online_users, room=room)



@sock_io.on("chat")
def chat(data):
    message, receiver, room, sender = data['message'], data['receiver'], data['room'], data['sender']
    join_room(room)
    sock_io.emit("receive", data, room=room, include_self=False)

    to_notif = {
        'title': 'Chat Message',
        'body': f'[{sender}] sent you a message',
        'sender': sender
    }

    sock_io.emit("receive_notification", to_notif, room=room, include_self=False)
    leave_room(room)

@app.route("/client/library/settings", methods=["GET", "POST", "PUT"])
def settings():
    return "This is settings tab"


@app.route("/server/library/function/add", methods=["GET", "POST", "PUT"])
def add_book():
    ...
    with Model() as m:
        book_file = request.files  # dict_keys(['file', 'cover'])
        book_data = request.form  # dict_keys(['title', 'author', 'subject'])

        file_identifier = Model.generate_string()

        book_dir = os.path.join("app_library", "books", book_data['subject'])
        os.makedirs(book_dir, exist_ok=True)
        file_name = book_data['title'] + f" [{file_identifier}].pdf"
        file_path = os.path.join(book_dir, file_name)
        book_cover_dir = os.path.join("app_library", "cover_pages", book_data['subject'])
        os.makedirs(book_cover_dir, exist_ok=True)
        book_cover_path = os.path.join(book_cover_dir, book_data['title'] + f" [{file_identifier}]" + ".jpg")

        # PDFs only
        with open(file_path, "wb") as f:
            f.write(book_file['file'].read())

        with open(book_cover_path, "wb") as f:
            f.write(book_file['cover'].read())

        about_book = {
            'title': book_data['title'],
            'author': book_data['author'],
            'subject': book_data['subject'],
            'file_name': file_name,
            'file_path': file_path,
            'cover': book_cover_path
        }
        print(about_book['title'], about_book['author'])
        # Check if the book exists in the database
        check_book = m.query(["TITLE", "AUTHOR"], 'Books', 'TITLE', about_book['title'])[0]
        if check_book:
            return "Book already exists", 400
        else:
            if m.add_book(**about_book):
                return f"{about_book['title']} was added.", 200
            return "Failed adding book", 400


@sock_io.on("announce_add")
def add_announce(data):
    to_client = {
        'to_announce': f"[{data['title']}] by [{data['author']}] was added in the library "
                       f"under {data['subject']} catalog. Please check it out.",
        'announce_type': "Main",
        'tag': "Addition of Book"
    }
    with Model() as m:
        store_announcement = m.store_announcement(**to_client)
        """Returns a tuple<5>: number, to_announce, type, tag, date_made"""
        retrieve_keys = ['number', 'to_announce', 'announce_type', 'tag', 'date']
        retrieve_values = [value for value in store_announcement]
        retrieve_dictionary = dict(zip(retrieve_keys, retrieve_values))
        if store_announcement:
            sock_io.emit("receive_announcement", retrieve_dictionary)


if __name__ == "__main__":
    sock_io.run(app=app, debug=True)
