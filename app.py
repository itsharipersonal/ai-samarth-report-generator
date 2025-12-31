import streamlit as st
import pandas as pd
import os
import shutil
from pathlib import Path
import zipfile
from io import BytesIO
from report_code import AISmarthProcessor, create_summary_excel, validate_language_files

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Samarth Report Generator",
    page_icon="📊",
    layout="wide"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #366092;
        color: white;
    }
    .stDownloadButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #28a745;
        color: white;
    }
    .success-text {
        color: #28a745;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("📊 AI Samarth Report Processor")
    st.markdown("""
    Welcome! This tool processes AI Samarth CSV files, calculates completion metrics, 
    and generates a summary Excel report.
    """)

    st.sidebar.header("Instructions")
    st.sidebar.info("""
    1. Upload exactly **5 CSV files**.
    2. Ensure languages are: **English, Hindi, Marathi, Bengali, Odia**.
    3. Click **Process Files**.
    4. Download the Summary Excel and the Processed CSVs.
    """)

    # --- File Upload Section ---
    st.subheader("1. Upload CSV Files")
    uploaded_files = st.file_uploader(
        "Drag and drop your 5 AI Samarth CSV files here", 
        type="csv", 
        accept_multiple_files=True
    )

    if uploaded_files:
        st.write(f"📁 Files uploaded: {len(uploaded_files)}")
        
        # Validation
        if len(uploaded_files) != 5:
            st.warning("⚠️ Please upload exactly 5 files (one for each language).")
        else:
            # Temporary directory to store files for processing
            temp_dir = Path("temp_uploads")
            temp_dir.mkdir(exist_ok=True)
            
            output_dir = Path("temp_output")
            csv_output_dir = output_dir / "Processed_CSVs"
            output_dir.mkdir(exist_ok=True)
            csv_output_dir.mkdir(exist_ok=True, parents=True)

            file_paths = []
            for uploaded_file in uploaded_files:
                file_path = temp_dir / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(str(file_path))

            # Validate languages
            is_valid, validation_msg = validate_language_files(file_paths)
            
            if not is_valid:
                st.error(validation_msg)
            else:
                st.success("✅ All required files present and valid!")
                
                if st.button("🚀 Process Files"):
                    with st.spinner("Processing data..."):
                        all_stats = []
                        processed_files = []

                        for file_path in file_paths:
                            processor = AISmarthProcessor(file_path)
                            base_name = os.path.splitext(os.path.basename(file_path))[0]
                            output_csv_path = csv_output_dir / f"{base_name}_processed.csv"
                            
                            stats = processor.process_and_add_columns(str(output_csv_path))
                            
                            if stats:
                                stats['language'] = processor.extract_language()
                                stats['filename'] = os.path.basename(file_path)
                                all_stats.append(stats)
                                processed_files.append(output_csv_path)

                        # Create Summary Excel
                        summary_excel_path = output_dir / "AI_Samarth_Summary.xlsx"
                        create_summary_excel(all_stats, str(summary_excel_path))

                        st.balloons()
                        st.subheader("2. Results & Downloads")
                        
                        col1, col2 = st.columns(2)
                        
                        # Download Summary Excel
                        with col1:
                            with open(summary_excel_path, "rb") as f:
                                st.download_button(
                                    label="📥 Download Summary Excel",
                                    data=f,
                                    file_name="AI_Samarth_Summary.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                        
                        # Create ZIP of processed CSVs
                        zip_buffer = BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w") as zf:
                            for pf in processed_files:
                                zf.write(pf, arcname=pf.name)
                        
                        with col2:
                            st.download_button(
                                label="📦 Download Processed CSVs (ZIP)",
                                data=zip_buffer.getvalue(),
                                file_name="Processed_CSVs.zip",
                                mime="application/zip"
                            )

                        # Display Summary Table for quick view
                        st.write("### Quick Stats Preview")
                        df_summary = pd.DataFrame(all_stats)
                        # Reorder columns for display
                        cols = ['language', 'total_users', 'started', '25_percent', '50_percent', '75_percent', '100_percent']
                        st.dataframe(df_summary[cols], use_container_width=True)

            # Cleanup
            # Note: In a real production app, you'd want to handle cleanup more carefully
            # but for local use this is fine.

    else:
        st.info("Please upload files to begin.")

if __name__ == "__main__":
    main()
