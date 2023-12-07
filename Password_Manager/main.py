from tkinter import *
from tkinter import messagebox
import pyperclip
from password_generator import password_generator
import mysql.connector

# ---------------------------- UI COLORS AND FONT ------------------------------- #
WINDOW_BG = "#111d5e"
FIELD_COLORS = "#dddddd"
FIELD_FONT_COLOR = "#c70039"
LABEL_COLOR = "white"
FONT = ("Courier", 15, "normal")

# MySQL Configuration
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "alwin"
MYSQL_DATABASE = "DBMS_Project"

# ---------------------------- PASSWORD GENERATOR ------------------------------- #
def get_password():
    password = password_generator()
    pyperclip.copy(password)
    password_entry.delete(0, END)
    password_entry.insert(END, password)

# ---------------------------- SAVE PASSWORD ------------------------------- #
def database_manager(new_user_entry):
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        cursor = connection.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS passwords (
            website VARCHAR(255) PRIMARY KEY,
            email VARCHAR(255),
            password VARCHAR(255)
        )
        """
        cursor.execute(create_table_query)

        insert_query = """
        INSERT INTO passwords (website, email, password)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE email = VALUES(email), password = VALUES(password)
        """
        cursor.execute(insert_query, (new_user_entry["website"], new_user_entry["email"], new_user_entry["password"]))

        connection.commit()
        connection.close()

    except mysql.connector.Error as err:
        messagebox.showerror(title="Database Error", message=f"Error: {err}")
    finally:
        website_entry.delete(0, END)
        email_entry.delete(0, END)
        password_entry.delete(0, END)

def save_password():
    website = website_entry.get()
    email = email_entry.get()
    password = password_entry.get()

    if len(website) == 0 or len(password) == 0:
        messagebox.showinfo(title="Oops", message="Please make sure you have not left any fields empty")
    else:
        is_ok = messagebox.askokcancel(
            title="Confirm entries",
            message=f"These are the details you entered\nEmail: {email}\nPassword: {password}\nIs it okay to save ?"
        )
        if is_ok:
            new_entry_in_json = {
                "website": website,
                "email": email,
                "password": password
            }
            database_manager(new_entry_in_json)

# ---------------------------- SEARCH PASSWORD ------------------------------- #
def search_password():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        cursor = connection.cursor()

        select_query = """
        SELECT email, password FROM passwords WHERE website = %s
        """
        cursor.execute(select_query, (website_entry.get(),))
        result = cursor.fetchone()

        connection.close()

        if result:
            email, password = result
            is_clipboard = messagebox.askokcancel(
                title=website_entry.get(),
                message=f"Email: {email}\nPassword: {password}\n\nSave to clipboard?"
            )
            if is_clipboard:
                pyperclip.copy(password)
                messagebox.showinfo(title="Saved to clipboard", message="Password has been saved to clipboard")
        else:
            messagebox.showinfo(
                title="Password not saved for this website",
                message=f"The password for {website_entry.get()} has not been saved"
            )

    except mysql.connector.Error as err:
        messagebox.showerror(title="Database Error", message=f"Error: {err}")

# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Password Manager")
window.config(padx=20, pady=20, bg=WINDOW_BG)

# Label for Website
website_label = Label(text="Website", bg=WINDOW_BG, padx=20, font=FONT, fg=LABEL_COLOR)
website_label.grid(column=0, row=1, sticky=W)

# Label for Email/Username
email_label = Label(text="Email/Username", bg=WINDOW_BG, padx=20, font=FONT, fg=LABEL_COLOR)
email_label.grid(column=0, row=2, sticky=W)

# Label for Password
password_label = Label(text="Password", bg=WINDOW_BG, padx=20, font=FONT, fg=LABEL_COLOR)
password_label.grid(column=0, row=3,sticky=W)
window.grid_columnconfigure(1, weight=1)

# Entry widgets
website_entry = Entry(width=30, bg=FIELD_COLORS, fg=FIELD_FONT_COLOR, font=FONT)
website_entry.insert(END, string="")
website_entry.grid(column=1, row=1)
website_entry.focus()

email_entry = Entry(width=30, bg=FIELD_COLORS, fg=FIELD_FONT_COLOR, font=FONT)
email_entry.insert(END, string="")
email_entry.grid(column=1, row=2)
email_entry.insert(0, "example@email.com")

password_entry = Entry(width=30, bg=FIELD_COLORS, fg=FIELD_FONT_COLOR, font=FONT)
password_entry.insert(END, string="")
password_entry.grid(column=1, row=3)

# Buttons
search_button = Button(text="Search", padx=95, font=FONT, command=search_password)
search_button.grid(column=3, row=1)

generate_button = Button(text="Generate Password", command=get_password, font=FONT)
generate_button.grid(column=3, row=3)

add_button = Button(text="Add", width=36, command=save_password, font=FONT)
add_button.grid(column=1, row=5, columnspan=2, sticky=W)

# Dummy widget for an empty row
dummy_label = Label(bg=WINDOW_BG)
dummy_label.grid(column=0, row=4, sticky=W)

# ---------------------------- MAIN LOOP ------------------------------- #
window.mainloop()
