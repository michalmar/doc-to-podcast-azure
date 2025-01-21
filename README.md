# doc-to-podcast-azure

This simple project takes a PDF and generates podcast script based on the content and also generates Audio file for the generated script.

## Prerequisites
- Azure AI Speech Service
- Azure Open Service

## How to run
- Clone the repository
- Create a `.env` file in the root directory and add the following variables
    ```bash
    AZURE_SPEECH_KEY=<YOUR_AZURE_SPEECH_KEY>
    AZURE_SPEECH_ENDPOINT=<YOUR_AZURE_SPEECH_ENDPOINT>
    AZURE_OPENAI_API_VERSION=<YOUR_AZURE_OPENAI_API_VERSION>
    AZURE_OPENAI_ENDPOINT=<YOUR_AZURE_OPENAI_ENDPOINT>

    ```
- Create Python virtual environment
    ```bash
    python -m venv venv
    ```

- Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```


- install the required packages
    ```bash
    pip install -r requirements.txt
    ```

- Run the following command to run as python script
    ```bash
    python doctopodcast.py
    ```

- Run the following command to run as a Streamlt app
    ```bash
    streamlit run app.py
    ```

- Open the browser and navigate to `http://localhost:8501` to access the Streamlit app
