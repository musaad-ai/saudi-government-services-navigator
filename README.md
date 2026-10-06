# 🇸🇦 Saudi Government Services Navigator

An AI-powered bilingual web application that helps users find Saudi government services using natural language queries in Arabic and English.

---

## 📋 Overview

This application uses a **local Large Language Model (Qwen2.5)** via Ollama to understand user queries and match them to government services. It provides step-by-step instructions for accessing services from platforms like Absher, Saudi Business Center, Qiyas, NWC, and Saudi Electricity.

### Key Features

| Feature | Description |
|---------|-------------|
|  **AI-Powered** | Natural language understanding with Qwen2.5 (14B model) |
|  **Bilingual** | Full support for Arabic (RTL) and English (LTR) |
|  **Chat Interface** | Modern conversational UI |
|  **Saudi Theme** | Official government color scheme (green and beige and lavender ) |
|  **Smart Matching** | Understands context and matches multiple services when needed |

---

## 📁 Project Structure

```
SAUDI_SERVICES_NAVIGATOR/
│
├── app.py                 # Main Streamlit application (UI)
├── llm_backend.py         # LLM classification and processing logic
├── services.json          # Government services database (33 services)
├── README.md              # This documentation file
│
├── logo.png               # App logo (optional - place in root)
├── icon.png               # Browser favicon (optional - place in root)
├── background.png         # Background image (optional - place in root)
│
└── .streamlit/
    └── config.toml        # Streamlit configuration
```

---

## 🛠️ Technology Stack

- **Frontend Framework**: Streamlit (Python web framework)
- **AI Model**: Qwen2.5:14b (via Ollama)
- **Programming Language**: Python 3.8+
- **Data Storage**: JSON (services database)
- **Font**: Cairo (Google Fonts - supports Arabic and English)

---

## 📦 Installation & Setup

### Prerequisites

1. **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
2. **Ollama** - [Download Ollama](https://ollama.ai)

### Step-by-Step Installation

#### 1. Install Ollama

- **Windows**: Download installer from [ollama.ai](https://ollama.ai)
- **Mac/Linux**: Follow instructions on [ollama.ai](https://ollama.ai)

#### 2. Pull the AI Model

Open terminal/command prompt and run:

```bash
ollama pull qwen2.5:14b
```

**Note**: This downloads ~8GB. Make sure you have enough disk space and a stable internet connection.

#### 3. Install Python Dependencies

Navigate to the project folder and run:

```bash
pip install streamlit Pillow
```
Or:

```bash
py -m pip install streamlit Pillow
```

This installs:
- `streamlit` - Web framework (for building the UI)
- `Pillow` - Image handling (for logo and icon support)

#### 4. Verify Installation

Test that Ollama is working:

```bash
ollama run qwen2.5:14b "Hello"
```

You should see a response from the model.

---

## 🚀 Running the Application

### Start the Application

```bash
python -m streamlit run app.py
```
Or:

```bash
py -m streamlit run app.py
```
Or:

```bash
streamlit run app.py
```


### First Time Setup

1. **Select Language**: Use the dropdown in the top-left to choose Arabic (العربية) or English
2. **Ask a Question**: Type your question about a government service
3. **Get Results**: The AI will match your query to a service and show detailed instructions

---

## 💡 Usage Examples

### Example Queries (Arabic)

| Query | Expected Result |
|-------|----------------|
| كيف اجدد رخصة القيادة؟ | Shows steps to renew driving license |
| أبي أطلع جواز سفر | Shows steps to issue passport |
| كيف احدث السجل التجاري | Shows steps to update commercial registration |
| كم فاتورة المياه | Shows how to check water bill |
| كيف أنقل ملكية عداد الكهرباء | Shows steps to transfer electricity meter ownership |

### Example Queries (English)

| Query | Expected Result |
|-------|----------------|
| How to renew driving license? | Shows steps to renew driving license |
| I want to issue a passport | Shows steps to issue passport |
| How to pay electricity bill | Shows steps to pay electricity bill |
| Check water bill | Shows how to check water bill |

### Multiple Services

The AI can match multiple services in one query:

**Query**: "أبغى أفتح مشروع تجاري وأحجز اسم تجاري، لكن سجلي القديم غير محدث"

**Result**: Shows both:
- تجديد / التأكيد السنوي للسجل التجاري
- حجز اسم تجاري

---

## 📊 Supported Services

The application currently supports **33 government services** across 5 platforms:

### Absher Services
- **Traffic**: Renew/Issue driving license, View digital license, Report lost license
- **Civil Affairs**: Renew national ID, Register newborn, Issue birth certificate, Update personal info
- **Passports**: Issue/Renew passport, Report lost passport, Track delivery, Add dependent

### Saudi Business Center
- **Business**: Register commercial registration, Annual confirmation, Trade name reservation, Transfer trade name

### Qiyas (Educational Testing)
- **Testing**: Paper test registration, Digital test rescheduling, View test results

### NWC (National Water Company)
- **Water**: Check bill, Pay bill, Request new meter, Transfer ownership, Report leak, Reconnection

### Saudi Electricity
- **Electricity**: Check bill, Pay bill, Request new meter, Transfer ownership, Report outage, Reconnection

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User Input  │────▶│  LLM Backend │────▶│   Services   │
│  (Streamlit) │     │  (Qwen2.5)   │     │    (JSON)    │
└──────────────┘     └──────────────┘     └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             ▼
                    ┌──────────────┐
                    │   Response   │
                    │     (UI)     │
                    └──────────────┘
```

### How It Works

1. **User Input**: User types a question in Arabic or English
2. **Language Detection**: System detects the language automatically
3. **LLM Processing**: Qwen2.5 model analyzes the query and matches it to service(s)
4. **Service Lookup**: System retrieves service details from `services.json`
5. **Response Display**: UI shows formatted response with steps, requirements, and links

---

## 📝 File Descriptions

### `app.py`
**Main Streamlit Application**

- **Purpose**: User interface and interaction
- **Key Functions**:
  - Language switching (Arabic/English)
  - Chat history management
  - CSS styling and theming
  - Response rendering
- **Key Variables**:
  - `st.session_state.messages`: Chat history storage

### `llm_backend.py`
**LLM Processing Logic**

- **Purpose**: AI-powered service classification
- **Key Functions**:
  - `detect_query_language()`: Detects Arabic vs English
  - `ask_llm_intent()`: Processes query with LLM and returns matched service(s)
  - `build_response()`: Formats service data for display
  - `extract_service_key()`: Extracts service keys from LLM response
- **Key Variables**:
  - `LLM_MODEL`: Model name ("qwen2.5:14b")
  - `SERVICES`: Loaded services database

### `services.json`
**Services Database**

- **Purpose**: Stores all government service information
- **Structure**: Each service has:
  - `platform`: Service platform (Absher, NWC, etc.)
  - `category`: Service category
  - `title_ar` / `title_en`: Service name in both languages
  - `description_ar` / `description_en`: Service description
  - `steps_ar` / `steps_en`: Step-by-step instructions
  - `requirements`: Requirements in both languages
  - `official_link`: Link to official service page

---

## 🔧 Configuration

### Changing the AI Model

Edit `llm_backend.py`:

```python
LLM_MODEL = "qwen2.5:14b"  # Change to "qwen2.5:7b" or "llama3.1" etc.
```

Then pull the new model:

```bash
ollama pull qwen2.5:7b
```

### Adding Custom Images

Place these files in the project root:
- `logo.png` - App logo (shown at top)
- `icon.png` - Browser favicon
- `background.png` - Background image (optional)

---

## 👨‍💻 Author Information

- **Made By**: Abdullah Alotaibi
- **Date**: November 2024
- **Project**: Saudi Government Services Navigator

---

## 📄 License

Educational use only.

---

## 🙏 Acknowledgments

- **Ollama** - For providing easy access to local LLMs
- **Qwen Team** - For the Qwen2.5 model
- **Streamlit** - For the web framework
- **Saudi Government** - For the services information

---


