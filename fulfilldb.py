from cs50 import SQL
from collections import Counter

from helpers import cookbook

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///cookbook.db")


allergies, data = cookbook()

# search dublicates in data
titles={}
titles_set=set()
titles_list=[]

for recipe in data:
    if (recipe) and (recipe['title']):
        titles_set.add(recipe['title']) # make a set of unique titles
        titles_list.append(recipe['title'])
#print (len(titles_set), len(titles_list))


# insert unique titles into the db
for title in titles_set:
    result = db.execute("INSERT INTO recipes2 (title) VALUES (:title)", title=title)

'''# get a dict with dublicates title:number of copies
count = Counter(titles_list)
for k in sorted(count, key=count.get):
    if count[k]>1:
        titles[k]=count[k]

# clean db from dublicates
for title in titles.keys():
    #result = db.execute("SELECT * from recipes WHERE title=:title", title=title)
    for i in range(1,titles[title]-1):
        result2=db.execute("SELECT * from recipes WHERE title=:title", title=title)
        #result2=db.execute("DELETE from recipes WHERE title=:title", title=title)
'''