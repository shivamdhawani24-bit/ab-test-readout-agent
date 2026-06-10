"""
Statistical calculations for A/B test evaluation.
Handles significance testing, lift calculation, and sample size validation.
"""

import math


def calculate_significance(control_n, control_rate, treatment_n, treatment_rate):
    """
    Two-proportion z-test for statistical significance.
    Returns p-value, z-score, and confidence level.
    """
    p1 = control_rate / 100
    p2 = treatment_rate / 100
    n1 = control_n
    n2 = treatment_n

    pooled = (p1 * n1 + p2 * n2) / (n1 + n2)

    if pooled == 0 or pooled == 1:
        return {"error": "Cannot compute — rate is 0% or 100%"}

    se = math.sqrt(pooled * (1 - pooled) * (1/n1 + 1/n2))

    if se == 0:
        return {"error": "Standard error is zero — check inputs"}

    z = (p2 - p1) / se

    # Approximate p-value from z-score (two-tailed)
    abs_z = abs(z)
    if abs_z >= 3.29:
        p_value = 0.001
    elif abs_z >= 2.576:
        p_value = 0.01
    elif abs_z >= 1.96:
        p_value = 0.05
    elif abs_z >= 1.645:
        p_value = 0.10
    else:
        p_value = 0.20

    if abs_z >= 2.576:
        confidence = 99
    elif abs_z >= 1.96:
        confidence = 95
    elif abs_z >= 1.645:
        confidence = 90
    else:
        confidence = round(max(50, 100 - p_value * 100), 1)

    return {
        "z_score": round(z, 3),
        "p_value": p_value,
        "confidence_level": confidence,
        "significant": p_value <= 0.05
    }


def calculate_lift(control_rate, treatment_rate):
    """
    Absolute and relative lift between control and treatment.
    """
    absolute_lift = treatment_rate - control_rate
    relative_lift = (absolute_lift / control_rate) * 100 if control_rate != 0 else 0

    return {
        "absolute_lift_pp": round(absolute_lift, 2),
        "relative_lift_pct": round(relative_lift, 2),
        "direction": "positive" if absolute_lift > 0 else "negative"
    }


def validate_sample_size(control_n, treatment_n, control_rate):
    """
    Minimum detectable effect check — is sample size sufficient?
    """
    p = control_rate / 100
    min_n = int((2 * p * (1 - p) * (1.96 + 0.84)**2) / (0.02**2))

    sufficient = control_n >= min_n and treatment_n >= min_n

    return {
        "sufficient": sufficient,
        "recommended_min_per_group": min_n,
        "control_n": control_n,
        "treatment_n": treatment_n,
        "note": "Sample size sufficient" if sufficient else f"Low sample size — recommend at least {min_n:,} per group for 80% power"
    }


def check_guardrail(guardrail_control, guardrail_treatment, threshold=0.5):
    """
    Check if guardrail metric has degraded beyond acceptable threshold.
    """
    delta = guardrail_treatment - guardrail_control
    degraded = delta > threshold

    return {
        "control": guardrail_control,
        "treatment": guardrail_treatment,
        "delta_pp": round(delta, 2),
        "status": "FAIL" if degraded else "PASS",
        "note": f"Guardrail degraded by {delta:.2f}pp — review before shipping" if degraded else "Guardrail stable"
    }


def estimate_business_impact(control_rate, treatment_rate, total_users, avg_revenue_per_activation=50):
    """
    Annualized revenue impact estimate from activation lift.
    """
    lift_rate = (treatment_rate - control_rate) / 100
    incremental_activations = total_users * lift_rate
    annual_impact = incremental_activations * avg_revenue_per_activation * 12

    return {
        "incremental_activations_monthly": int(incremental_activations),
        "estimated_annual_impact_usd": int(annual_impact),
        "assumption": f"${avg_revenue_per_activation} average revenue per incremental activation"
    }


def run_full_analysis(experiment: dict) -> dict:
    """
    Run complete statistical analysis on an experiment dict.
    """
    results = {}

    results["significance"] = calculate_significance(
        experiment["control_n"],
        experiment["control_rate"],
        experiment["treatment_n"],
        experiment["treatment_rate"]
    )

    results["lift"] = calculate_lift(
        experiment["control_rate"],
        experiment["treatment_rate"]
    )

    results["sample_size"] = validate_sample_size(
        experiment["control_n"],
        experiment["treatment_n"],
        experiment["control_rate"]
    )

    if "guardrail_control" in experiment and "guardrail_treatment" in experiment:
        results["guardrail"] = check_guardrail(
            experiment["guardrail_control"],
            experiment["guardrail_treatment"]
        )

    if "total_users" in experiment:
        results["business_impact"] = estimate_business_impact(
            experiment["control_rate"],
            experiment["treatment_rate"],
            experiment["total_users"]
        )

    return results
