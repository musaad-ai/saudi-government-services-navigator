import json
import os
import subprocess
import re
# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICES_PATH = os.path.join(BASE_DIR, "services.json")
LLM_MODEL = "qwen2.5:14b"  # Ollama model name
LLM_TIMEOUT = 60  # Maximum seconds to wait for LLM response

# ============================================================================
# DATA LOADING
# ============================================================================

def load_services():
    """Load all government services from JSON file."""
    with open(SERVICES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Load services when module is imported
SERVICES = load_services()

# ============================================================================
# LANGUAGE DETECTION
# ============================================================================

def detect_query_language(text):
    """
    Detect if text is Arabic or English by counting characters.
    
    Returns 'ar' for Arabic or 'en' for English.
    """
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    return "ar" if arabic_chars > english_chars else "en"

# ============================================================================
# SERVICE KEY EXTRACTION
# ============================================================================

def extract_service_key(response, valid_keys):
    """
    Extract a valid service key from LLM response text.
    
    Tries two strategies:
    1. Exact match with word boundaries
    2. Match with underscores replaced as spaces
    """
    text = response.lower().strip()
    
    # If LLM says "none", return None
    if "none" in text and len(text) < 20:
        return None
    
    # Strategy 1: Exact match
    for key in valid_keys:
        if re.search(r'\b' + re.escape(key) + r'\b', text):
            return key
    
    # Strategy 2: Match with underscores as spaces
    for key in valid_keys:
        if key.replace("_", " ") in text:
            return key
    
    return None

# ============================================================================
# LLM CLASSIFICATION
# ============================================================================

def ask_llm_intent(user_query):
    """
    Use LLM to understand user query and find matching government service(s).
    
    Returns a dictionary with:
        - type: "service", "multi_service", or "conversation"
        - service_key: Single service key (if one match)
        - service_keys: List of service keys (if multiple matches)
        - message: Conversational message (if no service match)
    """
    is_arabic = detect_query_language(user_query) == "ar"
    service_keys = list(SERVICES.keys())
    
    # Build services list for LLM prompt (includes titles and descriptions)
    services_list = "\n".join(
        f"- {key}: {svc.get('title_ar', '')} / {svc.get('title_en', '')} | {svc.get('description_ar', '')[:100]}"
        for key, svc in SERVICES.items()
    )
    
    lang = "Arabic" if is_arabic else "English"
    name = "موجه الخدمات الحكومية السعودية" if is_arabic else "Saudi Government Services Navigator"
    
    # Build prompt for LLM
    prompt = f"""You are {name}.

SERVICES:
{services_list}

USER: "{user_query}"

RULES:
1. Greeting → greet back, NO SERVICE_KEY
2. If the user asks for the list of available services (for example: "What are your services?", "List services", or Arabic equivalents), DO NOT output SERVICE_KEY or any service keys. Instead, the model MUST list ONLY the service TITLES AS SHOWN IN THE SERVICES as BULLETS, one title per line, and nothing else (no numbering, no descriptions, no extra commentary). Use the language of the user's query: Arabic → use `title_ar`; English → use `title_en`, LIST THEM AS BULLETS.
3. Service request → if you find matches, you MUST output ALL of them as:
   SERVICE_KEY: key1
   SERVICE_KEY: key2
   (one SERVICE_KEY per line, NO explanations before the keys)
4. No match → say "this service is not available" in {lang}, NO SERVICE_KEY, do NOT ask for clarification

HOW TO MATCH:
- Identify what the user ACTUALLY wants to DO (the ACTION/PROBLEM they need solved)
- Match ONLY if a service DIRECTLY SOLVES that specific problem
- If user needs MULTIPLE services, output ALL of them as SERVICE_KEY format
- Do NOT write explanations or descriptions - just output SERVICE_KEY lines
- Read service descriptions carefully to understand what each service actually does
- If a service doesn't solve the user's actual problem, do NOT match it
- If no service solves the user's actual problem → say "not available"

LANGUAGE: Reply ONLY in {lang}. Never use Russian or Chinese."""

    try:
        # Call Ollama CLI to get LLM response
        result = subprocess.run(
            ["ollama", "run", LLM_MODEL],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            timeout=LLM_TIMEOUT
        )
        
        response = result.stdout.decode("utf-8", errors="ignore").strip()
        print(f"[LLM Response] {response}")
        
        # Handle NO_MATCH response
        if "NO_MATCH" in response.upper():
            clean_msg = response.replace("NO_MATCH", "").strip()
            clean_msg = re.sub(r'SERVICE_KEY:\s*\S+', '', clean_msg).strip()
            if not clean_msg:
                clean_msg = "عذراً، هذه الخدمة غير متوفرة حالياً." if is_arabic else "Sorry, this service is not available."
            return {"type": "conversation", "service_key": None, "message": clean_msg}
        
        # Extract all SERVICE_KEY: occurrences from response
        matched_keys = []
        if "SERVICE_KEY:" in response.upper():
            for line in response.split('\n'):
                if "SERVICE_KEY:" in line.upper():
                    key_part = line.upper().split("SERVICE_KEY:")[-1].strip()
                    key_candidate = key_part.split()[0].lower().strip("*`,.[]()") if key_part.split() else ""
                    matched = extract_service_key(key_candidate, service_keys)
                    if matched and matched not in matched_keys:
                        matched_keys.append(matched)
        
        # Fallback: try to find keys directly in response if no SERVICE_KEY format
        if not matched_keys:
            for key in service_keys:
                if key in response.lower():
                    if key not in matched_keys:
                        matched_keys.append(key)
        
        # Return result based on number of matches
        if len(matched_keys) == 1:
            return {"type": "service", "service_key": matched_keys[0], "message": None}
        elif len(matched_keys) > 1:
            return {"type": "multi_service", "service_key": matched_keys[0], "service_keys": matched_keys, "message": None}
        
        # No keys found - return as conversation
        clean_response = re.sub(r'\[?\w+_\w+\]?', '', response).strip()
        clean_response = re.sub(r'SERVICE_KEY:\s*\S+', '', clean_response).strip()
        
        if not clean_response:
            clean_response = "كيف يمكنني مساعدتك؟" if is_arabic else "How can I help you?"
        
        return {"type": "conversation", "service_key": None, "message": clean_response}
        
    except subprocess.TimeoutExpired:
        msg = "انتهت المهلة، حاول مرة أخرى." if is_arabic else "Request timed out. Please try again."
        return {"type": "conversation", "service_key": None, "message": msg}
        
    except Exception as e:
        print(f"[LLM Error] {e}")
        msg = "حدث خطأ، حاول مرة أخرى." if is_arabic else "An error occurred. Please try again."
        return {"type": "conversation", "service_key": None, "message": msg}

# ============================================================================
# RESPONSE BUILDER
# ============================================================================

def build_response(service_key, language = "ar"):
    """
    Build formatted response dictionary for a service.
    
    Returns dictionary with: title, platform, category, description, 
    steps, requirements, and official_link.
    """
    service = SERVICES[service_key]
    
    if language == "en":
        return {
            "title": service["title_en"],
            "platform": service["platform"],
            "category": service["category"],
            "description": service["description_en"],
            "steps": service["steps_en"],
            "requirements": service["requirements"]["en"],
            "official_link": service["official_link"]
        }
    
    # Default: Arabic
    return {
        "title": service["title_ar"],
        "platform": service["platform"],
        "category": service["category"],
        "description": service["description_ar"],
        "steps": service["steps_ar"],
        "requirements": service["requirements"]["ar"],
        "official_link": service["official_link"]
    }
