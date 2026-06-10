import anthropic
import json
from stats import run_full_analysis

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a senior data scientist and experimentation expert with 8+ years of experience running A/B tests at scale across product and fintech platforms.

Your job is to interpret A/B experiment results and deliver a clear, decisive readout.

You will be given statistical analysis results from a tool. Use them to reason and return a JSON decision in this exact format:

{
  "verdict": "SHIP" | "KILL" | "RUN LONGER",
  "confidence": <0-100>,
  "primary_finding": "<one crisp sentence — what happened>",
  "business_impact": "<quantified impact if shipped>",
  "risk_flags": ["<flag1>", "<flag2>"],
  "guardrail_status": "PASS" | "FAIL" | "WATCH",
  "reasoning": "<2-3 sentences — plain English explanation of the decision>",
  "recommended_action": "<exactly what the team should do next>"
}

Be decisive. Think like an experienced DS who has shipped hundreds of experiments.
Flag novelty effects if test duration is under 7 days.
Flag sample size issues if raised in the analysis.
Never recommend shipping if guardrail is failing."""

tools = [
    {
        "name": "run_statistical_analysis",
        "description": "Run complete statistical analysis on an A/B experiment. Returns significance, lift, sample size validation, guardrail check, and business impact estimate.",
        "input_schema": {
            "type": "object",
            "properties": {
                "experiment": {
                    "type": "object",
                    "description": "Experiment data including control/treatment metrics",
                    "properties": {
                        "control_n": {"type": "number"},
                        "control_rate": {"type": "number"},
                        "treatment_n": {"type": "number"},
                        "treatment_rate": {"type": "number"},
                        "guardrail_control": {"type": "number"},
                        "guardrail_treatment": {"type": "number"},
                        "total_users": {"type": "number"}
                    },
                    "required": ["control_n", "control_rate", "treatment_n", "treatment_rate"]
                }
            },
            "required": ["experiment"]
        }
    }
]


def run_ab_agent(experiment: dict) -> dict:
    """
    Run the A/B test readout agent on experiment data.
    Returns a structured verdict with reasoning.
    """
    messages = [
        {
            "role": "user",
            "content": f"Analyze this A/B experiment and return a JSON readout:\n\n{json.dumps(experiment, indent=2)}"
        }
    ]

    reasoning_trace = []

    while True:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_block = next(b for b in response.content if b.type == "tool_use")
            exp_data = tool_block.input["experiment"]

            reasoning_trace.append("Running statistical analysis")
            stats_result = run_full_analysis(exp_data)

            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,
                        "content": json.dumps(stats_result)
                    }
                ]
            })

        elif response.stop_reason == "end_turn":
            final_text = next(b.text for b in response.content if hasattr(b, "text"))
            try:
                start = final_text.find("{")
                end = final_text.rfind("}") + 1
                verdict = json.loads(final_text[start:end])
            except Exception:
                verdict = {"raw_response": final_text}

            return {
                "verdict": verdict,
                "reasoning_trace": reasoning_trace,
                "experiment_name": experiment.get("name", "Unnamed Experiment")
            }


if __name__ == "__main__":
    sample = {
        "name": "One-Click Onboarding — Phase 3",
        "metric": "Activation Rate",
        "control_n": 10000,
        "control_rate": 54.0,
        "treatment_n": 10200,
        "treatment_rate": 61.0,
        "guardrail_control": 8.2,
        "guardrail_treatment": 8.5,
        "total_users": 1500000,
        "duration_days": 14
    }

    result = run_ab_agent(sample)
    print(json.dumps(result, indent=2))
