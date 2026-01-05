# Development Setup Guide

## Quick Start

### Option 1: Using the Launch Script (macOS)
```bash
./Launch_App.command
```

### Option 2: Direct Streamlit Command
```bash
streamlit run app.py
```

### Option 3: With Custom Port
```bash
streamlit run app.py --server.port 8501
```

## Installation (if needed)

If dependencies are not installed:

```bash
pip3 install -r requirements.txt
```

Or install individually:
```bash
pip3 install streamlit pandas openpyxl
```

## Testing the Application

1. **Start the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Access the app:**
   - The app will automatically open in your browser at `http://localhost:8501`
   - If it doesn't open automatically, copy the URL from the terminal

3. **Test with sample data:**
   - Upload 5 CSV files (one for each language: English, Hindi, Marathi, Bengali, Odia)
   - Click "Process Files"
   - Check the results:
     - Quick Stats Preview table
     - Month-wise "Only 1 Video" Analysis (Cumulative and Monthly tabs)
   - Download the Summary Excel and Processed CSVs

## Development Tips

- **Auto-reload:** Streamlit automatically reloads when you save changes to `app.py` or `report_code.py`
- **View logs:** Check the terminal for any error messages
- **Clear cache:** If you encounter issues, use `streamlit run app.py --server.headless true` or clear browser cache

## Testing the Report Code Directly

You can also test the processing logic directly:

```bash
python3 report_code.py
```

This will process files from the `data_files/` directory and create output in the `output/` directory.

## Troubleshooting

- **Port already in use:** Change the port with `--server.port 8502`
- **Module not found:** Make sure you're in the project directory and dependencies are installed
- **File upload issues:** Ensure you have write permissions in the workspace directory

