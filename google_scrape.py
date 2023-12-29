from apify_client import ApifyClient
from googlesearch import search
import os
import json
from functools import reduce
import re
from urllib.parse import urlparse, urlunparse
from config import APIFY_TOKEN
import time
import requests
from random import randint

client = ApifyClient(APIFY_TOKEN)

def search_apify(query, num_results):
    run_input = {
        "customDataFunction": "async ({ input, $, request, response, html }) => {\n  return {\n    pageTitle: $('title').text(),\n  };\n};",
        "includeUnfilteredResults": False,
        "maxPagesPerQuery": 1,
        "mobileResults": False,
        "queries": query,
        "resultsPerPage": num_results,
        "saveHtml": False,
        "saveHtmlToKeyValueStore": False
    }

    run = client.actor("nFJndFXA5zjCTuudP").call(run_input=run_input)

    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results = item.get("organicResults")
        break

    requests.delete(f"https://api.apify.com/v2/actor-runs/{run['id']}?token={APIFY_TOKEN}")
    
    return [res.get('url') for res in results]


def is_social_url(url, social):
    if social == 'instagram':
        pattern = re.compile(r'^https?://(?:www\.)?instagram\.com/[A-Za-z0-9_.]+/?$')
    elif social == 'linkedin':
        pattern = re.compile(r'^https?://(www\.)?linkedin.com/in/[A-Za-z0-9_.%-]+/?$')
    elif social == 'tiktok':
        pattern = re.compile(r'^https?://(?:m\.)?(?:www\.)?tiktok.com/@[A-Za-z0-9_.]+/?$')
    elif social == 'facebook':
        pattern = re.compile(r'^https?://(?:m\.)?(?:www\.)?facebook\.com/[A-Za-z0-9_.]+/?$')
    match = re.match(pattern, url)
    return bool(match)

def google_results(first_name, last_name, university, major, social):

    
    responses = search(f"{first_name} {last_name} {university} {social}", num_results= 2)

    urls = []
    for res in responses:
        url = urlunparse(urlparse(res)._replace(query=''))
        if is_social_url(url, social):
            urls.append(url)
    time.sleep(randint(30, 40))
    return urls

if __name__ == '__main__':

    for filename in os.listdir('results'):
        print(filename.split('.')[0])
        full_path = os.path.join('results', filename)

        with open(full_path, "r", encoding= "utf-8") as f:
            data = json.load(f)
        
        for key, value in data.items():
            for student in value:
                student['major'] = key

        student_data = reduce(lambda x, y: x + y, data.values())
        
        for student in student_data:

            first_name = student.get('first_name')
            last_name = student.get('last_name')
            university = student.get('university')
            major = student.get('major')

            if student_data.index(student) % 10 == 0:
                print(student_data.index(student))

            social = {}
            try:
                social['instagram'] = [student.get('instagram')] if student.get('instagram')\
                    else google_results(first_name, last_name, university, major, 'instagram')
                social['linkedin'] = google_results(first_name, last_name, university, major, 'linkedin')
                social['tiktok'] = google_results(first_name, last_name, university, major, 'tiktok')
                social['facebook'] = google_results(first_name, last_name, university, major, 'facebook')
                
            except Exception as e:
                print(e)


            student['social'] = social
            
            if student.get('instagram'):
                student.pop('instagram')

        with open(os.path.join('data', filename), 'w', encoding='utf-8') as f:
            json.dump(student_data, f, indent= 4)
        
        
        
