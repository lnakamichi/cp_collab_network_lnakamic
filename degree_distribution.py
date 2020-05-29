import matplotlib
import pandas as pd
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from db_writer import *

cnx, cur = init_connection_with_json("./login.json")


def get_degree(first_name, last_name):
    query_text = ("SELECT COUNT(DISTINCT cid) FROM (Authors2 LEFT JOIN Researchers2 ON Authors2.rid = Researchers2.rid)"
                  + " WHERE first_name = %s AND last_name = %s")
    return execute_select_operation((query_text, (first_name, last_name)), cur)[0][0]


MATH_FACULTY = [
    'Bonini, Vincent',
    'Borzellino, Joe',
    'Brussel, Eric',
    'Camp, Charles',
    'Champney, Danielle',
    'Charalampidis, Stathis',
    'Choboter, Paul',
    'Dimitrova, Elena',
    'Easton, Rob',
    'Grundmeier, Todd',
    'Gu, Caixing',
    'Hamilton, Emily',
    'Kato, Goro',
    'Kaul, Anton',
    'Kirk, Colleen',
    'Liese, Jeff',
    'Lin, Joyce',
    'Medina, Elsa',
    'Mendes, Anthony',
    'Paquin, Dana',
    'Patton, Linda',
    'Pearse, Erin',
    'Retsek, Dylan',
    'Richert, Ben',
    'Riley, Kate',
    'Robbins, Marian',
    'Schinck-Mikel, Amelie',
    'Shapiro, Jonathan',
    'Sherman, Morgan',
    'Stankus, Mark',
    'Sze, Lawrence',
    'White, Matthew',
    'Yoshinobu, Stan',
    # MATH LECTURERS
    'Bishop, Rebecca',
    'Chi, Haoyan',
    'Elwood, Jason',
    'Gervasi, Jeff',
    'Grishchenko, Lana',
    'Hahlbeck, Clint',
    'Hesselgrave, Bill',
    'Jenkin, Bryce',
    'Kreider, Brandy',
    'McCaughey, Tim',
    'Quackenbush, Blaine',
    'Robertson, Mike',
    'Schuster, Sonja',
    'Terry, Raymond',
    'Watson, Sean',
    'Yang, Fan'
]

BIO_FACULTY = [
    'Adams, Nikki',
    'Bean, Tim',
    'Black, Michael',
    'Blank, Jason',
    'Clement, Sandra',
    'Davidson, Jean',
    'Fidopiastis, Pat',
    'Francis, Clinton',
    'Grossenbacher, Dena',
    'Hardy, Kristin',
    'Himelblau, Ed',
    'Keeling, Elena',
    'Knight, Charles',
    'Kolluru, Gita',
    'Lema, Sean',
    'Liwanag, Heather',
    'Martinez, Nathaniel',
    'Pasulka, Alexis',
    'Perrine, John',
    'Rajakaruna, Nishi',
    'Ritter, Matthew',
    'Ruttenberg, Ben',
    'Strand, Christy',
    'Taylor, Emily',
    'Tomanek, Lars',
    'Villablanca, Francis',
    'Vredevoe, Larisa',
    'White, Crow',
    'Winstead, Candace',
    'Yep, Alejandra',
    'Yeung, Marie',
    'Yost, Jenn',
    # BIO LECTURERS
    'Bunting, Jamie',
    'Jones, Michael',
    'Babu, Praveen',
    'Bergen, Anne Marie',
    'Debruhl, Heather',
    'Goschke, Grace',
    'Hendricks, Steve',
    'Howes, Amy',
    'Jew, Kara',
    'Maj, Magdalena',
    'May, Mellisa',
    'McConnico, Laurie',
    'Neal, Emily',
    'Needles, Lisa',
    'O\'Neill, Megan',
    'Pisula, Anneka',
    'Polacek, Kelly',
    'Resner, Emily',
    'Roest, Michele',
    'Ryan, Sean',
    'Trunzo, Juliana',
    'VanderKelen, Jennifer'
]

EE_FACULTY = [
    'Dennis Derickson',
    'Samuel Agbo',
    'William Ahlgren',
    'Dean Arakaki',
    'Bridget Benson',
    'David Braun',
    'Joseph Callenes-Sloan',
    'Andrew Danowitz',
    'Fred DePiero',
    'Dale Dolan',
    'Ben Hawkins',
    'Xiaomin Jin',
    'Albert Liddicoat',
    'Art MacCarley',
    'James Mealy',
    'Ahmad Nafisi',
    'John Oliver',
    'Wayne Pilkington',
    'Majid Poshtan',
    'Vladimir Prodanov',
    'John Saghri',
    'Ali Shaban',
    'Lynne Slivovsky',
    'Tina Smilkstein',
    'Taufik Taufik',
    'Xiao-Hua Yu',
    'Jane Zhang',
    # EE LECTURERS
    'Kurt Behpour',
    'Chuck Bland',
    'Nazeih Botros',
    'Mostafa Chinichian',
    'Ali Dehghan Banadaki',
    'Steve Dunton',
    'Ron Eisworth',
    'Mona El Helbawy',
    'John Gerrity',
    'Doug Hall',
    'Paul Hummel',
    'Marty Kaliski',
    'Amin Malekmohammadi',
    'Dan Malone',
    'David McDonald',
    'Clay McKell',
    'Rich Murray',
    'Maxwell Muscarella',
    'Gary Perks',
    'John Planck',
    'Asit Rairkar',
    'Joe Sparks',
    'Hiren Trada',
    'Siddharth Vyas',
    'Michael Wilson'
]

CS_FACULTY = [
    'Chris Lupo',
    'Paul Anderson',
    'Hisham Assal',
    'John Bellardo',
    'John Clements',
    'Bruno da Silva',
    'Bruce DeBruhl',
    'Alex Dekhtyar',
    'Christian Eckhardt',
    'Sussan Einakian',
    'Davide Falessi',
    'Dongfeng Fang',
    'Sara Ford',
    'Kris Fox',
    'Hasmik Gharibyan',
    'Paul Hatalsky',
    'Michael Haungs',
    'Irene Humer',
    'David Janzen',
    'Daniel Kauffman',
    'Aaron Keen',
    'Foaad Khosmood',
    'Toshihiro Kuboi',
    'Franz Kurfess',
    'Kurt Mammen',
    'Andrew Migler',
    'Theresa Migler',
    'Kirsten Mork',
    'Phillip Nico',
    'Maria Pantoja',
    'David Parkinson',
    'Zachary Peterson',
    'John Planck',
    'Michael Reynosa',
    'Nicholas Sakellariou',
    'John Seng',
    'Erin Sheets',
    'Christopher Siu',
    'Hugh Smith',
    'Clint Staley',
    'Lubomir Stanchev',
    'Clark Turner',
    'Ignatios Vakalis',
    'Michael Van De Vanter',
    'Jonathan Ventura',
    'Kurt Voelker',
    'Zoë Wood',
    'Julie Workman'
]

# degrees = []
# for researcher in CS_FACULTY:
#     name_split = researcher.split()
#     degree = get_degree(name_split[0].lower().strip(), ' '.join(name_split[1:]).lower().strip())
#     if degree > 20:
#         print("researcher: {0}".format(researcher))
#         print(degree)
#     degrees.append(degree)
#
# for degree in set(degrees):
#     print("{0}: {1}".format(degree, degrees.count(degree)))

# Generate Degree distribution plot
cnx, cur = init_connection_with_json("./login.json")
t = list(filter(lambda x: x < 150, map(lambda t: t[0], select_degrees(cur))))
num_bins = 25
n, bins, patches = plt.hist(t, num_bins, facecolor='blue', alpha=0.5)
plt.xlabel(r"Co-authorship Experience Count")
plt.ylabel(r"Number of Researchers")

plt.savefig('./data/degree_distribution.jpg')
close_connection(cnx, cur)
