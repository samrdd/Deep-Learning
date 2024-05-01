from flask import Flask, send_from_directory, jsonify, render_template, request
import os
import time
from model import ImageDescriptionGenerator
from metadata import check_and_embed_tags
import base64

app = Flask(__name__, static_folder='static')

image_directory = r'C:\Users\rgujjula1153\PycharmProjects\Gallery_Web_App\test_images'
model_path = r"C:\Users\rgujjula1153\PycharmProjects\Gallery_Web_App\best_model.h5"  # Adjust the path as needed
tokenizer_path = r"C:\Users\rgujjula1153\PycharmProjects\Gallery_Web_App\tokenizer.pkl"  # Adjust the path as needed
img_desc_gen = ImageDescriptionGenerator(model_path, tokenizer_path)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/images')
def list_images():
    images = []
    for f in os.listdir(image_directory):
        if os.path.isfile(os.path.join(image_directory, f)):
            try:
                # Get the last modified time of the file
                mod_time = os.path.getmtime(os.path.join(image_directory, f))
                # Convert it to a human-readable date (or keep it as a timestamp if you prefer)
                mod_time = time.strftime('%Y-%m-%d', time.localtime(mod_time))
                description = img_desc_gen.get_description(os.path.join(image_directory, f))

                with open(os.path.join(image_directory, f), 'rb') as file:
                    file_data = base64.b64encode(file.read()).decode('utf-8')

                images.append({'filename': f, 'date': mod_time, 'description': description, 'filedata': file_data})
            except Exception as e:
                print(f"Error processing image {f}: {e}")

    # Sort images by the modification date
    images.sort(key=lambda x: x['date'])

    return jsonify(images)


@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(image_directory, filename)


@app.route('/check_and_embed_tags', methods=['POST'])
def check_and_embed_tags_api():
    try:
        data = request.get_json()

        if 'hashtags' in data and isinstance(data['hashtags'], list) and len(data['hashtags']) > 0:
            # Assuming check_and_embed_tags is a function that processes the data
            filename = data.get('filename')
            if filename:
                image_path = os.path.join(image_directory, filename)
                check_and_embed_tags(image_path, data['hashtags'])
                return jsonify({"message": 'success'})
            else:
                return jsonify({'error': 'Filename is missing in the request data.'})
        else:
            return jsonify({'error': 'Hashtags have to be present in the body and should be a non-empty list.'})
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'})


if __name__ == '__main__':
    app.run(debug=True)