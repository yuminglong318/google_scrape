import json
import re

import google_scrape

def get_username_from_url(url, social):
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

    with open("Duke_Students_Outlook.json", "r", encoding= "utf-8") as f:
        students = json.load(f)
    
    total_students = len(students)
    print("Total Stuents: ", total_students)
    count = 4000
    google_scraped_students = []
    for student in students[4000:]:
        print(count + 1, "of", total_students, end= "\r")
        
        if count % 100 == 0:
            with open(f"./outlook/Duke_Students_Outlook.json", "w", encoding= "utf-8") as f:
                json.dump(google_scraped_students, f, indent= 4, ensure_ascii= False)
        try:
            socials = ["instagram", "linkedin", "tiktok", "facebook"]
            for social in socials:
                if any(s.get("name") == social for s in student.get("social")):
                    continue
                else:
                    urls = google_scrape.google_results(
                        student.get("first_name"),
                        student.get("last_name"),
                        "student",
                        student.get("university"),
                        social
                    )
                    if len(urls) > 0:
                        student["social"].append({
                            "name": social,
                            "userName": get_username_from_url(urls[0], social)
                        })
            google_scraped_students.append(student)
        except Exception as e:
            print(e)
            print(student.get("first_name"), student.get("last_name"))
        
        count += 1
    
    with open(f"./outlook/Duke_Students_Outlook.json", "w", encoding= "utf-8") as f:
                json.dump(google_scraped_students, f, indent= 4, ensure_ascii= False)