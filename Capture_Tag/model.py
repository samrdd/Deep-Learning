import pickle
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

class ImageDescriptionGenerator:
    def __init__(self, model_path, tokenizer_path, max_length=74):
        self.model = load_model(model_path)
        self.tokenizer = self._load_tokenizer(tokenizer_path)
        self.max_length = max_length

    def _load_tokenizer(self, tokenizer_path):
        with open(tokenizer_path, 'rb') as handle:
            tokenizer = pickle.load(handle)
        return tokenizer

    def _prepare_image(self, image_path):
        photo = self._extract_features(image_path)
        return photo

    def _extract_features(self, filename):
        model = VGG16()
        model.layers.pop()
        model = Model(inputs=model.inputs, outputs=model.layers[-1].output)
        image = load_img(filename, target_size=(224, 224))
        image = img_to_array(image)
        image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
        image = preprocess_input(image)
        feature = model.predict(image, verbose=0)
        return feature

    def _predict_description(self, photo):
        in_seq = 'startseq'
        for i in range(self.max_length):
            seq = self.tokenizer.texts_to_sequences([in_seq])[0]
            seq = pad_sequences([seq], maxlen=self.max_length)
            y_hat = self.model.predict([photo, seq], verbose=0)
            y_hat = np.argmax(y_hat)
            word = self._int2word(y_hat)
            if word is None:
                break
            in_seq += ' ' + word
            if word == 'endseq':
                break
        return in_seq

    def _int2word(self, integer):
        for word, index in self.tokenizer.word_index.items():
            if index == integer:
                return word
        return None

    def get_description(self, image_path):
        photo = self._prepare_image(image_path)
        description = self._predict_description(photo)
        return ' '.join(description.split()[1:-1])


def main():
    model_path = r"C:\Users\kiran\OneDrive\Desktop\Twitter WebApp\flaskvenv\best_model.h5"
    tokenizer_path = r"C:\Users\kiran\OneDrive\Desktop\Twitter WebApp\flaskvenv\tokenizer.pkl"

    img_desc_gen = ImageDescriptionGenerator(model_path, tokenizer_path)

    img_path = r"C:\Users\kiran\Downloads\1.jpg"
    description = img_desc_gen.get_description(img_path)
    print(description)

if __name__ == "__main__":
    main()
