import os
from flask import Flask, request, render_template_string, redirect, url_for, render_template
import google.generativeai as genai
import urllib.parse

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

genai.configure(api_key='AIzaSyC_xdMDEPfqZmR0xEx0lGq5Al5-X_jQKRc')
model = genai.GenerativeModel("gemini-1.5-flash")
curr_ingredients = []


def contactGemini1(file_path):
    my_file = genai.upload_file(file_path)
    ingredients = model.generate_content(
        [my_file, "\n\n", "write me a comma separated list of all of the groceries in this image."]
    )
    menu = model.generate_content('Joey needs 4 delicious, healthy, nutritious, and balanced dishes using ' + ingredients.text +
                                  '. Only give Joey the names of the four singular dishes in a comma separated list!!! Do not provide an introduction and jump straight into the list of dishes because Joey is so hungry he could die if you waste any time!!')

    global curr_ingredients
    curr_ingredients = ingredients.text
    return menu.text.split(', ')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return "No file part"

    file = request.files['image']

    if file.filename == '':
        return "No selected file"

    if file:

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        menu = contactGemini1(file_path)

        serialized_menu = urllib.parse.quote(','.join(menu))

        return redirect(url_for('menu_page', menu=serialized_menu))

@app.route('/menu')
def menu_page():
    menu = request.args.get('menu', '')

    menu_list = urllib.parse.unquote(menu).split(',')

    return render_template('menu.html', string_list=menu_list)

@app.route('/item/<item>')
def item_page(item):
    format = '''Yield: 
                Prep Time: 
                Cook time: 
                Ingredients: 
                Instructions:
                Notes: '''
    recipe = model.generate_content("Make a recipe for " + item + "and try to mainly use the following ingredients: " +
                                    curr_ingredients + ". Follow the format of " + format)
    formatted_recipe = recipe.text.replace('\n', '<br>')
    return render_template('recipe.html', item=item, recipe=formatted_recipe)

if __name__ == '__main__':
    app.run(debug=True)