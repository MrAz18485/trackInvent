# trackInvent
#### Video Demo:  [<https://youtu.be/VyaUjn2F5c8>]
#### Description:
trackInvent is an application that will help its users to keep track of their inventory by allowing them to add or view records of the items in their inventory. It's a web application which will support a registering system and a user-friendly interface which will appeal both functionally and visually to its users. During the making of this project, I used Python, HTML, CSS, JavaScript and Flask, but mainly Python, JavaScript and Flask. I also used the web framework Bootstrap for the UI part of this project, and Flask frameworks flask_session and flask_login for the authentication of the users in the website and saving their information for the session they are in, such as their userid.

For the database system of this project, I used sqlite which suited my needs and used an extension called SQLTools to run various queries on the database in the debugging process to spot possible mistakes.


app.py
It's possible to state that this file is the heart of the project itself.

Helper Functions

hashPassword() -> Used for hashing the inputted password of the user

loadInventory() -> Loads the inventory of the user by running a query on the database file and returning the result (if exists). Mainly used when loading the pages

updateInventory() -> In case of any changes that are made in user's inventory, this function gets called to make the updates on the database possible. This function runs various queries depending on the arguments passed to it on table "inventory"

updateLogs() -> Whenever a change has been made (i.e. adding or deleting item(s)) this function gets called, which runs a query that inserts a row to the table "logs" about the last change committed into the database to keep track of any changes that are made in user's inventory

sort_tuple() -> sorts the tuple that's passed to the function as a parameter in descending order. Helps in sorting the items from highest count to lowest count in pages.


Functions related to Flask

app.py:

inventory(), additem(), deleteitem(), retrievehistory(), adjustsetting(), login(), register()

inventory() -> helps in showing the inventory page of the user.

additem() -> helps in showing the "add item" page

deleteitem() -> helps in showing the "delete item" page

retrievehistory() -> helps in showing the history page

adjustsetting() -> handles the settings page

login() -> takes care of login process

register() -> takes care of registering process

logout() -> logs the user out of account

All of these pages connect to the database maindb.db to either validate, retrieve or do both in order to get the site running.


helpers.py:

login_required() -> validates that the user is logged in. Prevents user from browsing pages other than registration and login pages.


HTML templates

additem.html -> html file which is shown in add items tab

deleteitem.html -> html file related to delete items tab

history.html -> html file related to history tab

inventory.html -> html file related to inventory tab

layout.html -> heart of all files. It's like the template almost all other html files inherit from partially, such as additem, deleteitem and inventory using the first table and history using the second table, while settings uses either of the tables but still inherits the alerts.

login.html -> html file related to login process, doesn't inherit from layout.html due to its unique structure.

register.html -> html file related to registering process, same as login.html in terms of inheritance.

settings.html -> html file related to settings tab.


static folder

setting.png -> used for making a clickable picture for settings tab in navigation bar of the website, non-commercial use only.


db folder

maindb.db -> a sqlite database file which lies in center of all database operations committed in this application. Includes 3 tables: userinformation, inventory and logs.

userinventory consists of 3 values: userid (primary key, text), email (text) and password (text). userid is in the format of uuid4 and password is in format of a sha256-encrypted string.

inventory consists of 3 values: userid (text), item(text) and count(integer)
userid is again in the format of a uuid4 value, item is in string format and count is in integer format.

logs consists of 4 values: userid(text), item(text), count(text) and date(text)
userid is in the same format as mentioned above, while item, count and text are just strings.

DESIGN CHOICES

I prefered to not use anything other than bootstrap in the front-end visuals since it seemed sufficient enough, also since I'm not really a front-end person I decided not to spend so much effort on UI

I used sqlite for my database since it's lightweight and sufficient for my project.

Instead of django I used flask since I already had some knowledge about flask thanks to week 9 of CS50.