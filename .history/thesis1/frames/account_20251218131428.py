import tkinter as tk 




class account(tk.Frame):
    def __init__(self, root):
      super().__init__(root, bg="#b2e5ed")
      self.root = root

      root.title("RFID MANAGEMENT SYSTEM - ACCOUNT LIST")
      root.geometry("1350x700+0+0")
      self.pack(fill="both", expand=False)


      # button 

      self.search_var = tk.StringVar()
      self.search_entry = tk.Entry(self, textvariable=self.search_var, width=30,
                                     font=("Arial", 15), fg="gray")
      self.search_entry.place(x=20, y=20)
        self.search_entry.insert(0, "Search")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)
        tk.Button(self, text="🔍", command=self.search).place(x=260, y=20)

