# stockSense

**stockSense** is a web-based stock data visualization tool designed to help traders easily identify important technical indicators like Bollinger Bands, RSI, and Wavetrends. The project is hosted on a Heroku server (without Dynos assigned to avoid costs) but can also be run locally using Python, Flask, and Dash.

---

# Table of Contents

1. [Features](#features)
   - [Stock Price Visualization](#stock-price-visualization)
   - [Technical Indicators](#technical-indicators)
   - [Conjunctions Detection](#conjunctions-detection)
   - [Interactive Graphs](#interactive-graphs)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Clone the repository](#clone-the-repository)
   - [Install required dependencies](#install-required-dependencies)
   - [Run the app locally](#run-the-app-locally)
5. [Usage](#usage)
6. [Deployment on Heroku](#deployment-on-heroku)
7. [Contributing](#contributing)
8. [License](#license)

---

## Features

1. **Stock Price Visualization:**
   - Real-time stock price data fetched using Yahoo Finance (`yfinance`).
   - Displays the Close price and 20-Day Moving Average (MA20).
   - Shows Upper and Lower Bollinger Bands for detecting volatility and potential breakout zones.

2. **Technical Indicators:**
   - **RSI (Relative Strength Index):** Detects overbought (RSI > 70) and oversold (RSI < 30) conditions.
   - **Wavetrend (WT1 & WT2):** Identifies trend directions and potential reversals using Wavetrend signals.

3. **Conjunctions Detection:**
   - Green markers appear where the stock price exceeds the Upper Bollinger Band, and RSI crosses above 70, or the price goes below the Lower Bollinger Band, and RSI drops below 30.
   - Red markers appear where the stock price exceeds the Upper Bollinger Band, and Wavetrend WT1 or WT2 is above 60, or the price goes below the Lower Bollinger Band, and Wavetrend is below -60.

4. **Interactive Graphs:**
   - Dynamic, interactive Plotly-based charts.
   - Provides an easy way to visualize price changes and relevant indicators in one place.

---

## Tech Stack

- **Dash**: Python framework for building web applications.
- **Plotly**: Data visualization library used to plot stock prices and indicators.
- **yfinance**: Yahoo Finance API to fetch real-time stock data.
- **Flask**: Lightweight WSGI web application framework.
- **Gunicorn**: Python WSGI HTTP Server for deployment.
- **Heroku**: Cloud platform for hosting applications.

---

## Project Structure
```bash
    stockSense/
├── app.py                   # Main application code
├── Procfile                 # For Heroku deployment
├── requirements.txt         # Dependencies for the project
├── .gitignore               # Ignoring unnecessary files
└── README.md                # Project documentation
```
---

## Installation

To run stockSense locally, follow these steps:

### Prerequisites
Ensure you have the following installed:
- Python 3.x
- `pip` (Python package installer)

### Clone the repository:
```bash
git clone https://github.com/your-username/stocksense.git
cd stocksense
```

### Install required dependencies:
```bash
pip install -r requirements.txt
```
### Run the app locally:
```bash
python app.py
```

The application will be available at: 
```bash
http://127.0.0.1:8050/
```

---

---

## Usage

Once the application is running, follow these steps to use stockSense:

1. **Input Stock Symbol**:
   - Enter the stock symbol of your choice (e.g., `AAPL`, `GOOGL`, `MSFT`) in the input field and click the "Submit" button.

2. **View Visualization**:
   - The main graph will display:
     - The stock's closing price over time.
     - The 20-Day Moving Average (MA20).
     - Upper and Lower Bollinger Bands.

3. **Analyze Indicators**:
   - Check for green markers that indicate potential buying opportunities when the price exceeds the Upper Bollinger Band and the RSI is above 70.
   - Look for red markers indicating potential selling opportunities when the price exceeds the Upper Bollinger Band and Wavetrend indicators signal strength above 60.

4. **Interpret Results**:
   - Use the visual cues to make informed trading decisions based on the current market conditions.

---

## Deployment on Heroku

If you'd like to deploy stockSense on Heroku, follow these steps:

1. **Login to Heroku**:
   ```bash
   heroku login
   ```
2. **Create a new app:**
    ```bash
    heroku create your-app-name
    ```
3. **Deploy the app:**
    ```bash
    git push heroku master
    ```
4. **Open the app:** After deployment, you can open your app with:
    ```bash
    heroku open
    ```
---

## Contributing
Contributions to stockSense are welcome! To contribute, please follow these steps: 
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository. 

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.