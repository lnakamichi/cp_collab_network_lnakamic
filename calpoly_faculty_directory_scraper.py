import re
import requests
import pandas as pd

from bs4 import BeautifulSoup


def split_name_hire_department(text_block):
    if text_block.count('(') == 1:
        return re.split(r'[()]', text_block)
    # assume first is nickname
    elif text_block.count('(') == 2:
        initial_list = re.split(r'[()]', text_block)
        # nickname is at initial_list[2]
        return [initial_list[0], initial_list[3], initial_list[4]]
    else:
        raise Exception('Malformed Text Block: ' + text_block)


def separate_names(name_string):
    if 'Taufik' in name_string:
        return 'Taufik', '', 'Taufik'
    first_split = name_string.split(', ')
    last_name = first_split[0]
    second_split = first_split[1].split()
    first_name = second_split[0]
    middle_name = ''
    if len(second_split) > 1:
        middle_name = second_split[1].replace('.', '')
    return first_name.lower(), middle_name.lower(), last_name.lower()


def get_calpoly_faculty_dict():
    url = "http://catalog.calpoly.edu/facultyandstaff/#facultystaffemeritustext"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    faculty_block = soup.find_all('table', {'class': 'tbl_facdir'})[0]
    row_list = list(
        filter(
            lambda block: (
                    'Mathematics' in block.text or
                    'Biological Sciences' in block.text or
                    'Electrical Engineering' in block.text or
                    'Computer Science' in block.text),
            faculty_block.find_all('tr')[1:]))
    name_to_info = {}
    for row in row_list:
        name_hire_department_block = row.find('td', {'class': 'column0'}).text
        name_hire_department_list = split_name_hire_department(name_hire_department_block)
        name = name_hire_department_list[0].strip()
        first_name, middle_name, last_name = separate_names(name)
        hire_year = name_hire_department_list[1].strip()
        department = name_hire_department_list[2].strip()
        position = row.find('td', {'class': 'column1'}).text
        education = row.find('td', {'class': 'column2'}).text
        # df_rows.append(
        #     {
        #         'first_name': first_name.lower(),
        #         'middle_name': middle_name.lower(),
        #         'last_name': last_name.lower(),
        #         'hire_year': hire_year,
        #         'department': department,
        #         'position': position,
        #         'education': education
        #     }
        # )
        name_to_info[(first_name, last_name)] = (hire_year, position, education)

    return name_to_info
