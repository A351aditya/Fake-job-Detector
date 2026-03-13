import streamlit as st 
import pandas as pd
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import watchdog
import warnings
warnings.filterwarnings('ignore')

# set page config
st.set_page_config(
    page_title="Fake job Detector",
    page_icon="🔎",
    layout="wide"
)

# Title  and description
st.title("🔎 Fake job Detector for cal Center/Scam jons")
st.markdown("Paste a job post below to anlayis its lagitimacy and identify potential red flags.")

# Intialize session state for model and vectorizer

if 'model' not in st.session_state:
    st.session_state.model = None
    
if 'vectorizer' not in st.session_state:
    st.session_state.vectorizer = None
    
# load or create a simple model
def load_model():
    """create or load a simple ML for demonstration"""
    
    sample_scam_texts = ["Earn ₹5000 daily from home. Pay ₹1000 registration fee to start.",
                        "Online typing job available. Send ₹999 verification fee now.",
                        "Work from home and earn ₹40,000 monthly. Limited seats available.",
                        "Selected for Amazon online job. Pay ₹2000 training fee today.",
                        "Urgent hiring! Data entry job. Contact HR on WhatsApp.",
                        "part-time social media job. Earn daily without interview.",
                        "Guaranteed income job. Pay processing fee to join.",
                        "Simple online work. Earn money by liking posts."
                        ]
    
    sample_lagit_texts = ["We are hiring a Python Developer. Experience with Django preferred. Apply through our official website.",
                         "Software Engineer Intern needed in Noida. Knowledge of Python and ML required.",
                         "Customer Support Executive required. Good communication skills needed. Apply online.",
                         "Digital Marketing Intern position available. Freshers can apply. Training provided.",
                         "Looking for Data Analyst with knowledge of Excel and SQL. Full-time role.",
                         "Frontend Developer needed. Skills in HTML, CSS, and JavaScript required.",
                         "Hiring Graphic Designer for our marketing team. Portfolio required.",
                         "Part-time content writer needed."
                         ]
    
    #combine and label
    texts = sample_scam_texts + sample_lagit_texts
    labels = [1] * len(sample_scam_texts) + [0] * len(sample_lagit_texts)
    
    # create and train vectorizer nad model
    vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
    x = vectorizer.fit_transform(texts)
    
    model = LogisticRegression()
    model.fit(x, labels)
    
    return model, vectorizer

# Rule-based detection functions

def detect_urgency(text):
    """Detect urgency indicators in text"""
    urgency_keywords = ["urgent hiring", "apply immediately", "limited seats",
                        "last chance", "immediate joining", "act now",
                        "hurry up", "today only", "instant job", "quick selection"
                    ]
    
    matches = []
    for keyword in urgency_keywords:
        if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
            matches.append(keyword)
            return matches
        
def detect_salary_language(text):
    """Detect unrealistic salary promises"""
    salary_patterns = [
        r'\$\d{3,5}\s*(weekly| daily| per week| per day)',
        r'earn\s+\$\d{3,}\s*(easily|quickly|fast)',
        r'high\s+salary\s+no\s+experince',
        r'guaranteed\s+(income|salary|payment)',
        r'\$\d{2,5}k?\s*(monthly|per month)',
        r'make\s+money\s+fast',
        r'get\s+rich\s+quick'
    ]
    
    matches = []
    for pattern in salary_patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            matches.extend(found)
            
    return matches

def detect_contact_methods(text):
    """Detect suspicious contact"""
    contact_patterns = [
        r'whatsapp',
        r'telegram',
        r'@[\w]+',
        r'\+\d{10,}',
        r'cash\s*app',
        r'paypal\s*me',
        r'direct\s*message',
        r'DM\s*us',
        r'message\s*us\s*on'
    ]
    
    matches =[]
    for pattern in contact_patterns:
        found = re.findall(pattern, text,re.IGNORECASE)
        if found:
            matches.extend(found)
            
    return matches

def detect_grammer_issues(text):
    """Detect poor grammer and excssive punctuation"""
    issues = []
    
    # Excessive capitalization
    if re.search(r'[A-Z]{4,}', text):
        issues.append("Excessive capitalization")
        
    # Multiple exclamation marks
    if re.search(r'!{2,}', text):
        issues.append("Multilple exclamation marks")
        
    # poor sentence structure
    lines = text.split('\n')
    shor_lines = [line for line in lines if len(line.split())< 3 and len(line) > 10]
    if len(shor_lines) > 3:
        issues.append('poor sentence structure')
        
    # Missing professional language
    professional_terms = ['experience', 'qualifications', 'resume', 'interview', 'position']
    
    if not any(term in text.lower() for term in professional_terms):
        issues.append('Lacks professional terminolgy')
        
    return issues
    
def detect_catch(text):
    """Detect offers that seems catch"""
    patterns = [
        r'no\s+experience\s+needed',
        r'work\s+from\s+home',
        r'flexible\s+hours',
        r'high\s+pay',
        r'easy\s+money',
        r'get\s+paid\s+to',
        r'no\s+interview',
        r'no\s+resume',
        r'instant\s+hiring',
        r'guranteed\s+job'
    ]
        
    matches =[]
    for pattern in patterns:
        found = re.findall(pattern, text,re.IGNORECASE)
        if found:
            matches.extend(found)
           
        return matches
        
def calculate_scam_score(red_flags):
    """calculate scam proability based on red flag"""
    base_score = 0
    weights = {
        'urgency': 15,
        'salary': 20,
        'contact': 25,
        'grammer': 10,
        'too_good': 20,
        'ml_prediction': 10
    }
    
    for flag_type, flag_list in red_flags.items():
        if flag_type != 'score' and flag_list:
            if flag_type == 'ml_prediction':
                base_score += flag_list[0] * weights[flag_type]
            else:
                base_score += min(len(flag_list) * 5, weights[flag_type])
                
    return min(100, base_score)
    
def analyze_job_post(text):
    """Analyze job post and return red flags"""
    if not text or len(text.strip()) < 20:
        return None
    
    red_flags = {
        'urgency': detect_urgency(text),
        'salary': detect_salary_language(text),
        'contact': detect_contact_methods(text), 
        'grammer': detect_grammer_issues(text),
        'too_good': detect_catch(text),
        'ml_prediction': []
    }
    
    if st.session_state.model and st.session_state.vectorizer:
        try:
            transformed = st.session_state.vectorizer.transform([text])
            prediction = st.session_state.model.predict_proba(transformed)[0][1]
            red_flags['ml_prediction'] = [prediction]
        except:
            red_flags['ml_prediction'] = [0.5]
            
    red_flags['score'] = calculate_scam_score(red_flags)
            
    return red_flags
        
def generate_explanation(red_flags):
    """Generate explanation based on red flags"""
    explanations = []
    
    if red_flags['urgency']:
        explanations.append(f"Urgency detected: The post uses urgent language ({', '.join(red_flags['urgency'][:3])}). Legitimate jobs rarely pressure applicants.")
    
    if red_flags['salary']:
        explanations.append(f"Unrealistic salary: Mentions unrealistic earnings ({', '.join(red_flags['salary'][:3])}). Scams often promise high pay for little work.")
    
    if red_flags['contact']:
        explanations.append(f"Suspicious contact methods: Uses informal channels ({', '.join(red_flags['contact'][:3])}). Legitimate companies use professional communication.")
    
    if red_flags['grammer']:
        explanations.append(f"Language issues: Shows signs of poor professionalism ({', '.join(red_flags['grammer'])}). Professional job posts are well-written.")
    
    if red_flags['too_good']:
        explanations.append(f"Too good to be true: Promises unrealistic benefits ({', '.join(red_flags['too_good'][:3])}). Be wary of offers requiring no experience for high pay.")
    
    if red_flags.get('ml_prediction', [0])[0] > 0.7:
        explanations.append(f"AI detection: Our machine learning model identified patterns consistent with scam job posts.")
    
    if not explanations:
        explanations.append("No major red flags detected. However, always verify the company through official channels.")
    
    return explanations

# Load the model
if st.session_state.model is None:
    with st.spinner("Loading detection model..."):
        st.session_state.model, st.session_state.vectorizer =load_model()

# Create tabs
tab1, tab2, tab3 = st.tabs(["Analyze Job Post", "Red Flag Guide", "About"])

with tab1:
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        job_text = st.text_area(
            "Paste the job post here:",
            height=300,
            placeholder="Example: URGENT HIRING!!! Work from home and earn $5000 weekly. No experience needed. WhatsApp us at +1234567890 for immediate start..."
        )
    
    with col2:
        st.markdown("### What to look for:")
        st.markdown("""
        - Urgent hiring language
        - Unrealistic salary promises
        - Contact via WhatsApp/Telegram
        - Poor grammar & excessive punctuation
        - 'Too good to be true' offers
        - Lack of company details
        """)
        
        st.markdown("### Example scam indicators:")
        st.markdown("""
        ```
        "EARN $5000 WEEKLY!"
        "WhatsApp for interview"
        "No experience needed"
        "Immediate start"
        ```
        """)
# Analyze button
    if st.button("Analyze Job Post", type="primary", use_container_width=True):
        if job_text:
            with st.spinner("Analyzing job post..."):
                # Analyze the text
                red_flags = analyze_job_post(job_text)
                
                if red_flags:
                    # Display results
                    st.subheader("Analysis Results")
                    
                    # Create metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        score = red_flags['score']
                        if score < 30:
                            st.metric("Scam Probability", f"{score}%", delta="LOW RISK", delta_color="normal")
                        elif score < 70:
                            st.metric("Scam Probability", f"{score}%", delta="MEDIUM RISK", delta_color="off")
                        else:
                            st.metric("Scam Probability", f"{score}%", delta="HIGH RISK", delta_color="inverse")
                    
                    with col2:
                        st.metric("Red Flags Found", len([v for k, v in red_flags.items() if k != 'score' and v]))
                    
                    with col3:
                        urgency_count = len(red_flags.get('urgency') or [])
                        st.metric("Urgency Indicators", urgency_count)
                    
                    with col4:
                        contact_count = len(red_flags.get('contact') or [])
                        st.metric("Suspicious Contacts", contact_count)
                        
                    # Progress bar for score
                    st.progress(red_flags['score'] / 100)
                    
                    # Detailed breakdown
                    st.subheader("Detailed Breakdown")
                    
                    explanations = generate_explanation(red_flags)
                    for explanation in explanations:
                        st.info(explanation)
                    
                    # Show specific findings
                    with st.expander("View specific detected issues"):
                        for flag_type, flag_list in red_flags.items():
                            if flag_type != 'score' and flag_list and flag_type != 'ml_prediction':
                                st.write(f"**{flag_type.title()}**:")
                                for item in flag_list[:5]:  # Show first 5 items
                                    st.write(f"  - {item}")
                                    
                                    
                    # Recommendations              
                    st.subheader("Recommendations")
                    
                    if red_flags['score'] > 70:
                        st.error("**HIGH RISK DETECTED** - This job post shows multiple scam indicators:")
                        st.markdown("""
                        1. **DO NOT** share personal information
                        2. **DO NOT** pay any "registration" or "training" fees
                        3. **DO NOT** contact through suspicious channels
                        4. Research the company on official platforms
                        5. Report suspicious posts to authorities
                        """)
                    elif red_flags['score'] > 30:
                        st.warning("**CAUTION ADVISED** - Verify this opportunity carefully:")
                        st.markdown("""
                        1. Research the company's official website
                        2. Check employee reviews on Glassdoor/LinkedIn
                        3. Ensure communication is through professional channels
                        4. Never pay money to get a job
                        5. Trust your instincts
                        """)
                        
                    else:
                        st.success("**LOW RISK** - This appears legitimate, but always verify:")
                        st.markdown("""
                        1. Still research the company
                        2. Ensure proper interview process
                        3. Verify job offer through official channels
                        4. Read the contract carefully
                        """)
                        
                else:
                    st.error("please enter a longer job for analysis.")
                    
        else:
            st.warning("please paste a job post for analyze.")
            
    with tab2:
        st.header("Red Flag Guide for Job Seekers")
        
        st.subheader("Common Scam Tactics")
    
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Urgency & Pressure
            - "Hiring immediately"
            - "Limited time offer"
            - "Must start today"
            - "Quick hiring process"
        
            ### Unrealistic Promises
            - "Earn $5000 weekly from home"
            - "No experience needed"
            - "Guaranteed income"
            - "Get rich quick schemes"
        
            ### Unprofessional Contact
            - WhatsApp/Telegram interviews
            - Generic email addresses
            - No company phone number
            - Direct messages only
            """)
            
        with col2:
            st.markdown("""
            ### Poor Presentation
            - Bad grammar/spelling
            - Excessive punctuation!!!!
            - ALL CAPS TEXT
            - Lack of company details
        
            ### Vague Requirements
            - No specific skills needed
            - "Anyone can do it"
            - No interview process
            - No background check
        
            ### Request for Money
            - "Training fee"
            - "Registration cost"
            - "Equipment deposit"
            - "Background check fee"
            """)
            
        st.subheader("Legitimate Job Indicators")
        st.markdown("""
        - Clear company information and website
        - Professional email addresses (name@company.com)
        - Structured interview process
        - Realistic salary ranges
        - Specific job requirements
        - Professional communication
        - No request for money
        - Physical office address (or verified remote)
        """)
    
    st.subheader("Safety Checklist")
    checklist = st.columns(2)
    
    with checklist[0]:
        st.checkbox("Company has official website")
        st.checkbox("Job posted on reputable platform")
        st.checkbox("Professional email/contact provided")
        st.checkbox("Realistic job requirements")
    
    with checklist[1]:
        st.checkbox("No money requested upfront")
        st.checkbox("Clear interview process")
        st.checkbox("Physical address verifiable")
        st.checkbox("Employee reviews available")
        
        
    with tab3:
        st.header("About Fake Job Detector")
    
        st.markdown("""
        ### How It Works
    
        This tool uses a combination of techniques to identify potential scam job posts:
    
        1. **Rule-based Detection**: Identifies specific patterns and keywords commonly used in scams
        2. **Machine Learning**: Analyzes text patterns using a trained classifier
        3. **Heuristic Analysis**: Checks for multiple scam indicators
    
        ### Detection Methods
    
        - **Salary-Language Tricks**: Identifies unrealistic earnings promises
        - **Grammar & Urgency Analysis**: Detects poor writing and pressure tactics
        - **Contact Method Verification**: Flags suspicious communication channels
        - **Too-Good-To-Be-True Detection**: Identifies unrealistic offers
    
        ### Technology Stack
    
        - **Python** with Natural Language Processing (NLP)
        - **Regex Patterns** for rule-based detection
        - **Machine Learning Classifier** (Logistic Regression)
        - **Streamlit** for web interface
    ### Important Disclaimer
    
    This tool provides **risk assessment only** and is not 100% accurate. Always:
    
    - Conduct your own research
    - Verify through official channels
    - Never share sensitive information
    - Report suspicious posts to authorities
    
    ### For Employers
    
    If you're a legitimate employer and your posts are flagged:
    
    1. Use professional language in job descriptions
    2. Provide clear company information
    3. Use official communication channels
    4. Avoid excessive urgency language
    """)
        
    st.info("**Note**: This is a demonstration tool. For production use, the model should be trained on a larger, real-world dataset of scam and legitimate job posts.")


# footer

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p> Use this tool as a first line of defense against job scams. Always verify opportunities through official channels.</p>
        <p><small>Note: This tool is for educational purposes. Accuracy may vary.</small></p>
    </div>
    """,
    unsafe_allow_html=True
)