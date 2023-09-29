import threading
import io
import requests
from PyPDF2 import PdfReader
from tkinter import ttk
from tkinter import *
import tkinter as tk
from tkinter.messagebox import showinfo
from queue import Queue


pb_value_temp = 0
def Scan(journals,start_year,end_year,keywords):
    Shared_queue_scan = Queue()
    def Scan_PB_update():
        global pb_value_temp
        data = Shared_queue_scan.get()
        while data!=100:
            data = Shared_queue_scan.get()
            pb_value_temp +=data
            pb['value'] = (int(pb_value_temp))
        
        showinfo(message='Scan complete! result is found in scan_result.txt')
        Progress.destroy()
        Progress.quit()
        pb_value_temp = 0
        thread1.join()
        return
    def main_Scan():
        global pb_value_temp
        count = 0
        for journal in journals:
            File_location = str(journal) + '.txt'
            file = open(f'Pdf list per site/{File_location}')
            links = file.readlines()
            for link in links:
                year = link.split(' ')[0]
                if year == 0:
                    count+=1
                if year <= end_year and year >= start_year:
                    count+=1
        Length = count
        value_label['text'] = f'Scanning Through {Length} PDFs'
        file_results = open('scan_result.txt','w')
        for journal in journals:
            print(journal)
            # get file name
            File_location = str(journal) + '.txt'
            file = open(f'Pdf list per site/{File_location}')

            PDF_links=[]
            links = file.readlines()

            for link in links:
                year = link.split(' ')[0]
                if year == 0:
                    PDF_links.append(link)
                if year <= end_year and year >= start_year:
                    PDF_links.append(link)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
            }
            while len(PDF_links)>0:
                try:
                    data = PDF_links.pop()
                    year = data.split(' ')[0]
                    url = data.split(' ')[1].replace('\n','')
                    req = requests.get(url.replace('\n',''),headers=headers)
                    File = io.BytesIO(req.content)
                    reader = PdfReader(File)
                    Pages = reader.getNumPages()
                    for word in keywords.split(';'):
                        Detected = False
                        count_total = 0
                        pages = []
                        for x in range(0,Pages):
                            contents = reader.getPage(x).extract_text()
                            if word in contents.lower():
                                count_total +=1
                                Detected = True
                                pages.append(x+1)
                        if Detected == True:
                            file_results.write(f'\nDetected \"{word}\" {count_total} times in {journal} (Link = {url} - Year = {year} - Pages: {pages})')
                            

                except Exception as e:
                    if 'SSL' in str(e):
                        showinfo(message='Need SSL Verification!')
                    else:
                        print(e)
                Shared_queue_scan.put(100/Length)
                count -=1
                value_label['text'] = f'{count} PDF left out of {Length}'
        Shared_queue_scan.put(100)
        file_results.close()
        return
    # root window
    Progress = tk.Tk()
    Progress.geometry('420x90')
    Progress.title('Progressbar')
    # progressbar
    bar_value = tk.IntVar()
    pb = ttk.Progressbar( Progress,orient='horizontal',mode='determinate', length=390,variable=bar_value)
    pb.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
    value_label = ttk.Label(Progress, text='')
    value_label.grid(column=0, row=1, columnspan=2)
    thread1 = threading.Thread(target=main_Scan)
    thread1.start()
    Shared_queue_scan.put(0)
    thread2 = threading.Thread(target=Scan_PB_update)
    thread2.start()
    Progress.mainloop()
    