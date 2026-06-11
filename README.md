# 🧪 A/B Test Readout Agent

🌐 [Live Project Page](https://shivamdhawani24-bit.github.io/ab-test-readout-agent)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Anthropic](https://img.shields.io/badge/Anthropic-Claude-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

An **agentic AI system** that interprets A/B experiment results and delivers a structured readout — statistical significance, guardrail evaluation, business impact estimate, and a decisive **SHIP / KILL / RUN LONGER** recommendation.

> Built to automate the experiment readout process that product and data science teams run manually after every A/B test.

---

## How It Works

```
Experiment Input (control vs treatment metrics)
              ↓
     Claude Agent (claude-opus-4-5)
              ↓
  [Tool Call] run_statistical_analysis()
              ↓
     stats.py — significance, lift,
     sample size, guardrail, impact
              ↓
  Structured Readout: SHIP / KILL / RUN LONGER
  + Confidence + Business Impact + Risk Flags
```

The agent uses **Claude tool use** — it calls a statistical analysis tool mid-reasoning, interprets the results, checks for risk flags (novelty effect, guardrail degradation, low sample size), and delivers a decisive recommendation.

---

## Sample Output

```json
{
  "verdict": "SHIP",
  "confidence": 95,
  "primary_finding": "Treatment improved activation rate by 7pp (+13% relative) with statistical significance at 95% confidence.",
  "business_impact": "~$6.3M annualized based on 1.5M eligible users",
  "risk_flags": [],
  "guardrail_status": "PASS",
  "reasoning": "Treatment is clearly winning on the primary metric with sufficient sample size and adequate test duration. Guardrail metric shows a minor 0.3pp increase but remains within acceptable range.",
  "recommended_action": "Ship to 100% traffic. Monitor guardrail metric for first 7 days post-launch."
}
```

---

## Experiment Signals Evaluated

| Check | What it does |
|---|---|
| Statistical Significance | Two-proportion z-test, p-value, confidence level |
| Lift Calculation | Absolute (pp) and relative (%) lift |
| Sample Size Validation | Minimum detectable effect check |
| Guardrail Evaluation | Flags regressions on secondary metrics |
| Novelty Effect Flag | Warns if test duration under 7 days |
| Business Impact | Annualized revenue estimate from lift |

---

## Tech Stack

- **Anthropic Claude** — `claude-opus-4-5` with tool use
- **Python 3.10+** — agent logic and statistical calculations
- **Streamlit** — interactive experiment input UI
- **Custom stats engine** — `stats.py` handles all significance testing

---

## Getting Started

```bash
git clone https://github.com/shivamdhawani24-bit/ab-test-readout-agent.git
cd ab-test-readout-agent
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_api_key_here
streamlit run app.py
```

---

## Project Structure

```
ab-test-readout-agent/
├── agent.py                    # Claude agentic logic with tool use
├── stats.py                    # Statistical analysis engine
├── app.py                      # Streamlit UI
├── requirements.txt
└── sample_experiments/
    └── test_cases.json         # 4 sample experiments for testing
```

---

## About

Built by **Shivam Dhawan** — Senior Data Scientist with 8+ years at Intuit, Chime, and Airbnb.

Inspired by real experimentation work — owning A/B experiment readouts, metric definition, and go/no-go recommendations for product launches at Intuit across millions of QuickBooks customers.

[LinkedIn](https://www.linkedin.com/in/shivam-dhawan/) • [GitHub](https://github.com/shivamdhawani24-bit)
