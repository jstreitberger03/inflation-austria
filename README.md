# Inflation Report Austria

A Python-based tool for analyzing and comparing inflation rates between Austria and the Euro zone. This project fetches real-time data from Eurostat and generates comprehensive reports with visualizations.

## Features

- **Real-time Data**: Fetches the latest HICP (Harmonized Index of Consumer Prices) inflation data from Eurostat
- **Comprehensive Analysis**: 
  - Statistical analysis (mean, median, min, max, standard deviation)
  - Year-by-year comparison between Austria and Euro zone
  - Cumulative inflation calculations
  - Trend identification and extremes
- **Rich Visualizations**:
  - Line chart comparing inflation trends
  - Bar chart showing differences
  - Statistical comparison charts
  - Cumulative inflation visualization
- **Detailed Reports**: Generates text reports with all findings

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jstreitberger03/inflation-report-austria.git
cd inflation-report-austria
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script to generate the complete inflation report:

```bash
python main.py
```

Or make it executable and run directly:

```bash
chmod +x main.py
./main.py
```

## Output

The script generates the following files in the `output/` directory:

1. **inflation_comparison.png** - Line chart comparing Austria vs Euro zone inflation over time
2. **inflation_difference.png** - Bar chart showing year-by-year differences
3. **statistics_comparison.png** - Statistical metrics comparison
4. **cumulative_inflation.png** - Cumulative inflation visualization
5. **inflation_report.txt** - Comprehensive text report with all analysis

## Data Source

This project uses the Eurostat API to fetch official inflation data:
- Dataset: `prc_hicp_aind` (HICP - annual data, index and rate of change)
- Regions: Austria (AT) and Euro zone (EA19)
- Metric: Annual rate of change (RCH_A_AVG)

## Project Structure

```
inflation-report-austria/
├── main.py                  # Main script to run the analysis
├── data_fetcher.py         # Module for fetching data from Eurostat
├── analysis.py             # Statistical analysis functions
├── visualization.py        # Visualization generation
├── report_generator.py     # Text report generation
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── output/                # Generated reports (created on first run)
```

## Example Output

The analysis provides insights such as:
- Current inflation rates for both regions
- Historical trends and patterns
- Years with highest/lowest inflation
- Average differences between regions
- Cumulative inflation over the analysis period

## License

This project is open source and available for educational and analytical purposes.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Author
Julian Streitberger
Created for analyzing inflation trends in Austria compared to the Euro zone.