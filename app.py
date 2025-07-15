import base64
from flask import Flask, render_template, request, redirect, url_for, send_file
import cv2
import numpy as np
from io import BytesIO
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
from thirukkural_model_code.numerals import numerals_main_code
from thirukkural_model_code.characters import characters_main_code as thirukkural_main
from siddha_model_code.characters import characters_main_code as siddha_main
from U_ve_sa_model_code.characters import characters_main_code as uvsa_main

# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
from time import ctime

# def to_gsheet(file_name, char_array,changed_text):
#     # Load Google Sheets API credentials from the JSON file
#     scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#     creds = ServiceAccountCredentials.from_json_keyfile_name('./palm-leaf-data-34f660ec63e1.json', scope)
#     client = gspread.authorize(creds)
#
#     # Open the Google Sheet by title
#     sheet = client.open('palm leaf predicted datas').sheet1
#
#     # Append the first row of the data
#     first = [ctime(),file_name,char_array[0],changed_text[0]]
#     sheet.append_row(first)
#     for i in range(1,len(char_array)):
#         remaining = ['','',char_array[i],changed_text[i]]
#         sheet.append_row(remaining)


# from model_code.character_preprocess import characters_pre_main_code

# from model_code.character_preprocess import
app = Flask(__name__)


# numerals code
def numerals(image):
    # reading the image as cv2 file from the web encoded image
    img = cv2.imdecode(np.fromstring(image.read(), np.uint8), cv2.IMREAD_COLOR)
    img2 = img.copy()
    img2 = cv2.resize(img2, (600, 200))
    final_output, total = numerals_main_code(img)
    # Encode the processed image to base64 to export the output
    _, img_encoded = cv2.imencode('.jpg', final_output)
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')
    _, img_encoded2 = cv2.imencode('.jpg', img2)
    img_base642 = base64.b64encode(img_encoded2).decode('utf-8')
    # Return the base64 encoded image
    return img_base64, img_base642, total


# characters
def characters(image, model_name):
    # reading the image as cv2 file from the web encoded image
    img = cv2.imdecode(np.fromstring(image.read(), np.uint8), cv2.IMREAD_COLOR)
    img2 = img.copy()
    print(model_name)
    # img2=cv2.resize(img2,(600,200))
    if model_name == 'thirukkural':
        final_output, char_array, changed_text = thirukkural_main(img)
    elif model_name == 'siddha':
        final_output, char_array, changed_text = siddha_main(img)
    elif model_name == 'uvesa':
        final_output, char_array, changed_text = uvsa_main(img)

    # Encode the processed image to base64 to export the output
    final_output = np.asarray(final_output)
    _, img_encoded = cv2.imencode('.jpg', final_output)
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')
    _, img_encoded2 = cv2.imencode('.jpg', img2)
    img_base642 = base64.b64encode(img_encoded2).decode('utf-8')
    # Return the base64 encoded image
    return img_base64, img_base642, char_array, changed_text


def characters_preprocess(image):
    # reading the image as cv2 file from the web encoded image
    img = cv2.imdecode(np.fromstring(image.read(), np.uint8), cv2.IMREAD_COLOR)
    img2 = img.copy()
    # img2=cv2.resize(img2,(600,200))
    # final_output, preprocessed_img = characters_pre_main_code(img)
    # Encode the processed image to base64 to export the output
    # final_output = np.asarray(final_output)
    # preprocessed_img = np.asarray(preprocessed_img)
    _, img_encoded = cv2.imencode('.jpg', final_output)
    img_base64_final = base64.b64encode(img_encoded).decode('utf-8')
    _, img_encoded2 = cv2.imencode('.jpg', img2)
    img_base64_original = base64.b64encode(img_encoded2).decode('utf-8')
    _, img_encoded3 = cv2.imencode('.jpg', preprocessed_img)
    img_base64_pre = base64.b64encode(img_encoded3).decode('utf-8')
    # Return the base64 encoded image
    return img_base64_final, img_base64_original, img_base64_pre


# login page
@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        print("email", email == "tamil@gamil.com", "password", password, type(email), type(password))
        if email == "tamil@gmail.com" and password == "123":
            print("logged In")
            return redirect(url_for('characters_upload'))
        else:
            print("login Fails !!")
            return render_template('/login.html')

    return render_template('/login.html')


# numerals page
@app.route('/numerals', methods=['GET', 'POST'])
def numerals_upload():
    if request.method == 'POST' and 'image' in request.files:
        original_image = request.files['image']
        output_image, image, total = numerals(original_image)
        # print(image)
        # filestr = image.read()
        # image = base64.b64efncode(filestr).decode('utf-8')

        return render_template('/upload.html', output_image=output_image, image=image,
                               file_name=original_image.filename, total=total)
    return render_template('/upload.html')


# characters page
@app.route('/characters', methods=['GET', 'POST'])
def characters_upload():
    if request.method == 'POST' and 'image' in request.files:
        original_image = request.files['image']
        model_name = request.form['model_name']
        output_image, image, char_array, changed_text = characters(original_image, model_name)
        if model_name == 'thirukkural':
            selected = 1
        elif model_name == 'siddha':
            selected = 2
        elif model_name == 'uvesa':
            selected = 3
        # print(tanglish)
        # print(image)
        # filestr = image.read()
        # image = base64.b64efncode(filestr).decode('utf-8')
        # to_gsheet(original_image.filename,char_array,changed_text)
        return render_template('/characters.html', output_image=output_image, image=image,
                               file_name=original_image.filename, char_array=char_array, changed_text=changed_text,
                               selected=selected)
    return render_template('/characters.html')


if __name__ == '__main__':
    # IPv4 = "10.10.145.35"
    # app.run(debug=True, host=IPv4, port=5000)
    app.run(debug=True)
