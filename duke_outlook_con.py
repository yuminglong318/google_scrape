import json
import re
from urllib.parse import urlparse, urlunparse
import google_scrape
import asyncio

def get_username_from_url(url, social):

    url = urlunparse(urlparse(url)._replace(query=''))
    
    if social == 'instagram':
        pattern = re.compile(r'^https?://(?:www\.)?instagram\.com/([A-Za-z0-9_.]+)/?$')
    elif social == 'linkedin':
        pattern = re.compile(r'^https?://(?:www\.)?linkedin.com/in/([A-Za-z0-9_.%-]+)/?$')
    elif social == 'tiktok':
        return url
    elif social == 'facebook':
        pattern = re.compile(r'^https?://(?:m.|www\.)?facebook\.com/([A-Za-z0-9_.]+)/?$')
    else:
        return None
    match = pattern.findall(url)
    return match[0] if match else None

if __name__ == '__main__':

    with open("duke_students.json", "r", encoding= "utf-8") as f:
        students = json.load(f)
    
    total_students = len(students)
    print("Total Stuents: ", total_students)
    count = 0
    google_scraped_students = []
    for student in students[count:]:
        print(count + 1, "of", total_students, end= "\r")
        
        if count % 100 == 0:
            with open(f"./outlook/duke_students_part4.json", "w", encoding= "utf-8") as f:
                json.dump(google_scraped_students, f, indent= 4, ensure_ascii= False)
        try:
            socials = ["instagram", "linkedin", "tiktok", "facebook"]
            results = asyncio.run(google_scrape.concurrent_google_results(
                student.get("first_name"), 
                student.get("last_name"),
                student.get("university"),
                socials
            ))
            for key, value in results.items():
                if len(value) > 0:
                    student["social"].append({
                        "name": key,
                        "userName": get_username_from_url(value[0], key)
                    })
            google_scraped_students.append(student)
        except Exception as e:
            print("ERROR: ", student.get("first_name"), student.get("last_name"))
        
        count += 1
    
    with open(f"./outlook/duke_students_part4.json", "w", encoding= "utf-8") as f:
        json.dump(google_scraped_students, f, indent= 4, ensure_ascii= False)