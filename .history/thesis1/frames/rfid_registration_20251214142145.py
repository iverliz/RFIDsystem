import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class RfidRegistration(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - RFID REGISTRATION")
        root.geometry("1350x700+0+0")

        self.pack(fill="both", expand=True)

        # ================= SEARCH BAR (TOP LEFT) =================
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


    #left fetcher form information 
        height = 500
        width = 500
        self.fetcher_frame = tk.Frame(self, width=self.width, height=self.height, bg="white", bd=2, relief="groove")
        self.fetcher_frame.place(x=675 + (675 - width)//2, y=(700 - height)//2)
        self.fetcher_frame.pack_propagate(False)

        title = tk.Label(self.fetcher_frame, text="", font=("Arial", 24, "bold"), bg="white", fg="#0047AB")


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
