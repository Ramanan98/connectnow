# ConnectNow
A Django based web application that connects like-minded people with each other.
Users will be able to register their interests and preferences and start chatting with others with similar interests.

# Front end
The front end of the application is built using HTML and JavaScript along with CSS for design. This part implements the presentation layer. This is the part of the application with which the user directly interacts. This part of the application does only a small part of the processing. Front end sends API calls to the back end for most functions like user login, sign up, setting preferences, etc. Its main function is to provide a graphical user interface by formatting the data sent by the server and presenting it in a user friendly manner.

# Back end
This is the backbone of the application as it implements the business logic and data access layers. It’s written using Python and Django server and uses a PostgreSQL database, and Django channels to implement WebSockets connection for matching users. It receives API requests from the client (front end), does the necessary processing, stores and retrieves the required data from database, and returns the relevant data to the client. It has the responsibility of maintaining security and preventing any kinds of errors from occurring in the database.

