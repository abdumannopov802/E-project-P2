import openpyxl
import pandas as pd

workbook = openpyxl.Workbook()

class Excel:
    def __init__(self, filename):
        self.filename = filename
        self.workbook = openpyxl.Workbook()
        self.sheet = self.workbook.active

    def create(self, data):
        try:
            for row in data:
                self.sheet.append(row)
        except Exception as error:
            return error
        return "Successfully created"

    def append(self, data):
        try:
            for row in data:
                self.sheet.append(row)
        except Exception as error:
            return error
        return "Successfully appended"

    def save(self):
        try:
            self.workbook.save(self.filename)
        except Exception as error:
            return error
        return "Workbook saved successfully"