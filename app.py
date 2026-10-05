import os
import json
import urllib.request
import urllib.error
import streamlit as st

# पेज कॉन्फ़िगरेशन
st.set_page_config(page_title="HomeoGuide AI", page_icon="🌿", layout="centered")

st.title("🌿 HomeoGuide AI - होम्योपैथिक लक्षण गाइड")
st.write("अपनी परेशानी और लक्षण नीचे विस्तार से लिखें:")

# Streamlit Secrets या Environment से API Key लोड करना
API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

# यूजर इनपुट बॉक्स
complaint = st.text_area(
    "लक्षण और परेशानी लिखें:",
    placeholder="जैसे: मुझे 3 दिन से सिरदर्द है, धूप में जाने से बढ़ता है, और ठंड लगने जैसा महसूस होता है...",
    height=120
)

# बटन और लॉजिक
if st.button("दवा का सुझाव देखें 🔍", use_container_width=True):
    if not complaint.strip():
        st.warning("कृपया पहले अपनी तकलीफ या लक्षण दर्ज करें।")
    elif not API_KEY:
        st.error("कृपया Streamlit Secrets में अपनी GEMINI_API_KEY सेट करें!")
    else:
        with st.spinner("AI लक्षणों का विश्लेषण कर रहा है..."):
            prompt_text = f"""
            You are an expert Homeopathic consultant based strictly on Boericke and Kent Materia Medica.
            Patient Complaint: {complaint}

            Provide response in clean Hindi with:
            1. Top 2-3 most matching Homeopathic remedies.
            2. Key symptoms (लक्षण मिलान) and Modalities (कब घटता/बढ़ता है).
            3. Suggested common potency (e.g., 30C).
            4. Clear medical safety advice.
            """

            # Google Gemini Direct REST API Call (बिना किसी बाहरी लाइब्रेरी के)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt_text}
                        ]
                    }
                ]
            }

            try:
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                
                with urllib.request.urlopen(req) as response:
                    res_body = response.read().decode('utf-8')
                    res_json = json.loads(res_body)
                    
                    # जवाब निकालना
                    ai_reply = res_json['candidates'][0]['content']['parts'][0]['text']
                    
                    st.success("विश्लेषण पूरा हुआ!")
                    st.markdown(ai_reply)
                    st.warning("⚠️ **महत्वपूर्ण सूचना:** यह जानकारी केवल शैक्षणिक और संदर्भ के उद्देश्य से है। किसी भी होम्योपैथिक दवा के सेवन से पहले किसी योग्य रजिस्टर्ड चिकित्सक (BHMS/MD) से परामर्श अवश्य लें।")

            except urllib.error.HTTPError as http_err:
                err_content = http_err.read().decode('utf-8')
                st.error(f"API एरर आया: {err_content}")
            except Exception as e:
                st.error(f"त्रुटि आई: {e}")
