// public/js/app.js

// URL of your deployed Google Cloud Function
// Update this once you deploy the function to GCP
const GCP_FUNCTION_URL = 'https://us-central1-vocal-tracker-387016.cloudfunctions.net/butterfly-classifier';

document.getElementById('image-upload').onchange = function (event) {
    const file = event.target.files[0];
    if (file) {
        // Create a URL for the file to show preview
        const reader = new FileReader();
        reader.onload = function (e) {
            const previewImage = document.getElementById('image-preview');
            const previewContainer = document.getElementById('preview-container');
            const uploadForm = document.getElementById('upload-form');

            uploadForm.classList.add('hidden');

            // Set image source and show container
            previewImage.src = e.target.result;
            previewContainer.classList.remove('hidden');
            previewContainer.classList.add('flex'); // Ensure flex layout is active
        }
        reader.readAsDataURL(file);
    }
};

document.getElementById('predict-btn').addEventListener('click', async function () {
    const fileInput = document.getElementById('image-upload');
    const file = fileInput.files[0];
    const errorContainer = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const btnText = document.getElementById('predict-btn-text');

    if (!file) {
        errorText.textContent = "Please select an image first.";
        errorContainer.classList.remove('hidden');
        return;
    }

    try {
        // Hide previous errors
        errorContainer.classList.add('hidden');
        btnText.textContent = "Analyzing...";
        this.disabled = true;
        this.classList.add('opacity-75');

        // Create form data
        const formData = new FormData();
        formData.append('image', file);

        // Send to GCP Function
        const response = await fetch(GCP_FUNCTION_URL, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to predict image');
        }

        // Hide upload section, show results
        document.getElementById('upload-section').classList.add('hidden');
        document.getElementById('upload-section').classList.remove('flex');

        document.getElementById('result-section').classList.remove('hidden');
        document.getElementById('result-section').classList.add('flex');

        // Populate results
        document.getElementById('result-name').textContent = data.prediction;
        document.getElementById('result-confidence').textContent = data.confidence;
        document.getElementById('result-scientific-name').textContent = data.scientific_name;
        document.getElementById('result-description').textContent = data.description;
        document.getElementById('result-habitat').textContent = data.habitat;
        document.getElementById('result-common-in').textContent = data.common_in;
        document.getElementById('result-image').style.backgroundImage = `url(${document.getElementById('image-preview').src})`;

    } catch (error) {
        console.error("Prediction Error:", error);
        errorText.textContent = error.message || "Could not connect to the cloud function.";
        errorContainer.classList.remove('hidden');
    } finally {
        btnText.textContent = "Predict Species";
        this.disabled = false;
        this.classList.remove('opacity-75');
    }
});

function resetApp() {
    document.getElementById('image-upload').value = '';
    document.getElementById('result-section').classList.add('hidden');
    document.getElementById('result-section').classList.remove('flex');

    document.getElementById('upload-section').classList.remove('hidden');
    document.getElementById('upload-section').classList.add('flex');

    document.getElementById('preview-container').classList.add('hidden');
    document.getElementById('preview-container').classList.remove('flex');

    document.getElementById('upload-form').classList.remove('hidden');
    document.getElementById('error-message').classList.add('hidden');
}
