import requests as rq
import os
import json
file = open('www.ejdv.eg.net.txt', encoding="utf8", errors='replace')
count = 0
dictionary = {}
for line in file:
    try:
        data = line.split(' --- ')
        country = data[0]
        journal = data[1]
        year = data[2]
        month = data[3]
        volume = data[4]
        issue = data[5]
        title = data[6]
        pdf = data[7].replace('\n','').replace('view','download')
        try:
            try:
                os.makedirs(f'Articles/{country}')
            except:
                pass
            try:
                os.makedirs(f'Articles/{country}/{journal}')
            except:
                pass
            json_file = open(f'Articles/{country}/{journal}/info.json','w')
            response = rq.get(pdf)
            dictionary[count]={}
            dictionary[count] = {
                "title": title,
                "url": pdf,
                "year": year,
                "month":month,
                "volume":volume,
                "issue":issue,
                "id":count}
            pdf_file = open(f'Articles/{country}/{journal}/{count}.pdf','wb')
            count+=1
            pdf_file.write(response.content)
            pdf_file.close()
        except Exception as e:
            print(e)
        json.dump(dictionary, json_file,indent=2)
        json_file.close()
    except Exception as e:
        print(pdf)
        print(e)
