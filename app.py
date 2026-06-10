import streamlit as st
import json
from agent import run_ab_agent

st.set_page_config(
    page_title="A/B Test Readout Agent",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 A/B Test Readout Agent")
st.caption("Powered by Claude (Anthropic) — Agentic experiment interpretation with statistical analysis")

VERDICT_COLORS = {
    "SHIP": "🟢",
    "KILL": "🔴",
    "RUN LONGER": "🟡"
}

SAMPLE_EXPERIMENTS = {
    "One-Click Onboarding — Ship": {
        "name": "One-Click Onboarding — Phase 3",
        "metric": "Activation Rate (%)",
        "control_n": 10000,
        "control_rate": 54.0,
        "treatment_n": 10200,
        "treatment_rate": 61.0,
        "guardrail_control": 8.2,
        "guardrail_treatment": 8.5,
        "total_users": 1500000,
        "duration_days": 14
    },
    "GTKM Onboarding — Run Longer": {
        "name": "GTKM Onboarding Flow",
        "metric": "Activation Rate (%)",
        "control_n": 800,
        "control_rate": 48.0,
        "treatment_n": 820,
        "treatment_rate": 51.0,
        "guardrail_control": 6.5,
        "guardrail_treatment": 6.8,
        "total_users": 500000,
        "duration_days": 5
    },
    "Feature X — Kill": {
        "name": "Simplified Dashboard Feature",
        "metric": "7-Day Retention Rate (%)",
        "control_n": 15000,
        "control_rate": 62.0,
        "treatment_n": 14800,
        "treatment_rate": 59.5,
        "guardrail_control": 4.1,
        "guardrail_treatment": 5.8,
        "total_users": 2000000,
        "duration_days": 21
    }
}

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Experiment Input")

    sample_choice = st.selectbox(
        "Load a sample experiment or enter your own:",
        ["Custom"] + list(SAMPLE_EXPERIMENTS.keys())
    )

    if sample_choice != "Custom":
        exp = SAMPLE_EXPERIMENTS[sample_choice]
    else:
        exp = {
            "name": "",
            "metric": "Activation Rate (%)",
            "control_n": 10000,
            "control_rate": 50.0,
            "treatment_n": 10000,
            "treatment_rate": 53.0,
            "guardrail_control": 5.0,
            "guardrail_treatment": 5.2,
            "total_users": 1000000,
            "duration_days": 14
        }

    with st.form("experiment_form"):
        name = st.text_input("Experiment Name", value=exp.get("name", ""))
        metric = st.text_input("Primary Metric", value=exp.get("metric", "Activation Rate (%)"))

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Control**")
            control_n = st.number_input("Sample Size", value=exp["control_n"], key="cn", min_value=1)
            control_rate = st.number_input("Metric Rate (%)", value=exp["control_rate"], key="cr", min_value=0.0, max_value=100.0)
        with c2:
            st.markdown("**Treatment**")
            treatment_n = st.number_input("Sample Size", value=exp["treatment_n"], key="tn", min_value=1)
            treatment_rate = st.number_input("Metric Rate (%)", value=exp["treatment_rate"], key="tr", min_value=0.0, max_value=100.0)

        st.markdown("**Guardrail Metric** (optional — e.g. support contact rate)")
        g1, g2 = st.columns(2)
        with g1:
            guardrail_control = st.number_input("Guardrail Control (%)", value=exp.get("guardrail_control", 0.0), key="gc")
        with g2:
            guardrail_treatment = st.number_input("Guardrail Treatment (%)", value=exp.get("guardrail_treatment", 0.0), key="gt")

        total_users = st.number_input("Total Eligible Users (for impact estimate)", value=exp.get("total_users", 1000000), min_value=1)
        duration_days = st.number_input("Test Duration (days)", value=exp.get("duration_days", 14), min_value=1)

        submitted = st.form_submit_button("🔍 Run Readout", use_container_width=True, type="primary")

with col2:
    st.subheader("Experiment Readout")

    if submitted:
        experiment_data = {
            "name": name,
            "metric": metric,
            "control_n": int(control_n),
            "control_rate": control_rate,
            "treatment_n": int(treatment_n),
            "treatment_rate": treatment_rate,
            "guardrail_control": guardrail_control,
            "guardrail_treatment": guardrail_treatment,
            "total_users": int(total_users),
            "duration_days": int(duration_days)
        }

        with st.spinner("Agent is analyzing experiment results..."):
            result = run_ab_agent(experiment_data)

        verdict_data = result.get("verdict", {})
        verdict = verdict_data.get("verdict", "UNKNOWN")
        confidence = verdict_data.get("confidence", 0)
        icon = VERDICT_COLORS.get(verdict, "⚪")

        st.markdown(f"## {icon} {verdict}")
        st.progress(confidence / 100)
        st.caption(f"Confidence: {confidence}%")
        st.divider()

        st.markdown(f"**Primary Finding:** {verdict_data.get('primary_finding', 'N/A')}")
        st.markdown(f"**Business Impact:** {verdict_data.get('business_impact', 'N/A')}")

        guardrail_status = verdict_data.get("guardrail_status", "N/A")
        status_color = "🟢" if guardrail_status == "PASS" else "🔴" if guardrail_status == "FAIL" else "🟡"
        st.markdown(f"**Guardrail Status:** {status_color} {guardrail_status}")

        risk_flags = verdict_data.get("risk_flags", [])
        if risk_flags:
            st.markdown("**Risk Flags:**")
            for flag in risk_flags:
                st.markdown(f"- ⚠️ {flag}")

        st.divider()
        st.info(verdict_data.get("reasoning", ""))
        st.success(verdict_data.get("recommended_action", ""))

        with st.expander("🔧 Agent Reasoning Trace"):
            for step in result.get("reasoning_trace", []):
                st.markdown(f"→ {step}")

        with st.expander("📄 Raw JSON Output"):
            st.json(result)

    else:
        st.markdown("""
        #### How it works
        1. Enter your experiment metrics — control vs treatment
        2. Add a guardrail metric to protect against regressions
        3. Click **Run Readout**
        4. Agent runs statistical analysis, checks significance, evaluates guardrails
        5. Returns **SHIP / KILL / RUN LONGER** with confidence and reasoning

        ---
        *Built with Anthropic Claude tool-use API + Streamlit*
        """)

st.divider()
st.caption("A/B Test Readout Agent — Portfolio project by Shivam Dhawan | github.com/shivamdhawani24-bit")
