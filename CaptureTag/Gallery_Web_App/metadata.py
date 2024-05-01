from PIL import Image
import piexif
import os
from nltk.tokenize import word_tokenize


def find_images_with_tags(folder_path, sentence):
    """
    Returns a list of images that contain any of the words in the sentence within their tags.

    :param folder_path: The file path to the folder containing images.
    :param sentence: A sentence to tokenize into words.
    :return: A list of image filenames that contain any of the sentence tokens in their tags.
    """
    # Tokenize the sentence into words
    tokens = set(word_tokenize(sentence.lower()))

    # List to hold the names of images that contain the tokens in their tags
    matching_images = []

    # Iterate over each file in the directory
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)

            # Attempt to read the image and its tags
            try:
                img = Image.open(image_path)
                if 'exif' in img.info:
                    exif_data = piexif.load(img.info['exif'])
                    if piexif.ImageIFD.XPKeywords in exif_data['0th']:
                        # Retrieve the tags
                        tags_bytes = exif_data['0th'][piexif.ImageIFD.XPKeywords]
                        # Check if the tags are in a tuple format and decode appropriately
                        if isinstance(tags_bytes, tuple):
                            tags = "".join([chr(b) for b in tags_bytes if isinstance(b, int)])
                            # tags = b''.join(tags_bytes).decode('utf-16le', errors='ignore').replace('\x00', '')

                        else:
                            tags = tags_bytes.decode('utf-16le', errors='ignore').replace('\x00', '')

                        tags = tags.lower()

                        filtered_tags = ''.join(i for i in tags if ord(i))

                        # Split the tags into a set of words
                        tags_set = set(filtered_tags.replace(';', ' ').split())

                        # Check if any of the tokens are in the tags
                        if tokens.intersection(tags_set):
                            matching_images.append(filename)

            except Exception as e:
                print(f"Error reading image {filename}: {e}")

    return matching_images

# # Example usage:
# folder_path = '/content/test_images/test images'  # Replace with the actual path to your folder containing images
# sentence = 'A beautiful sunset at the beach'

# # Call the function
# matching_image_files = find_images_with_tags(folder_path, sentence)
# print("Images with matching tags:", matching_image_files)

def check_and_embed_tags(image_path, words_list):
    """
    Checks if the image already has tags in its metadata.
    If not, it embeds the provided list of words as tags.

    :param image_path: The file path of the image to check and modify.
    :param words_list: A list of words to embed as tags in the image metadata if tags are not present.
    """
    # Load the image
    img = Image.open(image_path)

    # Check if the image has existing EXIF data
    if 'exif' in img.info:
        exif_dict = piexif.load(img.info['exif'])
        
        # Check if there are already tags in the 'XPKeywords' field
        if piexif.ImageIFD.XPKeywords in exif_dict['0th']:
            print("Tags already present in the image metadata.")
            return 
        else:
            print("No tags found. Embedding new tags.")
            embed_tags_in_image(image_path, words_list)
    else:
        print("No EXIF data found. Embedding new tags.")
        embed_tags_in_image(image_path, words_list)

def embed_tags_in_image(image_path, words_list):
    """
    Embeds a list of words as tags into the metadata of a JPEG image and overwrites the original image.

    :param image_path: The file path of the image to modify.
    :param words_list: A list of words to embed as tags in the image metadata.
    """
    tags_string = '; '.join(words_list).encode('utf-16le')
    img = Image.open(image_path)
    exif_dict = piexif.load(img.info['exif']) if 'exif' in img.info else {}
    if not exif_dict:
        exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}
    exif_dict['0th'][piexif.ImageIFD.XPKeywords] = tags_string
    exif_bytes = piexif.dump(exif_dict)
    img.save(image_path, "jpeg", exif=exif_bytes)

# Example usage
# image_path = '/content/10.jpg'  # Replace with the actual path to your JPEG image
# words_list = ['nature', 'trees', 'sun']  # List of words to embed as tags

# # Call the function
# check_and_embed_tags(image_path, words_list)




def check_images_with_tags(image_path):
    """
    Checks if the image already has tags in its metadata.

    :param image_path: The file path of the image to check and modify.
    """
    # Load the image
    img = Image.open(image_path)

    # Check if the image has existing EXIF data
    if 'exif' in img.info:
        exif_dict = piexif.load(img.info['exif'])
        
        # Check if there are already tags in the 'XPKeywords' field
        if piexif.ImageIFD.XPKeywords in exif_dict['0th']:
            print("Tags already present in the image metadata.")
            return True
        else:
            print("No tags found. Embedding new tags.")
            return False
    else:
        print("No EXIF data found. Embedding new tags.")
        return False

