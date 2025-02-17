import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyBreHt9SdvkNBtljDE-L0sCJHgpH5h9tlw"
genai.configure(api_key=GEMINI_API_KEY)

try:
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content("Hello, what is machine learning?")
    print(response.text)  # Should print a valid response
except Exception as e:
    print(f"API is not responding: {e}")
