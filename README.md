
# 🧠 Debatify – AI-Powered Telegram Bot for Fact-Based Debates

**Finalist – CS Faculty Hackathon on Disinformation, May 2025**

> _Combating disinformation and polarization through civil, source-backed debates between AI agents._

---

## 🚨 Problem

Online discourse, especially on political or polarizing issues, is increasingly shaped by **fake news**, **biased sources**, and **algorithm-driven echo chambers**. Many heated arguments online are rooted in **claims based on misinformation**, often without proper fact-checking or exposure to alternative viewpoints.

---

## 🎯 Our Goal

**Debatify** aims to raise awareness of disinformation by simulating **fact-based, respectful debates** between two AI agents. Each "bot" adopts one side of a claim and cites real sources, helping users understand **how bias influences argumentation**—and how critical thinking and civil dialogue can bridge divides **without compromising truth**.

---

## 🛠️ Features & Technical Overview

- 🔍 **Claim Extraction & Polarity Detection**  
  Using OpenAI’s API, the system extracts the main claim from a user-provided article and identifies opposing viewpoints.

- 🌐 **Web Search with Exa API**  
  For each side of the claim, we fetch real-time web articles using [Exa's API](https://exa.ai/), focused on diverse perspectives.

- 🧭 **Bias Classification**  
  Articles are classified for bias (Side A / Side B / Neutral) using OpenAI models to ensure balanced input into the debate.

- 🤖 **AI-Generated Debate Simulation**  
  Two bots argue their side using retrieved, biased sources. They engage respectfully, fact-check each other, and aim to find **truth-based consensus** when possible.

- 📄 **Summary & Non-Biased Verdict**  
  When the conversation ends, a concise, **fact-checked summary and neutral verdict** is provided to the user.

- 🗨️ **Interactive User Mode**  
  Users can continue the debate, ask questions, or stop the discussion at any point.

---

## 🧰 Tech Stack

- **Python 3.10+**
- **Telegram Bot API**
- **OpenAI GPT-4 API** – NLP, debate generation, summarization
- **Exa API** – Search engine for real-time web content
- **LangChain** – (Optional, if used, for chaining modules)
- **BeautifulSoup / Requests** – For HTML parsing (if needed)

---

## 📸 Demo

![Debatify Demo](demo.gif)  
*(or embed a short video/GIF here if available)*

---

## 🧪 How to Run

```bash
git clone https://github.com/yourusername/debatify.git
cd debatify
pip install -r requirements.txt
# Add your API keys to config.yaml or environment variables
python src/main.py
```

*Note: You’ll need valid OpenAI and Exa API keys to run the full pipeline.*

---

## 🤝 Team & Acknowledgments

Built in 36 hours by a team of CS students from [Your University].  
We thank the CS Faculty Hackathon organizers for the opportunity to build technology that blends **AI**, **ethics**, and **social impact**.

---

## 📌 Why It Matters

> “Disinformation is not just a technical challenge—it's a social one. Debatify shows how we can use AI not to polarize further, but to **inform, reflect, and repair**.”
