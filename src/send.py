from time import sleep
import os
import json
import requests as rq

resend = range(-1,1000000)
Country='egypt'
Journal = 'Egyptian Journal of Internal Medicine'
api_link = 'https://els.qsysi.com/public/api/api_journal'
for country in os.listdir('Articles'):
    journal_dir = 'Articles/'+country
    if country.lower() == Country:
        for journal in os.listdir(journal_dir):
            if journal == Journal:
                # if journa; != 'Pakistan Journal of Medical Sciences' and journal != 'Journal of Emergency Medicine, Trauma and Acute Care' andjournal != 'Yemeni Journal for Medical Sciences' and journal != 'Saudi Journal of Medicine' and journal != 'Saudi Journal of Medical and Pharmaceutical Sciences' and journal !='Saudi Journal of Biomedical Research' and journal!='Haya, The Saudi Journal of life sciences' and 'Tanzania' not in journal and journal !='Egyptian Journal of Internal Medicine' and journal !='Journal for the Egyptian Ophthalmology Society' and journal != 'Journal of Emergency Medicine, Trauma and Acute Care'and journal != 'Pakistan Journal of Medical Sciences' and journal !='sultan qaboos university medical journal' and journal !='Journal of Medical and surgical Research' and journal !='Mediterranean Journal of Emergency Medicine' and journal !='Lebanese Science Journal' and journal !='East African Scholars Journal of Medical Sciences'and journal !='EAS Journal of Pharmacy and Pharmacology' and journal !='EAS Journal of Orthopaedic and Physiotherapy' and journal !='EAS Journal of Medicine and Surgery'and journal !='EAS Journal of Anaesthesiology and Critical Care' and journal !='Jordan Medical Journal' and journal !='Jordan Journal of Pharmaceutical Sciences' and journal !='Iraqi Journal of Pharmacy' and journal != 'Al- Anbar Medical Journal' and journal != 'Basrah Journal of Surgery' and journal != 'Egyptian Journal of Bronchology' and journal !='Batna Journal of Medical Sciences' and journal != 'Medical Technologies Journal' and journal !='Egyptian Pharmaceutical Journal' and journal !='Egyptian Retina Journal':
                print(journal)
                # sleep(5)
                result = open(f'{journal}.txt','w')
                count=0
                success = 0
                failed = 0
                failed_list = []
                f = open(f'{journal_dir}/{journal}/info.json')
                data = json.load(f)
                for article in data:
                    id = data[article]['id']
                    if id in resend:
                        pdf_file = open(f'{journal_dir}/{journal}/{id}.pdf','rb')

                        payload = {
                        'country': country,
                        'magazine_name': journal+ ' * ' +data[article]['title']+ ' * ' +data[article]['issue']+ ' * ' +data[article]['volume'],
                        'year': data[article]['year'],
                        'month': data[article]['month'],
                        'pdf_link': data[article]['url'],
                        'failed':0
                        }
                        if int(data[article]['year']) >= 2021:
                            file = {'pdf_file': pdf_file}
                            r = rq.post(api_link,data=payload,files=file)
                            count+=1
                            if r.text !='"success"':
                                print(f'error sending: {id}')
                                failed +=1
                                failed_list.append(id)
                            else:
                                success +=1
                                print(f"{id} - Status Code: {r.status_code}, Response: {r.text}")
            result.write(str(failed_list))
            print(f'{journal} - Failed:{failed_list}')