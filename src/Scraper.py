import threading
from time import sleep
import requests
import datetime
from datetime import datetime
from bs4 import BeautifulSoup
from tkinter import ttk
from tkinter import *
import tkinter as tk
from tkinter.messagebox import showinfo
from queue import Queue
from time import strptime
import os
import json

articles = []
Abstracts = []
Issues_links = []
Volume_links = []
PDF_links = []
Abstracts_link = []
shared_queue = Queue()
shared_queue_output = Queue()


def GetPDFs(article):

    def scrapeStructure_A(country, journal, page, main): # journals.ekb.eg 
        soup = parse(page)

        # fetch Volumes available in archive page.
        for volume in soup.find_all('a'):
            if 'Volume ' in  volume.text:
                Volume_links.append(main + volume['href'].replace('./',''))
                print(main + volume['href'].replace('./',''))

        print(f'\n\nGathered {len(Volume_links)} Volumes')
        output_text['text'] = f'Gathering Issues in {len(Volume_links)} Volumes' # ui output text

        # fetch issue links from volumes
        while len(Volume_links) > 0:
            soup = parse(Volume_links.pop())
            links = soup.find_all('a')
            for link in links:
                try:
                    if 'issue_' in link['href']:
                        Issues_links.append(main + link['href'].replace('./',''))
                        print(main + link['href'].replace('./',''))
                except:
                    pass
            print(f'\n{len(Volume_links)} Volumes left')
        print(f'\n\nGathered {len(Issues_links)} Issues')

        output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues' # ui output text

        # fetch PDF links from Issues
        for link in Issues_links:
            try:
                soup = parse(link)
                xml = soup.find('a',{'title':'XML'})['href'] # xmol file available in issue page, contains all data.
                res = requests.get(main + xml)
                soup = BeautifulSoup(res.text,'xml')
                for article in soup.find_all('Article'):
                    year = article.find('Year').text
                    month = article.find('Month').text
                    Volume = article.find('Volume').text
                    issue = article.find('Issue').text
                    Title = article.find('ArticleTitle').text.replace('‎','').replace('‏','') # some titles contain invalid chars, so we removed them.
                    link = article.find('ArchiveCopySource').text
                    print(country+ ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + Volume + ' --- ' + issue + ' --- ' + Title + ' --- ' + link)
                    PDF_links.append(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + Volume + ' --- ' + issue + ' --- ' + Title + ' --- ' + link)
            except:
                pass
        print(f'\n\nGathered {len(PDF_links)} PDFs')
        output_text['text'] = f'Gathered {len(PDF_links)} PDFs' # ui output text

    def scrapeStructure_B(country, journal, page,main): # all ending with .asp
        PDF_Page = []
        global Issues_links, PDF_links
        res = requests.get(page)
        soup = BeautifulSoup(res.text,'html.parser')

        # fetch all Issue pages.
        Issues_links = soup.find_all('a',{'title':'Table of Contents'}) 
        try:
            for issue in Issues_links:
                Issues_links.append(main + issue['href'])
                print(main + issue['href'])
        except:
            pass
        print(f'Gathered {len(Issues_links)} Issues\n')
        output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues' # ui output text

        # fetch PDF pages links (direct pdf links are available in invidual pages seperately)
        while len(Issues_links) > 0:
            try:
                issue = Issues_links.pop()
                res = requests.get(issue)
                soup = BeautifulSoup(res.text,'html.parser')
                links = soup.find_all('a',text = '[PDF]') # all PDF Pages that contain the direct PDF links.
                info = soup.find('table',{'class','articlepage'}).text.replace('\xa0',' ').replace('\n\n','').split('\n')[0].split(' ') # to exract year - month - volume - issue
                year = info[1][:4]

                # some pages post the info differently.
                if len(info[0].split('-')) == 1:
                    month = str(strptime(info[0][:3],'%b').tm_mon)
                else:
                    month = str(strptime(info[0].split('-')[0][:3],'%b').tm_mon) + '/' + str(strptime(info[0].split('-')[1][:3],'%b').tm_mon)

                Volume = info[2]
                issue = info[5].replace('\r','')
                for link in links:
                    PDF_Page.append(year + ' --- ' + month + ' --- ' + Volume + ' --- ' + issue + ' --- ' + main + link['href'])
                    print(year + ' --- ' +month + ' --- ' + Volume + ' --- ' + issue + ' --- ' + main + link['href'])
                print(f'{len(Issues_links)} Issues left\n\n')
            except:
                pass
            
        print(f'\n\nGathered {len(PDF_Page)} PDF pages\n')
        output_text['text'] = f'Gathering direct PDF link in {len(PDF_Page)} PDF pages' # ui output text

        # fetch direct PDF link
        while len(PDF_Page) > 0:
            data = PDF_Page.pop().split(' --- ')
            year = data[0]
            month = data[1]
            Volume = data[2]
            issue = data[3]
            page = data[4]
            res = requests.get(page)
            soup = BeautifulSoup(res.text,'html.parser')

            # fetch title.
            try:
                Title = soup.find('font',{'class':'sTitle'}).text
            except:
                Title = 'Couldn\'nt find title'
            
            links = soup.find_all('a')
            for link in links:
                if '.pdf' in link['href']: # checks if the link fetched is a pdf link
                    PDF_links.append(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + Volume + ' --- ' + issue + ' --- ' + Title + ' --- ' + main + link['href'])
                    print(country+ ' --- ' +journal+ ' --- ' +year + ' --- ' + month + ' --- ' + Volume + ' --- ' + issue + ' --- ' + Title + ' --- ' + main + link['href'])
            print(f'{len(PDF_Page)} Pages left\n\n')
        
        output_text['text'] = f'Gathered {len(PDF_links)} PDFs' # ui output text


    def scrapeStructure_C(country,journal,page,main): # www.karger.com
        stat= True

        # overcome SLL error
        try:
            soup = parse(page,stat)
        except Exception as e:
            if 'SSL' in str(e):
                ans = input('Error while parsing website, do you want to disable SSL verification? (y/n): ')
                if ans.lower() == 'y':
                    soup = parse(page,False)
                    stat = False
                else:
                    print("Program terminated manually!")
                    raise SystemExit
       
       # saves Prev and next page links
        Prev_driver = main + soup.find('a',{'class':'previous'})['href']
        Next_driver = main + soup.find('a',{'class':'next'})['href']
        
        # looping through all Prev pages.
        while Prev_driver != None:
            soup = parse(Prev_driver)
            print(Prev_driver)

            # fetch data.
            C_getPDFs(country,journal,soup,main)

            #checks if there is another Prev page
            try:
                Prev_driver = main +soup.find('a',{'class':'previous'})['href']
            except:
                Prev_driver = None

        print('\nno more previous version')

        # looping through all Next pages.
        while Next_driver != None:
            soup = parse(Next_driver)
            print(Next_driver)
            C_getPDFs(country,journal,soup,main)
            try:
                Next_driver = main + soup.find('a',{'class':'next'})['href']
            except:
                Next_driver = None
        print('\nno more next versions')
    def C_getPDFs(country,journal,soup,main):
        links = soup.find_all('a') # fetch all links

        for link in links:

            # fetch articles info
            info = soup.find('h1',{'class':'mb-0'}).text.lower().replace(' ','').split(',')
            year = info[2][:4]
            volume_nb=info[0].split('vol.')[1]
            issue_nb=info[1].split('.')[1]
            for div in soup.find_all('div'):
                if len(div.text) <=100:
                    if 'release date' in div.text:
                        try:
                            month = str(strptime(div.text.lower().replace('\n','').replace('\r','').replace(' ','').split(':')[1][:3],'%b').tm_mon)
                        except:
                            month = '1'

            # fetch PDF link
            try:
                href = link['href'].lower()
                if 'article/fulltext' in href or 'article/abstract' in href and int(year) >=1998: # checks if link is for abstract or PDF
                    try:
                        block = link['class']
                    except:
                        title=link.text.replace('\n','')
                        if 'abstract' not in title.lower():
                            PDF = href.replace('FullText','PDF').replace('fulltext','PDF').replace('Abstract','PDF').replace('abstract','PDF')
                            PDF_links.append(country+ ' --- ' +journal+ ' --- ' +year+ ' --- ' +month+ ' --- ' +volume_nb+ ' --- ' +issue_nb+ ' --- ' +title+ ' --- ' +main+PDF)
                            print(country+ ' --- ' +journal+ ' --- ' +year+ ' --- ' +month+ ' --- ' +volume_nb+ ' --- ' +issue_nb+ ' --- ' +title+ ' --- ' +main+PDF)
                            output_text['text'] = f'Gathered {len(PDF_links)} PDFs in this page'
            except Exception as e:
                pass

    def scrapeStructure_D(country,journal, page,main): # springeropen
        global Issues_links
        soup = parse(page)
        output_text['text']=f'Gathering PDFs in {len(Issues_links)} Issues.'

        # Issue_links already contains the archive page
        # looping through Issue_links (getting new link every loop)
        while len(Issues_links) > 0:
            soup = parse(Issues_links.pop())

            # fetching PDF links
            for article in soup.find_all('li',{'class':'c-listing__item'}):
                
                if article.find('a',{'data-test':'pdf-link'})['href'].startswith('/'):
                    pdf = main[:-1] + article.find('a',{'data-test':'pdf-link'})['href']
                else:
                    pdf = main + article.find('a',{'data-test':'pdf-link'})['href']

                # fetching info
                info = article.find('span',{'itemprop':'datePublished'}).text.split(' ')
                title = article.find('a',{'data-test':'title-link'}).text.replace('‎','').replace('‏','').replace('\n','')
                year = info[2]
                volume_nb= str(int(year)-2006)
                issue_nb = '1'
                month = str(strptime(info[1][:3],'%b').tm_mon)
                PDF_links.append(country+ ' --- ' +journal+ ' --- ' +year+ ' --- ' +month+ ' --- ' +volume_nb+ ' --- ' +issue_nb+ ' --- ' +title+ ' --- ' +pdf)
                print(country+ ' --- ' +journal+ ' --- ' +year+ ' --- ' +month+ ' --- ' +volume_nb+ ' --- ' +issue_nb+ ' --- ' +title+ ' --- ' +pdf)
            
            # fetching new issue link
            try:
                Issues_links.append(main + soup.find('a',{'data-test':'next-page'})['href'][1:])
            except:
                pass
        output_text['text']=f'Gathered a total of {len(PDF_links)} PDFs.'

    def scrapeStructure_E(country, journal, page,main): # www.journal-jmsr.net
        global PDF_links
        Issues_links = E_getIssues(page,main) # fetching all Issues
        output_text['text'] = f'Gathering PDFs in {len(Volume_links)} Volumes.'
        for issue in Issues_links: # looping through issues
            print(issue)
            soup = parse(issue)

            # info
            info = soup.find('div',{'class':'col-sm-6'}).text.replace(',','').replace('(Special Issue)','').replace('  ',' ').split(' ')
            year = info[5][:4]
            month = str(strptime(info[4][:3],'%b').tm_mon)
            volume_nb = info[1]
            issue_nb = info[3]
            
            # fetching pdf links and title
            for article in soup.find_all('tr'):
                try:
                    title = article.find('a').text.replace('‎','').replace('‏','')
                    pdf = article.find('a',{'title':'Download PDF file'})['href']
                    PDF_links.append(country+ ' --- ' +journal+ ' --- ' +year+ ' --- ' +month+ ' --- ' +volume_nb+ ' --- ' +issue_nb+ ' --- ' +title+ ' --- ' +main+pdf)
                    print(country+ ' --- ' +journal+ ' --- ' +year+ ' --- ' +month+ ' --- ' +volume_nb+ ' --- ' +issue_nb+ ' --- ' +title+ ' --- ' +main+pdf)
                except:
                    pass
    def E_getIssues(page,main,stat=True):

        # overcomming SSL error
        try:
            soup = parse(page,stat)
        except Exception as e:
            if 'SSL' in str(e):
                soup = parse(page,False)
                stat = False
        volumes = []
        links = soup.find_all('a') # fetching all links
        for link in links:
            if 'Vol. ' in link.text: # checking if link fetched is a volume link
                volumes.append(main+link['onclick'].split("','")[0].replace("window.open('",''))
        print(f'{len(volumes)} Volumes gathered')
        output_text['text'] = f'{len(volumes)} Volumes gathered'
        return volumes

    def scrapeStructure_F(country,journal,page,main=''): # batnajms.net
        global res
        soup = parse(page)
        container = soup.find('div',{'class':'entry-content'}) # getting main container that contains all data
        for link in container.find_all('a'): # fetching all links inside the container
            year = link.text.replace(' ','').replace(')','')[-4:]

            # there is a covid 19 issue, its mentioned instead of the year.
            if 'covid-19' in link['href']:
                year = '2020'

            # some links contain both http and https, so we removed one of them
            if 'http://' in link['href'] and 'https://' in link['href']:
                Issues_links.append(year +' '+ link['href'].replace('http://',''))
                print(year +' '+ link['href'].replace('http://',''))
            else:
                Issues_links.append(year +' '+ link['href'])
                print(year +' '+ link['href'])
        print(len(Issues_links))
        output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues.'

        # looping through issue links
        for data in Issues_links:
            issue = data.split(' ')[1]
            year = data.split(' ')[0]
            print('\n'+issue)
            soup = ''

            # this website will timeout the script after certain connections, this loop is to overcome it.
            while soup == '':
                try:
                    soup = parse(issue)
                except :
                    print('Error parsing page, retrying in 10 second:\n')
                    sleep(10)

            # fetching info for yea - month - issue - volume
            info = soup.find('h1',{'class':'entry-title'}).text

            if 'COVID' in info: # covid release don't have details, so we set it manually.
                year = '2022'
                Month = '1'
                Volume_nb = '9'
                issue_nb = '1'
            else:
                Volume_nb = info.lower().split('volume')[1].replace(' ','')[:1]
                Month = '1' # no specific month.
                issue_nb = info[-1]

            # getting the container that contains the PDF links
            container = soup.find('div',{'class':'entry-content'})
            print('\nGetting real PDF link')

            # fetching pdf links
            for article in container.find_all('p'):
                try:
                    Title = article.find('strong').text.replace('‎','').replace('‏','')
                    pdf = article.find('a')['href']
                    print(country+ ' --- ' +journal+ ' --- ' +year+ ' --- ' +Month+ ' --- ' +Volume_nb+ ' --- ' +issue_nb+ ' --- ' +Title+ ' --- ' +pdf)
                    PDF_links.append(country+ ' --- ' +journal+ ' --- ' +year+ ' --- ' +Month+ ' --- ' +Volume_nb+ ' --- ' +issue_nb+ ' --- ' +Title+ ' --- ' +pdf)
                except:
                    pass
        output_text['text'] = f'Gathering PDF links in {len(PDF_links)} Pages'
        links = PDF_links.copy()
        PDF_links.clear()

        # PDF links gathered above are not direct links, they redirect us to the main PDF, so we send a request to each link to get the main link.
        for info in links:
            data=info.split(' --- ')
            country = data[0]
            journal = data[1]
            year = data[2]
            Month = data[3]
            Volume_nb = data[4]
            issue = data[5]
            Title = data[6]
            link = data[7]
            # try:
            res = requests.get(link).url
            if '.pdf' in res:
                    print(country+ ' --- ' +journal+ ' --- ' +year+ ' --- ' +Month+ ' --- ' +Volume_nb+ ' --- ' +issue_nb+ ' --- ' +Title+ ' --- ' +res)
                    PDF_links.append(country+ ' --- ' +journal+ ' --- ' +year+ ' --- ' +Month+ ' --- ' +Volume_nb+ ' --- ' +issue_nb+ ' --- ' +Title+ ' --- ' +res)
            # except:
            #     print(f'Error in URL: {link}')
        
        output_text['text'] = f'Gathered {len(PDF_links)} PDFs'

    def scrapeStructure_G(country, journal, page,main): # journals.ekb.eg  --  bfpc
        global Volume_links,Issues_links,PDF_links
        pages = []
        pages.append(page)
        Volume_links = findAttrintarget(pages,'a','/volume','href','href',main) # getting all Volumes.
        output_text['text'] = f'Gathering Issues in {len(Volume_links)} Volumes'

        for volume in Volume_links: # getting all issues inside each volume page.
            soup = parse(volume)
            for issue_div in soup.find_all('div',{'class':'issue_dv'}):
                Issues_links.append(main+issue_div.find('a')['href'])
        output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues'

        for link in Issues_links: # fetching PDF links from XML file
            soup = parse(link)
            xml = soup.find('a',{'title':'XML'})['href'] # XML file available in issue page contains all data
            res = requests.get(main + xml)
            soup = BeautifulSoup(res.text,'xml')
            for article in soup.find_all('Article'):
                year = article.find('Year').text
                month = article.find('Month').text
                volume_nb = article.find('Volume').text
                issue_nb = article.find('Issue').text
                Title = article.find('ArticleTitle').text.replace('‎','')
                link = article.find('ArchiveCopySource').text
                PDF_links.append(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + volume_nb + ' --- ' + issue_nb + ' --- ' +  Title + ' --- ' +link)

    def scrapeStructure_H(country,journal,page,main=''): # lsj.cnrs.edu.lb
        global PDF_links
        soup = parse(page)
        issues_section = soup.find('div',{'class':'kcite-section'}) # section that contains the issues
        for link in issues_section.find_all('a',{'title':''}): # fetching issues from section
            Issues_links.append(link['href'])
            print(f'{len(Issues_links)} issues gathered')
            output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues '

        for issue in Issues_links: # fetching data from issue links
            print(issue)
            soup = parse(issue)
            info = soup.find('article').find('h1').text.lower().replace(',','').replace('.',' ').replace('  ',' ').split(' ')
            year = info[4]
            volume_nb = info[1]
            issue_nb = info[3]
            month = '1/12'
            if 'special' in issue: # special issue
                issue_nb = '1'

            # PDF links and titles
            for article in soup.find('div',{'class':'kcite-section'}).find_all('div',{'class':'kcite-section'}):
                title = article.text.replace('‎','').replace('‏','').replace('\n','').replace('  ','')
                pdf = article.find('a')['href']
                print(country + ' --- ' + journal + ' --- ' + year + ' --- ' + month + ' --- ' + volume_nb + ' --- ' + issue_nb + ' --- ' +  title + ' --- ' +pdf)
                PDF_links.append(country + ' --- ' + journal +' --- ' + year + ' --- ' + month + ' --- ' + volume_nb + ' --- ' + issue_nb + ' --- ' +  title + ' --- ' +pdf)
        output_text['text'] = f'Gathered {len(PDF_links)} PDFs'
        
    def scrapeStructure_I(page,main): # ljmr.com
        soup = parse(page)
        div = soup.find('div',{'class':'cat-children'}) # section that contains Issues
        for link in div.find_all('a'): #fetching issues from section
            Issues_links.append(main + link['href'])
        print(f'{len(Issues_links)} Issues gathered')
        output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues'
        I_getPDFs(main)
    def I_getPDFs(main):
        global PDF_links
        PDF_pages = []
        while len(Issues_links) > 0:
            soup = parse(Issues_links.pop()) # fetching pages that contains pdf page
            for link in soup.find_all('td',{'class':'list-title'}):
                PDF_pages.append(main + link.find('a')['href'])
                print(main + link.find('a')['href'])
            try: # check for possible next page
                Issues_links.append(soup.find('a',{'data-original-title':'Next'})['href'])
            except:
                pass

        PDF_links = findAttrintarget(PDF_pages,'a','.pdf','href','href',main,True) # get PDF links
        output_text['text'] = f'Gathered {len(PDF_links)} PDFs'

    def scrapeStructure_J(country,journal,page, main): # qscience.com
        global Issues_links
        # gets Volume links then gets Issue links inside every volume
        Issues_links = findAttrintarget(findElemintargetByPartialText([page],'a','Volume ','href',main),'a','','href','href',main)
        output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues'
        J_getPDFs(country, journal,main)
    def J_getPDFs(country,journal,main):
        temp_PDF_pages,temp_PDF_links,PDF_Pages = [],[],[]
        global PDF_links
        while len(Issues_links) > 0:
            issue = Issues_links.pop()
            if 'Size' not in issue: # view all pages
                issue += '?pageSize=100&page=1'
            soup = parse(issue)
            main_div = soup.find('div',{'class':'issue-listing'}) # container that contains articles
            for link in main_div.find_all('a'): # fetching pages that contain pdf links
                if '/jemtac.' in link['href'] and 'doi.org' not in link['href']:
                    try:

                        temp_PDF_pages.append(main + link['href'])
                        print(main + link['href'])
                    except:
                        pass
        PDF_Pages = list(dict.fromkeys(temp_PDF_pages))
        print(f'Gathered a total of {len(PDF_Pages)} PDFs pages')
        output_text['text'] = f'Gathering PDF links in {len(PDF_Pages)} pages'

        # looping through pages and getting data
        while len(PDF_Pages) > 0: 
            page = PDF_Pages.pop()
            sleep(1)
            soup = parse(page)
            try:
                try:
                    month = soup.find('meta',{'name':'citation_date'})['content'].split('/')[1]
                except:
                    month = str(strptime(soup.find('meta',{'name':'citation_date'})['content'].split(' ')[0][:3],'%b').tm_mon)
                volume = soup.find('meta',{'name':'citation_volume'})['content']
                issue = soup.find('meta',{'name':'citation_issue'})['content']
                title = soup.find('meta',{'name':'dc.title'})['content']
                form = soup.find('form',{'class':'ft-download-content__form--pdf'}) # pdf link
                year=volume
                temp_PDF_links.append(country+' --- '+journal+' --- '+year+' --- '+month+' --- '+volume+' --- '+issue+' --- '+title+' --- '+main + form['action'])
                print(country+' --- '+journal+' --- '+year+' --- '+month+' --- '+volume+' --- '+issue+' --- '+title+' --- '+main + form['action'])
            except Exception as e:
                print(page)
                print(e)
        PDF_links = list(dict.fromkeys(temp_PDF_links))
        output_text['text'] = f'Gathered {len(PDF_links)} PDFs'

    def scrapeStructure_K(page,main =''): # www.annalsofafricansurgery
        Volume_links_temp =[]
        global Volume_links
        soup = parse(page)
        print(page)
        for div in soup.find_all('div',{'role':'listitem'}): # fetching Volume links
            year = div.find_all('div',{'data-testid':'richTextElement'})[1].text[-4:]
            Volume_links_temp.append(year + ' ' + div.find('a')['href'])
            print(year + ' ' + div.find('a')['href'])
        Volume_links = list(dict.fromkeys(Volume_links_temp))
        print(f'Gathered a total of {len(Volume_links)} Volumes')
        output_text['text'] = f'Gathering PDFs in  {len(Volume_links)} Volumes'
        K_getPDFs()
    def K_getPDFs():
        PDF_Pages_temp =[]
        PDF_Pages =[]
        global PDF_links
        while len(Volume_links)>0:
            data = Volume_links.pop()
            url = data.split(' ')[1]
            soup = parse(url)
            print(url)
            year = data.split(' ')[0]
            for link in soup.find('div',{'id':'SITE_PAGES_TRANSITION_GROUP'}).find_all('a'): # getting pages that contain the pdfs
                try:
                    PDF_Pages_temp.append(year + ' ' + link['href'])
                    print(year +' ' + link['href'])
                except:
                    pass
            print(f'{len(Volume_links)} not scanned yet')

        PDF_Pages = list(dict.fromkeys(PDF_Pages_temp)) # remove duplucates
        print(f'Gathered {len(PDF_Pages)} PDF Pages')
        output_text['text'] = f'Gathering PDf links in {len(PDF_Pages)} Pages'
        # get pdf links form pages
        PDF_links = findAttrintarget(PDF_Pages,'a','_files','href','href') # getting PDF links from Pages
        print(f'Gathered a total of {len(PDF_links)} PDFs')
        output_text['text'] = f'Gathered a total of {len(PDF_links)} PDFs'

    def scrapeStructure_L(page,main): # jomenas.org
        global Issues_links,PDF_links
        Issues_links = findAttrintarget([page],'a','--vol','href','href',main) # get Issue links
        output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues'
        PDF_links = findElemintargetByPartialText(Issues_links,'a','Download','href',main,True) # get pdf links
        output_text['text'] = f'Gathered {len(PDF_links)} PDFs'

    def scrapeStructure_M(page,main = ''): # academicjournals
        soup = parse(page)
        volumes = soup.find_all('a')
        Abstract_links =[] 
        for volume in volumes: # checking for volume links in all links that we fetched
            if 'ajpp/archive/' in volume['href'].lower():
                Volume_links.append(main + volume['href'])
                print(main + volume['href'])
        print(f'Gathered a total of {len(Volume_links)} Volumes')
        output_text['text'] = f'Gathering issues in {len(Volume_links)} Volumes...'
        Issues_links = findAttrintarget(Volume_links,'a','AJPP/edition','href','href',main) # fetching ISsue links from volumes
        output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues'
        Abstract_links = findAttrintarget(Issues_links,'a','article-abstract','href','href',main,True) # fetching abstracts
        for abstract in Abstract_links: # getting pdf links from abstracts
            year = abstract.split(' ')[0]
            url = abstract.split(' ')[1]
            if url.startswith('http'):
                PDF_links.append(year + ' ' + url.replace('abstract','full-text-pdf'))
            else:
                PDF_links.append(year + ' ' + main + url.replace('abstract','full-text-pdf'))
        
        output_text['text'] = f'Gathered a total of {len(PDF_links)} PDF Links'

    def scrapeStructure_N(page,main=''): # journals.uokerbala.edu.iq
        global Abstracts, Abstracts_link, Issues_links, PDF_links
        soup = parse(page)
        for li in soup.find('ul',{'class':'issues_archive'}).find_all('li',recursive=False): # fetching ISsue links
            for issue in li.find_all('a'):
                if 'view' in issue['href']:
                    Issues_links.append(issue['href'])
        output_text['text'] = f'Gathering PDFs in  {len(Issues_links)} Issues'
        temp = Issues_links.copy()
        Abstracts_link = findAttrintarget(Issues_links,'a','article/view','href','href',main,True) # fetching abstracts links
        PDF_links = findAttrintarget(temp,'a','obj_galley_link','class','href',main,True) # fetching PDFs
        Abstract_links_temp = Abstracts_link.copy()
        print(len(PDF_links))
        print(len(Abstracts_link))
        while len(Abstract_links_temp)>0: # getting abstracts from abstract link ( some articles don't have pdfs )
            data = Abstract_links_temp.pop()
            soup = parse(data.split(' ')[1])
            year = data.split(' ')[0]
            try:
                Abstracts.append(year+ ' '+ soup.find('section',{'class','item abstract'}).text.lower())
                print(f'Gathered {len(Abstracts)} Abstracts!')
                output_text['text'] = f'Gathered {len(Abstracts)} Abstracts!'
            except:
                pass

    def scrapeStructure_O(page,main =''): # ejmsonline.org
        Issues_links_temp = []
        Volume_links = findElemintargetByPartialText([page],'a','Volume ','href',main) # fetching Volume links
        output_text['text'] = f'Gathering Issues in {len(Volume_links)} Volumes'
        while len(Volume_links)>0:
            parse(Volume_links.pop())
            Issues_links_temp = findAttrintarget(Volume_links,'a','abstracts','href','href',main,True) # fetching Issue links
            Issues_links.extend(Issues_links_temp)
            print(f'{len(Issues_links)} Issues gathered in total.')
            output_text['text'] = f'Gathering Abstracts in {len(Issues_links)} Issues'
        while len(Issues_links)>0: # fetching abstracts ( this website has no pdfs)
            data = Issues_links.pop()
            link = data.split(' ')[1]
            year = data.split(' ')[0]
            if 'search' not in link:
                Abstracts_link.append(year+ ' ' +link)
        output_text['text'] = f'Gathered {len(Abstracts_link)} Abstracts'

    def scrapeStructure_P(main): # mejfm.com

        global PDF_links
        #  Old Archives Pages 
        #  Only full issue pdf is available
        #  Should add page in which the API was detected
        
        Issues_links.extend(['http://www.mejfm.com/Archives%202014%20-%202016.htm','http://www.mejfm.com/Archives%20June%202003-December%202013.htm','http://www.mejfm.com/archive.htm'])
        output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues'
        PDF_links = findAttrintarget(Issues_links,'a','.pdf','href','href',main,True)
        temp = PDF_links.copy()
        PDF_links.clear()
        for link in temp:
            PDF_links.append(f'0 {link}')# year = 0 / no year abailable
        output_text['text'] = f'Gathered {len(PDF_links)} PDFs'

    def scrapeStructure_Q(pages): # anafrimed.net
        global Issues_links, PDF_links
        PDF_Pages,PDF_Pages_temp = []
        for page in pages: # looping through archive pages.
            soup = parse(page)

            #fetching Issue links
            Issues_links_temp=soup.find_all('a',{'class':'theme-button'})
            for issue in Issues_links_temp:
                Issues_links.append(issue['href'].replace('https','http'))
            print(f'\n\ngathered a total of {len(Issues_links)} Issues')
            output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues'

            while len(Issues_links) > 0: #fetching pages that contain pdf links
                issue = Issues_links.pop()
                soup = parse(issue)
                main_div = soup.find('div',{'class':'single-blog-content entry clr'})# main container
                links = main_div.find_all('a')
                for link in links:
                    if 'anafrimed.net' in link['href']:
                        PDF_Pages_temp.append(link['href'].replace('https','http'))
                        print(link['href'].replace('https','http'))
                print(f'\n\n{len(Issues_links)} issues left')

                
            PDF_Pages = list(dict.fromkeys(PDF_Pages_temp)) # removing duplicates
            print(f'\n\ngathered a total of {len(PDF_Pages)} PDF Pages')
            output_text['text'] = f'gathering PDF links in {len(PDF_Pages)} Pages'
            print('\n\nNow getting PDF links')

            while len(PDF_Pages) > 0:# getting data from pages.
                issue = PDF_Pages.pop()
                print(issue)
                soup = parse(issue)
                try:
                    year = soup.find('meta',{'property':'article:modified_time'})['content'][0:4]
                    link = soup.find('a',{'class':'download-link'})# pdf link
                    print(year + ' '+link['href'].replace('https','http'))
                    PDF_links.append(year + ' '+link['href'].replace('https','http'))
                except:
                    pass
            output_text['text'] = f'Gathered {len(PDF_links)} PDFs'

    def scrapeStructure_R(page,main): # rmsjournal.org/
        global Issues_links, PDF_links
        soup = parse(page)
        for link in soup.find_all('a'): # getting issue links
            if 'Articles.aspx?VolId=' in link['href']:
                Issues_links.append(main+link['href'])
        output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues'
        PDF_links.extend(findAttrintarget(Issues_links,'a','.pdf','href','href',main,True)) # fetching PDf links
        output_text['text'] = f'Gathered {len(PDF_links)} PDFs'

    def scrapeStructure_S(country, journal,page,main): # www.iasj.net

        # this website has JS.

        soup = parse(page)
        code = soup.find('div',{'class':'isL'})['data-link'] # code used to load page using requests
        headers = returnRequestHeader(page) # adding header

        # request to load page instantly.
        soup = BeautifulSoup(requests.request("POST", f'https://www.iasj.net/iasj/issuesList/{code}', headers=headers, data={}).text,'html.parser')
        
        # fetching issue links
        for link in soup.find_all('a'):
            if '/iasj/issue' in link['href']:
                Issues_links.append(main+link['href'])
        
        print(len(Issues_links))
        output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues'

        while len(Issues_links) > 0:
            issue = Issues_links.pop()
            soup = parse(issue)
            print(issue)

            #new code for every page.
            code = soup.find('div',{'class':'arL'})['data-link']

            # info for details.
            info = soup.find('div',{'class':'narrowContent w3-container'}).find('h3').text
            year = info[0:4]
            month = '01/12'
            Volume_nb = '1'
            issue_nb = info.lower().split('issue')[1].replace(' ','')[:1]

            #adding header and loading the page (also contains JS so we used the code we got above)
            headers = returnRequestHeader(issue)
            soup = BeautifulSoup(requests.request("POST", f'https://www.iasj.net/iasj/issueList/{code}', headers=headers, data={}).text,'html.parser')
            
            articles = soup.find_all('div',{'class':'w3-section'}) # main section that contains the articles
            
            for article in articles:# fetching pdf links inside the main container.
                Title = article.find('h4').text.replace('‎','').replace('‏','').replace('  ','')
                for link in article.find_all('a'):
                    try:
                        if 'iasj/pdf' in link['href'] or 'iasj/download' in link['href']:
                            PDF_links.append(country+ ' --- ' +journal+ ' --- ' +year+ ' --- ' +month+ ' --- ' +Volume_nb+ ' --- ' +issue_nb+ ' - '  +Title + ' -  '+ main+link['href'])
                            print(country+ ' --- ' +journal+ ' --- ' +year+ ' --- ' +month+ ' --- ' +Volume_nb+ ' --- ' +issue_nb+ ' --- ' + Title + ' --- ' + main+link['href'])
                    except:
                        pass
            print(f'{len(Issues_links)} Targets left')
        output_text['text'] = f'Gathered {len(PDF_links)} PDFs'

    def scrapeStructure_T(country,journal, page,main): # www.easpublisher.com
        global Issues_links,PDF_links
        PDF_links_temp = []
        Issues_links = findAttrintarget([page],'a','issue-box','class','href',main) # fetching issue links
        for issue in Issues_links:
            soup = parse(issue)
            try: # fetching info for details
                date = soup.find('span',{'class':'article-tags'}).text.split('|')[1].replace(' ','')
                info = soup.find('section',{'class':'container'}).find('p').text.lower().split('volume')[1].split('-')
            except:
                month=Volume_nb=issue_nb= '1'

            year = date[-4:]
            month = str(strptime(date[:3],'%b').tm_mon)
            info = soup.find('section',{'class':'container'}).find('p').text.lower().split('volume')[1].split('-')
            Volume_nb = info[1]
            issue_nb = info[3]
            for article in soup.find_all('div',{'class':'has-padding-left-20 has-padding-top-20 has-padding-bottom-10'}): # looping through containers that contains the articles
                Title = article.find('a').text.replace('‎','').replace('‏','') # title
                pdf = article.find('a')['href'] # pdf
                if pdf.startswith('.') or pdf.startswith('/') : # some links starts with . or / so i removed them because of our "main" variable 
                    PDF_links_temp.append(country + ' --- ' + journal+ ' --- ' +year + ' --- ' + month + ' --- ' + Volume_nb + ' --- ' + issue_nb + ' --- ' + Title + ' --- ' + main + pdf[1:])
                    print(country + ' --- ' + journal+ ' --- ' +year + ' --- ' + month + ' --- ' + Volume_nb + ' --- ' + issue_nb + ' --- ' + Title + ' --- ' + main + pdf[1:])
                    
                else:
                    PDF_links_temp.append(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + Volume_nb + ' --- ' + issue_nb + ' --- ' + Title + ' --- ' + main + pdf)
                    print(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + Volume_nb + ' --- ' + issue_nb + ' --- ' + Title + ' --- ' + main + pdf)
                    
            PDF_links = list(dict.fromkeys(PDF_links_temp))
    
    def scrapeStructure_U(country,journal,page,main): # amj  --  iphr  --  bjsrg
        global Issues_links,PDF_links
        PDF_links_temp = []
        Issues_links = findAttrintarget([page],'a','/issue_','href','href',main) # issue links
        print(len(Issues_links))
        for issue in Issues_links:
            soup = parse(issue)
            xml_file = soup.find('li',{'class':'galley-links-items'}).find('a')['href'] # xml that contains all data.
            res = requests.get(main+xml_file)
            soup_info = BeautifulSoup(res.text,'xml')
            for article in soup_info.find_all('Article'): # looping through articles in the xml
                try:
                    year = article.find('Year').text
                    month = article.find('Month').text
                    Volume_nb = article.find('Volume').text
                    issue_nb = article.find('Issue').text
                    Title = article.find('ArticleTitle').text.replace('‎','').replace('‏','')
                    pdf= article.find('ArchiveCopySource').text
                    PDF_links_temp.append(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + Volume_nb + ' --- ' + issue_nb + ' --- ' + Title + ' --- ' + main + pdf)
                except:
                    pass
        PDF_links = list(dict.fromkeys(PDF_links_temp))

    def scrapeStructure_V(country,journal, page,main): # journals.ju
        global Issues_links,PDF_links
        PDF_links_temp = []
        Volume_links.append(page)
        soup = parse(page,False)

        try: # pages
            for link in soup.find_all('a'):
                if 'page=2' in link['href'].lower():
                    Volume_links.append(link['href'])
        except:
            pass

        Issues_links = findAttrintarget(Volume_links,'a','issue/view','href','href',main) # getting issue links
        for issue in Issues_links:
            try:
                soup = parse(issue,False) # getting details
                info = soup.find('div',{'id':'main'}).find('h2').text.lower().replace('(','').replace(')','').split(',')
                Volume_nb = info[0].split(' ')[1]
                issue_nb = info[1].split(' ')[2]
                Month = '1'
                year = info[1].split(' ')[3]
                articles = soup.find_all('table',{'class':'tocArticle'}) # table for each article
            except:
                pass

            for article in articles: # looping through tables (articles)
                try:
                    # title and pdf link
                    Title = article.find('div',{'class':'tocTitle'}).text.replace('‎','').replace('‏','').replace('\n','')
                    links = article.find('div',{'class':'tocGalleys'}).find_all('a')
                    for link in links:
                        if 'download' in link.text.lower():
                            pdf = link['href']
                            print(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + Month + ' --- ' + Volume_nb + ' --- ' + issue_nb + ' --- ' + Title + ' --- ' + main + pdf)
                            PDF_links_temp.append(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + Month + ' --- ' + Volume_nb + ' --- ' + issue_nb + ' --- ' + Title + ' --- ' + main + pdf)
                except:
                    pass
        
        PDF_links = list(dict.fromkeys(PDF_links_temp))

    def scrapeStructure_W(country,page,main): # bahrainmedicalbulletin  --  not finished yet
        global Issues_links,PDF_links
        PDF_links_temp = []
        Volume_links.append(page)
        Issues_links = findAttrintarget(Volume_links,'a','issue_','href','href',main)
        for issue in Issues_links:
            soup = parse(issue)
            date = issue.split('.htm')[0].split('issue_')[1]
            year = date[-4:]
            if 'current' in date:
                month = datetime.now().month
            else:
                month = str(strptime(date[:3],'%b').tm_mon)
            info = soup.find('em').text
            try:
                volume_nb = info.lower().split('volume')[1].replace(' ','').split(',')[0]
                if 'no.' in info:
                    issue_nb = info.lower().split('no.')[1].replace(' ','').replace('\n','').split(',')[0]
                else:
                    issue_nb = info.lower().split('number')[1].replace(' ','').replace('\n','').split(',')[0]

            except:
                volume_nb = issue_nb = 0
            for link in soup.find_all('a'):
                try:
                    href=link['href']
                    if'.pdf'in href:
                        print(href)
                        data = link.parent.parent.parent.find('font').text.split('\n')
                        temp = data[0] + data[1]
                        title = temp.replace('  ','-').replace('-',' ')
                        print(title)
                except:
                    pass
            # print(country + ' - '+title+' - '+year+' - '+month+' - '+volume_nb+' - '+issue_nb+' - '+title)
          
    def scrapeStructure_X(country,journal,page,main): # saudijournals.com
        Issues_links = findAttrintarget([page],'a','issue-box','class','href',main) # issue links
        for issue in Issues_links:
            soup = parse(issue)

            #info for details
            info = soup.find('div',{'class':'px-3 py-2 fs-5'}).text.replace(' ','').split('|')
            Volume_nb = info[0].split('-')[1]
            issue_nb = info[1].split('-')[1][:2]

            for div in soup.find_all('div',{'class':'article-box mt-3'}): # containers that contains the articles
                data = div.find('div').find('div').text.split('|')[1].replace(' ','')
                year = data[-4:]
                Month = str(strptime(data[:3],'%b').tm_mon)
                Title = div.find('div').find_all('div')[1].text
                pdf = div.find('div',{'class':'px-3 py-2'}).find_all('a')[1]['href']
                PDF_links.append(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + Month + ' --- ' + Volume_nb + ' --- ' + issue_nb + ' --- ' + Title + ' --- ' + main + pdf)
                print(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + Month + ' --- ' + Volume_nb + ' --- ' + issue_nb + ' --- ' + Title + ' --- ' + main + pdf)

    def scrapeStructure_Y(country,journal,page,main): # medtech.ichsmt.org
        Volume_links.append(page)
        soup = parse(page)
        try: # trying to get next pages
            Volume_links.append(soup.find('a',{'class':'next'})['href'])
        except:
            pass

        Issues_links = findAttrintarget(Volume_links,'a','issue/view','href','href',main) # issue links
        count = 0
        dictionary = {}
        for issue in Issues_links:
            print(issue)
            soup = parse(issue)

            # date
            published = soup.find('div',{'class':'published'}).find('span',{'class':'value'}).text.replace('\n','').split('-')

            year = published[0]
            month = published[1]

            #data for details
            data = soup.find('span',{'aria-current':'page'}).text.lower()
            Volume_nb = data.split('vol. ')[1].split(' ')[0]
            issue_nb = data.split('no. ')[1].split(' ')[0]
            try: # getting title and pdf link
                json_file = open(f'Articles/{country}/{journal}/info.json','w')
                for div in soup.find_all('div',{'class':'section'}): # section for each article
                    for li in div.find('ul').find_all('li',recursive=False):
                        title = li.find('h3',{'class':'title'}).text.replace('\n','')
                        pdf = li.find('li').find('a')['href']
                        soup=parse(pdf)
                        pdf_link = soup.find('a',{'class','download'})['href']
                        response = requests.get(pdf_link)
                        dictionary[count]={}
                        dictionary[count] = {
                        "title": title,
                        "url": pdf,
                        "year": year,
                        "month":month,
                        "volume":Volume_nb,
                        "issue":issue_nb,
                        "id":count}
                        pdf_file = open(f'Articles/{country}/{journal}/{count}.pdf','wb')
                        count+=1
                        pdf_file.write(response.content)
                        pdf_file.close()
                        response.close()
            except Exception as e:
                print(e)
            json.dump(dictionary, json_file,indent=2)
    
    def scrapeStructure_Z(country,journal,page,main=''): # videos
        Issues_links = findAttrintarget([page],'a','issue/view','href','href',main)
        
        count = 0
        dictionary = {}
        for issue in Issues_links:
            try:
                soup = parse(issue)
            except:
                sleep(10)
                soup = parse(issue)

            info = soup.find('div',{'class':'page-header page-issue-header'}).find('h1').text
            year = info.split('(')[1][:4]
            issue_nb = info.split('.')[1].split(' ')[1]
            month = '1-12'
            volume_nb = '1'
            try:
                json_file = open(f'Articles/{country}/{journal}/info.json','w')
                for div in soup.find_all('div',{'class':'article-summary'}):
                    title = div.find('div',{'class':'article-summary-title'}).text.replace('?','').replace(':','')
                    for char in title:
                        if not char.isalpha():
                            title = title.replace(char,'')
                        else:
                            break
                    pdf = div.find('div',{'class':'article-summary-galleys'}).find('a')['href']
                    response = requests.get(pdf.replace('view','download'))

                    dictionary[count]={}
                    dictionary[count] = {
                        "title": title,
                        "url": pdf,
                        "year": year,
                        "month":month,
                        "volume":volume_nb,
                        "issue":issue_nb,
                        "id":count}
                    pdf_file = open(f'Articles/{country}/{journal}/{count}.pdf','wb')
                    count+=1
                    pdf_file.write(response.content)
                    pdf_file.close() 
            except Exception as e:
                print(e)
            json.dump(dictionary, json_file,indent=2)
            json_file.close()
    
    def scrape__www_pjms_org_pk(country, journal,page,main=''):
        global Volume_links
        temp = [page]
        Volume_links.append(page)
        while len(temp)>0:
            soup = parse(temp.pop())
            try:
                temp.append(soup.find('a',{'class':'next'})['href'])
                Volume_links.append(soup.find('a',{'class':'next'})['href'])
            except:
                pass
        Issues_links = findAttrintarget(Volume_links,'a','title','class','href',main)
        for issue in Issues_links:
            print(issue)
            soup = parse(issue)
            info = soup.find('title').text.replace('\n','').replace('\t','').split(' ')
            volume = info[1]
            issue_nb = info[3]
            published = soup.find('div',{'class':'published'}).find('span',{'class':'value'}).text.replace('\n','').replace('\t','').split('-')
            year = published[0]
            month = published[1]
            for section in soup.find_all('ul',{'class':'cmp_article_list articles'}):
                for article in section.find_all('li',recursive=False):
                    try:
                        title = article.find('div',{'class':'title'}).text.replace('\n','').replace('\t','')
                        pdf = article.find('a',{'class':'obj_galley_link pdf'})['href']
                        PDF_links.append(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + volume + ' --- ' + issue_nb + ' --- ' + title + ' --- ' + main + pdf)
                        print(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + volume + ' --- ' + issue_nb + ' --- ' + title + ' --- ' + main + pdf)
                    except:
                        pass
    def scrape__journals_ust_edu(country,journal,page,main=''):
        Issues_links = findAttrintarget([page],'a','title','class','href',main)
        for issue in Issues_links:
            print(issue)
            soup = parse(issue)
            try:
                info = soup.find('li',{'class':'active'}).text.replace('\n','').replace('\t','').split(' ')
                volume = info[1]
                issue_nb = info[3]
                year = info[4].replace('(','').replace(')','')
                month = '1/12'
            except:
                info = soup.find('section',{'class':'current_issue'}).find('header',{'class':'page-header'}).text.replace('\n','').replace('\t','').split('|')
                year = info[2].split(':')[1].split('-')[0]
                month = info[2].split(':')[1].split('-')[1]
                volume = info[1][1:].split(' ')[1]
                issue_nb = info[1][1:].split(' ')[3]

            for article in soup.find_all('div',{'class':'media-body'}):
                try:
                    title = article.find('h3',{'class':'media-heading'}).text.replace('\n','').replace('\t','')
                    pdf = article.find('a',{'class':'galley-link btn btn-default role='})['href']
                    PDF_links.append(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + volume + ' --- ' + issue_nb + ' --- ' + title + ' --- ' + main + pdf)
                    print(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + volume + ' --- ' + issue_nb + ' --- ' + title + ' --- ' + main + pdf)
                except:
                    pass
    def scrape__ajol_info(country,journal,page,main=''):
        Issues_links = findAttrintarget([page],'a','title','class','href',main)
        for issue in Issues_links:
            print(issue)
            soup = parse(issue)
            try:
                info = soup.find('span',{'aria-current':'page'}).text.replace('\n','').replace('\t','').split(' ')
                volume = info[1]
                issue_nb = info[3]
                year = info[4].replace('(','').replace(')','')
                month = '1/12'
            except Exception as e:
                print(issue)
                print(e)
                info = soup.find('span',{'aria-current':'page'}).text.replace('\n','').replace('\t','').split(' ')
                volume = info[1]
                issue_nb = '1'
                year = info[2].replace('(','').replace(')','')
                month = '1/12'

            for article in soup.find_all('div',{'class':'obj_article_summary'}):
                try:
                    title = article.find('div',{'class':'title'}).text.replace('\n','').replace('\t','')
                    pdf = article.find('a',{'class':'obj_galley_link pdf'})['href']
                    PDF_links.append(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + volume + ' --- ' + issue_nb + ' --- ' + title + ' --- ' + main + pdf)
                    print(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + volume + ' --- ' + issue_nb + ' --- ' + title + ' --- ' + main + pdf)
                except Exception as e:
                    print(e)
    def scrape__journals_squ_edu_om(country,journal,page,main=''):
        Issues_links = findAttrintarget([page],'a','title','class','href',main)
        for issue in Issues_links:
            print(issue)
            soup = parse(issue)
            try:
                info = soup.find('li',{'class':'active'}).text.replace('\n','').replace('\t','').split(' ')
                volume = info[1]
                issue_nb = info[3]
                year = info[4].replace('(','').replace(')','')[:4]
                month = str(strptime(info[5][:3],'%b').tm_mon)
                
            except Exception as e:
                print(issue)
                print(e)
                # info = soup.find('span',{'aria-current':'page'}).text.replace('\n','').replace('\t','').split(' ')
                # volume = info[1]
                # issue_nb = '1'
                # year = info[2].replace('(','').replace(')','')
                # month = '1/12'

            for article in soup.find_all('div',{'class':'article-summary media'}):
                # try:
                    title = article.find('h3',{'class':'media-heading'}).text.replace('\n','').replace('\t','')
                    pdf = article.find('a',{'class':'galley-link pdf'})['href']
                    PDF_links.append(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + volume + ' --- ' + issue_nb + ' --- ' + title + ' --- ' + main + pdf)
                    print(country + ' --- ' +journal+ ' --- ' + year + ' --- ' + month + ' --- ' + volume + ' --- ' + issue_nb + ' --- ' + title + ' --- ' + main + pdf)
                # except Exception as e:
                #     print(e)
    # joker functions
    def make_dir(parent,dir):
        try:
            os.mkdir(f"{parent}/{dir}")
        except:
            pass
    def scrapeRequests(country, page,main,issueTag,issueTxtSearch,issueattrSearch,IssueTargetAttr,PDfTag,PDFTxtSearch,PDFattrSearch,PDFTargetAttr,info_issue=False,info_pdf=False,stat=True):
                global Issues_links,PDF_links
                Volume_links.append(page)
                Issues_links = findAttrintarget(Volume_links,issueTag,issueTxtSearch,issueattrSearch,IssueTargetAttr,main,info_issue)
                PDF_links_temp = findAttrintarget(Issues_links,PDfTag,PDFTxtSearch,PDFattrSearch,PDFTargetAttr,main,info_pdf)
                for x in PDF_links_temp:
                    PDF_links.append(country + ' --- ' + x)
    def parse(url,stat=True):
        payload = {}
        headers = returnRequestHeader(url)

        print('\nparsing')
        try:
            res = requests.get(url, verify=stat ,headers=headers, data=payload)
            soup = BeautifulSoup(res.text,'html.parser')
            res.close()
            return soup
        except:
            print('parse failed, retrying...')
            sleep(2)
            res = requests.get(url, verify=stat ,headers=headers, data=payload)
            soup = BeautifulSoup(res.text,'html.parser')
            res.close()
            return soup
    def returnRequestHeader(page): # returns header for 
        return {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8;',
            'Accept-Language': "lang=AR-DZ",
            'Connection': 'keep-alive',
            'Referer': f'{page}',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
            }
    def findAttrintarget(pages,tag,text,attr,target,main='',get_year=False,stat=True):
        result = []
        print(f'\nscanning through {len(pages)} targets')

        # loop through pages provided as parameter.
        while len(pages) > 0:
            data = pages.pop()
            year = ''

            # checks if data has anything other than a link
            if ' ' in data:
                url = data.split(' ')[1]
                year = data.split(' ')[0]
            else:
                url = data
            
            # overcome SSL error for some websites.
            try:
                soup = parse(url,stat)
            except Exception as e:
                if 'SSL' in str(e):
                    ans = input('Error while parsing website, do you want to disable SSL verification? (y/n): ')
                    if ans.lower() == 'y':
                        soup = parse(url,False)
                        stat = False
                    else:
                        print("Program terminated manually!")
                        raise SystemExit
                else:
                    print(e)
                    raise SystemExit
            print(url)

            # Gets the year of the article, every case is for a specific website
            for link in soup.find_all(tag):
                if get_year == True: 

                    if 'mchandaids.org' in url:
                        year = soup.find('div',{'obj_issue_toc'}).find('div',{'class':'published'}).find('span',{'class':'value'}).text.split('-')[0][-4:]
                    elif 'journalskuwait.org' in url:
                        year = soup.find('div',{'obj_issue_toc'}).find('div',{'class':'published'}).find('span',{'class':'value'}).text.split('-')[2][0:4]
                    elif 'mjemonline.com' in url:
                        year = soup.find('div',{'class':'container page-issue'}).find('h1').text.replace(')','')[-4:]
                    elif 'ljmr.com' in url:
                        year = soup.find('time',{'itemprop':'datePublished'})['datetime'][0:4]
                    elif 'ajps.uomustansiriyah.edu.iq' in url:
                        year = soup.find('div',{'class':'page page_issue'}).find('h1').text.split(':')[0].replace(')','')[-4:]
                    elif 'uobaghdad' in url:
                        year = soup.find('nav',{'class':'cmp_breadcrumbs'}).text.split(':')[0].replace(')','').replace('\n','')[-4:]
                    elif 'mbmj.org' in url:
                        year = soup.find('div',{'class':'page-header page-issue-header'}).find('h1').text.replace(')','')[-4:]
                    elif 'rmsjournal.org' in url:
                        year = soup.find('div',{'class':'left-bar'}).find('h3').text[-4:]
                        if '-' in year:
                            year = '2021'
                    elif 'gssrr.org' in url:
                        year = soup.find('title').text.split(')')[0][-4:]
                    elif 'www.asjp.cerist.dz' in url:
                        year = soup.find('div',{'class':'full-width-media-text'}).find('p').text.split('-')[-3][-4:]
                    elif 'academicjournals.org' in url:
                        year = soup.find('h3',{'class':'black'}).text.split(';')[0][-4:]
                        if 'May' in year:
                            year = '2010'
                    elif 'ajol.info' in url:
                        year = soup.find('title').text.split(')')[0][-4:]
                    elif 'journals.uokerbala.edu.iq' in url:
                        year = soup.find('title').text.split(')')[0][-4:]
                    elif 'www.iraqijms.net' in url:
                        year = soup.find('div',{'class':'hh5'}).text[-4:]
                    elif 'iraqmedj.org' in url:
                        year = soup.find('title').text.split(')')[0][-4:]
                    elif 'rmr.smr.ma' in url:
                        year = soup.find('ul',{'class':'uk-breadcrumb'}).find('li',{'class':'uk-active'}).text.replace(')','').replace(' ','')[-4:]
                        if year == 'néro':
                            year = str(datetime.date.today().year)
                    elif 'hsd-fmsb.org' in url:
                        year = soup.find('title').text.split(')')[0][-4:]
                    elif 'phcfm.org' in url:
                        print(soup.find('div',{'id':'content'}).find('p').text)
                        year = soup.find('div',{'id':'content'}).find('p').text.split('year: ')[1][0:4]
                    elif 'revues.imist.ma' in url:
                        year = soup.find('title').text.split(')')[0][-4:]
                        print(year)
                    elif 'bfpc.journals.ekb.eg' in url:
                        year = soup.find('div',{'class':'weight-200 nomargin-top'}).find('span').find('span').text.replace(' ','')[-4:]
                    elif 'ejmsonline.org' in url:
                        year = soup.find('h3',{'id':'issue-name'}).text[-4:]
                

                # fetch data depending on the parameters provided
                try:
                    if link[attr] != None and link[target] != None:
                        if text in link[attr]:
                            if link[target].startswith('.') or link[target].startswith('/') :
                                if year!='':
                                    result.append(year + ' ' + main + link[target][1:])
                                    print(year + ' ' + main + link[target][1:])
                                else:
                                    result.append(main + link[target][1:])
                                    print(main + link[target][1:])
                            else:
                                if year!='':
                                    result.append(year + ' ' + main + link[target])
                                    print(year + ' ' + main + link[target])
                                else:
                                    result.append(main + link[target])
                                    print(main + link[target])
                except:
                    pass
            print(f'{len(pages)} Targets left.')
        print(f'Gathered {len(result)} results.')
        output_text['text'] = f'gathered {len(result)} results' # output text to UI
        return list(dict.fromkeys(result)) # remove duplicates
    def findElemintargetByPartialText(pages, tag,text, target,main ='',selectyear = False):
        result = []
        for page in pages:
            soup = parse(page)
            print(page)
            year = ''
            if selectyear == True:
                if 'www.jomenas.org' in page:
                    for strong in soup.find_all('strong'):
                        strong = strong.text[-4:]
                        if strong.isnumeric():
                            year = strong
                if 'phcfm.org' in page:
                    year = soup.find('title').text.split('(')[1][0:4]
            for link in soup.find_all(tag):
                if text in link.text:
                    try:
                        if year != '':
                            print(year + ' ' + main + link[target])
                            result.append(year + ' ' + main + link[target])
                        else:
                            print(main + link[target])
                            result.append(main + link[target])
                    except:
                        pass
        return list(dict.fromkeys(result))
    
    # update UI 
    def update_PB_output():
        output_text.config(text=shared_queue_output.get())
    def Update_PB_update():
        data = shared_queue.get()
        while data != 'finished':
            data = shared_queue.get()
            update_PB_output()
        showinfo(message='Update has been complete, Please place the new file inside "Pdf list per site" folder to be used in scanning!')
        pb.stop()
        pb.destroy()

    def Scraper(article=article):
        pb.start(30)
        global PDF_links, Abstracts_link,Issues_links
        errors = open('ErrorLogs.txt','w', encoding="utf-8")
        file = ''
        print(article)

        # for every website we initialize - Country, journal, archive page, open/create a file and call its function
        if 'journals.ekb.eg' in article: # sent to database
            country = 'Egypt'
            if 'bfpc' in  article:
                journal = 'Bulletin of Faculty of Pharmacy, Cairo University'
                archives_page = 'https://bfpc.journals.ekb.eg/'
                scrapeStructure_G(country,journal,archives_page,'https://bfpc.journals.ekb.eg/')
                file = open("bfpc.journals.ekb.eg.txt",'w', encoding="utf-8")
            else:
                if 'ajps' in article:
                    journal = 'Al-Azhar Journal of Pharmaceutical Sciences'
                    archives_page = 'https://ajps.journals.ekb.eg/'
                    file = open("ajps.journals.ekb.eg.txt",'w', encoding="utf-8")
                    main = 'https://ajps.journals.ekb.eg/'
                if 'ebwhj' in article:
                    journal = 'Evidence Based Women Health Journal'
                    archives_page = 'https://ebwhj.journals.ekb.eg/'
                    file = open("ebwhj.journals.ekb.eg.txt",'w', encoding="utf-8")
                    main = 'https://ebwhj.journals.ekb.eg/'
                if 'aeji' in article:
                    journal = 'Afro-Egyptian Journal of Infectious and Endemic Diseases'
                    archives_page = 'https://aeji.journals.ekb.eg'
                    file = open("aeji.journals.ekb.eg.txt",'w', encoding="utf-8")
                    main = 'https://aeji.journals.ekb.eg/'
                scrapeStructure_A(country,journal,archives_page, main)
        elif '.asp' in article: # ready to send - PDF Links should update every x hours 
            if 'ljmsonline' in article: # website changed!!
                journal = 'Libyan Journal of Medical Sciences'
                archives_page = 'https://www.ljmsonline.com/backissues.asp' 
                main= 'https://www.ljmsonline.com/'
                file = open('www.ljmsonline.com.txt','w', encoding="utf-8")
                country = 'Lybia'
            elif 'epj.eg.net' in article:
                journal = 'Egyptian Pharmaceutical Journal'
                archives_page = 'https://www.epj.eg.net/backissues.asp'
                main= 'https://www.epj.eg.net/'
                file = open('www.epj.eg.net.txt','w', encoding="utf-8")
                country = 'Egypt'
            elif 'egyptretinaj' in article:
                journal = 'Egyptian Retina Journal'
                archives_page = 'https://www.egyptretinaj.com/backissues.asp'
                main = 'https://www.egyptretinaj.com/'
                file = open('www.egyptretinaj.com.txt','w', encoding="utf-8")
                country = 'Egypt'
            elif 'jeos.eg.net' in article:
                journal = 'Journal for the Egyptian Ophthalmology Society'
                archives_page = 'https://www.jeos.eg.net/backissues.asp'
                main = 'https://www.jeos.eg.net/'
                file = open('www.jeos.eg.net.txt','w', encoding="utf-8")
                country = 'Egypt'
            elif 'ejdv.eg.net' in article:
                journal = 'Egyptian Journal of Dermatology and Venerology'
                archives_page = 'https://www.ejdv.eg.net/backissues.asp'
                main = 'https://www.ejdv.eg.net/'
                file = open('www.ejdv.eg.net.txt','w', encoding="utf-8")
                country = 'Egypt'
            elif 'hamdanjournal' in article:
                journal = 'HMJ-Hamdan Medical Journal'
                archives_page = 'https://www.hamdanjournal.org/backissues.asp'
                main = 'https://www.hamdanjournal.org/'
                file = open('www.hamdanjournal.org.txt','w', encoding="utf-8")
                country = 'United Arab Emirates'
            elif 'medjbabylon' in article:
                journal = 'Medical Journal of Babylon'
                archives_page = 'https://www.medjbabylon.org/backissues.asp'
                main = 'https://www.medjbabylon.org/'
                file = open('www.medjbabylon.org.txt','w', encoding="utf-8")
                country='Iraq'
            elif 'mmjonweb' in article:
                journal = 'Mustansiriya Medical Journal'
                archives_page = 'https://www.mmjonweb.org/backissues.asp'
                main = 'https://www.mmjonweb.org/'
                file = open('www.mmjonweb.org.txt','w', encoding="utf-8")
                country='Iraq'
            
            make_dir(f'Articles/{country}',journal)
            scrapeStructure_B(country,journal,archives_page,main)
            PDF_links_temp = PDF_links.copy()
            PDF_links.clear()
            PDF_links =list(dict.fromkeys(PDF_links_temp)) # removing duplicates
        elif 'www.easpublisher.com' in article: # sent to new database
            country = 'Kenya'
            if 'easjms' in article: 
                journal = 'East African Scholars Journal of Medical Sciences'
                archives_page ='https://www.easpublisher.com/journal/easjms/archives'
                file = open('www.easpublisher.com easjms.txt','w', encoding="utf-8")
            if 'easjacc' in article:
                journal = 'EAS Journal of Anaesthesiology and Critical Care'
                archives_page ='https://www.easpublisher.com/journal/easjacc/archives'
                file = open('www.easpublisher.com easjacc.txt','w', encoding="utf-8")
            if 'easjop' in article:
                journal = 'EAS Journal of Orthopaedic and Physiotherapy'
                archives_page ='https://www.easpublisher.com/journal/easjop/archives'
                file = open('www.easpublisher.com easjop.txt','w', encoding="utf-8")
            if 'easjpp' in article:
                journal = 'EAS Journal of Pharmacy and Pharmacology'
                archives_page ='https://www.easpublisher.com/journal/easjpp/archives'
                file = open('www.easpublisher.com easjpp.txt','w', encoding="utf-8")
            if 'easms' in article:
                journal = 'EAS Journal of Medicine and Surgery'
                archives_page ='https://www.easpublisher.com/journal/easms/archives'
                file = open('www.easpublisher.com easms.txt','w', encoding="utf-8")
            main = 'https://www.easpublisher.com/'
            scrapeStructure_T(country, journal, archives_page,main)
        elif 'saudijournals.com' in article: # sent to new database
            country = 'United Arab Emirates'
            if 'sjmps' in article:
                journal = 'Saudi Journal of Medical and Pharmaceutical Sciences'
                archives_page = 'https://saudijournals.com/journal/sjmps/archives'
                file = open('www.saudijournals.com sjmps.txt','w', encoding="utf-8")
            elif 'sjbr' in article:
                journal = 'Saudi Journal of Biomedical Research'
                archives_page = 'https://saudijournals.com/journal/sjbr/archives'
                file = open('www.saudijournals.com sjbr.txt','w', encoding="utf-8")
            elif 'sjm' in article:
                journal = 'Saudi Journal of Medicine'
                archives_page ='https://saudijournals.com/journal/sjm/archives'
                file = open('www.saudijournals.com sjm.txt','w', encoding="utf-8")
            elif 'sjls' in article:
                journal = 'Haya: The Saudi Journal of life sciences'
                archives_page ='https://saudijournals.com/journal/sjls/archives'
                file = open('www.saudijournals.com sjls.txt','w', encoding="utf-8")
            main = 'https://saudijournals.com/'
            scrapeStructure_X(country,journal,archives_page,main)
        elif 'amj' in article or 'iphr' in article or 'bjsrg' in article: # sent to new database
            country ='Iraq'
            if 'amj' in article:
                journal = 'Al- Anbar Medical Journal'
                archives_page = 'https://amj.uoanbar.edu.iq/'
                file = open('amj.uoanbar.edu.iq.txt','w', encoding="utf-8")
                main = 'https://amj.uoanbar.edu.iq/'
            if 'iphr' in article:
                journal = 'Iraqi Journal of Pharmacy'
                archives_page = 'https://iphr.mosuljournals.com/'
                file = open('iphr.mosuljournals.com.txt','w', encoding="utf-8")
                main = 'https://iphr.mosuljournals.com/'
            if 'bjsrg' in article:
                journal = 'Basrah Journal of Surgery'
                archives_page = 'https://bjsrg.uobasrah.edu.iq/'
                file = open('bjsrg.uobasrah.edu.iq.txt','w', encoding="utf-8") 
                main = 'https://bjsrg.uobasrah.edu.iq/'
            scrapeStructure_U(country, journal, archives_page,main)
        elif 'www.iasj.net' in article: # title needed
            country = 'Iraq'
            if '14135' in article or '180' in article:
                journal = 'Karbala Journal of Pharmaceutical Sciences'
                archives_page = 'https://www.iasj.net/iasj/journal/180/issues'
                file = open('www.iasj.net-14135.txt','w', encoding="utf-8")
            if '13883' in article or '260' in article:
                journal = 'Journal of Basrah Researches (Sciences)'
                archives_page = 'https://www.iasj.net/iasj/journal/260/issues'
                file = open('www.iasj.net-13883.txt','w', encoding="utf-8")
            main = 'https://www.iasj.net'
            scrapeStructure_S(country,journal,archives_page,main)
            temp = PDF_links.copy()
            PDF_links.clear()
            for link in temp:
                PDF_links.append(link.replace('pdf','download'))
        elif 'batnajms' in article: # sent to new database
            journal = 'Batna Journal of Medical Sciences'
            country = 'Algeria'
            archives_page = 'https://batnajms.net/2019/11/archives-de-la-revue/'
            file = open('batnajms.net.txt','w', encoding="utf-8")
            main = 'https://batnajms.net/'
            scrapeStructure_F(country,journal,archives_page,main)
        elif 'journals.ju' in article: # sent to new database
            country = 'Jordan'
            if 'JJPS' in article:
                journal = 'Jordan Journal of Pharmaceutical Sciences'
                archives_page = 'http://journals.ju.edu.jo/JJPS/issue/archive'
                file = open('journals.ju.edu.jo-JJPS.txt','w', encoding="utf-8")
            if 'JMJ' in article:
                journal = 'Jordan Medical Journal'
                archives_page = 'http://journals.ju.edu.jo/JMJ/issue/archive'
                file = open('journals.ju.edu.jo-JMJ.txt','w', encoding="utf-8")
            scrapeStructure_V(country,journal,archives_page,'')
        elif 'www.karger.com' in article: # sent to database
            journal = 'Medical Principles and Practice'
            country = 'Kuwait'
            archives_page = 'https://www.karger.com/Journal/Issue/281490'
            main = 'https://www.karger.com'
            file = open('www.karger.com.txt','w', encoding="utf-8")
            scrapeStructure_C(country,journal, archives_page,main)
        elif 'springeropen' in article: # sent to new database
            country = 'Egypt'
            if 'ejb' in article:
                journal = 'Egyptian Journal of Bronchology'
                archives_page='https://ejb.springeropen.com/articles'
                Issues_links.append('https://ejb.springeropen.com/articles')
                file = open('ejb.springeropen.com.txt','w', encoding="utf-8")
                main='https://ejb.springeropen.com/'
            if 'ejim' in article:
                journal = 'Egyptian Journal of Internal Medicine'
                archives_page='https://ejim.springeropen.com/articles'
                Issues_links.append('https://ejim.springeropen.com/articles')
                file = open('ejim.springeropen.com.txt','w', encoding="utf-8")
                main = 'https://ejim.springeropen.com/'
            scrapeStructure_D(country,journal,archives_page,main)
        elif 'www.journal-jmsr.net' in article: # sent to new database
            journal = 'Journal of Medical and surgical Research'
            country='Morocco'
            archives_page = 'https://www.journal-jmsr.net/archives.php'
            file = open('www.journal-jmsr.net.txt','w', encoding="utf-8")
            main = 'https://www.journal-jmsr.net/'
            scrapeStructure_E(country,journal ,archives_page,main)   
        elif 'lsj.cnrs.edu.lb' in article: # sent new to database
            country= 'Lebanon'
            journal = 'Lebanese Science Journal'
            archives_page = 'https://lsj.cnrs.edu.lb/archives/'
            make_dir('Articles',country)
            make_dir(f'Articles/{country}',journal)
            file = open('lsj.cnrs.edu.lb.txt','w', encoding="utf-8")
            main = 'https://lsj.cnrs.edu.lb/'
            scrapeStructure_H(country,journal,archives_page,main)  
        elif 'www.pjms.org.pk' in article:
            country = 'Pakistan'
            journal = 'Pakistan Journal of Medical Sciences'
            archives_page = 'https://www.pjms.org.pk/index.php/pjms/issue/archive'
            make_dir('Articles',country)
            make_dir(f'Articles/{country}',journal)
            file = open('www.pjms.org.pk','w', encoding="utf-8")
            scrape__www_pjms_org_pk(country, journal,archives_page)
        elif 'journals.ust.edu'in article:
            country = 'Yemen'
            journal = 'Yemeni Journal for Medical Sciences'
            archives_page = 'https://journals.ust.edu/index.php/yjms/issue/archive'
            make_dir('Articles',country)
            make_dir(f'Articles/{country}',journal)
            file = open('journals.ust.edu','w', encoding="utf-8")
            scrape__journals_ust_edu(country,journal,archives_page)
        elif 'bahrainmedicalbulletin' in article: 
            country = 'Bahrain'
            archives_page = 'https://www.bahrainmedicalbulletin.com/previousisues.html'
            main = 'https://www.bahrainmedicalbulletin.com/'
            file = open('www.bahrainmedicalbulletin.com.txt','w', encoding="utf-8")
            scrapeStructure_W(country,archives_page,main)
        elif 'mchandaids' in article: 
            archives_page = 'http://mchandaids.org/index.php/IJMA/issue/archive'
            archives_page2 = 'http://mchandaids.org/index.php/IJMA/issue/archive/2' # 25 issue per page - 27 issues available at the time writing this code
            file = open('mchandaids.org.com-IJMA.txt','w',encoding="utf-8")
            main = ''
            Volume_links.append(archives_page)
            scrapeRequests(archives_page2,main,'a','cover','class','href','a','obj_galley_link','class','href',False,True)
            print(f'{len(PDF_links)}')
            temp = PDF_links.copy()
            PDF_links.clear()
            for data in temp: # getting pdf link
                link = data.split(' ')[1]
                year = data.split(' ')[0]
                soup = parse(link)
                PDF_links.append(year + ' ' + soup.find('a',{'class','download'})['href'])
                print(f'gathered {len(PDF_links)} PDFs')
                output_text['text'] = f'gathered {len(PDF_links)} PDFs'
        elif 'journalskuwait.org' in article: 
            archives_page = 'https://journalskuwait.org/kjs/index.php/KJS/issue/archive'
            file = open('journalskuwait.org-KJS.txt','w',encoding="utf-8")
            main = ''
            scrapeRequests(archives_page,main,'a','issue/view','href','href','a','obj_galley_link','class','href',False,True)
            print(f'{len(PDF_links)}')
            temp = PDF_links.copy()
            PDF_links.clear()
            for data in temp:# getting pdf link
                link = data.split(' ')[1]
                year = data.split(' ')[0]
                soup = parse(link)
                PDF_links.append(year + ' ' + soup.find('a',{'class','download'})['href'])
                print(f'gathered {len(PDF_links)} PDFs')
                output_text['text'] = f'gathered {len(PDF_links)} PDFs'
        elif 'mjemonline.com' in article: # sent to new database
            country = 'Lebanon'
            journal = 'Mediterranean Journal of Emergency Medicine'
            make_dir('Articles',country)
            make_dir(f'Articles/{country}',journal)
            archives_page = 'https://www.mjemonline.com/index.php/mjem/issue/archive'
            file = open('www.mjemonline.com.txt','w',encoding="utf-8")
            main = ''
            scrapeStructure_Z(country,journal,archives_page,main)
        elif 'ljmr.com' in article: 
            archives_page = 'http://www.ljmr.com.ly/index.php?option=com_content&view=category&id=27&Itemid=167'
            file = open('www.ljmr.com.ly.txt','w', encoding="utf-8")
            main = 'http://www.ljmr.com.ly/'
            scrapeStructure_I(archives_page,main)
        elif 'uomustansiriyah' in article: 
            archives_page = 'https://ajps.uomustansiriyah.edu.iq/index.php/AJPS/issue/archive'
            file = open('ajps.uomustansiriyah.edu.iq.txt','w',encoding="utf-8")
            main = ''
            temp = [archives_page]
            while len(temp) > 0:
                soup = parse(temp.pop())
                try:# getting next page
                    temp.append(soup.find('a',{'class':'next'})['href'])
                    Volume_links.append(soup.find('a',{'class':'next'})['href'])
                except:
                    pass
            scrapeRequests(archives_page,main,'a','issue/view','href','href','a','obj_galley_link','class','href',False,True)
            temp = PDF_links.copy()
            PDF_links.clear()
            for data in temp:# getting pdf link
                link = data.split(' ')[1]
                year = data.split(' ')[0]
                soup = parse(link)
                print(link)
                try:
                    PDF_links.append(year + ' ' + soup.find('a',{'class','download'})['href'])
                    print(f'gathered {len(PDF_links)} PDFs')
                    output_text['text'] = f'gathered {len(PDF_links)} PDFs'
                except:
                    pass
        elif 'uobaghdad' in article: 
            if 'jkmc' in article:
                archives_page = 'https://jkmc.uobaghdad.edu.iq/index.php/MEDICAL/issue/archive'
                file = open('jkmc.uobaghdad.edu.iq.txt','w',encoding="utf-8")
            if 'bijps' in article:
                archives_page = 'https://bijps.uobaghdad.edu.iq/index.php/bijps/issue/archive'
                file = open('bijps.uobaghdad.edu.iq.txt','w',encoding="utf-8")
            main = ''
            temp = [archives_page]
            while len(temp) > 0:# getting next page
                soup = parse(temp.pop())
                try:
                    temp.append(soup.find('a',{'class':'next'})['href'])
                    Volume_links.append(soup.find('a',{'class':'next'})['href'])
                except:
                    pass
            print(Volume_links)
            scrapeRequests(archives_page,main,'a','issue/view','href','href','a','obj_galley_link','class','href',False,True)
            temp = PDF_links.copy()
            PDF_links.clear()
            for data in temp:# getting pdf link
                link = data.split(' ')[1]
                year = data.split(' ')[0]
                soup = parse(link)
                print(link)
                try:
                    PDF_links.append(year + ' ' + soup.find('a',{'class','download'})['href'])
                    print(f'gathered {len(PDF_links)} PDFs')
                    output_text['text'] = f'gathered {len(PDF_links)} PDFs'
                except:
                    pass  
        elif 'mbmj.org' in article: 
            archives_page = 'https://www.mbmj.org/index.php/ijms/issue/archive'
            file = open('www.mbmj.org.txt','w',encoding="utf-8")
            main = ''
            scrapeRequests(archives_page,main,'a','issue/view','href','href','a','btn-primary','class','href',False,True)
            temp = PDF_links.copy()
            PDF_links.clear()
            for data in temp:# getting pdf link
                link = data.split(' ')[1]
                year = data.split(' ')[0]
                soup = parse(link)
                for link in soup.find_all('a'):
                    try:
                        if 'download' in link['href']:
                            PDF_links.append(year + ' ' + link['href'])
                            print(f'gathered {len(PDF_links)} PDFs')
                            output_text['text'] = f'gathered {len(PDF_links)} PDFs'
                    except:
                        pass
        elif 'qscience.com' in article: 
            country = 'Qatar'
            journal = 'Journal of Emergency Medicine, Trauma and Acute Care'
            archives_page = 'https://www.qscience.com/content/journals/jemtac/2022/4'
            file = open('www.qscience.com.txt','w',encoding="utf-8")
            main = 'https://www.qscience.com/'
            scrapeStructure_J(country,journal,archives_page,main)
        elif 'rmsjournal.org/' in article: # Can't go to next page in an Issue
            archives_page = 'http://rmsjournal.org/Archive.aspx'
            file = open('rmsjournal.org.txt','w',encoding="utf-8")
            scrapeStructure_R(archives_page,'http://rmsjournal.org/')
        elif 'www.annalsofafricansurgery' in article: 
            archives_page ='https://www.annalsofafricansurgery.com/past-publications'
            file = open('www.annalsofafricansurgery.com.txt','w',encoding="utf-8")
            Volume_links.append(str(datetime.date.today().year)+ ' '+'https://www.annalsofafricansurgery.com/current-issue') # current issue is not present in past issues page
            scrapeStructure_K(archives_page)
        elif 'jomenas.org' in article: 
            archives_page = 'https://www.jomenas.org/home.html'
            file = open('www.jomenas.org.com.txt','w',encoding="utf-8")
            main = 'https://www.jomenas.org/'
            scrapeStructure_L(archives_page,main)
        elif 'gssrr.org' in article: 
            archives_page = 'https://gssrr.org/index.php/JournalOfBasicAndApplied/issue/archive'
            file = open('gssrr.org.txt','w',encoding="utf-8")
            main = ''
            temp = [archives_page]
            while len(temp) > 0: # getting next page
                soup = parse(temp.pop())
                try:
                    temp.append(soup.find('a',{'class':'next'})['href'])
                    Volume_links.append(soup.find('a',{'class':'next'})['href'])
                except:
                    pass
            scrapeRequests(archives_page,main,'a','issue/view','href','href','a','obj_galley_link','class','href',False,True)
            temp = PDF_links.copy()
            PDF_links.clear()
            for data in temp:# getting pdf link
                link = data.split(' ')[1]
                year = data.split(' ')[0]
                soup = parse(link)
                print(link)
                try:
                    PDF_links.append(year + ' ' + soup.find('a',{'class','download'})['href'])
                    print(f'gathered {len(PDF_links)} PDFs')
                    output_text['text'] = f'gathered {len(PDF_links)} PDFs'
                except:
                    pass  
        elif 'asjp.cerist.dz' in article: 
            archives_page = 'https://www.asjp.cerist.dz/en/Articles/506'
            file = open('www.asjp.cerist.dz.txt','w',encoding="utf-8")
            main = ''
            scrapeRequests(archives_page,main,'a','en/article/','href','href','a','downArticle','href','href',False,True)
        elif 'academicjournals' in article: 
            archives_page = 'https://academicjournals.org/journal/AJPP/archive'
            file = open('academicjournals.org.txt','w',encoding="utf-8")
            scrapeStructure_M(archives_page,'https://academicjournals.org/')
        elif 'bhmedsoc.com' in article:
            current_year = datetime.date.today().year
            issue_year = 2018
            issue_nb = 1
            PDF_links_temp = []
            file = open('www.bhmedsoc.com.txt','w',encoding="utf-8")
            PDF_nbs = len(PDF_links_temp)
            main = 'https://www.bhmedsoc.com/jbms/'
            while issue_year <= current_year:
                Issues_links.append(f'https://www.bhmedsoc.com/jbms/archives.php?Article_Published_Year={issue_year}&Issues={issue_nb}') # issue links
                PDF_links = findAttrintarget(Issues_links,'a','Full_Text_PDF','href','href',main) # pdf links
                for link in PDF_links: # adding year to data
                    PDF_links_temp.append(str(issue_year)+' ' +link)
                if PDF_nbs == len(PDF_links_temp):# getting issue nb
                    issue_year += 1
                    issue_nb = 1
                else:
                    issue_nb+=1
                PDF_nbs = len(PDF_links_temp)
                print(f'{PDF_nbs} added till now')
            PDF_links = PDF_links_temp.copy()
        elif 'ajol.info' in article: 
            if 'jmbs' in article:
                archives_page ='https://www.ajol.info/index.php/jmbs/issue/archive'
                file = open('www.ajol.info-jmbs.txt','w',encoding="utf-8")
            if 'eaoj' in article:
                archives_page ='https://www.ajol.info/index.php/eaoj/issue/archive'
                file = open('www.ajol.info-eaoj.txt','w',encoding="utf-8")
            if 'ecajps' in article:
                archives_page ='https://www.ajol.info/index.php/ecajps/issue/archive'
                file = open('www.ajol.info-ecajps.txt','w',encoding="utf-8")
            if 'ajhs' in article:
                archives_page ='https://www.ajol.info/index.php/ajhs/issue/archive'
                file = open('www.ajol.info-ajhs.txt','w',encoding="utf-8")
            if 'ajr' in article: # paid
                archives_page ='https://www.ajol.info/index.php/ajr/issue/archive'
                file = open('www.ajol.info-ajr.txt','w',encoding="utf-8")
            if 'ajst' in article:
                archives_page ='https://www.ajol.info/index.php/ajst/issue/archive'
                file = open('www.ajol.info-ajst.txt','w',encoding="utf-8")
            if 'tjs' in article:
                archives_page = 'https://www.ajol.info/index.php/tjs/issue/archive'
                file = open('www.ajol.info-tjs.txt','w',encoding="utf-8")
                country='Tanzania'
                journal='Tanzania Journal of Science'
            main = ''
            scrape__ajol_info(country,journal,archives_page)
            # scrapeRequests(archives_page,main,'a','issue/view','href','href','a','obj_galley_link','class','href',False,True)
        elif 'ejmsonline.org' in article:
            archives_page = 'https://www.ejmsonline.org/volumes'
            file = open('www.ejmsonline.org-Abstracts.txt','w',encoding="utf-8")
            main = 'https://www.ejmsonline.org/'
            scrapeStructure_O(archives_page,main)
            print(len(Abstracts_link))
            for link in Abstracts_link:
                file.write(link+'\n')
            file.close()
        elif 'me-jaa.com' in article: 
            archives_page = 'http://www.me-jaa.com/me-jaapastissues.htm'
            file = open('www.me-jaa.com.txt','w',encoding="utf-8")
            main = 'http://www.me-jaa.com/'
            Issues_links.append(archives_page)
            PDF_links = findAttrintarget(Issues_links,'a','.pdf','href','href',main)
            temp = PDF_links.copy()
            PDF_links.clear()
            for link in temp:# getting year
                year = link[-8:-4]
                if not year.isnumeric():
                    year = link[-13:-9]
                PDF_links.append(year+' '+link)
        elif 'mejfm.com' in article: # Can't extract specifc year
            archives_page = 'http://www.mejfm.com/journal.htm'
            file = open('www.mejfm.com.txt','w',encoding="utf-8")
            main = 'http://www.mejfm.com/'
            scrapeStructure_P(main)
        elif 'journals.uokerbala.edu.iq' in article: 
            archives_page = 'https://journals.uokerbala.edu.iq/index.php/kj/issue/archive'
            file = open('journals.uokerbala.edu.iq-PDFs.txt','w',encoding="utf-8")
            abstract = open('journals.uokerbala.edu.iq-abstracts.txt','w',encoding="utf-8")
            scrapeStructure_N(archives_page)
            for link in Abstracts_link:
                abstract.write(link+'\n')
            abstract.close()
            temp = PDF_links.copy()
            PDF_links.clear()
            for data in temp:# getting pdf link
                link = data.split(' ')[1]
                year = data.split(' ')[0]
                soup = parse(link)
                print(link)
                try:
                    PDF_links.append(year + ' ' + soup.find('a',{'class','download'})['href'])
                    print(f'gathered {len(PDF_links)} PDFs')
                    output_text['text'] = f'gathered {len(PDF_links)} PDFs'
                except:
                    pass  
        elif 'www.iraqijms.net' in article: 
            archives_page = 'https://www.iraqijms.net/archive.html#parentVerticalTab10'
            file = open('www.iraqijms.net.txt','w',encoding="utf-8")
            main = 'https://www.iraqijms.net/'
            scrapeRequests(archives_page,main,'a','issue&id=','href','href','a','.pdf','href','href',False,True)
            temp = PDF_links.copy()
            PDF_links = list(dict.fromkeys(temp))
        elif 'iraqmedj.org' in article: 
            archives_page = 'https://iraqmedj.org/index.php/imj/issue/archive'
            file = open('iraqmedj.org-PDFs.txt','w',encoding="utf-8")
            abstract = open('iraqmedj.org-abstracts.txt','w',encoding="utf-8")
            scrapeStructure_N(archives_page)
            for link in Abstracts_link:
                abstract.write(link+'\n')
            abstract.close()
            temp = PDF_links.copy()
            PDF_links.clear()
            for data in temp:# getting pdf link
                link = data.split(' ')[1]
                year = data.split(' ')[0]
                soup = parse(link)
                print(link)
                try:
                    PDF_links.append(year + ' ' + soup.find('a',{'class','download'})['href'])
                    print(f'gathered {len(PDF_links)} PDFs')
                    output_text['text'] = f'gathered {len(PDF_links)} PDFs'
                except:
                    pass  
        elif 'rmr.smr.ma/' in article: 
            archives_page = 'http://rmr.smr.ma/archives'
            file = open('rmr.smr.ma.txt','w',encoding="utf-8")
            main = 'http://rmr.smr.ma/'
            Issues_links.append(main+'/dernier-numero')
            scrapeRequests(archives_page,main,'a','/archives/','href','href','a','/archives/','href','href',False,True)
            Issues_links = PDF_links.copy()
            PDF_links.clear()
            while len(Issues_links) >0:# getting pdf link
                data = Issues_links.pop()
                link = data.split(' ')[1]
                year = data.split(' ')[0]
                temp = findAttrintarget([link],'a','task=download','href','href',main)
                for x in temp:
                    PDF_links.append(year+' '+x)
        elif 'hsd-fmsb.org' in article: 
            archives_page = 'https://www.hsd-fmsb.org/index.php/hsd/issue/archive'
            file = open('www.hsd-fmsb.org.txt','w',encoding="utf-8")
            main = ''
            scrapeRequests(archives_page,main,'a','issue/view','href','href','a','galley-link','class','href',False,True)
            temp = PDF_links.copy()
            PDF_links.clear()
            for data in temp:# getting pdf link
                link = data.split(' ')[1]
                year = data.split(' ')[0]
                print(link)
                try:
                    soup = parse(link)
                    PDF_links.append(year + ' ' + soup.find('a',{'class','download'})['href'])
                    print(f'gathered {len(PDF_links)} PDFs')
                    output_text['text'] = f'Gathered {len(PDF_links)} PDFs'
                except:
                    pass  
        elif 'phcfm.org' in article: 
            archives_page = 'https://phcfm.org/index.php/phcfm/issue/archive'
            file = open('phcfm.org.txt','w',encoding="utf-8")
            main = ''
            Issues_links = findAttrintarget([archives_page],'a','issue/view','href','href')
            output_text['text'] = f'Gathering PDFs in {len(Issues_links)} Issues'
            PDF_pages = findElemintargetByPartialText(Issues_links,'a','PDF','href',main,True)
            header = {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://phcfm.org/plugins/generic/pdfJsViewer/pdf.js/build/pdf.worker.js',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
            }
            while len(PDF_pages) > 0:# getting pdf link
                page = PDF_pages.pop()
                year = page.split(' ')[0]
                url = page.split(' ')[1]
                page = requests.get(url,headers=header).url
                print(page)
                PDF_links.append(page)
                print(f'{len(PDF_pages)} Pages left')
        elif 'anafrimed.net' in article: 
            archives_page = 'http://anafrimed.net/rubrique/archives/'
            file = open('anafrimed.net.txt','w',encoding="utf-8")
            archives_pages = [archives_page]
            temp = [archives_page]
            while len(temp) > 0: # getting next pages
                soup = parse(temp.pop())
                try:
                    temp.append(soup.find('div',{'class':'alignright older-posts'}).find('a')['href'])
                    archives_pages.append(soup.find('div',{'class':'alignright older-posts'}).find('a')['href'])
                except:
                    print('no more older archives')
            scrapeStructure_Q(archives_pages)
        elif 'jaccrafrica.com' in article: 
            archives_page = 'https://www.jaccrafrica.com/Publications/'
            file = open('www.jaccrafrica.com.txt','w',encoding="utf-8")
            main = 'https://www.jaccrafrica.com/'
            soup = parse(archives_page)
            for link in soup.find_all('a'):
                try:
                    if '.pdf' in link['href']:
                        year = link.text[0:4]
                        if not year.isnumeric():
                            year = '2018'
                        url = link['href']
                        PDF_links.append(year+' '+main+url)
                        print(year+' '+url)
                except:
                    pass
        elif 'medtech.ichsmt.org' in article: # sent to new database
            archives_page = 'https://jkmc.uobaghdad.edu.iq/index.php/MEDICAL/issue/archive'
            journal = 'Medical Technologies Journal'
            country = 'Algeria'
            file = open('medtech.ichsmt.org.txt','w',encoding="utf-8")
            main = ''
            make_dir('Articles',country)
            make_dir(f'Articles/{country}',journal)
            scrapeStructure_Y(country, journal,archives_page,main)
        elif 'revues.imist.ma' in article:
            archives_page = 'https://revues.imist.ma/index.php/A2S/issue/archive'
            file = open('revues.imist.ma.txt','w',encoding="utf-8")
            Volume_links = findAttrintarget([archives_page],'a','issue/view','href','href')
            print('getting issues now')
            temp = Volume_links.copy()
            Volume_links.clear()
            for link in temp:# volume links
                Volume_links.append(link+'/showToc')

            Issues_links = findAttrintarget(Volume_links, 'a', 'file','class','href','',True) # issue links
            print('getting PDFs now')
            for data in Issues_links:# getting pdf link
                url = data.split(' ')[1]
                year = data.split(' ')[0]
                temp = findAttrintarget([url],'iframe','pdf.js','src','src')
                for x in temp:
                    PDF_links.append(year+ ' ' + x)
        elif 'journals.squ.edu.om' in article:
            archives_page = 'https://journals.squ.edu.om/index.php/squmj/issue/archive'
            file = open('journals.squ.edu.om','w',encoding="utf-8")
            country='Oman'
            journal='sultan qaboos university medical journal'
            scrape__journals_squ_edu_om(country,journal,archives_page)
        if file == '':
            print('Journal not supported yet')
        else:
            print(f'Gathered a total of {len(PDF_links)} PDFs')
            output_text['text'] = f'Gathered a total of {len(PDF_links)} PDFs'
            for link in PDF_links:
                file.write(link+'\n')
            file.close()
            output_text['text'] = f'Gathered a total of {len(PDF_links)} PDFs - You can close this window.'
        errors.close()
        PDF_links.clear()

        shared_queue.put('finished')

        return

    # root window
    Progress = tk.Tk()
    Progress.geometry('310x90')
    Progress.title('Scraping - No Estimated time')
    # progressbar
    bar_value = tk.IntVar()
    pb = ttk.Progressbar( Progress,orient='horizontal',mode='indeterminate', length=280,variable=bar_value)
    pb.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
    output_text = Label(Progress,text="Scraping...")
    output_text.grid(column=0, columnspan=2,row=1)
    threading.Thread(target=Scraper).start()
    shared_queue.put('scraping')
    threading.Thread(target=Update_PB_update).start()
    Progress.mainloop()
