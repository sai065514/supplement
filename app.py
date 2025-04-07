from flask import Flask, request, render_template
import google.generativeai as genai
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("⚠️ ERROR: GEMINI_API_KEY is missing in the environment variables.")

genai.configure(api_key=api_key)

# Home Route
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/about")
def about():
    return render_template("about.html")


# Route to display the form for a selected category
@app.route("/form")
def show_form():
    category = request.args.get("category", "").capitalize()
    title = request.args.get("title", "").capitalize()
    return render_template("form.html", form_title=f"Patient Details for {title}", category=category)

# Route to handle supplement suggestions
@app.route("/get-supplements", methods=["POST"])
def get_supplements():
    category = request.form.get("category", "").capitalize()
    name = request.form.get("name", "").strip()
    age = request.form.get("age", "").strip()
    gender = request.form.get("gender", "").strip()
    condition = request.form.get("condition", "Not specified").strip()

    # Validate Input
    if not category or not age or not gender:
        return render_template(
            "form.html",
            form_title=f"Patient Details for {category} Health",
            category=category,
            error="⚠️ Please fill in all required fields."
        )

    # Create the prompt for Gemini API
    prompt = f"""
Suggest a list of common **medicines** (both prescription and over-the-counter) for a {age}-year-old {gender} experiencing {category} health concerns.  
Specific condition: {condition}.  

For each medicine, must include:
1. Medicine Name 
2. Dosage & Frequency
3. Primary Benefits 
4. Possible Side Effects  
5. Precautions (if any)  

Provide a **numbered list (1-10)** with each medicine on a **new line**.  
Use simple language and ensure the recommendations are widely available and safe.
"""

    # Make API Request to Gemini AI
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        # Extract Response
        supplements = response.text.strip() if hasattr(response, 'text') and response.text else "⚠️ No recommendations found. Try modifying your input."

        return render_template("result.html", 
                               form_title=f"Supplements for {category} Health",
                               supplements=supplements)

    except Exception as e:
        return render_template("result.html", 
                               form_title="Supplement Suggestions",
                               supplements=f"⚠️ Error: Unable to fetch supplement suggestions. {str(e)}")

# Run Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)