######################## Start Import Modules ##################################
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
from PyQt5.uic import loadUiType , loadUi
import datetime
import sqlite3
from xlrd import *
from xlsxwriter import *
import os
import csv
import json
############################# End Import Modules ##################################

# function for justify the paths of externals files
def uiPaths(paths):
    try:
        basePath=sys._MEIPASS
    except Exception:
        basePath=os.path.abspath(".")
    return os.path.join(basePath,paths)

# returning the classes for setupUi
ui,_=loadUiType(uiPaths("Ui/Lib3.ui"))
ui2,_=loadUiType(uiPaths("Ui/Borrow_List.ui"))
ui3,_=loadUiType(uiPaths("Ui/export.ui"))
ui4,_=loadUiType(uiPaths("Ui/devloper.ui"))
ui5,_=loadUiType(uiPaths("Ui/import.ui"))
ui6,_=loadUiType(uiPaths("Ui/delete.ui"))

# borrow list class to show the borrow list window
class Borrowed_List(QDialog,ui2):
    def __init__(self,parent):
        super(Borrowed_List, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint , False)
        self.setWindowTitle("List")
        self.setWindowIcon(QIcon("Ui/Icons/b.png"))
    def item_insert(self,data):
        if data:
            self.tableWidget.setRowCount(0)
            self.tableWidget.insertRow(0)
            for row, data_lis in enumerate(data):
                for column, items in enumerate(data_lis[1:]):
                    self.tableWidget.setItem(row, column, QTableWidgetItem(str(items)))
                    column += 1
                row_pos = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row_pos)

# class for devloper window
class Devloper(QDialog,ui4):
    def __init__(self,parent):
        super(Devloper,self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon(uiPaths("Ui/Icons/devloper.png")))
        self.setWindowTitle("Devloper Details !!!")
        self.setWindowFlag(Qt.WindowContextHelpButtonHint , False)

# class for delete window
class Delete(QDialog,ui6):
    def __init__(self,parent):
        super(Delete,self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.check)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint , False)
        self.setWindowTitle("Delete All")
        self.setWindowIcon(QIcon("Ui/Icons/delete..png"))
    def check(self): # asking again to makesure deleting all data from databases
        mess = QMessageBox.question(self, "Sure?", "<h2>Are You Sure To Remove?</h2>", QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No)
        if mess == QMessageBox.Yes:
            self.deleteall()
    def deleteall(self):
        tex=self.comboBox.currentText()
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        if tex=="Books":
            self.crsor.execute("DELETE from Books")
        elif tex=="Author":
            self.crsor.execute("DELETE from Author")
        elif tex=="Members":
            self.crsor.execute("DELETE from Members")
        elif tex=="Cetagory":
            self.crsor.execute("DELETE from Cetagorys")
        elif tex=="Publisher":
            self.crsor.execute("DELETE from Publisher")
        elif tex=="Returns":
            self.crsor.execute("DELETE from Returns")
        elif tex=="Borrow":
            self.crsor.execute("DELETE from Borrows")
        self.db.commit()
        mess = QMessageBox.question(self, "Removed", "<h2>Successfully Removed!!</h2>", QMessageBox.Ok)
        self.db.close()

# class for import window
class import_(QDialog,ui5):
    def __init__(self,parent):
        self.parent=parent
        super(import_,self).__init__(parent)
        self.setupUi(self)
        self.Handle_Buttons()
        self.fileextension=""
        self.setWindowIcon(QIcon("Ui/Icons/import.png"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint , False)
        self.setWindowTitle("Import")
    def Handle_Buttons(self):
        self.openbtn.clicked.connect(self.openFileNameDialog)
        self.importbtn.clicked.connect(self.import_click)
    def import_click(self):
        comboText=self.comboBox.currentText()
        if self.fileextension == 'csv':
            self.readCsv(comboText)
        # #print(self.checkBox_2.isChecked(),self.checkBox.isChecked())
    #########################################################################
    ############ Rrad CSV @##################################################
    def readCsv(self,tablename):
        fileName=self.lineEdit.text()
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        self.crsor.execute(f"select * from {tablename}")
        #print(self.crsor.fetchall())
        columns=[]
        rows=[]
        with open(fileName,'r',encoding="utf-8") as csvfile:
            csvRead=csv.reader(csvfile,delimiter=",")
            line=0
            #print("X")
            for row in csvRead:
                #print(row)
                if line==0:
                    for cols in row:
                        columns.append(cols)
                        line+=1
                else:
                    if row:
                        rows.append(tuple(row[1:]))
                    line+=1
            csvfile.close()
        coll = self.crsor.execute(f"SELECT * FROM {tablename} LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        #print(columns)
        #print(columns_Name)
        if columns != columns_Name:
            QMessageBox.question(self, "Not Matching!", f"<h2>Columns are not matched!!</h2><br><h3>Please Change File. File is not comfirtable for database.</h3>", QMessageBox.Ok)
            return
        #print(rows)
        if tablename=="Books":
            self.import_Books(rows)
        elif tablename=="Members":
            self.import_Members(rows)
        elif tablename=="Cetagorys":
            self.import_cetagory(rows)
        elif tablename=="Author":
            self.import_author(rows)
        elif tablename=="Publisher":
            self.import_publisher(rows)
        QMessageBox.question(self, "Imported", "<h2>Successfully Import!!</h2>", QMessageBox.Ok)
    def openFileNameDialog(self):
        fileName = QFileDialog.getOpenFileName(self, 'Open file',
         os.path.abspath("."),"Data File Formate (*.csv)")
        if fileName:
            if "csv" in fileName[0][-5:]:
                self.fileextension="csv"
            elif "xlsx" in fileName[0][-5:]:
                self.fileextension="xlsx"
            elif "json" in fileName[0][-5:]:
                self.fileextension="json"
            self.lineEdit.setText(fileName[0])
    def import_Books(self,data):
        try:
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            if self.checkBox.isChecked():
                self.crsor.execute(f"DELETE from Books")
                self.db.commit()
            self.crsor.execute("select Book_Title, Book_Count, Book_Author, Book_Cetagory,Book_Publisher, Book_Dicription from Books")
            allBook=[tuple(map(str,i)) for i in self.crsor.fetchall()]
            #print(allBook,"a")
            for r in data:
                if r not in allBook and ("") not in r:
                    #print(r)
                    self.crsor.execute("""
                INSERT INTO Books(Book_Title, Book_Count, Book_Author, Book_Cetagory,Book_Publisher, Book_Dicription)
                VALUES(?,?,?,?,?,?)
                """,r)
                self.db.commit()
            self.crsor.execute("select Book_Cetagory from Books")
            cetagorisB=[i[0] for i in self.crsor.fetchall()]
            self.crsor.execute("select Book_Author from Books")
            authorB=[i[0] for i in self.crsor.fetchall()]
            self.crsor.execute("select Book_Publisher from Books")
            publisherB=[i[0] for i in self.crsor.fetchall()]

            self.crsor.execute("select Cetagory_Name from Cetagorys")
            cetagoris=[i[0] for i in self.crsor.fetchall()]
            self.crsor.execute("select Author_Name from Author")
            author=[i[0] for i in self.crsor.fetchall()]
            self.crsor.execute("select Publisher_Name from Publisher")
            publisher=[i[0] for i in self.crsor.fetchall()]
            #print("enter cetagory")
            #print(cetagorisB,cetagoris)
            for ceta in cetagorisB:
                if ceta not in cetagoris and ceta!="":
                    #print(ceta)
                    self.crsor.execute("""
                INSERT INTO Cetagorys(Cetagory_Name)
                VALUES(?)
                """,(ceta,))
                self.db.commit()
                self.crsor.execute("select Cetagory_Name from Cetagorys")
                cetagoris=[i[0] for i in self.crsor.fetchall()]
            for aut in authorB:
                if aut not in author and aut!="":
                    self.crsor.execute("""
                INSERT INTO Author(Author_Name)
                VALUES(?)
                """,(aut,))
                self.db.commit()
                self.crsor.execute("select Author_Name from Author")
                author=[i[0] for i in self.crsor.fetchall()]

            for pub in publisherB:
                if pub not in publisher and pub!="":
                    self.crsor.execute("""
                INSERT INTO Publisher(Publisher_Name)
                VALUES(?)
                """,(pub,))
                self.db.commit()
                self.crsor.execute("select Publisher_Name from Publisher")
                publisher=[i[0] for i in self.crsor.fetchall()]
        except Exception as e:
            QMessageBox.question(self, "None selected",e, QMessageBox.Ok)
        else:
            self.db.close()
    def import_Members(self,data):
        try:
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            if self.checkBox.isChecked():
                self.crsor.execute(f"DELETE from Members")
                self.db.commit()
            self.crsor.execute("select Name,Phone,Email,Class,Section,Roll,Address from Members")
            allmembers=[tuple(map(str,i)) for i in self.crsor.fetchall()]
            #print(allmembers,"a")
            for r in data:
                if r not in allmembers and ("") not in r:
                    #print(r)
                    self.crsor.execute("""
                    INSERT INTO Members(Name,Phone,Email,Class,Section,Roll,Address)
                    VALUES(?,?,?,?,?,?,?);
                    """,r)
                self.db.commit()
        except Exception as e:
            QMessageBox.question(self, "Error", e, QMessageBox.Ok)
    def import_cetagory(self,data):
        try:
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            if self.checkBox.isChecked():
                self.crsor.execute(f"DELETE from Cetagorys")
                self.db.commit()
            self.crsor.execute("select Cetagory_Name from Cetagorys")
            allCeta=[tuple(map(str,i)) for i in self.crsor.fetchall()]
            #print(allCeta,"a")
            for r in data:
                if r not in allCeta and ("") not in r:
                    #print(r)
                    self.crsor.execute("""
                INSERT INTO Cetagorys(Cetagory_Name)
                VALUES(?)
                """,r)
                self.db.commit()
        except Exception as e:
            QMessageBox.question(self, "Error", e, QMessageBox.Ok)
        else:
            self.db.close()
    def import_author(self,data):
        try:
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            if self.checkBox.isChecked():
                self.crsor.execute(f"DELETE from Author")
                self.db.commit()
            self.crsor.execute("select Author_Name from Author")
            allaut=[tuple(map(str,i)) for i in self.crsor.fetchall()]
            #print(allaut,"a")
            for r in data:
                if r not in allaut and ("") not in r:
                    #print(r)
                    self.crsor.execute("""
                INSERT INTO Author(Author_Name)
                VALUES(?)
                """,r)
                self.db.commit()
        except Exception as e:
            QMessageBox.question(self, "Error", e, QMessageBox.Ok)
        else:
            self.db.close()
    def import_publisher(self,data):
        try:
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            if self.checkBox.isChecked():
                self.crsor.execute(f"DELETE from Publisher")
                self.db.commit()
            self.crsor.execute("select Publisher_Name from Publisher")
            allpub=[tuple(map(str,i)) for i in self.crsor.fetchall()]
            #print(allpub,"a")
            for r in data:
                if r not in allpub and ("") not in r:
                    #print(r)
                    self.crsor.execute("""
                INSERT INTO Publisher(Publisher_Name)
                VALUES(?)
                """,r)
                self.db.commit()
        except Exception as e:
            QMessageBox.question(self, "Error", e, QMessageBox.Ok)
        else:
            self.db.close()
    def MessgBoxRemoveData(self):
        mess = QMessageBox.question(self, "None selected", f"<h2>You need to select one option from checkbox</h2><br><h3>Please Select anyone</h3>", QMessageBox.Ok)

# class for export window
class export_(QDialog,ui3):
    def __init__(self,parent):
        super(export_, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Export Data")
        self.hanndelButton()
        self.dateEdit.setDate(QDate.currentDate())
        if not os.path.exists("Export"):
            os.mkdir("Export")
        if not os.path.exists("Export/Execl"):
            os.mkdir("Export/Execl")
        if not os.path.exists("Export/Csv"):
            os.mkdir("Export/Csv")
        if not os.path.exists("Export/Json"):
            os.mkdir("Export/Json")

        self.exPath="Export/Execl"
        self.csPath="Export/Csv"
        self.jsPath="Export/Json"
        self.setWindowIcon(QIcon(uiPaths("Ui/Icons/export.png")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint , False)

    def deletdata(self,tablename):
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"DELETE FROM {tablename}")
        self.db.commit()
        self.db.close()
        self.label_5.setText(f"Return List Datas are Exported and Removed")
    def MessgBoxRemoveData(self,tablename):
        mess = QMessageBox.question(self, "Remove Data", f"<h2>Are you want to export and remove all return book list data</h2><br><h5>Application Need to Restart</h5>", QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        if mess == QMessageBox.Yes:
            self.deletdata(tablename)
            qApp.exit(-123)
        else:
            pass
    def hanndelButton(self):
        self.pushButton.clicked.connect(self.on_export_click)
    def all_books_ex(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Books LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Books')
        wb=Workbook(f'{self.exPath}/allBooks_ex{date}.xlsx')
        sheet1=wb.add_worksheet()
        for p,i in enumerate(columns_Name):
            sheet1.write(0,p,i)
        row=1
        for items in self.crsor.fetchall():
            for cols,item in enumerate(items):
                sheet1.write(row,cols,item)
            row+=1
        wb.close()
        self.db.close()
        self.label_5.setText(f"All Books are Exported at {date} in Execl formate")
    def all_books_cs(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Books LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Books')
        with open(f'{self.csPath}/allBooks_cs{date}.csv', 'w', encoding="utf-8") as fille:
            csv_out=csv.writer(fille)
            csv_out.writerow(columns_Name)
            for item in self.crsor.fetchall():
                csv_out.writerow(item)
            fille.close()
            self.db.close()
        self.label_5.setText(f"All Books are Exported at {date} in Csv formate")
    def all_books_js(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Books LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Books')
        books=self.crsor.fetchall()
        tmp={}
        data=[]
        for n in range(len(books)):
            for item in zip(columns_Name,books[n]):
                tmp[item[0]]=item[1]
            data.append(tmp)
            tmp={}
        with open(f'{self.jsPath}/allBooks_js{date}.json','w') as fille:
            fille.write(json.dumps(data))
            fille.close()
            self.db.close()
        self.label_5.setText(f"All Books are Exported at {date} in Json formate")

    def all_member_ex(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Members LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Members')
        wb=Workbook(f'{self.exPath}/allMember_ex{date}.xlsx')
        sheet1=wb.add_worksheet()
        for p,i in enumerate(columns_Name):
            sheet1.write(0,p,i)
        row=1
        for items in self.crsor.fetchall():
            for cols,item in enumerate(items):
                sheet1.write(row,cols,item)
            row+=1
        wb.close()
        self.db.close()
        self.label_5.setText(f"All Member are Exported at {date} in Execl formate")
    def all_member_cs(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Members LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Members')
        with open(f'{self.csPath}/allMember_cs{date}.csv' , 'w', encoding="utf-8") as fille:
            csv_out=csv.writer(fille)
            csv_out.writerow(columns_Name)
            for item in self.crsor.fetchall():
                csv_out.writerow(item)
            fille.close()
            self.db.close()
        self.label_5.setText(f"All Member are Exported at {date} in Csv formate")
    def all_member_js(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Members LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Members')
        books=self.crsor.fetchall()
        tmp={}
        data=[]
        for n in range(len(books)):
            for item in zip(columns_Name,books[n]):
                tmp[item[0]]=item[1]
            data.append(tmp)
            tmp={}
        with open(f'{self.jsPath}/allMember_js{date}.json','w') as fille:
            fille.write(json.dumps(data))
            fille.close()
            self.db.close()
        self.label_5.setText(f"All Member are Exported at {date} in Json formate")

    def returnBook_ex(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Returns LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Returns')
        wb=Workbook(f'{self.exPath}/returnBook_ex{date}.xlsx')
        sheet1=wb.add_worksheet()
        for p,i in enumerate(columns_Name):
            sheet1.write(0,p,i)
        row=1
        for items in self.crsor.fetchall():
            for cols,item in enumerate(items):
                sheet1.write(row,cols,item)
            row+=1
        wb.close()
        self.db.close()
        self.MessgBoxRemoveData("Returns")
        self.label_5.setText(f"Return Books are Exported at {date} in Execl formate")
    def returnBook_cs(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Returns LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Returns')
        with open(f'{self.csPath}/returnBook_cs{date}.csv' , 'w', encoding="utf-8") as fille:
            csv_out=csv.writer(fille)
            csv_out.writerow(columns_Name)
            for item in self.crsor.fetchall():
                csv_out.writerow(item)
            fille.close()
            self.db.close()
        self.MessgBoxRemoveData("Returns")
        self.label_5.setText(f"Return Books are Exported at {date} in Csv formate")
    def returnBook_js(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Returns LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Returns')
        books=self.crsor.fetchall()
        tmp={}
        data=[]
        for n in range(len(books)):
            for item in zip(columns_Name,books[n]):
                tmp[item[0]]=item[1]
            data.append(tmp)
            tmp={}
        with open(f'{self.jsPath}/returnBook_js{date}.json','w') as fille:
            fille.write(json.dumps(data))
            fille.close()
            self.db.close()
        self.MessgBoxRemoveData("Returns")
        self.label_5.setText(f"Return Books are Exported at {date} in Json formate")

    def borrowBook_ex(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Borrows LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Borrows')
        wb=Workbook(f'{self.exPath}/borrowBook_ex{date}.xlsx')
        sheet1=wb.add_worksheet()
        for p,i in enumerate(columns_Name):
            sheet1.write(0,p,i)
        row=1
        for items in self.crsor.fetchall():
            for cols,item in enumerate(items):
                sheet1.write(row,cols,item)
            row+=1
        wb.close()
        self.db.close()
        self.label_5.setText(f"Borrow Book are Exported at {date} in Execl formate")
    def borrowBook_cs(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Borrows LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Borrows')
        with open(f'{self.csPath}/borrowBook_cs{date}.csv' , 'w', encoding="utf-8") as fille:
            csv_out=csv.writer(fille)
            csv_out.writerow(columns_Name)
            for item in self.crsor.fetchall():
                csv_out.writerow(item)
            fille.close()
            self.db.close()
        self.label_5.setText(f"Borrow Books are Exported at {date} in Csv formate")
    def borrowBook_js(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Borrows LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Borrows')
        books=self.crsor.fetchall()
        tmp={}
        data=[]
        for n in range(len(books)):
            for item in zip(columns_Name,books[n]):
                tmp[item[0]]=item[1]
            data.append(tmp)
            tmp={}
        with open(f'{self.jsPath}/borrowBook_js{date}.json','w') as fille:
            fille.write(json.dumps(data))
            fille.close()
            self.db.close()
        self.label_5.setText(f"Borrow Books are Exported at {date} in Json formate")

    def allCetagory_ex(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Cetagorys LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Cetagorys')
        wb=Workbook(f'{self.exPath}/allCetagory_ex{date}.xlsx')
        sheet1=wb.add_worksheet()
        for p,i in enumerate(columns_Name):
            sheet1.write(0,p,i)
        row=1
        for items in self.crsor.fetchall():
            for cols,item in enumerate(items):
                sheet1.write(row,cols,item)
            row+=1
        wb.close()
        self.db.close()
        self.label_5.setText(f"Book cetagory are Exported at {date} in Execl formate")
    def allCetagory_cs(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Cetagorys LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Cetagorys')
        with open(f'{self.csPath}/allCetagory_cs{date}.csv' , 'w', encoding="utf-8") as fille:
            csv_out=csv.writer(fille)
            csv_out.writerow(columns_Name)
            for item in self.crsor.fetchall():
                csv_out.writerow(item)
            fille.close()
            self.db.close()
        self.label_5.setText(f"Books cetagory are Exported at {date} in Csv formate")
    def allCetagory_js(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Cetagorys LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Cetagorys')
        books=self.crsor.fetchall()
        tmp={}
        data=[]
        for n in range(len(books)):
            for item in zip(columns_Name,books[n]):
                tmp[item[0]]=item[1]
            data.append(tmp)
            tmp={}
        with open(f'{self.jsPath}/allCetagory_js{date}.json','w') as fille:
            fille.write(json.dumps(data))
            fille.close()
            self.db.close()
        self.label_5.setText(f"Books cetagory are Exported at {date} in Json formate")

    def allAuthor_ex(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Author LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Author')
        wb=Workbook(f'{self.exPath}/allAuthor_ex{date}.xlsx')
        sheet1=wb.add_worksheet()
        for p,i in enumerate(columns_Name):
            sheet1.write(0,p,i)
        row=1
        for items in self.crsor.fetchall():
            for cols,item in enumerate(items):
                sheet1.write(row,cols,item)
            row+=1
        wb.close()
        self.db.close()
        self.label_5.setText(f"Book cetagory are Exported at {date} in Execl formate")
    def allAuthor_cs(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Author LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Author')
        with open(f'{self.csPath}/allAuthor_cs{date}.csv' , 'w', encoding="utf-8") as fille:
            csv_out=csv.writer(fille)
            csv_out.writerow(columns_Name)
            for item in self.crsor.fetchall():
                csv_out.writerow(item)
            fille.close()
            self.db.close()
        self.label_5.setText(f"Books author are Exported at {date} in Csv formate")
    def allAuthor_js(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Author LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Author')
        books=self.crsor.fetchall()
        tmp={}
        data=[]
        for n in range(len(books)):
            for item in zip(columns_Name,books[n]):
                tmp[item[0]]=item[1]
            data.append(tmp)
            tmp={}
        with open(f'{self.jsPath}/allAuthor_js{date}.json','w') as fille:
            fille.write(json.dumps(data))
            fille.close()
            self.db.close()
        self.label_5.setText(f"Books Athour are Exported at {date} in Json formate")

    def allPublisher_ex(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Publisher LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Publisher')
        wb=Workbook(f'{self.exPath}/allPublisher_ex{date}.xlsx')
        sheet1=wb.add_worksheet()
        for p,i in enumerate(columns_Name):
            sheet1.write(0,p,i)
        row=1
        for items in self.crsor.fetchall():
            for cols,item in enumerate(items):
                sheet1.write(row,cols,item)
            row+=1
        wb.close()
        self.db.close()
        self.label_5.setText(f"Book publisher are Exported at {date} in Execl formate")
    def allPublisher_cs(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Publisher LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Publisher')
        with open(f'{self.csPath}/allPublisher_cs{date}.csv' , 'w', encoding="utf-8") as fille:
            csv_out=csv.writer(fille)
            csv_out.writerow(columns_Name)
            for item in self.crsor.fetchall():
                csv_out.writerow(item)
            fille.close()
            self.db.close()
        self.label_5.setText(f"Books publisher are Exported at {date} in Csv formate")
    def allPublisher_js(self):
        date=f"{self.dateEdit.date().day()}-{self.dateEdit.date().month()}-{self.dateEdit.date().year()}"
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        coll = self.crsor.execute(f"SELECT * FROM Publisher LIMIT 0")
        columns_Name = [c[0] for c in self.crsor.description]
        self.crsor.execute('select * from Publisher')
        books=self.crsor.fetchall()
        tmp={}
        data=[]
        for n in range(len(books)):
            for item in zip(columns_Name,books[n]):
                tmp[item[0]]=item[1]
            data.append(tmp)
            tmp={}
        with open(f'{self.jsPath}/allPublisher_js{date}.json','w') as fille:
            fille.write(json.dumps(data))
            fille.close()
            self.db.close()
        self.label_5.setText(f"Books publisher are Exported at {date} in Json formate")


    def on_export_click(self):
        fileType=self.comboBox_2.currentText()
        data_list=self.comboBox.currentText()
        qdate=self.dateEdit.date()
        if data_list=="All Books":
            if fileType=="Execl":
                self.all_books_ex()
            elif fileType=="Csv":
                self.all_books_cs()
            elif fileType=="Json":
                self.all_books_js()
        elif data_list=="All Members":
            if fileType=="Execl":
                self.all_member_ex()
            elif fileType=="Csv":
                self.all_member_cs()
            elif fileType=="Json":
                self.all_member_js()
        elif data_list=="Return Books":
            if fileType=="Execl":
                self.returnBook_ex()
            elif fileType=="Csv":
                self.returnBook_cs()
            elif fileType=="Json":
                self.returnBook_js()
        elif data_list=="Borrwed Books":
            if fileType=="Execl":
                self.borrowBook_ex()
            elif fileType=="Csv":
                self.borrowBook_cs()
            elif fileType=="Json":
                self.borrowBook_js()
        elif data_list=="All Cetagory":
            if fileType=="Execl":
                self.allCetagory_ex()
            elif fileType=="Csv":
                self.allCetagory_cs()
            elif fileType=="Json":
                self.allCetagory_js()

        elif data_list=="All Author":
            if fileType=="Execl":
                self.allAuthor_ex()
            elif fileType=="Csv":
                self.allAuthor_cs()
            elif fileType=="Json":
                self.allAuthor_js()
        elif data_list=="All Publisher":
            if fileType=="Execl":
                self.allPublisher_ex()
            elif fileType=="Csv":
                self.allPublisher_cs()
            elif fileType=="Json":
                self.allPublisher_js()


class MainApp(QMainWindow, ui, import_):
    def __init__(self):
        QMainWindow.__init__(self)
        if not os.path.exists(uiPaths("DataBases")):
            os.mkdir(uiPaths("DataBases"))
        if not os.path.exists("DataBases/library"):
            with open("DataBases/library",'w') as f:
                f.close()
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            self.crsor.execute('''
                CREATE TABLE `Author` (
	`Id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`Author_Name`	TEXT
);
            ''')
            self.db.commit()
            self.crsor.execute('''
                CREATE TABLE "Books" ( `Id` INTEGER NOT NULL, `Book_Title` TEXT, `Book_Count` INTEGER, `Book_Author` TEXT, `Book_Cetagory` TEXT, `Book_Publisher` TEXT, `Book_Dicription` TEXT, PRIMARY KEY(`Id`) )
            ''')
            self.db.commit()
            self.crsor.execute('''
                CREATE TABLE "Borrows" ( `Id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Member` TEXT, `Class` TEXT, `Section` TEXT, `Roll` TEXT, `Book` TEXT, `Day` INTEGER, `From_` TEXT, `To_` TEXT )
            ''')
            self.db.commit()
            self.crsor.execute('''
                CREATE TABLE "Cetagorys" ( `Id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Cetagory_Name` TEXT )
            ''')
            self.db.commit()
            self.crsor.execute('''
                CREATE TABLE "Members" ( `Id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Name` TEXT, `Phone` INTEGER, `Email` TEXT, `Class` TEXT, `Section` TEXT, `Roll` TEXT, `Address` TEXT )
            ''')
            self.db.commit()
            self.crsor.execute('''
                CREATE TABLE "Publisher" ( `Id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Publisher_Name` TEXT )
            ''')
            self.db.commit()
            self.crsor.execute('''
                CREATE TABLE "Returns" ( `Id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Member` TEXT, `Class` TEXT, `Section` TEXT, `Roll` TEXT, `Book` TEXT, `Day` INTEGER, `From_` TEXT, `To_` TEXT, `Return_` TEXT )
            ''')
            self.db.commit()
            self.db.close()

        self.setupUi(self)
        self.showing=False
        self.lis2=set()
        self.setWindowTitle("Root")
        self.Handle_Buttons()
        self.Handle_Ui_Changes()
        self.Show_Cetagory_TABLE()
        self.Show_Author_TABLE()
        self.Show_Publisher_TABLE()
        self.Show_Cetagory_Combo()
        self.Show_Author_Combo()
        self.Show_Publisher_Combo()
        self.Show_All_Books()
        self.Show_All_Users()
        self.Show_Borrow_Books()
        self.Show_Taking_Books()
        self.bookSearch.hide()
        self.listWidget.hide()
        def_style=open(uiPaths("themes/def_.css"),'r')
        self.setStyleSheet(def_style.read())
        self.setWindowIcon(QIcon("Ui/Icons/b.png"))
    def uiPaths(self,paths):
        try:
            basePath=sys._MEIPASS
        except Exception:
            basePath=os.path.abspath(".")
        return os.path.join(basePath,paths)
    def Handle_Ui_Changes(self):
        self.Hide_Theme()
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.tabBar().setVisible(False)
        self.lineEdit_30.textChanged.connect(self.searchBook)
        self.lineEdit_5.textChanged.connect(self.searchAnotherBook)
        self.lineEdit_33.textChanged.connect(self.ontextChange)
        self.comboBox_3.currentIndexChanged.connect(self.OnChangeItem)
        self.comboBox_4.currentIndexChanged.connect(self.OnChangeItem)
        self.comboBox.currentIndexChanged.connect(self.onBorrowReurnComboChange)
        self.bookSearch.itemClicked.connect(self.onSearchBookItemClick)
        self.listWidget.itemClicked.connect(self.onClickAnotherSearchBookItem)
    def Handle_Buttons(self):
        self.pushButton_6.clicked.connect(self.Show_Theme)
        self.pushButton_2.clicked.connect(self.Open_Books_Tab)
        self.pushButton_4.clicked.connect(self.Open_Member_Tab)
        self.pushButton_3.clicked.connect(self.Open_Setting_Tab)
        self.pushButton.clicked.connect(self.Open_Day_Book_Brrow)

        self.pushButton_8.clicked.connect(self.Add_New_Books)
        self.pushButton_16.clicked.connect(self.Add_Cetagory)
        self.pushButton_15.clicked.connect(self.Delete_Cetagory)
        self.pushButton_18.clicked.connect(self.Add_Author)
        self.pushButton_17.clicked.connect(self.Delete_Author)
        self.pushButton_20.clicked.connect(self.Add_Publisher)
        self.pushButton_19.clicked.connect(self.Delete_Publisher)
        # self.pushButton_10.clicked.connect(self.Search_Books)
        self.pushButton_9.clicked.connect(self.Edit_Books_Details)
        self.pushButton_11.clicked.connect(self.Delete_Books)
        self.pushButton_21.clicked.connect(self.delete)
        self.pushButton_7.clicked.connect(self.Add_Users)
        self.pushButton_26.clicked.connect(self.Search_Users)
        self.pushButton_13.clicked.connect(self.Delete_Users)
        self.pushButton_14.clicked.connect(self.Edit_User_Info)


        self.pushButton_22.clicked.connect(self.dark_blue)
        self.pushButton_23.clicked.connect(self.dark_)

        self.pushButton_5.clicked.connect(self.Add_Book_Borrow)

        self.pushButton_10.clicked.connect(self.export_file)
        self.pushButton_25.clicked.connect(self.show_Devloper)
        self.pushButton_12.clicked.connect(self.import_file)
    ###################################################################################
    ######################## Handle Search book and member ############################
    def searchBook(self,text):
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        self.crsor.execute('select Book_Title from Books')
        books=[j[0] for j in self.crsor.fetchall()]
        textPos=len(text)
        if textPos==0:
            self.bookSearch.clear()
            self.listWidget.clear()
            self.lis2.clear()
            self.bookSearch.hide()
            self.listWidget.hide()
            return 0
        if textPos==1:
            self.lis2.clear()
            for i in books:
                if text==i[0]:
                    if i not in self.lis2:
                        self.lis2.add(i)
        else:
            self.lis2.clear()
            for i in books:
                if i[0:textPos] == text:
                    if i not in self.lis2:
                        self.lis2.add(i)


        self.bookSearch.clear()
        self.listWidget.clear()
        lis2=list(self.lis2)
        lis2.sort()

        self.bookSearch.addItems(lis2)
        self.listWidget.addItems(lis2)
        self.bookSearch.show()
        self.listWidget.show()
        if len(self.lis2)==0:
            self.bookSearch.clear()
            self.listWidget.clear()
            self.bookSearch.addItem("Not Found")
            self.listWidget.addItem("Not Found")
        self.db.close()
    def onSearchBookItemClick(self,item):
        self.lineEdit_28.setText(item.text())
        self.bookSearch.hide()
        self.lineEdit_30.setText('')
    def onClickAnotherSearchBookItem(self,item):
        search_book_title=item.text()

        if search_book_title:
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            sql_qure='''select * from Books where Book_Title=?'''
            self.crsor.execute(sql_qure,(search_book_title,))
            data=self.crsor.fetchone()
            #print(data)
            if data:
                self.lineEdit_2.setText(data[1])
                self.textEdit_2.setPlainText(data[6])
                self.lineEdit_6.setText(str(data[2]))
                self.comboBox_8.setCurrentText(data[4])
                self.comboBox_9.setCurrentText(data[3])
                self.comboBox_10.setCurrentText(data[5])
                self.lineEdit_5.setText("")
                self.listWidget.hide()
            else:
                self.statusBar().showMessage("Book Not Found")
        else:
            self.statusBar().showMessage("Enter Book Name in empty search field")
    def searchAnotherBook(self,text):
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        self.crsor.execute('select Book_Title from Books')
        books=[j[0] for j in self.crsor.fetchall()]
        textPos=len(text)
        if textPos==0:
            self.listWidget.clear()
            self.lis2.clear()
            self.listWidget.hide()
            return 0
        if textPos==1:
            self.lis2.clear()
            for i in books:
                if text==i[0]:
                    if i not in self.lis2:
                        self.lis2.add(i)
        else:
            self.lis2.clear()
            for i in books:
                if i[0:textPos] == text:
                    if i not in self.lis2:
                        self.lis2.add(i)

        self.listWidget.clear()
        lis2=list(self.lis2)
        lis2.sort()

        self.listWidget.addItems(lis2)
        self.listWidget.show()
        if len(self.lis2)==0:
            self.listWidget.clear()
            self.listWidget.addItem("Not Found")
        self.db.close()


    def OnChangeItem(self):
        class_=self.comboBox_3.currentText()
        section=self.comboBox_4.currentText()
        roll=self.lineEdit_33.text()
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        if class_!="Class" and section!="Section" and roll!="":
            self.crsor.execute('select Name from Members where Class=? and Section=? and Roll=?',(class_,section,roll))
            data=self.crsor.fetchone()
            if data!=None:
                self.lineEdit.setText(data[0])
    def ontextChange(self,text):
        class_=self.comboBox_3.currentText()
        section=self.comboBox_4.currentText()
        roll=text
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        if class_!="Class" and section!="Section" and roll!="":
            self.crsor.execute('select Name from Members where Class=? and Section=? and Roll=?',(class_,section,roll))
            data=self.crsor.fetchone()
            if data!=None:
                self.lineEdit.setText(data[0])
    ######################################################################
    ############### Shoing Theme #########################################
    def Show_Theme(self):
        if self.showing==False:
            self.open_anim_theme()
            # self.Show_Theme()
            self.showing=True
        elif self.showing==True:
            # self.Hide_Theme()
            self.close_anim_theme()
            self.showing=False
    def Hide_Theme(self):
        self.groupBox_6.hide()
        self.showing=False
    ###########################################################
    ################ UI Themes ##############################

    def dark_blue(self):
        style=open(uiPaths('themes/dark_blue.css'),'r')
        self.setStyleSheet(style.read())
        with open(uiPaths("themes/def_.css"),'w') as f:
            style = open(uiPaths('themes/dark_blue.css'), 'r')
            f.write(style.read())
            f.close()
            self.Hide_Theme()

    def dark_(self):
        style=open(uiPaths('themes/dark_.css'),'r')
        self.setStyleSheet(style.read())
        with open(uiPaths("themes/def_.css"),'w') as f:
            style = open(uiPaths('themes/dark_.css'), 'r')
            f.write(style.read())
            f.close()
            self.Hide_Theme()


    #############################################################
    ##################Animation #################################
    def open_anim_theme(self):
        self.anim = QPropertyAnimation(self.groupBox_6,b"size")
        self.anim.setDuration(1000)
        self.anim.setLoopCount(1)
        self.anim.setStartValue(QSize(0,73))
        self.anim.setEndValue(QSize(261,73))
        self.groupBox_6.show()
        self.anim.start()
    def close_anim_theme(self):
        self.anim = QPropertyAnimation(self.groupBox_6,b"size")
        self.anim.setDuration(1000)
        self.anim.setLoopCount(1)
        self.anim.setStartValue(QSize(261,73))
        self.anim.setEndValue(QSize(0,73))
        self.groupBox_6.show()
        self.anim.start()

    #############################################################
    ####################### Opening Tab #########################
    def Open_Day_Book_Brrow(self):
        self.tabWidget.setCurrentIndex(0)
        self.setWindowTitle("Root")
        self.setWindowIcon(QIcon(uiPaths("Ui/Icons/today.png")))
        self.__()
    def Open_Books_Tab(self):
        self.tabWidget.setCurrentIndex(1)
        self.setWindowTitle("Books")
        self.setWindowIcon(QIcon(uiPaths("Ui/Icons/books.png")))
        self.__()
    def Open_Member_Tab(self):
        self.tabWidget.setCurrentIndex(2)
        self.setWindowTitle("Members")
        self.setWindowIcon(QIcon(uiPaths("Ui/Icons/user.png")))
        self.__()
    def Open_Setting_Tab(self):
        self.tabWidget.setCurrentIndex(3)
        self.setWindowTitle("C.A.P")
        self.setWindowIcon(QIcon(uiPaths("Ui/Icons/setting.png")))
        self.__()
    #################################################################
    ########### Handle Book Borrow and Taking Oparetions ###########
    def Add_Book_Borrow(self):
        class_=self.comboBox_3.currentText()
        section=self.comboBox_4.currentText()
        roll=self.lineEdit_33.text()
        if class_=="Class" or section=="Section" or roll=="":
            QMessageBox.question(self,"Not Detect!","<h2>You have to search member!</h2>",QMessageBox.Ok)
            return
        member=self.lineEdit.text()
        book=self.lineEdit_28.text()
        type_=self.comboBox.currentText()
        day=self.comboBox_2.currentIndex()+1
        from_=datetime.date.today()
        to=from_+datetime.timedelta(days=day)
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        self.crsor.execute('select Book_Title from Books')
        books=[j[0] for j in self.crsor.fetchall()]
        self.crsor.execute('select Name,Class,Section,Roll from Members')
        members=[i[0] for i in self.crsor.fetchall()]

        if member!='' and book!='':
            if book in books:
                self.crsor.execute('select Book_Count from Books where Book_Title=?',(book,))
                book_count=self.crsor.fetchone()[0]
            else:
                self.statusBar().showMessage("Book is not in database")
                return 0
            if member not in members:
                self.statusBar().showMessage("Member is not in database")
                return 0
            if type_=="Borrow":
                if (member in members) and book_count>0:
                    book_count-=1
                    self.crsor.execute('update Books set Book_Count=? where Book_Title=?',(book_count,book))
                    self.crsor.execute("""
                INSERT INTO Borrows(Member, Class, Section, Roll, Book ,Day, From_, To_) VALUES(?,?,?,?,?,?,?,?);
                """,(member,class_,section,roll,book,day,from_,to))
                    self.db.commit()
                    self.statusBar().showMessage("Book Borrowed")
                    self.Show_Borrow_Books()
                    self.Show_All_Books()
                    self.comboBox_3.setCurrentIndex(0)
                    self.comboBox_4.setCurrentIndex(0)
                    self.comboBox_2.setCurrentIndex(0)
                    self.lineEdit_33.setText("")
                    self.lineEdit.setText("")
                    self.lineEdit_28.setText("")
                elif book_count==0:
                    t=Borrowed_List(self)
                    self.crsor.execute('''
                    select * from Borrows where Book=?
                    ''',(book,))
                    data=self.crsor.fetchall()
                    t.item_insert(data)
                    t.show()
                else:
                    self.statusBar().showMessage("Member is not in databases")

            elif type_=="Return":
                self.crsor.execute("""select Member from Borrows""")
                borrow_members=[m[0] for m in self.crsor.fetchall()]
                self.crsor.execute('select Book from Borrows')
                borrow_books=[b[0] for b in self.crsor.fetchall()]
                self.crsor.execute('select From_ from Borrows where Member=? and Book=?',(member,book))
                _form=self.crsor.fetchone()[0]
                self.crsor.execute('select To_ from Borrows where Member=? and Book=?',(member,book))
                _to=self.crsor.fetchone()[0]
                self.crsor.execute('select Day from Borrows where Member=? and Book=?',(member,book))
                _day=self.crsor.fetchone()[0]
                if (member in borrow_members) and (book in borrow_books) and book_count>=0:
                    book_count += 1
                    self.crsor.execute('update Books set Book_Count=? where Book_Title=?', (book_count, book))
                    today=datetime.date.today()
                    self.crsor.execute("""
                INSERT INTO Returns(Member, Class, Section, Roll, Book, Day, From_, To_, Return_ ) VALUES(?,?,?,?,?,?,?,?,?);
                """,(member,class_,section,roll,book,_day,_form,_to,today))
                    self.crsor.execute('delete from Borrows where Member=? and Book=? and Day=?',(member,book,_day))
                    self.db.commit()
                    self.statusBar().showMessage("Book Recevied")
                    self.Show_Taking_Books()
                    self.Show_All_Books()
                    self.Show_Borrow_Books()
                    self.comboBox_3.setCurrentIndex(0)
                    self.comboBox_4.setCurrentIndex(0)
                    self.comboBox_2.setCurrentIndex(0)
                    self.lineEdit_33.setText("")
                    self.lineEdit.setText("")
                    self.lineEdit_28.setText("")
                else:
                    self.statusBar().showMessage("The Member Who Wants to Return The Book He is not in Borrwed list")
        else:
            self.statusBar().showMessage("Fill empty fields")
        self.db.close()
    def Show_Borrow_Books(self):
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        self.crsor.execute("""select * from Borrows ORDER by Day""")
        data=self.crsor.fetchall()
        if data:
            self.tableWidget.setRowCount(0)
            self.tableWidget.insertRow(0)
            for row,data_lis in enumerate(data):
                for column,items in enumerate(data_lis[1:]):
                    self.tableWidget.setItem(row,column,QTableWidgetItem(str(items)))
                    column+=1
                row_pos=self.tableWidget.rowCount()
                self.tableWidget.insertRow(row_pos)
            h=self.tableWidget.horizontalHeader()
            for i in range(self.tableWidget.columnCount()):
                h.setSectionResizeMode(i,QHeaderView.ResizeToContents)
        else:
            if self.tableWidget.rowCount() > 0:
                self.tableWidget.removeRow(0)
                self.tableWidget.setRowCount(0)
    def Show_Taking_Books(self):
        self.db=sqlite3.connect("DataBases/library")
        self.crsor = self.db.cursor()
        self.crsor.execute("""select * from Returns ORDER by Day""")
        data = self.crsor.fetchall()
        if data:
            self.tableWidget_7.setRowCount(0)
            self.tableWidget_7.insertRow(0)
            for row, data_lis in enumerate(data):
                for column, items in enumerate(data_lis[1:]):
                    self.tableWidget_7.setItem(row, column, QTableWidgetItem(str(items)))
                    column += 1
                row_pos = self.tableWidget_7.rowCount()
                self.tableWidget_7.insertRow(row_pos)
            h = self.tableWidget_7.horizontalHeader()
            for i in range(self.tableWidget_7.columnCount()):
                h.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        else:
            if self.tableWidget_7.rowCount() > 0:
                self.tableWidget_7.removeRow(0)
                self.tableWidget_7.setRowCount(0)


    def onBorrowReurnComboChange(self):
        data=self.comboBox.currentText()
        if data=="Borrow":
            self.pushButton_5.setText("Add")
        else:
            self.pushButton_5.setText("Return")
    ##############################################################
    ######################## Books ###############################
    def Add_New_Books(self):
        book_title=self.lineEdit_7.text()
        book_count=self.lineEdit_3.text()
        book_discription=self.textEdit.toPlainText()
        book_cetagory=self.comboBox_5.currentText()
        book_author=self.comboBox_6.currentText()
        book_publisher=self.comboBox_7.currentText()
        if (book_author!="" and book_cetagory!="" and book_count!="" and book_discription!="" and book_publisher!="" and book_title!=""):
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            self.crsor.execute("select Book_Title from Books")
            b=self.crsor.fetchall()
            if tuple([book_title]) in b:
                QMessageBox.question(self, "Not Added", f"<h2>Can't Added!!</h2><br><h3>Book is already in database.</h3>", QMessageBox.Ok)
                return
            self.crsor.execute("""
            INSERT INTO Books(Book_Title, Book_Count, Book_Author, Book_Cetagory,Book_Publisher, Book_Dicription)
            VALUES(?,?,?,?,?,?)
            """,(book_title,book_count,book_author,book_cetagory,book_publisher,book_discription))
            self.db.commit()
            self.statusBar().showMessage("New Book Added")
            self.db.close()
            self.lineEdit_7.setText("")
            self.lineEdit_3.setText("")
            self.textEdit.setPlainText("")
            self.comboBox_5.setCurrentIndex(0)
            self.comboBox_6.setCurrentIndex(0)
            self.comboBox_7.setCurrentIndex(0)
            self.Show_All_Books()
        else:
            self.statusBar().showMessage("Fill empty field")
    def Edit_Books_Details(self):
        book_title=self.lineEdit_2.text()
        book_count=self.lineEdit_6.text()
        book_discription=self.textEdit_2.toPlainText()
        book_cetagory=self.comboBox_8.currentText()
        book_author=self.comboBox_9.currentText()
        book_publisher=self.comboBox_10.currentText()

        searched_book=self.lineEdit_5.text()
        if (book_author!="" and book_cetagory!="" and book_count!="" and book_discription!="" and book_publisher!="" and book_title!=""):
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            self.crsor.execute('''
            UPDATE Books SET Book_Title=? ,Book_Count=? ,Book_Dicription=? ,Book_Cetagory=? ,Book_Author=? ,Book_Publisher=? WHERE Book_Title=?;
            ''',(book_title,book_count,book_discription,book_cetagory,book_author,book_publisher,book_title))
            self.statusBar().showMessage("Book Updated")
            self.db.commit()
            self.db.close()
            self.Show_All_Books()
            self.lineEdit_5.setText("")
            self.lineEdit_2.setText("")
            self.lineEdit_6.setText("")
            self.textEdit_2.setPlainText("")
            self.comboBox_8.setCurrentIndex(0)
            self.comboBox_9.setCurrentIndex(0)
            self.comboBox_10.setCurrentIndex(0)
        else:
            self.statusBar().showMessage("Fill Empty Field")
    def Delete_Books(self):
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        book_title=self.lineEdit_2.text()
        if book_title:
            self.crsor.execute('''
            DELETE FROM Books WHERE Book_Title=?
            ''',(book_title,))
            self.statusBar().showMessage("Book Deleted")
            self.db.commit()
            self.db.close()
            self.Show_All_Books()


            self.lineEdit_5.setText("")
            self.lineEdit_2.setText("")
            self.lineEdit_6.setText("")
            self.textEdit_2.setPlainText("")
            self.comboBox_8.setCurrentIndex(0)
            self.comboBox_9.setCurrentIndex(0)
            self.comboBox_10.setCurrentIndex(0)
        else:
            self.statusBar().showMessage("Fill Empty Boxes")
    def Show_All_Books(self):
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        self.crsor.execute("""select * from Books ORDER by Book_Title""")
        data=self.crsor.fetchall()
        if data:
            self.tableWidget_6.setRowCount(0)
            self.tableWidget_6.insertRow(0)
            for row,data_lis in enumerate(data):
                for column,items in enumerate(data_lis[1:]):
                    self.tableWidget_6.setItem(row,column,QTableWidgetItem(str(items)))
                    column+=1
                row_pos=self.tableWidget_6.rowCount()
                self.tableWidget_6.insertRow(row_pos)
            h=self.tableWidget_6.horizontalHeader()
            for i in range(self.tableWidget_6.columnCount()):
                h.setSectionResizeMode(i,QHeaderView.ResizeToContents)
        else:
            if self.tableWidget_6.rowCount() > 0:
                self.tableWidget_6.removeRow(0)
                self.tableWidget_6.setRowCount(0)


    ##########################################################
    ################## User #################################
    def Add_Users(self):
        name=self.lineEdit_8.text()
        phone_Num=self.lineEdit_4.text()
        email=self.lineEdit_10.text()
        address=self.textEdit_3.toPlainText()
        class_=self.lineEdit_25.text()
        secition=self.lineEdit_26.text()
        roll=self.lineEdit_27.text()
        if name!="" and phone_Num!="" and email!="" and address!="" and class_!="" and secition!="" and roll!="":
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            self.crsor.execute("""
            INSERT INTO Members(Name,Phone,Email,Class,Section,Roll,Address)
            VALUES(?,?,?,?,?,?,?);
            """,(name,phone_Num,email,class_,secition,roll,address))
            self.db.commit()
            self.db.close()
            self.statusBar().showMessage("New Member Added")
            self.lineEdit_8.setText('')
            self.lineEdit_4.setText('')
            self.lineEdit_10.setText('')
            self.textEdit_3.setPlainText('')
            self.lineEdit_25.setText('')
            self.lineEdit_26.setText('')
            self.lineEdit_27.setText('')
            self.Show_All_Users()
        else:
            self.statusBar().showMessage("Fill all entries")
    def Edit_User_Info(self):
        name=self.lineEdit_12.text()
        phone=self.lineEdit_14.text()
        email=self.lineEdit_13.text()
        address=self.textEdit_4.toPlainText()
        class_=self.lineEdit_19.text()
        section=self.lineEdit_20.text()
        roll=self.lineEdit_21.text()

        search_class=self.lineEdit_22.text()
        search_section=self.lineEdit_23.text()
        search_roll=self.lineEdit_24.text()
        if name!="" and phone!="" and email!="" and address!="" and class_!="" and section!="" and roll!="" and search_class!="" and search_roll!="" and search_section!="":
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            self.crsor.execute("""
            UPDATE Members SET Name=? , Phone=? , Email=?  , Class=? , Section=? , Roll=?, Address=? WHERE Class=? and Section=? and Roll=?;
            """,(name,phone,email,class_,section,roll,address,search_class,search_section,search_roll))
            self.db.commit()
            self.statusBar().showMessage("User Info Updated")
            self.db.close()
            self.lineEdit_12.setText('')
            self.lineEdit_13.setText('')
            self.lineEdit_14.setText('')
            self.textEdit_4.setPlainText('')
            self.lineEdit_19.setText('')
            self.lineEdit_20.setText('')
            self.lineEdit_21.setText('')
            self.lineEdit_22.setText('')
            self.lineEdit_23.setText('')
            self.lineEdit_24.setText('')
            self.Show_All_Users()
        else:
            self.statusBar().showMessage("Fill all entries")


    def Delete_Users(self):
        search_class=self.lineEdit_22.text()
        search_section=self.lineEdit_23.text()
        search_roll=self.lineEdit_24.text()
        if search_class!="" and search_roll!="" and search_section!="":
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            self.crsor.execute("""
            DELETE FROM Members WHERE Class=? and Section=? and Roll=?
            """,(search_class,search_section,search_roll))
            self.db.commit()
            self.statusBar().showMessage("User Deleted")
            self.db.close()
            self.lineEdit_12.setText('')
            self.lineEdit_14.setText('')
            self.lineEdit_13.setText('')
            self.textEdit_4.setPlainText('')
            self.lineEdit_19.setText('')
            self.lineEdit_20.setText('')
            self.lineEdit_21.setText('')
            self.lineEdit_22.setText('')
            self.lineEdit_23.setText('')
            self.lineEdit_24.setText('')
            self.Show_All_Users()
        else:
            self.statusBar().showMessage("Fill all entries")
    def Search_Users(self):
        search_class=self.lineEdit_22.text()
        search_section=self.lineEdit_23.text()
        search_roll=self.lineEdit_24.text()
        if search_class!="" and search_roll!="" and search_section!="":
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            sql_qure='''select * from Members where Class=? and Roll=? and Section=?;'''
            self.crsor.execute(sql_qure,(search_class,search_roll,search_section))
            data=self.crsor.fetchone()
            #print(data)
            if data:
                self.lineEdit_12.setText(str(data[1]))
                self.lineEdit_14.setText(str(data[2]))
                self.lineEdit_13.setText(str(data[3]))
                self.textEdit_4.setPlainText(str(data[-1]))
                self.lineEdit_19.setText(str(data[5]))
                self.lineEdit_20.setText(str(data[6]))
                self.lineEdit_21.setText(str(data[7]))
            else:
                self.statusBar().showMessage("Member is Not Found")
        else:
            self.statusBar().showMessage("Fill all search entries")
    def Show_All_Users(self):
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        self.crsor.execute("""select * from Members ORDER by Class""")
        data=self.crsor.fetchall()
        if data:
            self.tableWidget_2.setRowCount(0)
            self.tableWidget_2.insertRow(0)
            for row,data_lis in enumerate(data):
                for column,items in enumerate(data_lis[1:]):
                    self.tableWidget_2.setItem(row,column,QTableWidgetItem(str(items)))
                    column+=1
                row_pos=self.tableWidget_2.rowCount()
                self.tableWidget_2.insertRow(row_pos)
            h=self.tableWidget_2.horizontalHeader()
            for i in range(self.tableWidget_2.columnCount()):
                h.setSectionResizeMode(i,QHeaderView.ResizeToContents)
        else:
            if self.tableWidget_2.rowCount() > 0:
                self.tableWidget_2.removeRow(0)
                self.tableWidget_2.setRowCount(0)


    ###########################################################
    ##################### Cetagory ############################
    def Add_Cetagory(self):
        cetagory=self.lineEdit_9.text()
        if cetagory:
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            self.crsor.execute("select Cetagory_Name from Cetagorys")
            c=[i[0] for i in self.crsor.fetchall()]
            if cetagory in c:
                QMessageBox.question(self, "Not Added", f"<h2>Can't Added!!</h2><br><h3>Cetagory is already in database.</h3>", QMessageBox.Ok)
                return
            try:
                self.crsor.execute("""
            INSERT INTO Cetagorys(Cetagory_Name) VALUES(?)
            """,(cetagory,))
                self.db.commit()
                self.statusBar().showMessage("New Cetagory Added")
                self.db.close()
                self.lineEdit_9.setText("")
                self.Show_Cetagory_TABLE()
                self.Show_Cetagory_Combo()
            except Exception as e:
                self.statusBar().showMessage(e)
        else:
            self.statusBar().showMessage("Fill cetagory field")
    def Show_Cetagory_TABLE(self):
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        self.crsor.execute("""select Cetagory_Name from Cetagorys""")
        data=self.crsor.fetchall()
        if data:
            self.tableWidget_3.setRowCount(0)
            self.tableWidget_3.insertRow(0)
            for row,data_lis in enumerate(data):
                for column,items in enumerate(data_lis):
                    self.tableWidget_3.setItem(row,column,QTableWidgetItem(str(items)))
                    column+=1
                row_pos=self.tableWidget_3.rowCount()
                self.tableWidget_3.insertRow(row_pos)
            h=self.tableWidget_3.horizontalHeader()
            h.setSectionResizeMode(0,QHeaderView.ResizeToContents)
            # self.tableWidget_3.item(4,0).setFont(QFont("SutonnyMj",30))
        else:
            if self.tableWidget_3.rowCount() > 0:
                self.tableWidget_3.removeRow(0)
                self.tableWidget_3.setRowCount(0)
    def Delete_Cetagory(self):
        """"""
        cetagory_name=self.lineEdit_11.text()
        if cetagory_name:
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            try:
                self.crsor.execute("""
            DELETE FROM Cetagorys WHERE Cetagory_Name=?;
            """,(cetagory_name,))
                self.db.commit()
                self.statusBar().showMessage("Cetagory Removed")
                self.db.close()
                self.lineEdit_11.setText("")
                self.Show_Cetagory_TABLE()
                self.Show_Cetagory_Combo()
            except Exception as e:
                self.statusBar().showMessage(e)
        else:
            self.statusBar().showMessage("Fill cetagory entries")

    ###########################################################
    ##################### Author ############################
    def Add_Author(self):
        author=self.lineEdit_16.text()
        if author:
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            self.crsor.execute("select Author_Name from Author")
            c=[i[0] for i in self.crsor.fetchall()]
            if author in c:
                QMessageBox.question(self, "Not Added", f"<h2>Can't Added!!</h2><br><h3>Author is already in database.</h3>", QMessageBox.Ok)
                return
            try:
                self.crsor.execute("""
            INSERT INTO Author(Author_Name) VALUES(?)
            """,(author,))
                self.db.commit()
                self.statusBar().showMessage("New Author Added")
                self.db.close()
                self.lineEdit_16.setText("")
                self.Show_Author_TABLE()
                self.Show_Author_Combo()
            except Exception as e:
                self.statusBar().showMessage(e)
        else:
            self.statusBar().showMessage("Fill author entries")
    def Show_Author_TABLE(self):
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        self.crsor.execute("""select Author_Name from Author""")
        data=self.crsor.fetchall()
        if data:
            self.tableWidget_4.setRowCount(0)
            self.tableWidget_4.insertRow(0)
            for row,data_lis in enumerate(data):
                for column,items in enumerate(data_lis):
                    self.tableWidget_4.setItem(row,column,QTableWidgetItem(str(items)))
                    column+=1
                row_pos=self.tableWidget_4.rowCount()
                self.tableWidget_4.insertRow(row_pos)
            h=self.tableWidget_4.horizontalHeader()
            h.setSectionResizeMode(0,QHeaderView.ResizeToContents)
        else:
            if self.tableWidget_4.rowCount() > 0:
                self.tableWidget_4.removeRow(0)
                self.tableWidget_4.setRowCount(0)
    def Delete_Author(self):
        author_name=self.lineEdit_15.text()
        if author_name:
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            try:
                self.crsor.execute("""
            DELETE FROM Author WHERE Author_Name=?;
            """,(author_name,))
                self.db.commit()
                self.statusBar().showMessage("Author Removed")
                self.db.close()
                self.lineEdit_15.setText("")
                self.Show_Author_TABLE()
                self.Show_Author_Combo()
            except Exception as e:
                self.statusBar().showMessage(e)
        else:
            self.statusBar().showMessage("Fill author entries")

    ###########################################################
    ##################### Publisher ############################
    def Add_Publisher(self):
        publisher=self.lineEdit_17.text()
        if publisher:
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            self.crsor.execute("select Publisher_Name from Publisher ")
            c=[i[0] for i in self.crsor.fetchall()]
            if publisher in c:
                QMessageBox.question(self, "Not Added", f"<h2>Can't Added!!</h2><br><h3>Publisher is already in database.</h3>", QMessageBox.Ok)
                return
            try:
                self.crsor.execute("""
            INSERT INTO Publisher(Publisher_Name) VALUES(?)
            """,(publisher,))
                self.db.commit()
                self.statusBar().showMessage("New Publisher Added")
                self.db.close()
                self.lineEdit_17.setText("")
                self.Show_Publisher_TABLE()
                self.Show_Publisher_Combo()
            except Exception as e:
                self.statusBar().showMessage(e)
        else:
            self.statusBar().showMessage("Fill publisher field")
    def Show_Publisher_TABLE(self):
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        self.crsor.execute("""select Publisher_Name from Publisher""")
        data=self.crsor.fetchall()
        if data:
            self.tableWidget_5.setRowCount(0)
            self.tableWidget_5.insertRow(0)
            for row,data_lis in enumerate(data):
                for column,items in enumerate(data_lis):
                    self.tableWidget_5.setItem(row,column,QTableWidgetItem(str(items)))
                    column+=1
                row_pos=self.tableWidget_5.rowCount()
                self.tableWidget_5.insertRow(row_pos)
            h=self.tableWidget_5.horizontalHeader()
            h.setSectionResizeMode(0,QHeaderView.ResizeToContents)
        else:
            if self.tableWidget_5.rowCount() > 0:
                self.tableWidget_5.removeRow(0)
                self.tableWidget_5.setRowCount(0)
    def Delete_Publisher(self):
        publisher_name=self.lineEdit_18.text()
        if publisher_name:
            self.db=sqlite3.connect("DataBases/library")
            self.crsor=self.db.cursor()
            try:
                self.crsor.execute("""
            DELETE FROM Publisher WHERE Publisher_Name=?;
            """,(publisher_name,))
                self.db.commit()
                self.statusBar().showMessage("Publisher Removed")
                self.db.close()
                self.lineEdit_18.setText("")
                self.Show_Publisher_TABLE()
                self.Show_Publisher_Combo()
            except Exception as e:
                self.statusBar().showMessage(e)
        else:
            self.statusBar().showMessage("Fill publisher field")

    ###############################################################
    ############ Setting Data to Combo BOx #######################
    def Show_Cetagory_Combo(self):
        self.comboBox_5.clear()
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        self.crsor.execute('''select Cetagory_Name from Cetagorys  ORDER by Cetagory_Name''')
        data=self.crsor.fetchall()
        if data:
            self.comboBox_5.clear()
            self.comboBox_8.clear()
            for cetagory_list in data:
                self.comboBox_5.addItem(cetagory_list[0])
                self.comboBox_8.addItem(cetagory_list[0])
        self.db.close()
    def Show_Author_Combo(self):
        self.comboBox_6.clear()
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        self.crsor.execute('''select Author_Name from Author  ORDER by Author_Name''')
        data=self.crsor.fetchall()
        if data:
            self.comboBox_6.clear()
            self.comboBox_9.clear()
            for author_list in data:
                self.comboBox_6.addItem(author_list[0])
                self.comboBox_9.addItem(author_list[0])
        self.db.close()
    def Show_Publisher_Combo(self):
        self.comboBox_7.clear()
        self.db=sqlite3.connect("DataBases/library")
        self.crsor=self.db.cursor()
        self.crsor.execute('''select Publisher_Name from Publisher ORDER by Publisher_Name''')
        data=self.crsor.fetchall()
        if data:
            self.comboBox_7.clear()
            self.comboBox_10.clear()
            for publisher_list in data:
                self.comboBox_7.addItem(publisher_list[0])
                self.comboBox_10.addItem(publisher_list[0])
        self.db.close()
    def export_file(self):
        ex=export_(self)
        ex.show()
    def show_Devloper(self):
        dev=Devloper(self)
        dev.show()
    def import_file(self):
        im=import_(self)
        im.show()
    def delete(self):
        dl=Delete(self)
        dl.show()
    def __(self):
        self.Show_All_Books()
        self.Show_All_Users()
        self.Show_Author_Combo()
        self.Show_Author_TABLE()
        self.Show_Cetagory_TABLE()
        self.Show_Cetagory_Combo()
        self.Show_Publisher_TABLE()
        self.Show_Publisher_Combo()
        self.Show_Borrow_Books()
        self.Show_Taking_Books()
def main():
    app=QApplication(sys.argv)
    win=MainApp()
    win.show()
    app.exec()

if __name__ == "__main__":
    try:
        main()
    except:
        pass
