import re
from urllib.parse import urlparse, urlunparse
from config import ZENROWS_API_KEY
import requests
from zenrows import ZenRowsClient
import asyncio

zClient = ZenRowsClient(apikey=ZENROWS_API_KEY, retries= 0, concurrency= 5)

def search_zenrows(search_term, num_results):
    query = search_term.replace(" ", "%20") 
    res = zClient.get(
        url= f"https://www.google.com/search?q={query}",
        params={
            "premium_proxy":"true",
            "autoparse":"true"
        }
    )
    if res.status_code == 200:
        results = res.json().get('organic_results')
        return [result.get('link') for result in results[:num_results]]
    else:
        print(f"Error {res.status_code} occured in {search_term}")
        return []

async def multiple_search_zenrows(search_terms, num_results):
    queries = [search_term.replace(" ", "%20") for search_term in search_terms]
    params={
        "premium_proxy":"true",
        "autoparse":"true"
    }
    urls = [f"https://www.google.com/search?q={query}" for query in queries]
    responses = await asyncio.gather(*[zClient.get_async(url, params=params) for url in urls])

    links = []
    
    for res in responses:
        if res.status_code == 200:
            results = res.json().get('organic_results')
            links.append([result.get('link') for result in results[:num_results]])
        else:
            links.append([])
    
    return links


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
    
    responses = search_zenrows(f"{first_name} {last_name} {university} {social}", num_results= 2)

    urls = []
    for res in responses:
        url = urlunparse(urlparse(res)._replace(query=''))
        if is_social_url(url, social):
            urls.append(url)
    return urls

async def concurrent_google_results(first_name, last_name, university, socials):
    search_terms = [f"{first_name} {last_name} {university} {social}" for social in socials]

    responses = await multiple_search_zenrows(search_terms=search_terms, num_results=2)
    results = {}
    for res, social in zip(responses, socials):
        results[social] = []
        for link in res:
            url = urlunparse(urlparse(link)._replace(query=''))
            if is_social_url(url, social):
                results[social].append(url)
    
    return results

async def get_google_results_by_terms(search_terms, socials):

    responses = await multiple_search_zenrows(search_terms=search_terms, num_results=2)
    results = {}
    for res, social in zip(responses, socials):
        results[social] = []
        for link in res:
            url = urlunparse(urlparse(link)._replace(query=''))
            if is_social_url(url, social):
                results[social].append(url)
    
    return results