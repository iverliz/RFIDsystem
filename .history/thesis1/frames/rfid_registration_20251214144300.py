import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class RfidRegistration(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - RFID REGISTRATION")
        root.geometry("1350x700+0+0")

        self.pack(fill="both", expand=True)

        # ================= SEARCH BAR =================
        self.search_var = tk.StringVar()

        self.search_entry = tk.Entry(
            self,
            textvariable=self.search_var,
            width=30,
            font=("Arial", 15),
            fg="gray"
        )
        self.search_entry.place(x=20, y=20)

        self.search_entry.insert(0, "Search")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)

        tk.Button(self, text="🔍", command=self.search).place(x=260, y=20)

        # ================= FETCHER FRAME =================
        width = 500
        height = 500

        self.fetcher_frame = tk.Frame(
            self,
            width=width,
            height=height,
            bg="white",
            bd=2,
            relief="groove"
        )

        self.fetcher_frame.place(
            x=30,
            y=(700 - height) // 2
        )

        self.fetcher_frame.pack_propagate(False)

        title = tk.Label(
            self.fetcher_frame,
            text="FETCHER INFORMATION",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#0047AB"
        )
        title.place(x=20, y=20)

        # ================= RFID SECTION =================
        tk.Label(
            self.fetcher_frame,
            text="RFID:",
            font=("Arial", 14),
            bg="white"
        ).place(x=20, y=80)

        # >>> RFID Entry <<<
        self.rfid_var = tk.StringVar()
        self.rfid_entry = tk.Entry(
            self.fetcher_frame,
            textvariable=self.rfid_var,
            font=("Arial", 14),
            width=30
        )
        self.rfid_entry.place(x=90, y=80)

        # Bind Enter key (RFID scan ends with Enter)
        self.rfid_entry.bind("<Return>", self.on_rfid_scanned)

        # Auto-focus so scanner works immediately
        self.rfid_entry.focus()

        tk.Label(
            self.fetcher_frame,
            text="Name:",
            font=("Arial", 14),
            bg="white"
        ).place(x=20, y=120)

# ================= NAME =================
        tk.Label(
    self.fetcher_frame,
    text="Name:",
    font=("Arial", 14),
    bg="white"
).place(x=20, y=120)

        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(
    self.fetcher_frame,
    textvariable=self.name_var,
    font=("Arial", 14),
    width=30
)
        self.name_entry.place(x=90, y=120)

# ================= ADDRESS =================
        tk.Label(
    self.fetcher_frame,
    text="Address:",
    font=("Arial", 14),
    bg="white"
).place(x=20, y=160)

        self.address_var = tk.StringVar()
        self.address_entry = tk.Entry(
    self.fetcher_frame,
    textvariable=self.address_var,
    font=("Arial", 14),
    width=30
)
        self.address_entry.place(x=140, y=160)

# ================= CONTACT =================
        tk.Label(
    self.fetcher_frame,
    text="Contact Number:",
    font=("Arial", 14),
    bg="white"
).place(x=20, y=200)

        self.contact_int_var = tk.StringVar()
        self.contact_entry = tk.Entry(
    self.fetcher_frame,
    textvariable=self.contact_int_var,
    font=("Arial", 14),
    width=30
)
self.contact_entry.place(x=170, y=200)

    # ================= RFID FUNCTION =================
    def on_rfid_scanned(self, event):
        rfid_tag = self.rfid_var.get().strip()

        if not rfid_tag:
            return

        print("RFID scanned:", rfid_tag)

        # Example: show confirmation
        messagebox.showinfo("RFID Scanned", f"Tag ID: {rfid_tag}")

        # Clear for next scan
        self.rfid_var.set("")

        # Keep focus for next scan
        self.rfid_entry.focus()

    # ================= PLACEHOLDER FUNCTIONS =================
    def clear_placeholder(self, event):
        if self.search_entry.get() == "Search":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def add_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search")
            self.search_entry.config(fg="gray")

    # ================= SEARCH FUNCTION =================
    def search(self):
        value = self.search_var.get()
        if value != "Search":
            print("Searching for:", value)


if __name__ == "__main__":
    root = tk.Tk()
    app = RfidRegistration(root)
    root.mainloop()
