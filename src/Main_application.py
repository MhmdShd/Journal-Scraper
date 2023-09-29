import threading
from tkinter import ttk
from tkinter import *
from Scraper import GetPDFs
from Scanner import Scan


Sites = ['academicjournals.org', 'aeji.journals.ekb.eg', 'ajps.journals.ekb.eg',
                                        'ajps.uomustansiriyah.edu.iq', 'amj.uoanbar.edu.iq',
                                        'anafrimed.net', 'batnajms.net', 'bfpc.journals.ekb.eg',
                                        'bijps.uobaghdad.edu.iq', 'bjsrg.uobasrah.edu.iq', 'ebwhj.journals.ekb.eg',
                                        'ejb.springeropen.com', 'ejim.springeropen.com', 'gssrr.org',
                                        'iphr.mosuljournals.com', 'iraqmedj.org-abstracts', 'iraqmedj.org-PDFs',
                                        'jkmc.uobaghdad.edu.iq', 'journals.ju.edu.jo-JJPS', 'journals.ju.edu.jo-JMJ',
                                        'journals.uokerbala.edu.iq-abstracts', 'journals.uokerbala.edu.iq-PDFs',
                                        'journalskuwait.org-KJS', 'lsj.cnrs.edu.lb', 'mchandaids.org.com-IJMA',
                                        'medtech.ichsmt.org', 'phcfm.org', 'revues.imist.ma', 'rmr.smr.ma',
                                        'rmsjournal.org', 'www.ajol.info-ajhs (NOT FREE)', 'www.ajol.info-ajr',
                                        'www.ajol.info-ajst', 'www.ajol.info-eaoj', 'www.ajol.info-ecajps (NOT FREE)',
                                        'www.ajol.info-jmbs', 'www.annalsofafricansurgery.com', 'www.asjp.cerist.dz',
                                        'www.bahrainmedicalbulletin.com', 'www.bhmedsoc.com', 'www.easpublisher.com-easjacc',
                                        'www.easpublisher.com-easjms', 'www.easpublisher.com-easjop', 'www.easpublisher.com-easjpp',
                                        'www.easpublisher.com-easms', 'www.egyptretinaj.com (24 hrs)',
                                        'www.ejdv.eg.net (24 hrs)','www.ejmsonline.org-Abstracts',
                                        'www.epj.eg.net (24 hrs)', 'www.hamdanjournal.org (24 hrs)',
                                        'www.hsd-fmsb.org', 'www.iasj.net-13883', 'www.iasj.net-14135',
                                        'www.iraqijms.net', 'www.jaccrafrica.com', 'www.jeos.eg.net (24 hrs)',
                                        'www.jomenas.org.com', 'www.journal-jmsr.net', 'www.karger.com',
                                        'www.ljmr.com.ly', 'www.ljmsonline.com (24 hrs)', 'www.mbmj.org', 'www.me-jaa.com',
                                        'www.medjbabylon.org (24 hrs)', 'www.mejfm.com', 'www.mjemonline.com',
                                        'www.mmjonweb.org (24 hrs)', 'www.qscience.com', 'www.saudijournals.com-sjbr',
                                        'www.saudijournals.com-sjls', 'www.saudijournals.com-sjm', 'www.saudijournals.com-sjmps']
Sites_Algeria =['phcfm.org','www.hsd-fmsb.org','rmr.smr.ma','anafrimed.net','www.jaccrafrica.com',
                'medtech.ichsmt.org','revues.imist.ma','batnajms.net','mchandaids.org.com-IJMA']
Sites_Bahrain=['www.bahrainmedicalbulletin.com','www.bhmedsoc.com']
Sites_UAE=['www.hamdanjournal.org (24 hrs)','www.saudijournals.com-sjbr','www.saudijournals.com-sjls',
            'www.saudijournals.com-sjm', 'www.saudijournals.com-sjmps']
Sites_Iraq=['iraqmedj.org-abstracts', 'iraqmedj.org-PDFs','www.iraqijms.net','www.medjbabylon.org (24 hrs)',
            'bijps.uobaghdad.edu.iq','jkmc.uobaghdad.edu.iq','www.mmjonweb.org (24 hrs)','amj.uoanbar.edu.iq','iphr.mosuljournals.com',
            'journals.uokerbala.edu.iq-abstracts', 'journals.uokerbala.edu.iq-PDFs','www.iasj.net-13883', 'www.iasj.net-14135',
            'bjsrg.uobasrah.edu.iq','ajps.uomustansiriyah.edu.iq']
Sites_Jordan=['journals.ju.edu.jo-JJPS', 'journals.ju.edu.jo-JMJ','rmsjournal.org','www.jomenas.org.com','gssrr.org']
Sites_Kenya=['www.annalsofafricansurgery.com','www.ajol.info-ajhs (NOT FREE)', 'www.ajol.info-ajr','www.ajol.info-ajst',
            'www.ajol.info-eaoj', 'www.ajol.info-ecajps','www.easpublisher.com-easjacc','www.easpublisher.com-easjms',
            'www.easpublisher.com-easjop', 'www.easpublisher.com-easjpp','www.easpublisher.com-easms']
Sites_Kuwait=['journalskuwait.org-KJS','www.karger.com']
Sites_Lebanon=['www.mejfm.com','www.mjemonline.com','www.me-jaa.com','lsj.cnrs.edu.lb']
Sites_Libya=['www.ljmr.com.ly','www.ljmsonline.com (24 hrs)']
Sites_Morocco=['www.journal-jmsr.net','www.mbmj.org']
Sites_Qatar=['www.qscience.com']
Sites_Ghana=['www.ajol.info-jmbs','academicjournals.org']
Sites_Egypt=['www.ejmsonline.org-Abstracts','ebwhj.journals.ekb.eg','ejb.springeropen.com', 'ejim.springeropen.com','www.epj.eg.net (24 hrs)'
            ,'www.egyptretinaj.com (24 hrs)','www.jeos.eg.net (24 hrs)','www.ejdv.eg.net.asp','aeji.journals.ekb.eg', 'ajps.journals.ekb.eg','bfpc.journals.ekb.eg',]
Sites_Tunsia =['phcfm.org','rmr.smr.ma','www.hsd-fmsb.org']
Countries =['All','Algeria','Bahrain','Egypt','Ghana','Iraq','Jordan','Kenya','Kuwait','Lebanon','Libya','Morocco','Qatar','Tunsia','UAE']

Scan_list = []


def Update_Scan_list():
    if JournalMenu_scan.get().split(' ')[0] not in Scan_list:
        Scan_list.append(JournalMenu_scan.get().split(' ')[0])
    Scan_list_output.delete("1.0","end")
    for journal in Scan_list:
        Scan_list_output.insert(END,journal+'\n')
def reset_Scan_list():
    Scan_list.clear()
    Scan_list_output.delete("1.0","end")

def get_sites_by_country(x):
    if Country.get() == 'All':
        JournalMenu_scan['values'] = sorted(Sites)
    if Country.get() == 'Algeria':
        JournalMenu_scan['values'] = sorted(Sites_Algeria)
    if Country.get() == 'Bahrain':
        JournalMenu_scan['values'] = sorted(Sites_Bahrain)
    if Country.get() == 'Egypt':
        JournalMenu_scan['values'] = sorted(Sites_Egypt)
    if Country.get() == 'Ghana':
        JournalMenu_scan['values'] = sorted(Sites_Ghana)
    if Country.get() == 'Iraq':
        JournalMenu_scan['values'] = sorted(Sites_Iraq)
    if Country.get() == 'Jordan':
        JournalMenu_scan['values'] = sorted(Sites_Jordan)
    if Country.get() == 'Kenya':
        JournalMenu_scan['values'] = sorted(Sites_Kenya)
    if Country.get() == 'Kuwait':
        JournalMenu_scan['values'] = sorted(Sites_Kuwait)
    if Country.get() == 'Lebanon':
        JournalMenu_scan['values'] = sorted(Sites_Lebanon)
    if Country.get() == 'Libya':
        JournalMenu_scan['values'] = sorted(Sites_Libya)
    if Country.get() == 'Morocco':
        JournalMenu_scan['values'] = sorted(Sites_Morocco)
    if Country.get() == 'Qatar':
        JournalMenu_scan['values'] = sorted(Sites_Qatar)
    if Country.get() == 'Tunsia':
        JournalMenu_scan['values'] = sorted(Sites_Tunsia)
    if Country.get() == 'UAE':
        JournalMenu_scan['values'] = sorted(Sites_UAE)

def Update_thread():
    thread = threading.Thread(target=GetPDFs(JournalMenu_update.get()))
    thread.start()
    thread.join()
def Scan_thread():
    thread = threading.Thread(target=Scan(Scan_list,Starting_year.get(),Ending_year.get(),Keywords.get()))
    thread.start()
    thread.join()


root = Tk()
root.title('PDF Scanner')
root.geometry('1000x400')


root.config(bg='grey')

# Settings up UI Size
UI_frame = Frame(root, width=1500, height=600, bg='grey')
UI_frame.grid(row=0, column=0,)


# Single Scan
Label(UI_frame, text='Journal Scan: ', bg="grey", font='Helvetica 18 bold').grid(row=0, column=0, columnspan=3)

# Select Country:
Label(UI_frame, text='Country: ', bg="grey").grid(row=1, column=0)
Country = ttk.Combobox(UI_frame, values=Countries)
Country.grid(row=1, column=1,sticky=W)
Country.current(0)


# Select Journal (websites):
Label(UI_frame, text='Journal: ', bg="grey").grid(row=2, column=0,)
JournalMenu_scan = ttk.Combobox(UI_frame, values=Sites,width=35)
JournalMenu_scan.grid(row=2, column=1, columnspan=3,  sticky=W)
JournalMenu_scan.current(0)

Button(UI_frame, text='Add to Scan List', command=Update_Scan_list, bg='yellow').grid(row=2, column=3,sticky=W)
Button(UI_frame, text='Reset Scan List', command=reset_Scan_list, bg='yellow').grid(row=2, column=4,sticky=W)
# receives min year
Label(UI_frame, text='Starting year: ', bg="grey").grid(row=3, column=0,)
Starting_year = Entry(UI_frame)
Starting_year.insert(0, '0')
Starting_year.grid(row=3, column=1, sticky=W)

# receives max year
Label(UI_frame, text='Ending year: ', bg="grey").grid(row=4, column=0, )
Ending_year = Entry(UI_frame)
Ending_year.insert(0, '0')
Ending_year.grid(row=4, column=1, sticky=W)

# receives Keywords from user
Label(UI_frame, text='Keywords (;) ', bg="grey").grid(row=5, column=0, )
Keywords = Entry(UI_frame)
Keywords.grid(row=5, column=1,columnspan=2,sticky=W)

# Add a Scrollbar(horizontal)
Scan_list_output = Text(root, height = 10, width = 35)
Scan_list_output.insert(END,'Journals to be scanned: ')
# v = Scrollbar(orient=VERTICAL,)
# v.config(command=Scan_list_output.yview, )
# Scan_list_output["yscrollcommand"] = v.set
# v.grid(row=7,column=0,sticky="nse")
Scan_list_output.grid(row = 0,column=5,sticky=W)
# Launch the Scanner
Button(UI_frame, text='Start The search', command=Scan_thread, bg='green').grid(row=6, column=1,sticky=W)


Label(UI_frame, text='Journal Update: ', bg="grey", font='Helvetica 18 bold').grid(row=7, column=0,columnspan=3, padx=5, pady=5)
# Select Journal (websites):
Label(UI_frame, text='Journals: ', bg="grey").grid(row=8, column=0, padx=5, pady=5)
JournalMenu_update = ttk.Combobox(UI_frame, values=['academicjournals.org', 'aeji.journals.ekb.eg', 'ajps.journals.ekb.eg',
                                        'ajps.uomustansiriyah.edu.iq', 'amj.uoanbar.edu.iq',
                                        'anafrimed.net', 'batnajms.net', 'bfpc.journals.ekb.eg',
                                        'bijps.uobaghdad.edu.iq', 'bjsrg.uobasrah.edu.iq', 'ebwhj.journals.ekb.eg',
                                        'ejb.springeropen.com', 'ejim.springeropen.com', 'gssrr.org',
                                        'iphr.mosuljournals.com', 'iraqmedj.org-abstracts', 'iraqmedj.org-PDFs','journals.squ.edu.om',
                                        'jkmc.uobaghdad.edu.iq', 'journals.ju.edu.jo-JJPS', 'journals.ju.edu.jo-JMJ',
                                        'journals.uokerbala.edu.iq-abstracts', 'journals.uokerbala.edu.iq-PDFs',
                                        'journalskuwait.org-KJS', 'lsj.cnrs.edu.lb', 'mchandaids.org.com-IJMA',
                                        'medtech.ichsmt.org', 'phcfm.org', 'revues.imist.ma', 'rmr.smr.ma',
                                        'rmsjournal.org', 'www.ajol.info-ajhs (NOT FREE)', 'www.ajol.info-ajr',
                                        'www.ajol.info-ajst', 'www.ajol.info-eaoj', 'www.ajol.info-ecajps','www.ajol.info-tjs',
                                        'www.ajol.info-jmbs', 'www.annalsofafricansurgery.com', 'www.asjp.cerist.dz',
                                        'www.bahrainmedicalbulletin.com', 'www.bhmedsoc.com', 'www.easpublisher.com-easjacc',
                                        'www.easpublisher.com-easjms', 'www.easpublisher.com-easjop', 'www.easpublisher.com-easjpp',
                                        'www.easpublisher.com-easms', 'www.egyptretinaj.com.asp', 'www.ejdv.eg.net.asp',
                                        'www.ejmsonline.org-Abstracts', 'www.epj.eg.net.asp', 'www.hamdanjournal.org.asp',
                                        'www.hsd-fmsb.org', 'www.iasj.net-13883', 'www.iasj.net-14135',
                                        'www.iraqijms.net', 'www.jaccrafrica.com', 'www.jeos.eg.net.asp',
                                        'www.jomenas.org.com', 'www.journal-jmsr.net', 'www.karger.com',
                                        'www.ljmr.com.ly', 'www.ljmsonline.com.asp', 'www.mbmj.org', 'www.me-jaa.com',
                                        'www.medjbabylon.org.asp', 'www.mejfm.com', 'www.mjemonline.com',
                                        'www.mmjonweb.org.asp', 'www.qscience.com', 'www.saudijournals.com-sjbr',
                                        'www.saudijournals.com-sjls', 'www.saudijournals.com-sjm', 'www.saudijournals.com-sjmps','www.pjms.org.pk','journals.ust.edu'],width=40)
JournalMenu_update.grid(row=8, column=1, columnspan=2, padx=5, pady=5, sticky=W)
JournalMenu_update.current(0)

# Launch the Updater
Button(UI_frame, text='Start The Update', command=Update_thread, bg='green').grid(row=9, column=1, padx=5, pady=5,sticky=W)

UI_frame.grid_columnconfigure(0,weight=1)
Country.bind("<<ComboboxSelected>>", get_sites_by_country)

root.mainloop()