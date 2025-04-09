# import streamlit as st
# import os
# import tempfile
# from utils import extract_text_from_file, summarize_text, categorize_expenses, generate_pie_chart, answer_question

# st.set_page_config(page_title="💳 Expense Analyzer", layout="centered")
# st.title("💳 Expense Analyzer")
# st.markdown("Upload your credit card statement (PDF, DOCX, TXT, Image)")

# uploaded_file = st.file_uploader("Upload File", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])

# if uploaded_file:
#     st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
#     with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
#         tmp_file.write(uploaded_file.read())
#         file_path = tmp_file.name

#     text = extract_text_from_file(file_path)

#     if text:
#         # 🧠 Summary
#         summary = summarize_text(text)
#         st.subheader("📄 Summary Result")
#         st.markdown(summary)

#         # 📊 Categorized Pie Chart
#         categorized_data = categorize_expenses(text)
#         if categorized_data:
#             st.subheader("📊 Expense Breakdown")
#             fig = generate_pie_chart(categorized_data)
#             st.plotly_chart(fig)
#         else:
#             st.warning("Could not categorize expenses from the statement.")

#         # 💬 Q&A Section
#         st.subheader("💬 Ask a Question About Your Spending")
#         user_question = st.text_input("Type your question here...")

#         if user_question:
#             response = answer_question(text, user_question)
#             st.success(response)

#     else:
#         st.error("❌ Could not extract any text from the uploaded file.")




import streamlit as st
import os
import tempfile
from utils import (
    extract_text_from_file,
    is_credit_card_statement,
    categorize_expenses,
    generate_pie_chart,
    answer_question_from_summaries,
    generate_combined_summary_from_categorized_data
)

st.set_page_config(page_title="💳 Expense Analyzer", layout="wide")
st.title("💳 Expense Analyzer")
st.markdown("Upload your credit card statement(s) (PDF, DOCX, TXT, Image)")

# Upload mode selection
upload_mode = st.radio("Choose Upload Mode:", ["Single File", "Multiple Files"])

uploaded_files = []
combined_text = ""
summaries = {}
categorized_data_all = {}

if upload_mode == "Single File":
    uploaded_file = st.file_uploader("Upload File", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
    if uploaded_file:
        uploaded_files = [uploaded_file]
else:
    uploaded_files = st.file_uploader("Upload Multiple Files", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"], accept_multiple_files=True)

# Pie chart mode selection (only if multiple valid files uploaded)
if uploaded_files and len(uploaded_files) > 1:
    pie_chart_mode = st.radio("Choose Pie Chart Option:", ["Combined Pie Chart", "Individual Pie Charts"])
else:
    pie_chart_mode = "Individual Pie Charts"

# Process files
valid_files = []

for uploaded_file in uploaded_files:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    text = extract_text_from_file(file_path)
    os.remove(file_path)

    if not text or not is_credit_card_statement(text):
        st.warning(f"⚠️ Skipped '{uploaded_file.name}': This does not appear to be a valid credit card statement.")
        continue

    valid_files.append(uploaded_file.name)
    combined_text += text + "\n"
    categorized_data_all[uploaded_file.name] = categorize_expenses(text)

if valid_files:
    st.subheader("📄 Combined Summary")
    summary = generate_combined_summary_from_categorized_data(categorized_data_all)
    st.markdown(summary)
    summaries["Combined Summary"] = summary

    # Pie Chart
    st.subheader("📊 Expense Breakdown")
    if pie_chart_mode == "Combined Pie Chart" or len(valid_files) == 1:
        combined_data = {}
        for data in categorized_data_all.values():
            for category, amount in data.items():
                combined_data[category] = combined_data.get(category, 0) + amount
        fig = generate_pie_chart(combined_data)
        st.plotly_chart(fig, use_container_width=True)
    else:
        cols = st.columns(2)
        for i, filename in enumerate(valid_files):
            with cols[i % 2]:
                st.markdown(f"**{filename}**")
                fig = generate_pie_chart(categorized_data_all[filename])
                st.plotly_chart(fig, use_container_width=True)

    # Chat
    st.subheader("💬 Ask a Question About Your Spending")
    user_question = st.text_input("Type your question here...")
    if user_question:
        response = answer_question_from_summaries(summaries, user_question)
        st.success(response)
else:
    st.info("Please upload at least one valid credit card statement to proceed.")
