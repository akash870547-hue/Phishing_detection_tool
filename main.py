from flask import Flask, render_template, request
from google import genai
import os
import PyPDF2

# -------------------------------
# 1️⃣ Flask app initialization
# -------------------------------
app = Flask(__name__)

# -------------------------------
# 2️⃣ Set Google Gemini API Key
# -------------------------------
os.environ["GEMINI_API_KEY"] = "GEMINI API KEY "
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# -------------------------------
# 3️⃣ Functions
# -------------------------------

def predict_fake_or_real_email_content(text):
    prompt = f"""
You are an expert in identifying scam messages in text or email. 
Analyze the following text and classify it as Real/Legitimate or Scam/Fake.

Text: {text}

Return a clear message only indicating if it is real or a scam. 
If scam, briefly mention why. 
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[{"text": prompt}]
    )
    return response.text.strip() if response else "Classification failed."


def url_detection(url):
    prompt = f"""
Analyze the following URL for security threats and classify it as: 
benign, phishing, malware, or defacement. 
URL: {url}

Return only the class name in lowercase.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[{"text": prompt}]
    )
    return response.text.strip().lower() if response else "Detection failed."


# -------------------------------
# 4️⃣ Flask routes
# -------------------------------

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/scam/', methods=['POST'])
def detect_scam():
    if 'file' not in request.files:
        return render_template("index.html", message="No file uploaded.")

    file = request.files['file']
    extracted_text = ""

    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        extracted_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    elif file.filename.endswith('.txt'):
        extracted_text = file.read().decode("utf-8")
    else:
        return render_template("index.html", message="Invalid file type. Upload PDF/TXT only.")

    if not extracted_text.strip():
        return render_template("index.html", message="File is empty or could not extract text.")

    message = predict_fake_or_real_email_content(extracted_text)
    return render_template("index.html", message=message)


@app.route('/predict', methods=['POST'])
def predict_url():
    url = request.form.get('url', '').strip()
    if not url.startswith(("http://", "https://")):
        return render_template("index.html", message="Invalid URL format.", input_url=url)

    classification = url_detection(url)
    return render_template("index.html", input_url=url, predicted_class=classification)


# -------------------------------
# 5️⃣ Run Flask server
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)

