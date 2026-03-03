# India Export Analytics 🇮🇳

**India Export Analytics** is a data visualization and analysis tool designed to explore India's commodity export trends from 2017 to 2025. Built with **Streamlit** and **Python**, it offers an interactive dashboard to search HSCodes, view historical performance, and analyze growth metrics.

## 🚀 Features

-   **Interactive Dashboard**: Modern, responsive web-based UI.
-   **Smart Search**: Filter commodities by HSCode or description using a searchable dropdown.
-   **Visual Analytics**:
    -   Combined Line Charts for historical trend analysis.
    -   Bar Charts for yearly comparison.
    -   Automatic consolidation of export data across multiple fiscal years.
-   **Data Export**: Download filtered commodity data as CSV for offline analysis.
-   **Responsive Charts**: Powered by **Plotly** for zooming, panning, and detailed tooltips.

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/kirangugwade/exim-analytica.git
    cd india-export-analytics
    ```

2.  **Create a virtual environment** (Optional but recommended):
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, install manually below)*
    ```bash
    pip install streamlit pandas plotly
    ```

## 📂 Data Setup

Ensure your JSON data files (e.g., `data-year-2018-19.json`) are located in the `export-data-commodity-wise` directory. The application automatically detects and parses all files matching the pattern `export-data-commodity-wise/data-year-*.json`.

## ▶️ Usage

### Run the App
Launch the Streamlit dashboard:
```bash
streamlit run app.py
```
This will open the application in your default web browser (usually at `http://localhost:8501`).

### Run CLI Version (Legacy)
If you prefer a terminal-based interface:
```bash
python export_analysis.py
```

## 📊 Project Structure

-   `app.py`: Main Streamlit application entry point.
-   `export_analysis.py`: Legacy script for CLI-based analysis.
-   `data-year-*.json`: Input data source files.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
