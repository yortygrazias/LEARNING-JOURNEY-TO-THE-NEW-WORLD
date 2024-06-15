The client_ui codebase uses an OOP codewriting for reusability purpose and uses tkinter for interfaces.

The login_form codebase is actually the root and should be the one to run or I should say a starting point of running the application.
    It imports the client_ui which is actually a Toplevel widget and instantiate it after a success of login requests.

The server_ui is an additional interface for non-tech user (and should be usually handle by admin or in this case a librarian) so they can navigate, maintain and manage the application. 

    
MAJOR REMINDER!
    The main application the "Library Management System" uses a tkinter for frontend interface and Flask for backend interface.

    PROJECT: (Library Management System)
        tkinter - Frontend
        Flask - Backend
    
    All necessarry modules are used for client-to-server or server-to-client interaction. See them inside the the client_ui codebase.
