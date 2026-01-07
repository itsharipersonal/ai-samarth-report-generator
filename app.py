import streamlit as st
import pandas as pd
import os
import csv
import shutil
from pathlib import Path
import zipfile
from io import BytesIO
from report_code import AISmarthProcessor, create_summary_excel, validate_language_files, parse_start_date

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

                # Scan for date range
                min_date = None
                max_date = None
                all_dates = []

                # Quick scan for dates
                for fp in file_paths:
                    try:
                        with open(fp, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f)
                            next(reader) # Skip headers
                            # Start Date is column 12 (0-indexed)
                            for row in reader:
                                if len(row) > 12:
                                    d = parse_start_date(row[12])
                                    if d:
                                        all_dates.append(d)
                    except Exception:
                        pass
                
                if all_dates:
                    min_date = min(all_dates)
                    max_date = max(all_dates)

                st.subheader("2. Filter Settings (Optional)")
                if min_date and max_date:
                    st.info(f"📅 Found data from **{min_date.strftime('%d %b %Y')}** to **{max_date.strftime('%d %b %Y')}**")
                
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    default_start = min_date if min_date else None
                    start_date = st.date_input("Start Date", value=default_start, min_value=min_date, max_value=max_date)
                with col_d2:
                    default_end = max_date if max_date else None
                    end_date = st.date_input("End Date", value=default_end, min_value=min_date, max_value=max_date)

                if st.button("🚀 Process Files"):
                    with st.spinner("Processing data..."):
                        all_stats = []
                        processed_files = []

                        for file_path in file_paths:
                            processor = AISmarthProcessor(file_path)
                            base_name = os.path.splitext(os.path.basename(file_path))[0]
                            output_csv_path = csv_output_dir / f"{base_name}_processed.csv"
                            
                            stats = processor.process_and_add_columns(str(output_csv_path), start_date, end_date)
                            
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
                        if start_date and end_date:
                            st.caption(f"📅 Data from **{start_date.strftime('%d %b %Y')}** to **{end_date.strftime('%d %b %Y')}**")
                        df_summary = pd.DataFrame(all_stats)
                        # Reorder columns for display
                        cols = ['language', 'total_users', 'started', 'only_1_video', '25_percent', '50_percent', '75_percent', '100_percent']
                        df_display = df_summary[cols].copy()
                        
                        # Add Total Row
                        numeric_cols = ['total_users', 'started', 'only_1_video', '25_percent', '50_percent', '75_percent', '100_percent']
                        totals = df_display[numeric_cols].sum()
                        total_row = pd.DataFrame([['TOTAL'] + totals.tolist()], columns=cols)
                        df_display = pd.concat([df_display, total_row], ignore_index=True)
                        
                        st.dataframe(df_display, use_container_width=True)
                        
                        # Month-wise "At Least 1 Video" Analysis
                        st.write("### Month-wise 'At Least 1 Video' Analysis")
                        
                        # Create tabs for cumulative and monthly views
                        tab1, tab2 = st.tabs(["📈 Cumulative (Start to Month End)", "📅 Monthly (Month Only)"])
                        
                        with tab1:
                            st.write("**Cumulative Data:** Users who completed **at least 1 video** from program start to end of each month")
                            df_cumulative = pd.DataFrame(all_stats)
                            cum_cols = ['language', 'at_least_1_video_cumulative_oct', 'at_least_1_video_cumulative_nov', 'at_least_1_video_cumulative_dec']
                            
                            # Check if columns exist (for backward compatibility)
                            available_cum_cols = [col for col in cum_cols if col in df_cumulative.columns]
                            if available_cum_cols:
                                df_cum_display = df_cumulative[available_cum_cols].copy()
                                
                                # Rename columns for better display
                                df_cum_display.columns = ['Course Language', 'Up to Oct End', 'Up to Nov End', 'Up to Dec End']
                                
                                # Add Total Row
                                numeric_cum_cols = ['Up to Oct End', 'Up to Nov End', 'Up to Dec End']
                                cum_totals = df_cum_display[numeric_cum_cols].sum()
                                cum_total_row = pd.DataFrame([['TOTAL'] + cum_totals.tolist()], columns=['Course Language'] + numeric_cum_cols)
                                df_cum_display = pd.concat([df_cum_display, cum_total_row], ignore_index=True)
                                
                                st.dataframe(df_cum_display, use_container_width=True)
                            else:
                                st.info("Month-wise cumulative data not available in this dataset.")
                        
                        with tab2:
                            st.write("**Monthly Data:** Users who completed **at least 1 video** and started in that specific month")
                            df_monthly = pd.DataFrame(all_stats)
                            mon_cols = ['language', 'at_least_1_video_monthly_oct', 'at_least_1_video_monthly_nov', 'at_least_1_video_monthly_dec']
                            
                            # Check if columns exist (for backward compatibility)
                            available_mon_cols = [col for col in mon_cols if col in df_monthly.columns]
                            if available_mon_cols:
                                df_mon_display = df_monthly[available_mon_cols].copy()
                                
                                # Rename columns for better display
                                df_mon_display.columns = ['Course Language', 'October Only', 'November Only', 'December Only']
                                
                                # Add Total Row
                                numeric_mon_cols = ['October Only', 'November Only', 'December Only']
                                mon_totals = df_mon_display[numeric_mon_cols].sum()
                                mon_total_row = pd.DataFrame([['TOTAL'] + mon_totals.tolist()], columns=['Course Language'] + numeric_mon_cols)
                                df_mon_display = pd.concat([df_mon_display, mon_total_row], ignore_index=True)
                                
                                st.dataframe(df_mon_display, use_container_width=True)
                            else:
                                st.info("Month-wise monthly data not available in this dataset.")

            # Cleanup
            # Note: In a real production app, you'd want to handle cleanup more carefully
            # but for local use this is fine.

    else:
        st.info("Please upload files to begin.")

if __name__ == "__main__":
    main()
