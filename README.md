
# 🧠 Debatify – AI-Powered Telegram Bot for Fact-Based Debates

**Finalist – Technion CS Faculty Hackathon-Doing Good, on Disinformation, May 2025**

> _Combating disinformation and polarization through civil, source-backed debates between AI agents, and fact checking argumetns._

---

## 🚨 Problem

Online discourse, especially on political or polarizing issues, is increasingly shaped by **fake news**, **biased sources**, and **algorithm-driven echo chambers**. Most of the Heated discussions that deepen societal divisions and fuel hostility between opposing viewpoints within the same community online, are rooted in **claims based on misinformation and disinformation**, often without proper fact-checking or exposure to alternative viewpoints.

---

## 🎯 Our Goal

**Debatify** aims to heal social rifts by fostering constructive conversations grounded in verified information, help reconcile differing perspectives by prioritizing facts over friction and raise awareness of disinformation by Exposing users to multiple perspectives by simulating **fact-based, respectful debates with Tone aimed at mutual understanding and bridge-building** between two AI agents. Each "bot" adopts one side of a claim and cites real sources, helping users understand **how bias influences argumentation**—and how critical thinking and civil dialogue can bridge divides **without compromising truth or Fact checked Source backed argumetns**.

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

- **Python 3.11**
- **Telegram Bot API**
- **OpenAI GPT-4(gpt4.1 Nano model) API** – NLP, debate generation, summarization
- **Exa API** – Search engine for real-time web content

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

Built in 36 hours by a team of CS students from Technion Taub faculty of computer science.  
We thank the CS Faculty Hackathon organizers for the opportunity to build technology that blends **AI**, **ethics**, and **social impact**, and we would like to extend special thanks to the technical, product and humanities Mentors and entrepreneurs from all the participating Universitis and companies (Reichman university, BGU, University of Haifa, Apple, Mobileye, KLA, Israel internet association) for their invaluable guidance, technical advice, and encouragement throughout the hackathon. Their support helped us refine our idea, navigate challenges, and build a project with both technological depth and social relevance.

---

## 📌 Why It Matters

> “Disinformation is not just a technical challenge—it's a social one. Debatify shows how we can use AI not to polarize further, but to **inform, reflect, and repair**.”

![Alt text](hackathonPic.png)

