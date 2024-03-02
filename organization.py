from google_scrape import get_google_results_by_terms
import json
import asyncio

OUT_DIR = 'orgs'

if __name__ == '__main__':
    import os
    with open("Organizations.json", "r", encoding="utf-8") as f:
        orgs = json.load(f)
    
    total_count = len(orgs)
    print("Total organizations to scrape: ", total_count)
    count = 0
    socials_to_scrape = ["instagram", "tiktok", "facebook", "linkedin"]

    scraped_orgs= []
    for org in orgs:
        print(f"{count} of {total_count} completed", end="\r")
        if count % 100 == 0:
            with open(os.path.join(OUT_DIR, "organizations.json"), "w", encoding="utf-8") as f:
                json.dump(scraped_orgs, f, indent=4, ensure_ascii=False)
        name = org.get("name")
        university = org.get("university")
        socials = [social for social in socials_to_scrape if social not in [sc.get("name") for sc in org.get("social")]]
        search_terms = [f"{name.replace('&', '%26').replace('#', '%23')} {university} {social}" for social in socials]
        results = asyncio.run(get_google_results_by_terms(search_terms, socials))
        for key, value in results.items():
            if len(value) > 0:
                org['social'].append({
                    "name": key,
                    "site": value[0]
                })
        scraped_orgs.append(org)

        count += 1
        
    with open(os.path.join(OUT_DIR, "organizations.json"), "w", encoding="utf-8") as f:
        json.dump(scraped_orgs, f, indent=4, ensure_ascii=False)
        
        
        
        