import json
import os.path

def load_logos_from_json():
    global logo_list

    with open(logo_filename, "r") as read_file:
        logo_list = json.load(read_file)


def lookup_logo(lookup_name, look_for):

    load_logos_from_json()
    relevant_list = logo_list

    for logo in relevant_list:
        if lookup_name.upper() == logo['name'].upper():
            return logo['logo_url']

    return ""

logo_filename = "data_sources/logos.json"
logo_list = []

load_logos_from_json()
