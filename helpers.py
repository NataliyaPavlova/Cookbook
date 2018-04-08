import json
import pprint
import re
from collections import Counter
from flask import redirect, render_template, request, session
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code=400):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def cookbook():
    ''' Prepare the cookbook '''

    #open json file to read
    with open("full_format_recipes.json") as f:
        data=json.load(f)
        #pprint.pprint(data[2])

    # gather all unique categories in one set
    unique_categories=set()
    for dict_ in data:
        if (dict_):
            for category in dict_["categories"]:
                unique_categories.add(category)

    unique_categories=list(unique_categories)
    unique_categories.sort()
    #print(unique_categories)

    # make new data consisted of unique recipes
    titles_set=set()
    data_unique=[]

    for recipe in data:
        if (recipe) and (recipe['title']):
            titles_set.add(recipe['title']) # make a set of unique titles
    #print(len(titles_set))
    for recipe in data:
        if (recipe) and (recipe['title']):
            if recipe['title'] in titles_set:
                data_unique.append(recipe)
                #del from the set
                titles_set.remove(recipe['title'])
    #print(len(data_unique))


    # make 'allergy' lists of categories (gluten, eggs, dairy, nuts, honey, soy) to filter recipes thereafter
    gluten_list = ['Pizza', 'Pie', 'Bake', 'Barley', 'Biscuit', 'Bread', 'Breadcrumps', 'Bulgur',
                   'Cake', 'Cookie', 'Cookies', 'Cupcake', 'Flat Bread', 'Fritter', 'Grains',
                   'Hamburger', 'Noodle', 'Noodles', 'Oat', 'Oatmeal',
                   'Pasta', 'Pasta Maker', 'Pastry', 'Phyllo/Puff Pastry Dough', 'Pie', 'Pizza',
                   'Pot Pie', 'Quiche', 'Rye', 'Sandwich', 'Semolina', 'Sourdough', 'Tart', 'Tortillas',
                   'Waffle', 'Wheat']
    soy_list = ['Soy', 'Soy Sauce', 'Tofu']
    nuts_list = ['Almond', 'Butternut Squash', 'Chestnut', 'Coconut', 'Hazelnut', 'Macadamia Nut', 'Nut',
                 'Nutmeg', 'Peanut', 'Peanut Butter', 'Pecan', 'Pine Nut', 'Pistachio', 'Tree Nut',
                 'Walnut']
    dairy_list = ['Blue Cheese', 'Brie', 'Butter', 'Buttermilk', 'Cutterscotch/Caramel', 'Cheddar',
                  'Cheese', 'Cottage Cheese', 'Cream Cheese', 'Dairy', 'Feta', 'Goat Cheese',
                  'Ice Cream', 'Macaroni and Cheese', 'Marscarpone', 'Milk/Cream', 'Mozzarella',
                  'Parmesan', 'Ricotta', 'Sour Cream', 'Swiss Cheese', 'Yogurt']
    seafood_list = ['Clam', 'Cod', 'Crab', 'Fish', 'Octopus', 'Oyster', 'Salmon', 'Seafood', 'Shellfiosh',
                    'Shrimp', 'Swordfish', 'Tuna', 'Trout']
    eggs_list = ['Egg', 'Eggs', 'Egg Nog', 'Frittata', 'Mayonnaise', 'Omelet']
    honey_list = ['Honey', 'Honeydew']

    allergies={}
    allergies['eggs'] = list(map(lambda x: x.lower(), eggs_list))
    allergies['gluten'] = list(map(lambda x: x.lower(), gluten_list))
    allergies['soy'] = list(map(lambda x: x.lower(), soy_list))
    allergies['nuts'] = list(map(lambda x: x.lower(), nuts_list))
    allergies['dairy'] = list(map(lambda x: x.lower(), dairy_list))
    allergies['honey'] = list(map(lambda x: x.lower(), honey_list))
    allergies['seafood'] = list(map(lambda x: x.lower(), seafood_list))
   # print(allergies['gluten'])
    return allergies, data_unique

def check_ingr(ingredients, allerg, allergies):
    ''' Returns True if there is an allergen in ingredients'''
    ingr_list=set()
    # make a dict of ingredients
    for string in ingredients:
        string = re.split('[^a-z]', string.lower()) # only letters remain
        string = list(filter(lambda x: len(x)>2, string)) # words with >2 letters length remain
        for word in string:
            ingr_list.add(word)

    for ingr in ingr_list:
        if ingr in allergies[allerg]:
            return True
    return False


def meets_conditions(mark_allergies, recipe, allergies, preferencies, meal):
    ''' Returns True if a recipe meets the allergy conditions (no allergens in categories and ingredients) and user's given preferencies'''

    marker=0 #marker for preferencies
    if not 'categories' in recipe.keys():
        return False

    categories = list(map(lambda x: x.lower(), recipe["categories"]))
    preferencies = list(map(lambda x: x.lower(), preferencies))

    #check allergy criteria
    for allerg in mark_allergies:
        #check if category is allergic
        for category in categories:
            if category in allergies[allerg]:
                return False

        #check if allergen is in ingredients
        if check_ingr(recipe['ingredients'], allerg, allergies):
            return False

    #check meal criteria
    if meal=='snack':
        if not (meal in categories) and not ("hors d'oeuvre" in categories):
            return False
    else:
        if not meal in categories and not meal=='':
            return False

    #check preferencies criteria: if at least one preference fits categories, it's true
    '''if all(x in recipe["categories"] for x in preferencies):
        marker=1'''
    for category in categories:
        if category in preferencies:
            marker=1
    if not marker==1 and not preferencies==[]:
        return False

    '''    snack')  "Hors D'Oeuvre"
        Vegetarian') Vegan Vegetable
        Low Sugar')
        preferencies.append('Sugar Concious')
        preferencies.append('Low/No Sugar')
        Easy-Cooking"):
        preferencies.append('Quick & Easy')
        preferencies.append('Quick and Healthy')
        preferencies.append('22-Minute Meals')
        preferencies.append('3-Ingredient Recipes'

            '''

    return True


def search_recipes(mark_allergies, preferencies, meal):
    ''' Find all recipes from cookbook meeting the criteria '''

    recipes_result = [] #result
    allergies, data = cookbook()

    # iterate through the whole cookbook and filter recipes
    for recipe in data:
        if meets_conditions(mark_allergies, recipe, allergies, preferencies, meal):
            recipes_result.append(recipe['title'])

    return recipes_result


def find_recipe(title):
    ''' Find a recipe with given title'''

    title=title+' '
    allergies, data = cookbook()
    recipe=list(filter(lambda x: x and x['title']==title, data))

    return recipe[0]

def str_to_list(string):
    ''' Makes a list from string-former list'''

    string = re.split("[^a-zA-Z0-9\- &/]", string)
    string = list(filter(lambda x: len(x)>2, string))

    return string

