let hashtags = [];

function showLoader(message) {
    var loader = document.getElementById('loader');
    var overlay = document.getElementById('overlay');
    var body = document.body;
    var loaderMessage = document.getElementById('loaderMessage');
    loaderMessage.textContent = message;
    loader.style.display = 'block';
    overlay.style.display = 'block';
    body.classList.add('loading'); // Add a loading class to the body
}

function hideLoader() {
    var loader = document.getElementById('loader');
    var overlay = document.getElementById('overlay');
    var body = document.body;
    var loaderMessage = document.getElementById('loaderMessage');
    loaderMessage.style.display = 'none';
    loader.style.display = 'none';
    overlay.style.display = 'none';
    body.classList.remove('loading'); // Remove the loading class
}

async function check_and_embed_tags(hashtagsData) {
    showLoader('Checking and embedding tags for ' + hashtagsData.filename);
    try {
        const response = await fetch('/check_and_embed_tags', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(hashtagsData),
        });

        const data = await response.json();
        if (data.message == 'success') {
            console.log(hashtagsData.filename + ' file meta data updated');
            hideLoader();
        }
    } catch (error) {
        console.error('Error checking and embedding tags', error);
        hideLoader();
    }
}

async function generateHashtags(item) {
    try {
        showLoader('Generating hashtags for ' + item.filename);

        const { filename, date, description, filedata } = item;
        
        var requestData = {
            requests: [{
                features: [{ maxResults: 50, type: 'LABEL_DETECTION' }, { "maxResults": 50, "type": "OBJECT_LOCALIZATION" }],
                image: { content: filedata }
            }]
        };

        const response = await fetch(visionApiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
        });

        const data = await response.json();
        var labels = data.responses[0].labelAnnotations;
        let values = [];
        for (var i = 0; i < labels?.length; i++) {
            values.push(labels[i].description.toLowerCase().replace(/\s/g, ""));
        }
        var objects = data.responses[0].localizedObjectAnnotations;
        if (objects && objects?.length > 0) {
            for (var i = 0; i < objects.length; i++) {
                values.push(objects[i].name.replace(/\s/g, ""));
            }
        }
        var hashtagsData = {
            hashtags: values,
            filename: filename,
            description: description,
            filedata: filedata,
            date: date
        }
        hashtags.push(hashtagsData);
        await check_and_embed_tags(hashtagsData);
        return hashtagsData;
    } catch (error) {
        console.error('Error generating hashtags', error);
    } finally {
        hideLoader(); // Hide loader after processing each image
    }
}


async function loadImages() {
    showLoader('Loading images...');
    const response = await fetch('/images');
    const images = await response.json();
    const timeline = document.getElementById('imageGallery');
    timeline.innerHTML = ''; // Clear the timeline first
    timeline.className = 'timeline';
    let dateSections = {};

    for (const item of images) {
        const { filename, date, description, filedata } = item;

        // Create a new section for a new date
        if (!dateSections[date]) {
            const dateSection = document.createElement('div');
            dateSection.className = 'date-section';

            const dateHeader = document.createElement('div');
            dateHeader.className = 'date-header';
            dateHeader.textContent = date;
            dateSection.appendChild(dateHeader);

            const imagesContainer = document.createElement('div');
            imagesContainer.className = 'images-container';
            dateSection.appendChild(imagesContainer);

            timeline.appendChild(dateSection);
            dateSections[date] = imagesContainer;
        }

        // Append images to the correct date section
        const img = document.createElement('img');
        img.className = 'image-item';
        img.setAttribute('data-filename', filename);
        img.src = '/images/' + filename;
        const hashtagsData = await generateHashtags(item);
        dateSections[date].appendChild(img);
    }

    hideLoader(); // Hide loader after all images are processed
}

document.addEventListener('DOMContentLoaded', loadImages);

function searchImages() {
    // Implement search functionality here
    showLoader('Searching images...');
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();

    // Loop through each image item
    const matchingImages = hashtags.filter(data => {
        const hashtagsList = data.hashtags.map(tag => tag.toLowerCase());
        return hashtagsList.some(tag => tag.includes(searchTerm));
    });

    // Clear existing date sections
    const timeline = document.getElementById('imageGallery');
    timeline.innerHTML = '';

    let dateSections = {};

    // Loop through each matching image and update display
    matchingImages.forEach(data => {
        const { filename, date } = data;

        if (!dateSections[date]) {
            // Create a new section for a new date
            const dateSection = document.createElement('div');
            dateSection.className = 'date-section';

            const dateHeader = document.createElement('div');
            dateHeader.className = 'date-header';
            dateHeader.textContent = date;
            dateSection.appendChild(dateHeader);

            const imagesContainer = document.createElement('div');
            imagesContainer.className = 'images-container';
            dateSection.appendChild(imagesContainer);

            timeline.appendChild(dateSection);
            dateSections[date] = imagesContainer;
        }

        // Append images to the correct date section
        const img = document.createElement('img');
        img.className = 'image-item';
        img.src = '/images/' + filename;
        dateSections[date].appendChild(img);
    });
    hideLoader();
}


// Event listener for the search box
document.getElementById('searchInput').addEventListener('keyup', searchImages);

// Initial load of images