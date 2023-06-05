import csv
import time
import pickle
import os.path
import tkinter
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC

print(messagebox.askyesnocancel(title="Label site", message="Does this site use an anti adblocker?", default="no"))