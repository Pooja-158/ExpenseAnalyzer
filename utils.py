




import os
import re
import pytesseract
import docx2txt
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ✅ Detect if it's a credit card statement
def is_credit_card_statement(text: str) -> bool:
    keywords = [
        "credit card statement", "minimum payment", "payment due",
        "total balance", "previous balance", "interest charge",
        "transactions", "purchases", "cashback", "statement period"
    ]
    found_keywords = [kw for kw in keywords if kw.lower() in text.lower()]
    print("🧠 Detected keywords:", found_keywords)
    return len(found_keywords) >= 3

# ✅ Extract text from file (PDF, DOCX, Image, TXT)
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

# ✅ Categorize expenses using keyword mapping
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

# ✅ Generate combined summary for all uploaded data
def generate_combined_summary_from_categorized_data(categorized_data_all):
    """
    categorized_data_all: dict of {filename: {category: amount, ...}, ...}
    """
    # Merge all category-wise values
    combined = {}
    for data in categorized_data_all.values():
        for category, amount in data.items():
            combined[category] = combined.get(category, 0) + amount

    if not combined:
        return "❌ No categorized expenses found."

    total = sum(combined.values())
    sorted_items = sorted(combined.items(), key=lambda x: x[1], reverse=True)

    category_summary = "\n".join(
        [f"- {cat}: ${amt:.2f} ({amt/total:.0%} of total spending)" for cat, amt in sorted_items]
    )

    prompt = f"""
You are a smart finance assistant helping summarize a user's combined monthly credit card spending.

Total Spending: ${total:.2f}

Breakdown of Spending by Category:
{category_summary}

Provide a clean and friendly summary highlighting:
- Total spent
- all categories
- Any dominant or low-spend categories
- Suggestions or patterns if applicable
"""

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Could not generate summary. Error: {str(e)}"


# ✅ Generate pie chart

def generate_pie_chart(categorized_data):
    if not categorized_data:
        return None
    df = pd.DataFrame(list(categorized_data.items()), columns=["Category", "Amount"])
    fig = px.pie(df, names="Category", values="Amount", hole=0.4, title="Expense Breakdown by Category")
    return fig

# ✅ Chatbot to answer from summary

def answer_question_from_summaries(summary_dict, question):
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
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Failed to get answer. Error: {str(e)}"