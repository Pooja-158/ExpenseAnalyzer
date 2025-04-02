# import os
# import re
# import pytesseract
# import docx2txt
# import fitz  # PyMuPDF
# import cv2
# import numpy as np
# import tempfile
# from PIL import Image
# from groq import Groq
# from pdf2image import convert_from_path
# from dotenv import load_dotenv
# import pandas as pd
# import plotly.express as px

# load_dotenv()
# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# # ✅ Detect if it's a credit card statement
# def is_credit_card_statement(text: str) -> bool:
#     keywords = [
#         "credit card statement", "minimum payment", "payment due",
#         "total balance", "previous balance", "interest charge",
#         "transactions", "purchases", "cashback", "statement period"
#     ]
#     found_keywords = [kw for kw in keywords if kw.lower() in text.lower()]
#     print("🧠 Detected keywords:", found_keywords)
#     return len(found_keywords) >= 3  # Adjust threshold if needed

# # ✅ Extract text from various file types
# def extract_text_from_file(file_path):
#     ext = os.path.splitext(file_path)[1].lower()
#     text = ""

#     try:
#         if ext == ".pdf":
#             print("🔍 Starting OCR on PDF...")
#             images = convert_from_path(file_path)
#             print(f"🖼️ Total pages: {len(images)}")
#             for i, image in enumerate(images):
#                 gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
#                 page_text = pytesseract.image_to_string(gray)
#                 print(f"📄 Page {i+1} text length: {len(page_text)}")
#                 text += page_text + "\n"
#         elif ext == ".docx":
#             text = docx2txt.process(file_path)
#         elif ext in [".png", ".jpg", ".jpeg"]:
#             image = cv2.imread(file_path)
#             text = pytesseract.image_to_string(image)
#         elif ext == ".txt":
#             with open(file_path, "r", encoding="utf-8") as file:
#                 text = file.read()
#         else:
#             print("❌ Unsupported file type.")
#     except Exception as e:
#         print(f"❌ Error extracting text: {e}")

#     if text:
#         print("✅ Text extracted successfully.")
#     return clean_extracted_text(text)

# # ✅ Clean text formatting
# def clean_extracted_text(text):
#     text = re.sub(r"\s+", " ", text)
#     text = re.sub(r"\n", " ", text)
#     return text.strip()

# # ✅ Summarize statement with Groq
# def summarize_text(text):
#     prompt = f"""
#     You are a smart expense analyzer. Summarize the following credit card statement in a clean and human-friendly way.
#     Avoid technical jargon and unnecessary data like FICO scores. Focus on spending behavior, key highlights, and spending categories.

#     Statement:
#     {text}
#     """

#     try:
#         chat_response = client.chat.completions.create(
#             model="llama3-8b-8192",
#             messages=[
#                 {"role": "user", "content": prompt}
#             ]
#         )
#         return chat_response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"❌ Could not parse summary. Here's the raw output:\n\n{str(e)}"

# # ✅ Categorize expenses into buckets
# def categorize_expenses(text):
#     categories = {
#         "Restaurants": ["restaurant", "biryani", "barbeque", "grubhub", "tacobell", "royal sweets"],
#         "Groceries": ["bazaar", "supermarket", "patel brothers", "india bazaar", "grocery"],
#         "Entertainment": ["netflix", "spotify", "amc", "fubo", "movie", "streaming"],
#         "Travel": ["sw air", "lyft", "uber", "airlines", "flight", "transport"],
#         "Shopping": ["amazon", "walmart", "kohls", "ross", "shopping", "store"],
#         "Utilities": ["tmobile", "prepaid", "mobile", "bill", "recharge"],
#         "Services": ["salon", "nails", "services", "bar", "jadore"],
#     }

#     expense_data = {}
#     lines = text.split("\n")
#     for line in lines:
#         for cat, keywords in categories.items():
#             for keyword in keywords:
#                 if keyword.lower() in line.lower():
#                     amount_match = re.search(r"\$(\d+[\,\d]*\.\d{2})", line)
#                     if amount_match:
#                         amount = float(amount_match.group(1).replace(",", ""))
#                         expense_data[cat] = expense_data.get(cat, 0) + amount
#     return expense_data

# # ✅ Generate interactive pie chart
# def generate_pie_chart(categorized_data):
#     if not categorized_data:
#         return None

#     df = pd.DataFrame(list(categorized_data.items()), columns=["Category", "Amount"])
#     fig = px.pie(
#         df,
#         names="Category",
#         values="Amount",
#         title="Expense Breakdown by Category",
#         hole=0.4
#     )
#     return fig

# # ✅ Optional: Groq-powered Q&A
# def answer_question(text, question):
#     prompt = f"""
#     You are an intelligent expense assistant. The user uploaded a credit card statement. Use the text below to answer their question clearly and helpfully.

#     Statement:
#     {text}

#     Question: {question}
#     Answer:"""

#     try:
#         response = client.chat.completions.create(
#             model="llama3-8b-8192",
#             messages=[
#                 {"role": "user", "content": prompt}
#             ]
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"❌ Failed to get answer. Error: {str(e)}"
import os
import re
import pytesseract
import docx2txt
import fitz
import cv2
import numpy as np
import tempfile
from PIL import Image
from groq import Groq
from pdf2image import convert_from_path
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def is_credit_card_statement(text: str) -> bool:
    keywords = [
        "credit card statement", "minimum payment", "payment due",
        "total balance", "previous balance", "interest charge",
        "transactions", "purchases", "cashback", "statement period"
    ]
    found_keywords = [kw for kw in keywords if kw.lower() in text.lower()]
    print("🧠 Detected keywords:", found_keywords)
    return len(found_keywords) >= 3

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    try:
        if ext == ".pdf":
            print("🔍 Starting OCR on PDF...")
            images = convert_from_path(file_path)
            for i, image in enumerate(images):
                gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
                page_text = pytesseract.image_to_string(gray)
                text += page_text + "\n"
        elif ext == ".docx":
            text = docx2txt.process(file_path)
        elif ext in [".png", ".jpg", ".jpeg"]:
            image = cv2.imread(file_path)
            text = pytesseract.image_to_string(image)
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
    return re.sub(r"\s+", " ", text).strip()

def summarize_text(text):
    prompt = f"""
    You are a smart expense analyzer. Summarize the following credit card statement in a clean and human-friendly way.
    Avoid technical jargon. Focus on spending behavior and categories.
    Statement:
    {text}
    """
    try:
        chat_response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return chat_response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Could not parse summary. Here's the raw output:\n\n{str(e)}"

def categorize_expenses(text):
    categories = {
        "Restaurants": ["restaurant", "biryani", "barbeque", "grubhub", "tacobell"],
        "Groceries": ["bazaar", "supermarket", "grocery"],
        "Entertainment": ["netflix", "spotify", "amc", "fubo", "movie"],
        "Travel": ["sw air", "lyft", "uber", "flight", "transport"],
        "Shopping": ["amazon", "walmart", "kohls", "shopping", "store"],
        "Utilities": ["tmobile", "mobile", "bill", "recharge"],
        "Services": ["salon", "nails", "services", "jadore"]
    }
    expense_data = {}
    lines = text.split("\n")
    for line in lines:
        for cat, keywords in categories.items():
            for keyword in keywords:
                if keyword.lower() in line.lower():
                    amount_match = re.search(r"\$(\d+[\,\d]*\.\d{2})", line)
                    if amount_match:
                        amount = float(amount_match.group(1).replace(",", ""))
                        expense_data[cat] = expense_data.get(cat, 0) + amount
    return expense_data

def generate_pie_chart(categorized_data):
    if not categorized_data:
        return None
    df = pd.DataFrame(list(categorized_data.items()), columns=["Category", "Amount"])
    fig = px.pie(df, names="Category", values="Amount", hole=0.4, title="Expense Breakdown")
    return fig

def answer_question_from_summaries(summary_dict, question):
    # Use .items() to unpack (filename, summary) pairs
    summaries_text = "\n\n".join([f"Summary for {name}:\n{summary}" for name, summary in summary_dict.items()])

    prompt = f"""
    You are an intelligent assistant helping the user understand their expenses across multiple credit card statements.
    Use the summaries below to answer their question.

    Summaries:
    {summaries_text}

    Question: {question}
    Answer:
    """

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Failed to get answer. Error: {str(e)}"
