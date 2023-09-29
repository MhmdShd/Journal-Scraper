
from time import sleep
import os
import requests as rq

resend = range(-1,1000000)
api_link = 'https://els.qsysi.com/public/api/api_journal'
for journal in os.listdir('src/txt_files'):
    print(journal)
    result = open(f'{journal}.txt','w')
    count=0
    success = 0
    failed = 0
    failed_list = []
    f = open(f'txt_files/{journal}.txt', encoding="utf8")
    count = 0
    for line in f:
        data = line.split('*')
        country = data[0]
        journal=data[1]
        year=data[2]
        month=data[3]
        volume=data[4]
        issue=data[5]
        title=data[6]
        pdf=data[7]
        if count in resend:
            pdf_file = open(f'src/{title}','rb')

            payload = {
            'country': country,
            'magazine_name': journal+ ' * ' +title+ ' * ' +issue+ ' * ' +volume,
            'year': year,
            'month': month,
            'pdf_link': pdf,
            'failed':0
            }
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