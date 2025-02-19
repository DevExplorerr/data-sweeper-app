import streamlit as st
import pandas as pd
import os
from io import BytesIO

# set up our app 

st.set_page_config(page_title="Data Sweeper", page_icon="🧊", layout="wide")
st.title("Data Sweeper")
st.write("Upload your data file between CSV and Excel formats and we will clean it for you!")

uploaded_files = st.file_uploader("Upload your data file", type=["csv", "xlsx"], accept_multiple_files=True)   

file_name = None

if uploaded_files:
	for file in uploaded_files:
		file_ext = os.path.splitext(file.name)[1].lower()
		if file_ext == ".csv":
			df = pd.read_csv(file)
		elif file_ext == ".xlsx":
			df = pd.read_excel(file)
		else:
			st.error(f"File format not supported: {file_ext}. Please upload a CSV or Excel file.")
			continue

		# display info about the file
		st.write(f"**File name:** {file.name}")
		st.write(f"**File size:** {file.size/1024:.2f} KB")

		# Show 5 rows of our data frame
		st.write("🔍 Preview the Head of the Data:")
		st.dataframe(df.head())

		# Options for data cleaning
		st.subheader("🧹 Data Cleaning Options")
		if st.checkbox(f"Clean Data from {file.name}"):
			col1, col2 = st.columns(2)
			with col1:
				if st.button(f"Remove duplicates from {file.name}"):
					df.drop_duplicates(inplace=True)
					st.write("Duplicates removed.")

			with col2: 
				if st.button(f"Fill missing values for {file.name}"):
					numeric_cols = df.select_dtypes(include=["number"]).columns
					df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
					st.write("Missing values filled.")

		# choose specific columns to keep or convert 
		st.subheader("📌 Select Columns to Convert")
		columns = st.multiselect(f"Select columns to for {file.name}", df.columns, default=df.columns)
		df = df[columns]

		# create some visualizations 
		st.subheader("📊 Data Visualizations")
		if st.checkbox(f"Show Visualizations for {file.name}"):
			st.bar_chart(df.select_dtypes(include=["number"]).iloc[:,:2])

		# Initialize buffer and file_name before using them
		buffer = None  
		file_name = None  
		mime_type = None  
		conversion_done = False  # Track if conversion was performed

		# Convert the file: CSV -> Excel or Excel -> CSV
		st.subheader("🔁 Convert File")
		conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

		if st.button(f"Convert {file.name} to {conversion_type}"):
			buffer = BytesIO()  # ✅ Now buffer is always defined
			if conversion_type == "CSV":
				df.to_csv(buffer, index=False)
				file_name = file.name.replace(file_ext, ".csv")
				mime_type = "text/csv"
			elif conversion_type == "Excel":
				df.to_excel(buffer, index=False, engine="openpyxl")  # Ensure Excel export works
				file_name = file.name.replace(file_ext, ".xlsx")
				mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                

			buffer.seek(0)
			conversion_done = True
			st.success(f"📂 File successfully converted to {conversion_type}!")

		# ✅ Ensure `st.download_button()` only runs if `buffer` is not None
		if buffer:
			st.download_button(
				label=f"⬇️ Download {file_name} as {conversion_type} file",
				data=buffer,
				file_name=file_name,
				mime=mime_type
			)