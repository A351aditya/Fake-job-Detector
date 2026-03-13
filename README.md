# Fake-job-Detector
A Streamlit web application that analyzes job posts to detect potential scams. It combines rule-based heuristics with a simple machine learning model to identify red flags commonly found in fraudulent job advertisements.

✨ Features
Paste & Analyze: Enter any job description and get an instant scam probability score.

Multi‑factor Detection:

Urgency indicators (e.g., "urgent hiring", "limited seats")

Unrealistic salary promises ("earn ₹5000 daily")

Suspicious contact methods (WhatsApp, Telegram, personal emails)

Grammar & punctuation issues (excessive caps, multiple exclamation marks)

"Too‑good‑to‑be‑true" offers ("no experience needed", "instant hiring")

Machine Learning classification (trained on a small sample dataset)

Risk level classification: Low / Medium / High with color‑coded feedback.

Detailed explanations: Lists every red flag detected.

Actionable recommendations: Safety tips based on the risk level.

Red Flag Guide: Educational tab explaining common scam tactics.

Test Examples: Built‑in sample job posts to test the detector.

🧠 How It Works
The application performs two types of analysis:

Rule‑based detection
Uses regular expressions to scan the text for patterns that are common in scam posts. Each category of red flags contributes to a weighted score.

Machine Learning classification
A TfidfVectorizer + LogisticRegression model is trained on a tiny hand‑crafted dataset of scam and legitimate examples. The model outputs a probability, which is incorporated into the final score.

The total scam score is a weighted combination of all red flags (capped at 100%). A score below 30% is considered Low Risk, 30–70% Medium Risk, and above 70% High Risk.

🚀 Usage
Open the app and go to the Analyze Job Post tab.

Paste a job description into the text area (minimum 20 characters).

Click Analyze Job Post.

View the results:

Scam probability score

List of detected red flags

Recommendations based on risk level

Explore the Red Flag Guide for educational content.

Use the Test Examples tab to quickly evaluate the detector with pre‑defined samples.

🧪 Example Test Cases
Example	Expected Risk	Description
Obvious WhatsApp scam	🔴 High	"Urgent hiring, contact on WhatsApp, registration fee"
Legitimate IT job	🟢 Low	Professional description, company details, no fees
Sophisticated scam	🟡 Medium	Looks like a real company but asks for a "refundable deposit"
MLM offer	🔴 High	"Buy starter kit, recruit members, earn commission"
You can find these and more in test_jobs.py.

🧰 Technologies Used
Python 3.13

Streamlit – Web framework

scikit-learn – TF‑IDF vectorizer & Logistic Regression

pandas – Data handling (minimal)

re – Regular expressions for rule‑based detection

📌 Limitations & Disclaimer
Educational purpose only – This tool is a demonstration and should not be the sole basis for determining job legitimacy.

Small training dataset – The ML model is trained on a handful of examples; its accuracy is limited.

Rule‑based patterns – May produce false positives/negatives. Always verify through official channels.

No money requests – Legitimate employers never ask for money. If a post asks for a fee, treat it as highly suspicious.

🤝 Contributing
Contributions are welcome! If you have ideas for improving the detection rules, adding more test cases, or enhancing the UI, feel free to:

Fork the repository

Create a new branch (git checkout -b feature/YourFeature)

Commit your changes (git commit -m 'Add some feature')

Push to the branch (git push origin feature/YourFeature)

Open a Pull Request

 
🙏 Acknowledgements
Inspired by the need to protect job seekers from online scams.

Thanks to the Streamlit community for the amazing framework.

