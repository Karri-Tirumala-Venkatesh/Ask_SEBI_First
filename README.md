# FINTERNET – AI-Powered Financial Insights API

## About the Project
FINTERNET is a FastAPI-based service leveraging Google's Gemini API to deliver advanced financial insights via REST endpoints. Built for quick prototyping and hackathons, the project runs locally and can be publicly exposed via LocalTunnel for live demonstrations or testing. All instructions and commands are tailored for Windows environments.

## Quick Start (Windows)
1. **Clone the repository**  
   ```shell
   git clone https://github.com/Karri-Tirumala-Venkatesh/FINTERNET.git
   cd FINTERNET
   ```
2. **Create and activate a virtual environment**  
   ```shell
   python -m venv myenv
   myenv\Scripts\activate
   ```
3. **Install dependencies**  
   ```shell
   pip install -r requirements.txt
   ```
4. **Set up Gemini API key**  
   - Create a `.env` file in the project root.
   - Add your Gemini API key using the variable name referenced in `main.py`, for example:  
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     ```

## Run Locally
Use Uvicorn to launch the FastAPI server:
```shell
uvicorn main:app --host 0.0.0.0 --port 8000
```
- Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive Swagger API docs.
- Visit [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) for ReDoc documentation.

## Expose Public URL with LocalTunnel
Cloud platforms are not used due to large dependencies. To test remotely:
1. **Install LocalTunnel globally:**  
   ```shell
   npm install -g localtunnel
   ```
2. **Expose port 8000:**  
   Open a second terminal and run:  
   ```shell
   lt --port 8000
   ```
3. **Share the generated public URL** (e.g., `https://your-subdomain.loca.lt`).  
   Use this to share your API with others for testing, for example:  
   `https://your-subdomain.loca.lt/docs`

## API Endpoints

### Health Check
```
GET /
Response: Basic status or welcome message
```

### Example: Financial Analysis
```
POST /analyze
Headers: Content-Type: application/json
Body:
{
  "query": "Analyze the recent performance of XYZ and summarize key risks."
}
Response:
{
  "result": "<Gemini-powered financial insights>"
}
```

## Troubleshooting
- **401/403 errors:** Check your `.env` and make sure the API key variable name matches the one expected in `main.py`.
- **Module not found:** Make sure the virtual environment is activated and all requirements installed.
- **Port in use:** Change the port in both `uvicorn` and `lt` commands if 8000 is occupied (e.g., use 8080).
- **LocalTunnel issues:** Rerun `lt --port 8000`. Try a different port or restart if issues persist.
- **Windows vs. macOS/Linux:** For macOS/Linux, activate your venv with `source myenv/bin/activate`.

## No License
This project is being submitted for a hackathon and does not include a license.
