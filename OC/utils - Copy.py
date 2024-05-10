import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

TERMS_FILE = dir_path + "\\terms.txt"
PROXIES_FILE = dir_path + "\\proxies.txt"
WESTERN_COUNTRIES_FILE = dir_path + "\\western_countries.txt"
WESTERN_TOP_COUNTRIES_FILE = dir_path + "\\western_top_countries.txt"

def get_proxies():
    with open(PROXIES_FILE, "r") as f:
        data = f.read()
        data = data.split("\n\n")
        data = [item.split("\n") for item in data]
        for item in data:
            raw_list = item[0].strip().replace("\n", "").split(":", 2)
            # item[0] = raw_list
            item[0] = f"http://{raw_list[-1]}@{raw_list[0]}:{raw_list[1]}"
            item[1] = item[1].strip().replace("\n", "")
            item[2] = item[2].strip().replace("\n", "")
        # print(data)
        return data

def get_terms():
    with open(TERMS_FILE, "r") as f:
        return [term.strip().replace("\n", "") for term in f.readlines()]

def get_western_countries():
    with open(WESTERN_COUNTRIES_FILE, "r") as f:
        return [term.strip().replace("\n", "").lower().replace(" ", "") for term in f.readlines()]

def get_western_top_countries():
    with open(WESTERN_TOP_COUNTRIES_FILE, "r") as f:
        return [term.strip().replace("\n", "").lower().replace(" ", "") for term in f.readlines()]
