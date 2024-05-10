# from utils import (
#     get_proxies,
#     get_terms,
#     get_western_countries
# )
try:
    # from .utils import *
    from . import config
    from . import utils
except:
    # from utils import *
    import config
    import utils
import random
# import config
from tenacity import retry
from time import sleep
from fake_useragent import UserAgent
from collections import defaultdict
from bs4 import BeautifulSoup
import js2py
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import csv
from unidecode import unidecode
import httpx
import math
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

max_retries = config.max_retries
retries = defaultdict(int)
url = 'https://opencorporates.com/companies'
login_url = "https://opencorporates.com/users/sign_in"
threads = config.threads
western_countries = []
western_top_countries = []
proxies = []
proxies_in_use = []
results = {}

def get_proxy():
    proxy_str = ""
    while True:
        proxy_str = proxies[random.randrange(0, len(proxies))]
        if proxy_str[0] not in proxies_in_use:
            proxies_in_use.append(proxy_str[0])
            break
    return proxy_str

def release_proxy(proxy_str):
    if proxy_str:
        proxies_in_use.remove(proxy_str)


def mode1_func(term, non_profit, session, cookies):
    oc1_results = 0
    oc1_percentage = 0
    OC1 = 0
    oc1_us_results = 0
    oc1_western_results = 0
    oc1_western_top_results = 0
    oc1_page1_results = 0
    oc1_page1_good_results = 0
    params = {
        'utf8': '✓',
        'q': term,
        'commit': 'Go',
        'jurisdiction_code': '',
        'controller': 'searches',
        'action': 'search_companies',
        'inactive': 'false',
        'mode': 'best_fields',
        'search_fields[]': 'name',
        'branch': 'false',
        'nonprofit': non_profit,
        'order': 'incorporation_date'
    }

    sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
    # page = session.get(url, params=params, cookies=cookies, proxies={"http": proxy}, headers=headers, timeout=(3, 10))
    page = session.get(url, params=params, cookies=cookies)
    page.raise_for_status()
    # with open("test.html", "w") as f:
    #     f.write(page.text.encode('utf8').decode('ascii', 'ignore'))
    soup = BeautifulSoup(page.text, 'lxml')
    oc1_results = int(soup.select("div.span7 h2")[0].text.split()[1].replace(",", ""))

    if oc1_results>0:
        li_list = soup.select("div#results ul#companies li")
        oc1_page1_results = len(li_list)
        

        # oc1_page1_good_results = 0
        term_tmp = term.lower()
        term_tmp = "".join([ch for ch in term_tmp if ch.isalnum()])

        for li in li_list:
            txt = li.select(".company_search_result")[0].text
            txt = unidecode(txt)
            txt = txt.lower()
            txt = "".join([ch for ch in txt if ch.isalnum()])
            # print(term_tmp, txt)
            if txt.startswith(term_tmp) or txt.startswith("the" + term_tmp):
                # print(term_tmp, txt)
                oc1_page1_good_results+=1
        
        
        oc1_percentage = oc1_page1_good_results/oc1_page1_results
        OC1 = oc1_results * oc1_percentage
        # print("OC1", oc1_results, oc1_page1_results, oc1_page1_good_results, oc1_percentage)
        jurisdiction_list = soup.select("div.jurisdiction_code li")
        
        # oc1_us_results = 0
        # oc1_western_results = 0

        for li in jurisdiction_list:
            country = li.select("a")[0].text
            count = int(li.select("span")[0].text.replace(",", ""))
            # print(country, count)

            if "(us)" in country.lower().replace(" ", ""):
                oc1_us_results += count
            elif any(c in country.lower().replace(" ", "") for c in western_countries):
                # print(country)
                oc1_western_results += count
            elif any(c in country.lower().replace(" ", "") for c in western_top_countries):
                # print(country)
                oc1_western_top_results += count
    
    return {"results": oc1_results, "percentage": oc1_percentage, "OC": OC1, "us_results": oc1_us_results, "western_results": oc1_western_results, "western_top_results": oc1_western_top_results, "page1_results": oc1_page1_results, "page1_good_results": oc1_page1_good_results}


def mode2_func(term, non_profit, session, cookies):
    oc2_results = 0                
    oc2_percentage = 0
    OC2 = 0
    oc2_us_results = 0
    oc2_western_results = 0
    oc2_western_top_results = 0
    oc2_results = 0
    oc2_page1_results = 0
    oc2_page1_good_results = 0
    params = {
        'utf8': '✓',
        'q': term,
        'commit': 'Go',
        'jurisdiction_code': '',
        'utf8': '✓',
        'button': '',
        'controller': 'searches',
        'action': 'search_companies',
        'inactive': 'false',
        'mode': 'phrase_prefix',
        'branch': 'false',
        'nonprofit': non_profit,
        'order': 'incorporation_date',
    }
    sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
    # page = session.get(url, params=params, cookies=cookies, proxies={"http": proxy}, headers=headers, timeout=(3, 10))
    page = session.get(url, params=params, cookies=cookies)
    page.raise_for_status()
    # with open("test.html", "w") as f:
    #     f.write(page.text.encode('utf8').decode('ascii', 'ignore'))
    soup = BeautifulSoup(page.text, 'lxml')
    oc2_results = int(soup.select("div.span7 h2")[0].text.split()[1].replace(",", ""))

    if oc2_results>0:
        li_list = soup.select("div#results ul#companies li")
        oc2_page1_results = len(li_list)

        term_tmp = term.lower()
        term_tmp = "".join([ch for ch in term_tmp if ((ch.isalnum()) or (ch==" "))])
        for li in li_list:
            txt = li.select(".company_search_result")[0].text
            txt = unidecode(txt)
            txt = txt.lower()
            txt = "".join([ch for ch in txt if ((ch.isalnum()) or (ch==" "))])
            
            # print(term_tmp, txt)
            if (txt==term_tmp) or (txt.startswith(term_tmp + " ")):
                oc2_page1_good_results+=1
        # print("oc2", oc2_results, oc2_page1_good_results)

        oc2_percentage = oc2_page1_good_results/oc2_page1_results
        OC2 = oc2_results * oc2_percentage

        jurisdiction_list = soup.select("div.jurisdiction_code li")
        # western_countries = get_western_countries()
        # western_countries = [country.lower().replace(" ", "") for country in western_countries]

        for li in jurisdiction_list:
            country = li.select("a")[0].text
            count = int(li.select("span")[0].text.replace(",", ""))
            # print(country, count)

            if "(us)" in country.lower().replace(" ", ""):
                oc2_us_results += count
            elif any(c in country.lower().replace(" ", "") for c in western_countries):
                # print(country)
                oc2_western_results += count
            elif any(c in country.lower().replace(" ", "") for c in western_top_countries):
                # print(country)
                oc2_western_top_results += count
    
    return {"results": oc2_results, "percentage": oc2_percentage, "OC": OC2, "us_results": oc2_us_results, "western_top_results": oc2_western_top_results, "western_results": oc2_western_results, "page1_results": oc2_page1_results, "page1_good_results": oc2_page1_good_results}

                

@retry
def search_term(term_list):
    # print("config", config.nonprofits_only)
    try:
        input = get_proxy()
        # print(input)
        proxy = input[0]
        username = input[1]
        password = input[2]
        # term = input[0]
        
        user_agent = UserAgent().random
        term_under_process = ""
        # print("OC retry", term, retries[term])
        # retries[term]+=1
        # if retries[term]>max_retries:
        #     return (term, 0, 0, 0, 0, 0)
        
        headers = {
            'user-agent': user_agent
        }

        non_profit = ""

        if config.nonprofits_only==1:
            non_profit = True

        # with requests.session() as session:
        with httpx.Client(proxies=proxy, headers=headers) as session:
            # session.headers.update({'User-Agent': user_agent})
            sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
            # p = session.get(login_url, proxies={"http": proxy}, headers=headers)
            p = session.get(login_url)
            p.raise_for_status()
            soup = BeautifulSoup(p.text, 'lxml')
            code = soup.find('script').text
            code = code.replace("<!--", "")
            code = code.replace("//-->", "")
            code = code.replace("document.cookie", "let ky")
            code = code.replace("document.location.reload(true)", "return ky")
            res = js2py.eval_js(code)
            ky = res().split(";")[0].split("=")[1]
            cookies={}
            cookies["KEY"] = ky
            sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
            # p = session.get(login_url, proxies={"http": proxy}, cookies=cookies, headers=headers, timeout=(3, 10))
            p = session.get(login_url, cookies=cookies)
            p.raise_for_status()
            soup = BeautifulSoup(p.text, 'lxml')
            authenticity_token = soup.find('input', attrs={'name':'authenticity_token', 'type':'hidden'}).get('value')
            
            data = {
                "utf8" : "✓",
                "authenticity_token": authenticity_token,
                "user[email]": username,
                "user[password]": password,
                "user[remember_me]": "on"
            }
            cookies["KEY"] = ky

            sleep(random.uniform(config.delay_range[0], config.delay_range[1]))
            # login = session.post(login_url, cookies=cookies, data=data, proxies={"http": proxy}, headers=headers, timeout=(3, 10))
            login = session.post(login_url, cookies=cookies, data=data, follow_redirects=True)
            login.raise_for_status()
            
            # cookies = {
            #     '_openc_session': login.cookies.get_dict()['_openc_session'],
            #     'KEY': ky,
            # }

            for k, v in login.cookies.items():
                if k=='_openc_session':
                    cookies[k] = v
                    break
            # print(set(term_list)-set(results.keys()))
            for term in set(term_list)-set(results.keys()):
                print("OC Searching for term :", term)
                oc1_results = 0
                oc1_percentage = 0
                OC1 = 0
                oc1_us_results = 0
                oc1_western_results = 0
                oc1_western_top_results = 0
                oc1_page1_results = 0
                oc1_page1_good_results = 0
                oc1_returns = defaultdict(int)

                oc2_results = 0                
                oc2_percentage = 0
                OC2 = 0
                oc2_us_results = 0
                oc2_western_results = 0
                oc2_western_top_results = 0
                oc2_page1_results = 0
                oc2_page1_good_results = 0
                oc2_returns = defaultdict(int)

                if (" " in term) or ("-" in term):
                    tmp_lst1 = term.lower().split()
                    tmp_lst2 = term.lower().split("-")
                    if ("the" in tmp_lst1) or ("the" in tmp_lst2):
                        oc1_returns = mode1_func(term.replace(" ", "").replace("-", ""), non_profit, session, cookies)
                        oc2_returns = mode1_func(term, non_profit, session, cookies)
                    else:
                        oc1_returns = mode2_func(term.replace(" ", "").replace("-", ""), non_profit, session, cookies)
                        oc2_returns = mode2_func(term, non_profit, session, cookies)

                        if (oc1_returns["results"]>config.mode2_results_threshold) and (oc1_returns["percentage"]<config.mode2_percentage_threshold):
                            oc1_returns = mode1_func(term.replace(" ", "").replace("-", ""), non_profit, session, cookies)

                else:
                    if len(term)<config.mode2_unspaced_terms_len_threshold:
                        oc1_returns = mode1_func(term, non_profit, session, cookies)
                    else:
                        oc1_returns = mode2_func(term, non_profit, session, cookies)
                        if (oc1_returns["results"]>config.mode2_results_threshold) and (oc1_returns["percentage"]<config.mode2_percentage_threshold):
                            oc1_returns = mode1_func(term, non_profit, session, cookies)




                # if "-" not in term:
                #     if (" " not in term) and (len(term)<config.unspaced_terms_oc2_len):
                #         # term_under_process = term
                #         oc1_returns = oc1_func(term.replace(" ", ""), non_profit, session, cookies)
                    
                #     if (" " in term):
                #         if term.lower().startswith("the ") or (" the " in term.lower()):
                #             oc1_returns = oc1_func(term.replace(" ", ""), non_profit, session, cookies)
                #         else:
                #             oc1_returns = oc2_func(term.replace(" ", ""), non_profit, session, cookies)

                #             if (oc1_returns["results"]>config.oc2_results_threshold) and (oc1_returns["percentage"]<config.oc2_percentage_threshold):
                #                 oc1_returns = oc1_func(term.replace(" ", ""), non_profit, session, cookies)
                   
                
                    # if term_under_process == "Knock Knock":
                    #     raise Exception()
                    
                # print(oc1_us_results, oc1_western_results)

                # params = False
                # if (term.lower().startswith("the ")) or (" the " in term.lower()):
                #     oc2_returns = oc1_func(term, non_profit, session, cookies)
                # elif (" " in term.lower()):
                #     oc2_returns = oc2_func(term, non_profit, session, cookies)
                # elif (" " not in term) and (len(term)>=config.unspaced_terms_oc2_len):
                #     oc2_returns = oc2_func(term, non_profit, session, cookies)
                #     if (oc2_returns["results"]>config.oc2_results_threshold) and (oc2_returns["percentage"]<config.oc2_percentage_threshold):
                #         oc1_returns = oc1_func(term, non_profit, session, cookies)

                
                oc1_results = oc1_returns["results"]
                oc1_percentage = oc1_returns["percentage"]
                OC1 = oc1_returns["OC"]
                oc1_us_results = oc1_returns["us_results"]
                oc1_western_results = oc1_returns["western_results"]
                oc1_western_top_results = oc1_returns["western_top_results"]
                oc1_page1_results = oc1_returns["page1_results"]
                oc1_page1_good_results = oc1_returns["page1_good_results"]

                
                oc2_results = oc2_returns["results"]
                oc2_percentage = oc2_returns["percentage"]
                OC2 = oc2_returns["OC"]
                oc2_us_results = oc2_returns["us_results"]
                oc2_western_results = oc2_returns["western_results"]
                oc2_western_top_results = oc2_returns["western_top_results"]
                oc2_page1_results = oc2_returns["page1_results"]
                oc2_page1_good_results = oc2_returns["page1_good_results"]

                # term,OC_Score, OC1, OC2, OC_US, OC_West
                # OC_Score = oc1_us_results*oc1_percentage + oc2_us_results*oc2_percentage + 0.5*(oc1_western_results*oc1_percentage + oc2_western_results*oc2_percentage)
                # print(OC_Score, oc1_us_results, oc1_percentage, oc2_us_results, oc2_percentage , oc1_western_results, oc1_percentage, oc2_western_results, oc2_percentage)
                OC_Score1 = 0
                OC_Score2 = 0

                if oc1_results<=30:
                    OC_Score1=oc1_us_results*oc1_percentage + 0.5*oc1_western_top_results*oc1_percentage + 0.25*oc1_western_results*oc1_percentage
                else:
                    OC_Score1 = oc1_us_results*oc1_percentage + 0.5*(oc1_western_top_results*oc1_percentage) + 0.25*(oc1_western_results*oc1_percentage)
                
                if oc2_results<=30:
                    OC_Score2 = oc2_us_results*oc2_percentage + 0.5*oc2_western_top_results*oc2_percentage + 0.25*oc2_western_results*oc2_percentage
                else:
                    OC_Score2 = oc2_us_results*oc2_percentage + 0.5*(oc2_western_top_results*oc2_percentage) + 0.25*(oc2_western_results*oc2_percentage)
                
                # print(OC_Score1, OC_Score2)
                OC_Score = OC_Score1 + OC_Score2
                OC_US = 0
                OC_West = 0
                OC_West_Top = 0
                if (oc1_results +  oc2_results)>0:
                    OC_US = (oc1_us_results + oc2_us_results) / (oc1_results +  oc2_results)

                    OC_West = (oc1_western_results + oc2_western_results) / (oc1_results +  oc2_results)
                    
                    OC_West_Top = (oc1_western_top_results + oc2_western_top_results) / (oc1_results +  oc2_results)


                print ("OC", term, int(round(OC_Score, 0)), int(round(OC1, 0)), int(round(OC2, 0)), round(OC_US, 2), round(OC_West_Top, 2), round(OC_West, 2))
                results[term] = (int(round(OC_Score, 0)), int(round(OC1, 0)), int(round(OC2, 0)), round(OC_US, 2), round(OC_West_Top, 2), round(OC_West, 2))
                
                # return (term, int(round(OC_Score, 0)), int(round(OC1, 0)), int(round(OC2, 0)), round(OC_US, 2), round(OC_West, 2))
    except:
        print("OC Exception", term_under_process)
        release_proxy(proxy)
        if len(term_under_process)>0:
            print("OC ", term_under_process, "Retries :", retries[term_under_process])
            if retries[term_under_process]>=max_retries:
                results[term_under_process] = (0, 0, 0, 0, 0)
                print("OC", term_under_process, 0, 0, 0, 0, 0)
            else:
                retries[term_under_process]+=1
                raise Exception("Exception")
        else:
            raise Exception("Exception")
    finally:
        release_proxy(proxy)



def main(data):
    if (data) and ("nonprofits_only" in data.keys()):
        if (data["nonprofits_only"]==1) or (data["nonprofits_only"]==2):
            config.nonprofits_only = data["nonprofits_only"]
    
    if (data) and ("TERMS_FILE" in data.keys()):
        utils.TERMS_FILE = data["TERMS_FILE"]
    terms = utils.get_terms()
    # terms = ["heavy lift"]
    # print("OC", terms)
    global proxies
    proxies = utils.get_proxies()
    global western_countries
    western_countries = utils.get_western_countries()

    global western_top_countries
    western_top_countries = utils.get_western_top_countries()

    terms_reshaped = []
    start = 0
    end = math.ceil(len(terms)/config.threads)
    while start<len(terms):
        terms_reshaped.append(terms[start:min(end, len(terms))])
        start=end
        end+=math.ceil(len(terms)/config.threads)
    # print(terms_reshaped)
    
    executor = ThreadPoolExecutor(max_workers=threads)
    for result in executor.map(search_term, [term_list for term_list in terms_reshaped]):
        pass

    # for term in terms_reshaped:
    #     search_term(term)
    global results
    results = [[term, results[term][0], results[term][1], results[term][2], results[term][3], results[term][4], results[term][5]] for term in terms]
    today = datetime.today()
    with open(f"{dir_path}\\OC_output_{today.strftime('%Y%d%m_%H%M%S')}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "OC_Score", "OC1", "OC2", "OC_US", "OC_West_Top", "OC_West"])
        writer.writerows(results)
    return results

# main()
if __name__ == '__main__':
    main({})