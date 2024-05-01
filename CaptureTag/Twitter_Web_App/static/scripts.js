let hashtags = [];

function showLoader() {
    var loader = document.getElementById('loader');
    var overlay = document.getElementById('overlay');
    var body = document.body;

    loader.style.display = 'block';
    overlay.style.display = 'block';
    body.classList.add('loading'); // Add a loading class to the body
}

function hideLoader() {
    var loader = document.getElementById('loader');
    var overlay = document.getElementById('overlay');
    var body = document.body;

    loader.style.display = 'none';
    overlay.style.display = 'none';
    body.classList.remove('loading'); // Remove the loading class
}

function getHashtags(description) {
    var hashtagsData = [...new Set(hashtags)];
    var hashtagsDropdown = document.getElementById('hashtagsDropdown');
    var data = {
        description: description,
        hashtags: hashtagsData
    };
    fetch('/hashtags', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then((data) => {
            var hashtagData = data.hashtags;
            if (hashtagData?.length > 0) {
                hashtagData.forEach((hashtag) => {
                    hashtags.push(hashtag)
                })
            }
            hideLoader();
        })
        .catch(error => {
            hashtagsDropdown.innerHTML = 'Error generating hashtags: ' + error.message;
            hashtagsDropdown.style.display = 'block';
            hashtagsDropdown.style.top = '40px';
            hashtagsDropdown.style.width = '200px';
            hashtagsDropdown.style.maxHeight = '250px';
            hashtagsDropdown.style.zIndex = '10';
            hashtagsDropdown.style.backgroundColor = '#fff';
            hideLoader();
        });
}

function generateHashtags(file, description) {
    var hashtagsDropdown = document.getElementById('hashtagsDropdown');
    // Replace with your Google Vision API key
    var visionApiUrl = 'https://vision.googleapis.com/v1/images:annotate?key=AIzaSyA-3st-utqZV4XsMiQ8ELWMnGer1Dxbn7s'; // Replace with your Google Vision API key
    var requestData = {
        requests: [{
            features: [{ maxResults: 50, type: 'LABEL_DETECTION' }, { "maxResults": 50, "type": "OBJECT_LOCALIZATION" }],
            image: { content: file }
        }]
    };

    fetch(visionApiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
    })
        .then(response => response.json())
        .then(data => {
            var labels = data.responses[0].labelAnnotations;
            for (var i = 0; i < labels.length; i++) {
                hashtags.push(labels[i].description.replace(/\s/g, ""));
            }
            var objects = data.responses[0].localizedObjectAnnotations;
            if (objects && objects?.length > 0) {
                for (var i = 0; i < objects.length; i++) {
                    hashtags.push(objects[i].name.replace(/\s/g, ""));
                }
            }
            getHashtags(description);
        })
        .catch(error => {
            console.log(error);
            hashtagsDropdown.innerHTML = 'Error generating hashtags: ' + error.message;
            hashtagsDropdown.style.display = 'block';
            hashtagsDropdown.style.top = '40px';
            hashtagsDropdown.style.width = '200px';
            hashtagsDropdown.style.maxHeight = '250px';
            hashtagsDropdown.style.zIndex = '10';
            hashtagsDropdown.style.backgroundColor = '#fff';
            hideLoader();
        });
}

document.addEventListener('click', function (event) {
    var hashtagsDropdown = document.getElementById('hashtagsDropdown');
    if (!event.target.matches('#tweetTextarea') && !event.target.matches('#hashtagsDropdown')) {
        hashtagsDropdown.style.display = 'none';
    }
});

function previewImage() {
    var formId = document.getElementById('uploadForm');
    var formData = new FormData(formId);
    var imageInput = document.getElementById('imageInput');
    var selectedFile = imageInput.files[0];
    var previewDiv = document.getElementById('imagePreview');
    var previewImage = document.getElementById('previewImageDisplay');
    showLoader();

    // Use FileReader to read the file data
    var reader = new FileReader();

    // Define the callback function for when the file is loaded
    if (imageInput.files && imageInput.files[0]) {
        reader.onload = function (event) {
            // The file data is available in event.target.result
            var fileData = event.target.result;
            var base64Data = reader.result.split(',')[1];

            // Now you can include the file data in your FormData
            // Continue with your fetch logic
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    var outputDiv = document.getElementById('resultsOutput');
                    if (data.error) {
                        outputDiv.innerHTML = data.error;  // Display the error
                    } else if (data.description) {

                        previewDiv.style.display = 'block';

                        // Check if previewImage already exists, if yes, remove it
                        if (previewImage) {
                            previewDiv.removeChild(previewImage);
                        }

                        // Create a new img element
                        var img = document.createElement('img');
                        img.id = 'previewImageDisplay';
                        img.src = fileData;
                        img.alt = 'Uploaded Image';
                        img.style.maxWidth = '100%';
                        img.style.maxHeight = '100%';
                        img.style.borderRadius = '20px';

                        // Append the new img element
                        previewDiv.appendChild(img);



                        //model results

                        //var descriptionDiv = document.createElement('p');
                        //descriptionDiv.innerHTML = data.description;
                        //outputDiv.appendChild(descriptionDiv); // Display the description




                        generateHashtags(base64Data, data.description);
                    } else {
                        outputDiv.innerHTML = 'No description found';  // Fallback text
                    }
                })
                .catch(error => {
                    hideLoader();
                    console.error('Error:', error);
                });
        };

        // Read the file as data URL
        reader.readAsDataURL(selectedFile);
    } else {
        previewDiv.innerHTML = ''; // Clear the preview if no image is selected
        previewDiv.style.display = 'none'; // Hide the preview div
    }
}

// Function to remove the image preview
function removeImagePreview() {
    var previewDiv = document.getElementById('imagePreview');
    var previewImage = document.getElementById('previewImageDisplay');
    var outputDiv = document.getElementById('resultsOutput');
    previewDiv.style.display = 'none'; // Hide the preview div

    // Remove the image element
    if (previewImage) {
        previewDiv.removeChild(previewImage);
    }

    hashtags = []; // Clear the hashtags
    outputDiv.innerHTML = ''; // Clear the output div
}

var tweetTextarea = document.getElementById('tweetTextarea');
var hashtagsDropdown = document.getElementById('hashtagsDropdown');

function updateHashtagsDropdown() {
    hashtagsDropdown.innerHTML = '';
    var loader = document.getElementById('loader');
    var inputText = tweetTextarea.value;
    let hashtagD = [...new Set(hashtags)];

    let hashtagData = []

    // Find the index of the first element containing '#'
    let index = hashtagD.findIndex(tag => tag.includes('#'));

    // Check if '#' was found in any element
    if (index !== -1) {
        // Split the array into two parts and reorder them
        let firstPart = hashtagD.slice(0, index);
        let secondPart = hashtagD.slice(index);
        let reorderedArray = secondPart.concat(firstPart);
        hashtagData = reorderedArray
    }
    else {
        hashtagData = hashtagD
    }
    const inputAfterHash = inputText.split('#');
    var filteredHashtags = hashtagData.filter((hashtag) => !inputAfterHash.includes(hashtag));
    filteredHashtags.forEach(function (hashtag) {
        var hashtagElement = document.createElement('div');
        hashtagElement.textContent = hashtag;
        hashtagsDropdown.appendChild(hashtagElement);
        hashtagElement.addEventListener('click', function () {
            var newText = inputText.replace(/#\S+$/, '') + '#' + hashtag;
            tweetTextarea.value = newText;
            hashtagsDropdown.style.display = 'none';
        });
    });
    if (filteredHashtags.length > 0) {
        hashtagsDropdown.style.display = 'block';
        hashtagsDropdown.style.top = '40px';
        hashtagsDropdown.style.width = '250px';
        hashtagsDropdown.style.maxHeight = '250px';
        hashtagsDropdown.style.zIndex = '10';
        hashtagsDropdown.style.backgroundColor = '#fff';
    } else {
        if (loader.style.display === 'block') {
            hashtagsDropdown.innerHTML = 'Generating... !';
            hashtagsDropdown.style.display = 'block';
            hashtagsDropdown.style.top = '40px';
            hashtagsDropdown.style.width = '200px';
            hashtagsDropdown.style.maxHeight = '250px';
            hashtagsDropdown.style.zIndex = '10';
            hashtagsDropdown.style.backgroundColor = '#fff';
        }
        else {
            hashtagsDropdown.innerHTML = 'Nothing found !';
            hashtagsDropdown.style.display = 'block';
            hashtagsDropdown.style.top = '40px';
            hashtagsDropdown.style.width = '200px';
            hashtagsDropdown.style.maxHeight = '250px';
            hashtagsDropdown.style.zIndex = '10';
            hashtagsDropdown.style.backgroundColor = '#fff';
        }
    }
}

tweetTextarea.addEventListener('keypress', (key) => {
    if (key.key === '#') {
        updateHashtagsDropdown();
    }
    else {
        hashtagsDropdown.style.display = 'none';
    }
});