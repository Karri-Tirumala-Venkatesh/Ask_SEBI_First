# 🌐 FINTERNET

> 🚀 *Intelligent API for Natural Language Processing of Unstructured Financial Data*

## 📋 About the Project

Application Programming Interface (API), which can make use of large system modules, to process Natural Language queries, to recursively retrieve relevant information from large unstructured data.

## ⚡ Quick Start (Windows)

### 1. 📥 **Clone the repository**
   ```shell
   git clone https://github.com/Karri-Tirumala-Venkatesh/FINTERNET.git
   cd FINTERNET
   ```

### 2. 🐍 **Create and activate a virtual environment**
   ```shell
   python -m venv myenv
   myenv\Scripts\activate
   ```

### 3. 📦 **Install dependencies**
   ```shell
   pip install -r requirements.txt
   ```

### 4. 🔑 **Set up Gemini API key**
   - 📝 Create a `.env` file in the project root.
   - ➕ Add your Gemini API key using the variable name referenced in `main.py`, for example:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     ```

## 🏃 Run Locally

Use Uvicorn to launch the FastAPI server:

```shell
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 📚 Documentation Access

- 🔍 Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive Swagger API docs.
- 📖 Visit [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) for ReDoc documentation.

## 🌍 Expose Public URL with LocalTunnel

☁️ Cloud platforms are not used due to large dependencies. To test remotely:

### 1. 🛠️ **Install LocalTunnel globally:**
   ```shell
   npm install -g localtunnel
   ```

### 2. 🔓 **Expose port 8000:**
   Open a second terminal and run:
   ```shell
   lt --port 8000
   ```

### 3. 🔗 **Share the generated public URL**
   (e.g., `https://your-subdomain.loca.lt`).
   
   Use this to share your API with others for testing, for example:
   
   `https://your-subdomain.loca.lt/docs`
