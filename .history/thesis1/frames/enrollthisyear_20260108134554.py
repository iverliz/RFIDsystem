import tkinter as tk 
import os 
import sys


BIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BIN_DIR)

from utils.database import db_connect

class EnrollThisYear(tk.Frame):


