import requests
import os
import json

import twilio_app

custom_search_url = "https://www.googleapis.com/customsearch/v1"
cse_id = "003317418401341208282:jtfju-dm-8q"
key = ''

payload = {
    'cx': cse_id,
    'searchType': 'image',
    'key': os.environ['GOOGLE_CSE_API_KEY'],
    'imgSize': 'xlarge'
}
results = {}

previous_names = []
names = []
with open('search_results.txt', 'r') as h:
    for line in h:
        fields = line.split(',')
        previous_names.append(fields[0].strip())

with open('names_failed.txt', 'r') as f:
    names = f.readlines()

with open('search_results.txt', 'a+') as g:
    for name in names:
        '''if name.strip() in previous_names:
            continue'''
        payload['q'] = name
        resp = requests.get(custom_search_url, payload)
        json_obj = resp.json()
        for item in json_obj['items'][:3]:
            link = item['link']
            f = twilio_app.get_image_from_url(link)
            try:
                r = requests.post('http://localhost:8888/recognize', files={'file': f.getvalue()})
                print(r.text)
                face_obj = r.json()
                if name not in results:
                    results[name] = []
                if 'CelebrityFaces' in face_obj and len(face_obj['CelebrityFaces']) > 0:
                    results[name].append(face_obj['CelebrityFaces'][0]['Name'])
            except json.decoder.JSONDecodeError as e:
                print("{}".format(name))
                print(str(e))
                results[name] = []
            except requests.exceptions.ConnectionError:
                print("{}".format(name))
            finally:
                f.close()
        g.write("{}, {}\n".format(name.strip(), str(results[name])))

with open('search_results.txt', 'w') as f:
    for ref_name in results.keys():
        f.write("{}, {}\n".format(ref_name.strip(), str(results[ref_name])))
    