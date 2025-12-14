"""
Comprehensive Report Generator for ViWO Token Economy Simulator.

Generates full reports with executive summaries, risk assessments,
recommendations, and industry benchmarks.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import hashlib
import json


# Industry benchmarks for comparison
INDUSTRY_BENCHMARKS = {
    "profit_margin": {
        "excellent": 70,
        "good": 50,
        "average": 30,
        "poor": 10,
    },
    "recapture_rate": {
        "excellent": 60,
        "good": 40,
        "average": 25,
        "poor": 10,
    },
    "staking_participation": {
        "excellent": 40,
        "good": 25,
        "average": 15,
        "poor": 5,
    },
    "governance_participation": {
        "excellent": 30,
        "good": 20,
        "average": 10,
        "poor": 5,
    },
    "liquidity_ratio": {
        "excellent": 15,
        "good": 10,
        "average": 5,
        "poor": 2,
    },
    "token_velocity": {
        "healthy_min": 0.5,
        "healthy_max": 4.0,
    },
    "gini_coefficient": {
        "excellent": 0.4,
        "good": 0.6,
        "average": 0.75,
        "concentrated": 0.85,
    },
}


def calculate_overall_risk_score(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate aggregated risk scores from all risk-related metrics.
    Returns overall risk score (0-100, lower is better) and breakdown.
    """
    risk_factors = []
    risk_breakdown = {}
    
    # Whale concentration risk
    token_metrics = result.get("tokenMetrics") or result.get("token_metrics") or {}
    whale_analysis = token_metrics.get("whaleAnalysis") or token_metrics.get("whale_analysis") or {}
    if whale_analysis:
        whale_risk = whale_analysis.get("concentrationRiskScore") or whale_analysis.get("concentration_risk_score") or 50
        risk_factors.append(whale_risk * 0.25)  # 25% weight
        risk_breakdown["whaleConcentration"] = {
            "score": whale_risk,
            "level": whale_analysis.get("riskLevel") or whale_analysis.get("risk_level") or "Unknown",
            "weight": 0.25,
        }
    
    # Attack vulnerability
    attack_analysis = token_metrics.get("attackAnalysis") or token_metrics.get("attack_analysis") or {}
    if attack_analysis:
        attack_risk = attack_analysis.get("vulnerabilityScore") or attack_analysis.get("vulnerability_score") or 50
        risk_factors.append(attack_risk * 0.20)  # 20% weight
        risk_breakdown["attackVulnerability"] = {
            "score": attack_risk,
            "level": attack_analysis.get("riskLevel") or attack_analysis.get("risk_level") or "Unknown",
            "weight": 0.20,
        }
    
    # Liquidity risk
    liquidity = result.get("liquidity") or {}
    if liquidity:
        liquidity_health = liquidity.get("healthScore") or liquidity.get("health_score") or 50
        liquidity_risk = 100 - liquidity_health  # Invert since health is good
        risk_factors.append(liquidity_risk * 0.20)  # 20% weight
        risk_breakdown["liquidityRisk"] = {
            "score": liquidity_risk,
            "level": liquidity.get("healthStatus") or liquidity.get("health_status") or "Unknown",
            "weight": 0.20,
        }
    
    # Sustainability risk (runway)
    runway = token_metrics.get("runway") or {}
    if runway:
        runway_health = runway.get("runwayHealth") or runway.get("runway_health") or 50
        sustainability_risk = 100 - runway_health
        risk_factors.append(sustainability_risk * 0.20)  # 20% weight
        risk_breakdown["sustainabilityRisk"] = {
            "score": sustainability_risk,
            "isSustainable": runway.get("isSustainable") or runway.get("is_sustainable") or False,
            "runwayMonths": runway.get("runwayMonths") or runway.get("runway_months") or 0,
            "weight": 0.20,
        }
    
    # Staking health risk
    staking = result.get("staking") or {}
    if staking:
        staking_healthy = staking.get("isHealthy") or staking.get("is_healthy") or False
        staking_risk = 0 if staking_healthy else 60
        risk_factors.append(staking_risk * 0.15)  # 15% weight
        risk_breakdown["stakingRisk"] = {
            "score": staking_risk,
            "status": staking.get("stakingStatus") or staking.get("staking_status") or "Unknown",
            "weight": 0.15,
        }
    
    # Calculate overall
    overall_score = sum(risk_factors) if risk_factors else 50
    
    # Determine risk level
    if overall_score < 20:
        risk_level = "Low"
        risk_color = "emerald"
    elif overall_score < 40:
        risk_level = "Moderate"
        risk_color = "amber"
    elif overall_score < 60:
        risk_level = "Elevated"
        risk_color = "orange"
    else:
        risk_level = "High"
        risk_color = "red"
    
    return {
        "overallRiskScore": round(overall_score, 1),
        "riskLevel": risk_level,
        "riskColor": risk_color,
        "breakdown": risk_breakdown,
    }


def generate_executive_summary(
    result: Dict[str, Any],
    parameters: Dict[str, Any],
    monthly_progression: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate executive summary with key KPIs and investment thesis.
    """
    totals = result.get("totals") or {}
    token_metrics = result.get("tokenMetrics") or result.get("token_metrics") or {}
    recapture = result.get("recapture") or {}
    staking = result.get("staking") or {}
    governance = result.get("governance") or {}
    liquidity = result.get("liquidity") or {}
    starting_users = result.get("startingUsersSummary") or result.get("starting_users_summary") or {}
    
    # Key financial metrics
    revenue = totals.get("revenue") or 0
    profit = totals.get("profit") or 0
    margin = totals.get("margin") or 0
    
    # Token metrics
    overall_health = token_metrics.get("overallHealth") or token_metrics.get("overall_health") or 0
    velocity = token_metrics.get("velocity") or {}
    real_yield = token_metrics.get("realYield") or token_metrics.get("real_yield") or {}
    value_accrual = token_metrics.get("valueAccrual") or token_metrics.get("value_accrual") or {}
    
    # Calculate risk
    risk_assessment = calculate_overall_risk_score(result)
    
    # Identify key strengths
    strengths = []
    if margin > 70:
        strengths.append(f"Excellent profit margin of {margin}%")
    elif margin > 50:
        strengths.append(f"Strong profit margin of {margin}%")
    
    recapture_rate = recapture.get("recaptureRate") or recapture.get("recapture_rate") or 0
    if recapture_rate > 40:
        strengths.append(f"Strong token recapture rate of {recapture_rate}%")
    
    staking_participation = staking.get("participationRate") or staking.get("participation_rate") or 0
    if staking_participation > 20:
        strengths.append(f"Healthy staking participation at {staking_participation}%")
    
    liquidity_ratio = liquidity.get("liquidityRatio") or liquidity.get("liquidity_ratio") or 0
    if liquidity_ratio > 10:
        strengths.append(f"Strong liquidity ratio of {liquidity_ratio}%")
    
    real_yield_annual = real_yield.get("annualRealYield") or real_yield.get("annual_real_yield") or 0
    if real_yield_annual > 20:
        strengths.append(f"Sustainable real yield of {real_yield_annual}% annually")
    
    governance_participation = governance.get("effectiveParticipationRate") or governance.get("effective_participation_rate") or 0
    if governance_participation > 20:
        strengths.append(f"Active governance with {governance_participation}% participation")
    
    # Check organic growth
    organic_growth = result.get("organicGrowth") or result.get("organic_growth") or {}
    if organic_growth.get("enabled"):
        organic_percent = organic_growth.get("organicPercentOfTotal") or organic_growth.get("organic_percent_of_total") or 0
        k_factor = organic_growth.get("effectiveKFactor") or organic_growth.get("effective_k_factor") or 0
        if organic_percent > 20:
            strengths.append(f"Strong organic growth at {organic_percent:.1f}% of total acquisition (K-factor: {k_factor:.2f})")
        elif organic_percent > 10:
            strengths.append(f"Organic growth contributing {organic_percent:.1f}% with K-factor of {k_factor:.2f}")
    
    # Identify key risks
    risks = []
    gini = token_metrics.get("gini") or {}
    gini_value = gini.get("gini") or 0.7
    if gini_value > 0.75:
        risks.append(f"High token concentration (Gini: {gini_value:.2f})")
    
    whale_analysis = token_metrics.get("whaleAnalysis") or token_metrics.get("whale_analysis") or {}
    whale_risk = whale_analysis.get("concentrationRiskScore") or whale_analysis.get("concentration_risk_score") or 0
    if whale_risk > 50:
        risks.append(f"Elevated whale concentration risk ({whale_risk}%)")
    
    attack_analysis = token_metrics.get("attackAnalysis") or token_metrics.get("attack_analysis") or {}
    attack_risk = attack_analysis.get("vulnerabilityScore") or attack_analysis.get("vulnerability_score") or 0
    if attack_risk > 30:
        risks.append(f"Attack vulnerability score of {attack_risk}")
    
    staking_healthy = staking.get("isHealthy") or staking.get("is_healthy") or True
    if not staking_healthy:
        risks.append("Staking participation below target levels")
    
    inflation = token_metrics.get("inflation") or {}
    net_inflation_rate = inflation.get("annualNetInflationRate") or inflation.get("annual_net_inflation_rate") or 0
    if net_inflation_rate > 10:
        risks.append(f"High annual inflation rate of {net_inflation_rate}%")
    
    # Generate investment thesis
    thesis_parts = []
    active_users = starting_users.get("totalActiveUsers") or starting_users.get("total_active_users") or 0
    thesis_parts.append(f"ViWO token economy with {active_users:,} active users")
    
    if margin > 50:
        thesis_parts.append(f"generating ${revenue:,.0f} monthly revenue at {margin}% margin")
    else:
        thesis_parts.append(f"generating ${revenue:,.0f} monthly revenue")
    
    if recapture_rate > 30:
        thesis_parts.append(f"with strong {recapture_rate}% token recapture")
    
    # Add organic growth to thesis if enabled
    if organic_growth.get("enabled"):
        organic_percent = organic_growth.get("organicPercentOfTotal") or organic_growth.get("organic_percent_of_total") or 0
        if organic_percent > 15:
            thesis_parts.append(f"organic growth contributing {organic_percent:.1f}% of user acquisition")
    
    grade = value_accrual.get("grade") or "C"
    thesis_parts.append(f"Value accrual grade: {grade}")
    
    investment_thesis = ". ".join(thesis_parts) + "."
    
    # Monthly progression highlights
    progression_highlights = None
    if monthly_progression:
        monthly_data = monthly_progression.get("monthlyData") or monthly_progression.get("monthly_data") or []
        if monthly_data:
            progression_highlights = {
                "durationMonths": monthly_progression.get("durationMonths") or monthly_progression.get("duration_months") or 60,
                "totalRevenue": monthly_progression.get("totalRevenue") or monthly_progression.get("total_revenue") or 0,
                "totalProfit": monthly_progression.get("totalProfit") or monthly_progression.get("total_profit") or 0,
                "peakActiveUsers": monthly_progression.get("peakActiveUsers") or monthly_progression.get("peak_active_users") or 0,
                "finalActiveUsers": monthly_progression.get("finalActiveUsers") or monthly_progression.get("final_active_users") or 0,
                "monthsToProfitability": monthly_progression.get("monthsToProfitability") or monthly_progression.get("months_to_profitability"),
                "cagrRevenue": monthly_progression.get("cagrRevenue") or monthly_progression.get("cagr_revenue") or 0,
                "cagrUsers": monthly_progression.get("cagrUsers") or monthly_progression.get("cagr_users") or 0,
            }
    
    # Extract LTV/CAC metrics (handle both camelCase and snake_case)
    customer_acquisition = result.get("customerAcquisition") or result.get("customer_acquisition") or {}
    ltv_estimate = customer_acquisition.get("ltvEstimate") or customer_acquisition.get("ltv_estimate") or 0
    # effectiveCAC (uppercase CAC from Pydantic) or effective_cac (snake_case)
    effective_cac = customer_acquisition.get("effectiveCAC") or customer_acquisition.get("effectiveCac") or customer_acquisition.get("effective_cac") or 0
    ltv_cac_ratio = customer_acquisition.get("ltvCacRatio") or customer_acquisition.get("ltv_cac_ratio") or 0
    
    # Add LTV/CAC to strengths if good
    if ltv_cac_ratio >= 5:
        strengths.append(f"Excellent unit economics with {ltv_cac_ratio:.1f}x LTV/CAC ratio")
    elif ltv_cac_ratio >= 3:
        strengths.append(f"Healthy LTV/CAC ratio of {ltv_cac_ratio:.1f}x")
    elif ltv_cac_ratio < 1 and ltv_cac_ratio > 0:
        risks.append(f"Poor unit economics with {ltv_cac_ratio:.2f}x LTV/CAC ratio")
    
    # Extract supply dynamics
    inflation = token_metrics.get("inflation") or {}
    yearly_snapshots = inflation.get("yearlySnapshots") or inflation.get("yearly_snapshots") or []
    
    supply_dynamics_summary = None
    if yearly_snapshots:
        year1 = yearly_snapshots[0] if len(yearly_snapshots) > 0 else {}
        year5 = yearly_snapshots[4] if len(yearly_snapshots) > 4 else {}
        
        year1_rate = year1.get("annualRate") or year1.get("annual_rate") or 0
        year5_rate = year5.get("annualRate") or year5.get("annual_rate") or 0
        year5_deflationary = year5.get("isDeflationary") or year5.get("is_deflationary") or False
        
        supply_dynamics_summary = {
            "year1AnnualRate": year1_rate,
            "year5AnnualRate": year5_rate,
            "year5Status": year5.get("status", "Unknown"),
            "becomesDeflationary": year5_deflationary,
            "journey": f"Year 1: {year1_rate:.1f}% → Year 5: {year5_rate:.1f}%",
        }
        
        # Add to strengths/risks
        if year5_deflationary:
            strengths.append(f"Token becomes deflationary in Year 5 ({year5_rate:.1f}% annual rate)")
        elif year5_rate < 5:
            strengths.append(f"Low supply growth by Year 5 ({year5_rate:.1f}% annual)")
    
    return {
        "generatedAt": datetime.now().isoformat(),
        "activeUsers": active_users,
        "totalMonthlyRevenue": round(revenue, 2),
        "totalMonthlyProfit": round(profit, 2),
        "profitMargin": round(margin, 1),
        "overallHealthScore": round(overall_health, 1),
        "tokenVelocity": round(velocity.get("velocity") or 0, 4),
        "annualRealYield": round(real_yield_annual, 2),
        "valueAccrualGrade": grade,
        "recaptureRate": round(recapture_rate, 1),
        "stakingParticipation": round(staking_participation, 1),
        "governanceParticipation": round(governance_participation, 1),
        # NEW: LTV/CAC metrics
        "ltvCacRatio": round(ltv_cac_ratio, 2),
        "ltv": round(ltv_estimate, 2),
        "cac": round(effective_cac, 2),
        # NEW: Supply dynamics summary
        "supplyDynamics": supply_dynamics_summary,
        "riskLevel": risk_assessment["riskLevel"],
        "riskScore": risk_assessment["overallRiskScore"],
        "keyStrengths": strengths[:6],  # Top 6 strengths
        "keyRisks": risks[:5],  # Top 5 risks
        "investmentThesis": investment_thesis,
        "progressionHighlights": progression_highlights,
    }


def aggregate_recommendations(result: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Aggregate all recommendations from different modules into priority categories.
    """
    critical = []
    high = []
    medium = []
    optimization = []
    
    token_metrics = result.get("tokenMetrics") or result.get("token_metrics") or {}
    
    # Whale analysis recommendations
    whale_analysis = token_metrics.get("whaleAnalysis") or token_metrics.get("whale_analysis") or {}
    whale_recs = whale_analysis.get("recommendations") or []
    for rec in whale_recs:
        if "critical" in rec.lower() or "immediate" in rec.lower():
            critical.append(rec)
        elif "high" in rec.lower() or "priority" in rec.lower():
            high.append(rec)
        else:
            medium.append(rec)
    
    # Attack analysis recommendations
    attack_analysis = token_metrics.get("attackAnalysis") or token_metrics.get("attack_analysis") or {}
    attack_recs = attack_analysis.get("recommendations") or []
    for rec in attack_recs:
        if "critical" in rec.lower() or "🚨" in rec:
            critical.append(rec)
        elif "high" in rec.lower() or "⚡" in rec:
            high.append(rec)
        else:
            medium.append(rec)
    
    # Liquidity farming recommendations
    liq_farming = token_metrics.get("liquidityFarming") or token_metrics.get("liquidity_farming") or {}
    liq_recs = liq_farming.get("recommendations") or []
    for rec in liq_recs:
        optimization.append(rec)
    
    # Game theory recommendations
    game_theory = token_metrics.get("gameTheory") or token_metrics.get("game_theory") or {}
    game_recs = game_theory.get("recommendations") or []
    for rec in game_recs:
        if "✅" in rec:
            optimization.append(rec)
        else:
            medium.append(rec)
    
    # Staking sustainability warnings
    staking = result.get("staking") or {}
    staking_warning = staking.get("sustainabilityWarning") or staking.get("sustainability_warning")
    if staking_warning:
        high.append(staking_warning)
    
    # Add context-based recommendations
    recapture = result.get("recapture") or {}
    recapture_rate = recapture.get("recaptureRate") or recapture.get("recapture_rate") or 0
    if recapture_rate < 30:
        medium.append(f"Consider increasing token recapture mechanisms - current rate is {recapture_rate}%")
    
    governance = result.get("governance") or {}
    gov_health = governance.get("governanceHealthScore") or governance.get("governance_health_score") or 0
    if gov_health < 50:
        medium.append(f"Governance health score is low ({gov_health}%) - consider incentivizing participation")
    
    # Deduplicate
    critical = list(dict.fromkeys(critical))
    high = list(dict.fromkeys(high))
    medium = list(dict.fromkeys(medium))
    optimization = list(dict.fromkeys(optimization))
    
    return {
        "critical": critical,
        "high": high,
        "medium": medium,
        "optimization": optimization,
    }


def generate_benchmarks(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare simulation results against industry benchmarks.
    """
    totals = result.get("totals") or {}
    recapture = result.get("recapture") or {}
    staking = result.get("staking") or {}
    governance = result.get("governance") or {}
    liquidity = result.get("liquidity") or {}
    token_metrics = result.get("tokenMetrics") or result.get("token_metrics") or {}
    gini = token_metrics.get("gini") or {}
    velocity = token_metrics.get("velocity") or {}
    
    def rate_metric(value: float, benchmarks: Dict[str, float], higher_is_better: bool = True) -> str:
        if higher_is_better:
            if value >= benchmarks["excellent"]:
                return "Excellent"
            elif value >= benchmarks["good"]:
                return "Good"
            elif value >= benchmarks["average"]:
                return "Average"
            else:
                return "Below Average"
        else:
            if value <= benchmarks["excellent"]:
                return "Excellent"
            elif value <= benchmarks["good"]:
                return "Good"
            elif value <= benchmarks["average"]:
                return "Average"
            else:
                return "Below Average"
    
    benchmarks_result = {
        "profitMargin": {
            "value": totals.get("margin") or 0,
            "benchmark": INDUSTRY_BENCHMARKS["profit_margin"],
            "rating": rate_metric(totals.get("margin") or 0, INDUSTRY_BENCHMARKS["profit_margin"]),
        },
        "recaptureRate": {
            "value": recapture.get("recaptureRate") or recapture.get("recapture_rate") or 0,
            "benchmark": INDUSTRY_BENCHMARKS["recapture_rate"],
            "rating": rate_metric(
                recapture.get("recaptureRate") or recapture.get("recapture_rate") or 0,
                INDUSTRY_BENCHMARKS["recapture_rate"]
            ),
        },
        "stakingParticipation": {
            "value": staking.get("participationRate") or staking.get("participation_rate") or 0,
            "benchmark": INDUSTRY_BENCHMARKS["staking_participation"],
            "rating": rate_metric(
                staking.get("participationRate") or staking.get("participation_rate") or 0,
                INDUSTRY_BENCHMARKS["staking_participation"]
            ),
        },
        "governanceParticipation": {
            "value": governance.get("effectiveParticipationRate") or governance.get("effective_participation_rate") or 0,
            "benchmark": INDUSTRY_BENCHMARKS["governance_participation"],
            "rating": rate_metric(
                governance.get("effectiveParticipationRate") or governance.get("effective_participation_rate") or 0,
                INDUSTRY_BENCHMARKS["governance_participation"]
            ),
        },
        "liquidityRatio": {
            "value": liquidity.get("liquidityRatio") or liquidity.get("liquidity_ratio") or 0,
            "benchmark": INDUSTRY_BENCHMARKS["liquidity_ratio"],
            "rating": rate_metric(
                liquidity.get("liquidityRatio") or liquidity.get("liquidity_ratio") or 0,
                INDUSTRY_BENCHMARKS["liquidity_ratio"]
            ),
        },
        "giniCoefficient": {
            "value": gini.get("gini") or 0.7,
            "benchmark": INDUSTRY_BENCHMARKS["gini_coefficient"],
            "rating": rate_metric(gini.get("gini") or 0.7, INDUSTRY_BENCHMARKS["gini_coefficient"], higher_is_better=False),
            "interpretation": gini.get("interpretation") or "Concentrated",
        },
        "tokenVelocity": {
            "value": velocity.get("annualizedVelocity") or velocity.get("annualized_velocity") or 0,
            "healthyRange": INDUSTRY_BENCHMARKS["token_velocity"],
            "interpretation": velocity.get("interpretation") or "",
        },
    }
    
    # Calculate overall benchmark score
    ratings = [v.get("rating", "Average") for v in benchmarks_result.values() if "rating" in v]
    rating_scores = {"Excellent": 100, "Good": 75, "Average": 50, "Below Average": 25}
    avg_score = sum(rating_scores.get(r, 50) for r in ratings) / len(ratings) if ratings else 50
    
    benchmarks_result["overallBenchmarkScore"] = round(avg_score, 1)
    
    return benchmarks_result


def extract_future_modules(result: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract future modules results and roadmap.
    Includes VChain, Marketplace, BusinessHub, and CrossPlatform.
    """
    future_modules = {
        "enabled": [],
        "planned": [],
        "modules": {},
    }
    
    # VChain
    vchain = result.get("vchain") or {}
    vchain_enabled = parameters.get("enableVchain") or parameters.get("enable_vchain") or False
    if vchain or vchain_enabled:
        vchain_data = {
            "name": "VChain Cross-Chain Network",
            "enabled": vchain.get("enabled") or vchain_enabled,
            "launched": vchain.get("launched") or False,
            "launchMonth": vchain.get("launchMonth") or vchain.get("launch_month") or 24,
            "monthsActive": vchain.get("monthsActive") or vchain.get("months_active") or 0,
            "revenue": vchain.get("revenue") or 0,
            "profit": vchain.get("profit") or 0,
            "margin": vchain.get("margin") or 0,
            "description": "Cross-chain bridge and transaction network with enterprise API",
            "keyMetrics": {
                "txFeeRevenue": vchain.get("txFeeRevenue") or vchain.get("tx_fee_revenue") or 0,
                "bridgeFeeRevenue": vchain.get("bridgeFeeRevenue") or vchain.get("bridge_fee_revenue") or 0,
                "enterpriseApiRevenue": vchain.get("enterpriseApiRevenue") or vchain.get("enterprise_api_revenue") or 0,
                "validatorsActive": vchain.get("validatorsActive") or vchain.get("validators_active") or 0,
                "totalValidatorStake": vchain.get("totalValidatorStake") or vchain.get("total_validator_stake") or 0,
            },
        }
        future_modules["modules"]["vchain"] = vchain_data
        if vchain_data["enabled"]:
            future_modules["enabled"].append("VChain")
        else:
            future_modules["planned"].append({"name": "VChain", "launchMonth": vchain_data["launchMonth"]})
    
    # Marketplace
    marketplace = result.get("marketplace") or {}
    marketplace_enabled = parameters.get("enableMarketplace") or parameters.get("enable_marketplace") or False
    if marketplace or marketplace_enabled:
        marketplace_data = {
            "name": "ViWO Marketplace",
            "enabled": marketplace.get("enabled") or marketplace_enabled,
            "launched": marketplace.get("launched") or False,
            "launchMonth": marketplace.get("launchMonth") or marketplace.get("launch_month") or 18,
            "monthsActive": marketplace.get("monthsActive") or marketplace.get("months_active") or 0,
            "revenue": marketplace.get("revenue") or 0,
            "profit": marketplace.get("profit") or 0,
            "margin": marketplace.get("margin") or 0,
            "description": "Physical and digital goods marketplace with NFT support",
            "keyMetrics": {
                "monthlyGmv": marketplace.get("monthlyGmv") or marketplace.get("monthly_gmv") or 0,
                "activeSellers": marketplace.get("activeSellers") or marketplace.get("active_sellers") or 0,
                "commissionRevenue": marketplace.get("commissionRevenue") or marketplace.get("commission_revenue") or 0,
            },
        }
        future_modules["modules"]["marketplace"] = marketplace_data
        if marketplace_data["enabled"]:
            future_modules["enabled"].append("Marketplace")
        else:
            future_modules["planned"].append({"name": "Marketplace", "launchMonth": marketplace_data["launchMonth"]})
    
    # Business Hub
    business_hub = result.get("businessHub") or result.get("business_hub") or {}
    business_hub_enabled = parameters.get("enableBusinessHub") or parameters.get("enable_business_hub") or False
    if business_hub or business_hub_enabled:
        bh_data = {
            "name": "Business Hub",
            "enabled": business_hub.get("enabled") or business_hub_enabled,
            "launched": business_hub.get("launched") or False,
            "launchMonth": business_hub.get("launchMonth") or business_hub.get("launch_month") or 21,
            "monthsActive": business_hub.get("monthsActive") or business_hub.get("months_active") or 0,
            "revenue": business_hub.get("revenue") or 0,
            "profit": business_hub.get("profit") or 0,
            "margin": business_hub.get("margin") or 0,
            "description": "Freelancer platform, startup launchpad, and business tools",
            "keyMetrics": {
                "freelancerRevenue": business_hub.get("freelancerRevenue") or business_hub.get("freelancer_revenue") or 0,
                "startupRevenue": business_hub.get("startupRevenue") or business_hub.get("startup_revenue") or 0,
                "fundingRevenue": business_hub.get("fundingRevenue") or business_hub.get("funding_revenue") or 0,
                "activeFreelancers": business_hub.get("activeFreelancers") or business_hub.get("active_freelancers") or 0,
            },
        }
        future_modules["modules"]["businessHub"] = bh_data
        if bh_data["enabled"]:
            future_modules["enabled"].append("Business Hub")
        else:
            future_modules["planned"].append({"name": "Business Hub", "launchMonth": bh_data["launchMonth"]})
    
    # Cross-Platform
    cross_platform = result.get("crossPlatform") or result.get("cross_platform") or {}
    cross_platform_enabled = parameters.get("enableCrossPlatform") or parameters.get("enable_cross_platform") or False
    if cross_platform or cross_platform_enabled:
        cp_data = {
            "name": "Cross-Platform Content Sharing",
            "enabled": cross_platform.get("enabled") or cross_platform_enabled,
            "launched": cross_platform.get("launched") or False,
            "launchMonth": cross_platform.get("launchMonth") or cross_platform.get("launch_month") or 15,
            "monthsActive": cross_platform.get("monthsActive") or cross_platform.get("months_active") or 0,
            "revenue": cross_platform.get("revenue") or 0,
            "profit": cross_platform.get("profit") or 0,
            "margin": cross_platform.get("margin") or 0,
            "description": "Cross-platform content sharing, account renting, and analytics",
            "keyMetrics": {
                "subscriptionRevenue": cross_platform.get("subscriptionRevenue") or cross_platform.get("subscription_revenue") or 0,
                "rentalRevenue": cross_platform.get("rentalRevenue") or cross_platform.get("rental_revenue") or 0,
                "totalSubscribers": cross_platform.get("totalSubscribers") or cross_platform.get("total_subscribers") or 0,
            },
        }
        future_modules["modules"]["crossPlatform"] = cp_data
        if cp_data["enabled"]:
            future_modules["enabled"].append("Cross-Platform")
        else:
            future_modules["planned"].append({"name": "Cross-Platform", "launchMonth": cp_data["launchMonth"]})
    
    # Calculate total future revenue
    total_future_revenue = sum(m.get("revenue", 0) for m in future_modules["modules"].values())
    total_future_profit = sum(m.get("profit", 0) for m in future_modules["modules"].values())
    
    future_modules["summary"] = {
        "totalModulesEnabled": len(future_modules["enabled"]),
        "totalModulesPlanned": len(future_modules["planned"]),
        "totalFutureRevenue": total_future_revenue,
        "totalFutureProfit": total_future_profit,
        "roadmap": sorted(future_modules["planned"], key=lambda x: x["launchMonth"]),
    }
    
    return future_modules


def calculate_5_year_projections(
    result: Dict[str, Any],
    parameters: Dict[str, Any],
    monthly_progression: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate or extract 5-year projections.
    
    Priority:
    1. Use result.five_year_projections if available (backend-calculated, matches UI)
    2. Use monthly_progression if available
    3. Fall back to simple estimation
    """
    # Check if backend already calculated projections
    if isinstance(result, dict) and "fiveYearProjections" in result:
        five_year = result["fiveYearProjections"]
        if five_year and five_year.get("available"):
            return five_year
    
    # Check if result object has five_year_projections attribute
    if hasattr(result, 'five_year_projections') and result.five_year_projections:
        # Convert Pydantic model to dict
        if hasattr(result.five_year_projections, 'dict'):
            return result.five_year_projections.dict()
        elif hasattr(result.five_year_projections, 'model_dump'):
            return result.five_year_projections.model_dump()
    
    # Fall back to old logic
    projections = {
        "available": False,
        "source": "estimated",
        "years": [],
        "summary": {},
    }
    
    # If we have monthly progression, extract 5-year data from it
    if monthly_progression:
        monthly_data = monthly_progression.get("monthlyData") or monthly_progression.get("monthly_data") or []
        if len(monthly_data) >= 12:
            projections["available"] = True
            projections["source"] = "monthly_progression"
            
            # Group by year
            for year in range(1, 6):
                start_month = (year - 1) * 12
                end_month = year * 12
                year_data = monthly_data[start_month:end_month] if len(monthly_data) > start_month else []
                
                if year_data:
                    year_revenue = sum(m.get("revenue", 0) for m in year_data)
                    year_profit = sum(m.get("profit", 0) for m in year_data)
                    start_users = year_data[0].get("activeUsers") or year_data[0].get("active_users") or 0
                    end_users = year_data[-1].get("activeUsers") or year_data[-1].get("active_users") or 0
                    
                    projections["years"].append({
                        "year": year,
                        "startMonth": start_month + 1,
                        "endMonth": min(end_month, len(monthly_data)),
                        "startUsers": start_users,
                        "endUsers": end_users,
                        "totalRevenue": round(year_revenue, 2),
                        "totalProfit": round(year_profit, 2),
                        "avgMargin": round((year_profit / year_revenue * 100) if year_revenue > 0 else 0, 1),
                    })
            
            # Summary from progression
            projections["summary"] = {
                "totalRevenue": monthly_progression.get("totalRevenue") or monthly_progression.get("total_revenue") or 0,
                "totalProfit": monthly_progression.get("totalProfit") or monthly_progression.get("total_profit") or 0,
                "peakActiveUsers": monthly_progression.get("peakActiveUsers") or monthly_progression.get("peak_active_users") or 0,
                "finalActiveUsers": monthly_progression.get("finalActiveUsers") or monthly_progression.get("final_active_users") or 0,
                "cagrUsers": monthly_progression.get("cagrUsers") or monthly_progression.get("cagr_users") or 0,
                "cagrRevenue": monthly_progression.get("cagrRevenue") or monthly_progression.get("cagr_revenue") or 0,
                "monthsToProfitability": monthly_progression.get("monthsToProfitability") or monthly_progression.get("months_to_profitability"),
                "finalTokenPrice": monthly_progression.get("tokenPriceFinal") or monthly_progression.get("token_price_final") or parameters.get("tokenPrice", 0.03),
            }
    
    # If no monthly progression, estimate from base result
    if not projections["available"]:
        totals = result.get("totals") or {}
        starting_users = result.get("startingUsersSummary", {}).get("totalActiveUsers") or \
                        result.get("starting_users_summary", {}).get("total_active_users") or \
                        result.get("customerAcquisition", {}).get("totalUsers") or \
                        result.get("customer_acquisition", {}).get("total_users") or 0
        
        base_revenue = totals.get("revenue") or 0
        base_profit = totals.get("profit") or 0
        base_margin = totals.get("margin") or 0
        token_price = parameters.get("tokenPrice") or parameters.get("token_price") or 0.03
        
        projections["available"] = True
        projections["source"] = "estimated_from_base"
        
        # Growth assumptions by year (conservative estimates)
        growth_rates = [1.0, 2.5, 4.0, 5.5, 7.0]  # Cumulative multipliers
        user_growth = [1.0, 2.0, 3.2, 4.5, 6.0]  # User growth multipliers
        price_multipliers = [1.0, 1.5, 2.0, 2.8, 4.0]  # Token price multipliers
        
        for year in range(1, 6):
            year_revenue = base_revenue * 12 * growth_rates[year - 1]
            year_profit = base_profit * 12 * growth_rates[year - 1]
            year_users = int(starting_users * user_growth[year - 1])
            
            projections["years"].append({
                "year": year,
                "startMonth": (year - 1) * 12 + 1,
                "endMonth": year * 12,
                "startUsers": int(starting_users * (user_growth[year - 1] if year == 1 else user_growth[year - 2])),
                "endUsers": year_users,
                "totalRevenue": round(year_revenue, 2),
                "totalProfit": round(year_profit, 2),
                "avgMargin": round(base_margin, 1),
                "estimatedTokenPrice": round(token_price * price_multipliers[year - 1], 4),
            })
        
        # Summary
        total_5y_revenue = sum(y["totalRevenue"] for y in projections["years"])
        total_5y_profit = sum(y["totalProfit"] for y in projections["years"])
        
        projections["summary"] = {
            "totalRevenue": round(total_5y_revenue, 2),
            "totalProfit": round(total_5y_profit, 2),
            "peakActiveUsers": projections["years"][-1]["endUsers"] if projections["years"] else 0,
            "finalActiveUsers": projections["years"][-1]["endUsers"] if projections["years"] else 0,
            "estimatedFinalTokenPrice": round(token_price * price_multipliers[-1], 4),
            "note": "These are estimates based on conservative growth assumptions. Run 60-month progression for accurate projections.",
        }
    
    return projections


def extract_financial_summary(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract financial totals and summary metrics.
    """
    totals = result.get("totals") or {}
    
    return {
        "monthly": {
            "revenue": totals.get("revenue", 0),
            "costs": totals.get("costs", 0),
            "profit": totals.get("profit", 0),
            "margin": totals.get("margin", 0),
        },
        "annualized": {
            "revenue": round(totals.get("revenue", 0) * 12, 2),
            "costs": round(totals.get("costs", 0) * 12, 2),
            "profit": round(totals.get("profit", 0) * 12, 2),
            "margin": totals.get("margin", 0),
        },
        "breakdown": totals.get("breakdown", {}),
        "profitabilityStatus": "Profitable" if totals.get("profit", 0) > 0 else "Not Profitable",
        "marginHealth": "Excellent" if totals.get("margin", 0) > 70 else "Good" if totals.get("margin", 0) > 50 else "Moderate" if totals.get("margin", 0) > 30 else "Low",
    }


def extract_core_modules(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract core revenue module breakdowns.
    
    Covers the 4 main revenue-generating modules:
    - Identity: KYC/verification fees
    - Content: Creator tips, subscriptions
    - Advertising: Ad revenue
    - Exchange: Crypto trading fees
    """
    identity = result.get("identity") or {}
    content = result.get("content") or {}
    advertising = result.get("advertising") or {}
    exchange = result.get("exchange") or {}
    platform_fees = result.get("platformFees") or result.get("platform_fees") or {}
    
    # Calculate totals
    total_core_revenue = sum([
        identity.get("revenue", 0),
        content.get("revenue", 0),
        advertising.get("revenue", 0),
        exchange.get("revenue", 0),
        platform_fees.get("totalFeeRevenue") or platform_fees.get("total_fee_revenue") or 0,
    ])
    
    return {
        "identity": {
            "name": "Identity Verification",
            "revenue": identity.get("revenue", 0),
            "costs": identity.get("costs", 0),
            "profit": identity.get("profit", 0),
            "margin": identity.get("margin", 0),
            "revenuePercent": round((identity.get("revenue", 0) / total_core_revenue * 100) if total_core_revenue > 0 else 0, 1),
            "breakdown": identity.get("breakdown", {}),
        },
        "content": {
            "name": "Content & Tipping",
            "revenue": content.get("revenue", 0),
            "costs": content.get("costs", 0),
            "profit": content.get("profit", 0),
            "margin": content.get("margin", 0),
            "revenuePercent": round((content.get("revenue", 0) / total_core_revenue * 100) if total_core_revenue > 0 else 0, 1),
            "breakdown": content.get("breakdown", {}),
        },
        "advertising": {
            "name": "Advertising",
            "revenue": advertising.get("revenue", 0),
            "costs": advertising.get("costs", 0),
            "profit": advertising.get("profit", 0),
            "margin": advertising.get("margin", 0),
            "revenuePercent": round((advertising.get("revenue", 0) / total_core_revenue * 100) if total_core_revenue > 0 else 0, 1),
            "breakdown": advertising.get("breakdown", {}),
        },
        "exchange": {
            "name": "Exchange/Wallet",
            "revenue": exchange.get("revenue", 0),
            "costs": exchange.get("costs", 0),
            "profit": exchange.get("profit", 0),
            "margin": exchange.get("margin", 0),
            "revenuePercent": round((exchange.get("revenue", 0) / total_core_revenue * 100) if total_core_revenue > 0 else 0, 1),
            "breakdown": exchange.get("breakdown", {}),
        },
        "platformFees": {
            "name": "Platform Transaction Fees (5%)",
            "totalFeeRevenue": platform_fees.get("totalFeeRevenue") or platform_fees.get("total_fee_revenue") or 0,
            "feeRate": platform_fees.get("feeRate") or platform_fees.get("fee_rate") or 0.05,
            "transactionVolume": platform_fees.get("transactionVolume") or platform_fees.get("transaction_volume") or 0,
            "revenuePercent": round(((platform_fees.get("totalFeeRevenue") or platform_fees.get("total_fee_revenue") or 0) / total_core_revenue * 100) if total_core_revenue > 0 else 0, 1),
        },
        "summary": {
            "totalCoreRevenue": round(total_core_revenue, 2),
            "moduleCount": 5,
            "topModule": max(
                [("Identity", identity.get("revenue", 0)),
                 ("Content", content.get("revenue", 0)),
                 ("Advertising", advertising.get("revenue", 0)),
                 ("Exchange", exchange.get("revenue", 0)),
                 ("Platform Fees", platform_fees.get("totalFeeRevenue") or platform_fees.get("total_fee_revenue") or 0)],
                key=lambda x: x[1]
            )[0],
        },
    }


def extract_customer_acquisition(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract customer acquisition metrics.
    
    Includes:
    - CAC (Customer Acquisition Cost)
    - LTV (Lifetime Value) - calculated from 5-year simulation
    - LTV/CAC Ratio
    - Retention and churn metrics
    - User growth data
    - 5-year acquisition economics
    """
    ca = result.get("customerAcquisition") or result.get("customer_acquisition") or {}
    starting_users = result.get("startingUsersSummary") or result.get("starting_users_summary") or {}
    
    # Get organic data if available
    organic = result.get("organicGrowth") or result.get("organic_growth") or {}
    organic_users = ca.get("organicUsers") or ca.get("organic_users") or 0
    total_with_organic = ca.get("totalUsersWithOrganic") or ca.get("total_users_with_organic") or ca.get("totalUsers") or ca.get("total_users") or 0
    
    # Get new LTV/CAC metrics (calculated from 5-year simulation)
    # Handle both camelCase and snake_case field names from Pydantic serialization
    ltv_estimate = ca.get("ltvEstimate") or ca.get("ltv_estimate") or ca.get("ltv") or 0
    ltv_cac_ratio = ca.get("ltvCacRatio") or ca.get("ltv_cac_ratio") or 0
    payback_months = ca.get("paybackMonths") or ca.get("payback_months") or 0
    # effectiveCAC (uppercase from Pydantic) or effectiveCac or effective_cac
    effective_cac = ca.get("effectiveCAC") or ca.get("effectiveCac") or ca.get("effective_cac") or ca.get("cac") or 0
    
    # Determine LTV/CAC health status
    if ltv_cac_ratio >= 5:
        ltv_cac_health = "Excellent"
        ltv_cac_interpretation = "Strong unit economics - high profitability per user"
    elif ltv_cac_ratio >= 3:
        ltv_cac_health = "Good"
        ltv_cac_interpretation = "Healthy unit economics - sustainable acquisition"
    elif ltv_cac_ratio >= 1:
        ltv_cac_health = "Moderate"
        ltv_cac_interpretation = "Break-even or slight profit per user"
    else:
        ltv_cac_health = "Poor"
        ltv_cac_interpretation = "Losing money on each user acquired"
    
    return {
        "metrics": {
            "totalUsers": ca.get("totalUsers") or ca.get("total_users") or 0,
            "totalUsersWithOrganic": total_with_organic,
            "organicUsers": organic_users,
            "organicPercent": ca.get("organicPercent") or ca.get("organic_percent") or 0,
            "activeUsers": ca.get("activeUsers") or ca.get("active_users") or 0,
            "monthlyChurn": ca.get("monthlyChurn") or ca.get("monthly_churn") or 0,
            "retentionRate": ca.get("retentionRate") or ca.get("retention_rate") or 0,
        },
        # Enhanced LTV/CAC economics (calculated from 5-year simulation)
        "economics": {
            "cac": ca.get("cac") or 0,
            "effectiveCac": round(effective_cac, 2),
            "ltv": round(ltv_estimate, 2),
            "ltvCacRatio": round(ltv_cac_ratio, 2),
            "ltvCacHealth": ltv_cac_health,
            "ltvCacInterpretation": ltv_cac_interpretation,
            "paybackMonths": round(payback_months, 1),
            "monthlyMarketingSpend": ca.get("monthlyMarketingSpend") or ca.get("monthly_marketing_spend") or 0,
            "calculationBasis": "5-year simulation (total revenue / final users)",
        },
        # 5-year unit economics summary
        "fiveYearUnitEconomics": {
            "ltv": round(ltv_estimate, 2),
            "cac": round(effective_cac, 2),
            "ltvCacRatio": round(ltv_cac_ratio, 2),
            "profitPerUser": round(ltv_estimate - effective_cac, 2) if ltv_estimate and effective_cac else 0,
            "roiPerUser": round((ltv_estimate / effective_cac - 1) * 100, 1) if effective_cac > 0 else 0,
            "isProfitable": ltv_estimate > effective_cac if ltv_estimate and effective_cac else False,
        },
        "startingUsers": {
            "waitlistSize": starting_users.get("waitlistSize") or starting_users.get("waitlist_size") or 0,
            "convertedUsers": starting_users.get("convertedUsers") or starting_users.get("converted_users") or 0,
            "conversionRate": starting_users.get("conversionRate") or starting_users.get("conversion_rate") or 0,
            "totalActiveUsers": starting_users.get("totalActiveUsers") or starting_users.get("total_active_users") or 0,
            "fomoMultiplier": starting_users.get("fomoMultiplier") or starting_users.get("fomo_multiplier") or 1.0,
        },
        "benchmarks": {
            "targetLtvCacRatio": "3:1 or higher is healthy",
            "excellentLtvCacRatio": "5:1+ indicates strong unit economics",
            "industryAvgCac": "$5-15 for consumer apps, $50-100 for fintech",
            "healthyRetention": "40-60% month-over-month for social apps",
            "targetPaybackMonths": "< 12 months for healthy SaaS/consumer apps",
        },
    }


def extract_prelaunch_modules(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract pre-launch module data.
    
    Covers:
    - Referral program metrics
    - Points system distribution  
    - Gasless onboarding costs
    """
    prelaunch = result.get("prelaunch") or {}
    
    if not prelaunch:
        return {
            "enabled": False,
            "summary": "No pre-launch modules active in this simulation.",
        }
    
    referral = prelaunch.get("referral") or {}
    points = prelaunch.get("points") or {}
    gasless = prelaunch.get("gasless") or {}
    
    return {
        "enabled": True,
        "referral": {
            "enabled": bool(referral),
            "totalUsers": referral.get("totalUsers") or referral.get("total_users") or 0,
            "usersWithReferrals": referral.get("usersWithReferrals") or referral.get("users_with_referrals") or 0,
            "totalReferrals": referral.get("totalReferrals") or referral.get("total_referrals") or 0,
            "qualifiedReferrals": referral.get("qualifiedReferrals") or referral.get("qualified_referrals") or 0,
            "bonusDistributedVcoin": referral.get("bonusDistributedVcoin") or referral.get("bonus_distributed_vcoin") or 0,
            "bonusDistributedUsd": referral.get("bonusDistributedUsd") or referral.get("bonus_distributed_usd") or 0,
            "viralCoefficient": referral.get("viralCoefficient") or referral.get("viral_coefficient") or 0,
            "effectiveReferralRate": referral.get("effectiveReferralRate") or referral.get("effective_referral_rate") or 0,
            "monthlyCostUsd": referral.get("monthlyReferralCostUsd") or referral.get("monthly_referral_cost_usd") or 0,
            "suspectedSybilReferrals": referral.get("suspectedSybilReferrals") or referral.get("suspected_sybil_referrals") or 0,
            "tierDistribution": referral.get("referralsByTier") or referral.get("referrals_by_tier") or {},
        },
        "points": {
            "enabled": bool(points),
            "pointsPoolTokens": points.get("pointsPoolTokens") or points.get("points_pool_tokens") or 0,
            "pointsPoolPercent": points.get("pointsPoolPercent") or points.get("points_pool_percent") or 0,
            "waitlistUsers": points.get("waitlistUsers") or points.get("waitlist_users") or 0,
            "participatingUsers": points.get("participatingUsers") or points.get("participating_users") or 0,
            "participationRate": points.get("participationRate") or points.get("participation_rate") or 0,
            "totalPointsDistributed": points.get("totalPointsDistributed") or points.get("total_points_distributed") or 0,
            "avgPointsPerUser": points.get("avgPointsPerUser") or points.get("avg_points_per_user") or 0,
            "tokensPerPoint": points.get("tokensPerPoint") or points.get("tokens_per_point") or 0,
            "avgTokensPerUser": points.get("avgTokensPerUser") or points.get("avg_tokens_per_user") or 0,
            "suspectedSybilUsers": points.get("suspectedSybilUsers") or points.get("suspected_sybil_users") or 0,
            "segmentBreakdown": points.get("usersBySegment") or points.get("users_by_segment") or {},
        },
        "gasless": {
            "enabled": bool(gasless),
            "totalUsers": gasless.get("totalUsers") or gasless.get("total_users") or 0,
            "newUsers": gasless.get("newUsers") or gasless.get("new_users") or 0,
            "totalSponsoredTransactions": gasless.get("totalSponsoredTransactions") or gasless.get("total_sponsored_transactions") or 0,
            "avgTransactionsPerUser": gasless.get("avgTransactionsPerUser") or gasless.get("avg_transactions_per_user") or 0,
            "totalSponsorshipCostUsd": gasless.get("totalSponsorshipCostUsd") or gasless.get("total_sponsorship_cost_usd") or 0,
            "avgCostPerUserUsd": gasless.get("avgCostPerUserUsd") or gasless.get("avg_cost_per_user_usd") or 0,
            "costPerTransactionUsd": gasless.get("costPerTransactionUsd") or gasless.get("cost_per_transaction_usd") or 0,
            "monthlyBudgetUsd": gasless.get("monthlySponsorshipBudgetUsd") or gasless.get("monthly_sponsorship_budget_usd") or 0,
            "budgetUtilization": gasless.get("budgetUtilization") or gasless.get("budget_utilization") or 0,
        },
        "summary": {
            "totalPrelaunchCostUsd": prelaunch.get("totalPrelaunchCostUsd") or prelaunch.get("total_prelaunch_cost_usd") or 0,
            "totalPrelaunchCostVcoin": prelaunch.get("totalPrelaunchCostVcoin") or prelaunch.get("total_prelaunch_cost_vcoin") or 0,
            "pointsTokensAllocated": prelaunch.get("pointsTokensAllocated") or prelaunch.get("points_tokens_allocated") or 0,
            "referralBonusDistributed": prelaunch.get("referralBonusDistributed") or prelaunch.get("referral_bonus_distributed") or 0,
            "referralUsersAcquired": prelaunch.get("referralUsersAcquired") or prelaunch.get("referral_users_acquired") or 0,
        },
    }


def extract_sensitivity_analysis(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract sensitivity and stress test analysis.
    """
    sensitivity = result.get("sensitivity") or {}
    
    if not sensitivity:
        return {
            "available": False,
            "summary": "Sensitivity analysis was not run for this simulation.",
        }
    
    stress_tests = sensitivity.get("stressTests") or sensitivity.get("stress_tests") or {}
    
    # Extract stress test scenarios
    scenarios = []
    for key, test in stress_tests.items():
        scenarios.append({
            "scenario": test.get("scenario") or key,
            "scenarioName": test.get("scenarioName") or test.get("scenario_name") or key,
            "description": test.get("description", ""),
            "immediateImpact": test.get("immediateImpact") or test.get("immediate_impact") or {},
            "maxDrawdownPercent": test.get("maxDrawdownPercent") or test.get("max_drawdown_percent") or {},
            "recoveryMonths": test.get("recoveryMonths") or test.get("recovery_months") or 0,
            "permanentImpactPercent": test.get("permanentImpactPercent") or test.get("permanent_impact_percent") or 0,
            "totalRevenueLoss": test.get("totalRevenueLoss") or test.get("total_revenue_loss") or 0,
        })
    
    return {
        "available": True,
        "stressTests": scenarios,
        "worstScenario": sensitivity.get("worstScenario") or sensitivity.get("worst_scenario") or "",
        "leastSevereScenario": sensitivity.get("leastSevereScenario") or sensitivity.get("least_severe_scenario") or "",
        "monteCarloRange": {
            "p5": sensitivity.get("monteCarloP5") or sensitivity.get("monte_carlo_p5") or 0,
            "p50": sensitivity.get("monteCarloP50") or sensitivity.get("monte_carlo_p50") or 0,
            "p95": sensitivity.get("monteCarloP95") or sensitivity.get("monte_carlo_p95") or 0,
        },
        "summary": f"Analyzed {len(scenarios)} stress scenarios. Worst case: {sensitivity.get('worstScenario') or sensitivity.get('worst_scenario') or 'N/A'}",
    }


def extract_staking_governance(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract detailed staking and governance metrics.
    """
    staking = result.get("staking") or {}
    governance = result.get("governance") or {}
    liquidity = result.get("liquidity") or {}
    
    return {
        "staking": {
            "enabled": bool(staking),
            "revenue": staking.get("revenue", 0),
            "costs": staking.get("costs", 0),
            "profit": staking.get("profit", 0),
            "margin": staking.get("margin", 0),
            "totalStaked": staking.get("totalStaked") or staking.get("total_staked") or 0,
            "totalStakedUsd": staking.get("totalStakedUsd") or staking.get("total_staked_usd") or 0,
            "participationRate": staking.get("participationRate") or staking.get("participation_rate") or 0,
            "avgStakeAmount": staking.get("avgStakeAmount") or staking.get("avg_stake_amount") or 0,
            "baseApr": staking.get("baseApr") or staking.get("base_apr") or 0,
            "effectiveApr": staking.get("effectiveApr") or staking.get("effective_apr") or 0,
            "totalRewardsDistributed": staking.get("totalRewardsDistributed") or staking.get("total_rewards_distributed") or 0,
            "isHealthy": staking.get("isHealthy") or staking.get("is_healthy") or False,
            "stakingStatus": staking.get("stakingStatus") or staking.get("staking_status") or "Unknown",
            "sustainabilityWarning": staking.get("sustainabilityWarning") or staking.get("sustainability_warning"),
            "tierBreakdown": staking.get("tierBreakdown") or staking.get("tier_breakdown") or {},
        },
        "governance": {
            "enabled": bool(governance),
            "totalVotingPower": governance.get("totalVotingPower") or governance.get("total_voting_power") or 0,
            "totalDelegated": governance.get("totalDelegated") or governance.get("total_delegated") or 0,
            "delegationRate": governance.get("delegationRate") or governance.get("delegation_rate") or 0,
            "effectiveParticipationRate": governance.get("effectiveParticipationRate") or governance.get("effective_participation_rate") or 0,
            "quorumReached": governance.get("quorumReached") or governance.get("quorum_reached") or False,
            "quorumPercent": governance.get("quorumPercent") or governance.get("quorum_percent") or 0,
            "governanceHealthScore": governance.get("governanceHealthScore") or governance.get("governance_health_score") or 0,
            "activeVoters": governance.get("activeVoters") or governance.get("active_voters") or 0,
            "proposalsPerMonth": governance.get("proposalsPerMonth") or governance.get("proposals_per_month") or 0,
        },
        "liquidity": {
            "enabled": bool(liquidity),
            "initialLiquidity": liquidity.get("initialLiquidity") or liquidity.get("initial_liquidity") or 0,
            "protocolOwnedPercent": liquidity.get("protocolOwnedPercent") or liquidity.get("protocol_owned_percent") or 0,
            "protocolOwnedUsd": liquidity.get("protocolOwnedUsd") or liquidity.get("protocol_owned_usd") or 0,
            "communityLpUsd": liquidity.get("communityLpUsd") or liquidity.get("community_lp_usd") or 0,
            "liquidityRatio": liquidity.get("liquidityRatio") or liquidity.get("liquidity_ratio") or 0,
            "healthScore": liquidity.get("healthScore") or liquidity.get("health_score") or 0,
            "healthStatus": liquidity.get("healthStatus") or liquidity.get("health_status") or "Unknown",
            "slippageData": {
                "1k": liquidity.get("slippage1k") or liquidity.get("slippage_1k") or 0,
                "5k": liquidity.get("slippage5k") or liquidity.get("slippage_5k") or 0,
                "10k": liquidity.get("slippage10k") or liquidity.get("slippage_10k") or 0,
                "50k": liquidity.get("slippage50k") or liquidity.get("slippage_50k") or 0,
                "100k": liquidity.get("slippage100k") or liquidity.get("slippage_100k") or 0,
            },
            "buyPressureUsd": liquidity.get("buyPressureUsd") or liquidity.get("buy_pressure_usd") or 0,
            "sellPressureUsd": liquidity.get("sellPressureUsd") or liquidity.get("sell_pressure_usd") or 0,
            "netPressureUsd": liquidity.get("netPressureUsd") or liquidity.get("net_pressure_usd") or 0,
        },
    }


def extract_organic_growth(
    result: Dict[str, Any],
    monthly_progression: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract organic growth metrics for the full report.
    
    Shows the impact of organic user acquisition on growth and revenue:
    - Word-of-mouth referrals
    - App store organic discovery  
    - Network effects
    - Social media sharing
    - Content virality
    """
    organic = result.get("organicGrowth") or result.get("organic_growth") or {}
    
    # Check if organic growth was enabled
    if not organic or not organic.get("enabled"):
        return {
            "enabled": False,
            "summary": "Organic growth module was not enabled for this simulation.",
            "impact": None,
        }
    
    # Calculate impact metrics
    total_organic = organic.get("totalOrganicUsers") or organic.get("total_organic_users") or 0
    organic_percent = organic.get("organicPercentOfTotal") or organic.get("organic_percent_of_total") or 0
    k_factor = organic.get("effectiveKFactor") or organic.get("effective_k_factor") or 0
    
    # Get customer acquisition data for comparison
    customer_acquisition = result.get("customerAcquisition") or result.get("customer_acquisition") or {}
    total_users = customer_acquisition.get("totalUsersWithOrganic") or customer_acquisition.get("total_users_with_organic") or \
                  customer_acquisition.get("totalUsers") or customer_acquisition.get("total_users") or 0
    paid_users = customer_acquisition.get("totalUsers") or customer_acquisition.get("total_users") or 0
    organic_users = customer_acquisition.get("organicUsers") or customer_acquisition.get("organic_users") or 0
    
    # Calculate revenue impact (organic users contribute to revenue)
    totals = result.get("totals") or {}
    total_revenue = totals.get("revenue") or 0
    
    # Estimate organic contribution to revenue
    if total_users > 0 and organic_users > 0:
        organic_revenue_contribution = (organic_users / total_users) * total_revenue
    else:
        organic_revenue_contribution = 0
    
    # Monthly progression organic data
    organic_progression = None
    if monthly_progression:
        monthly_data = monthly_progression.get("monthlyData") or monthly_progression.get("monthly_data") or []
        organic_by_month = []
        cumulative_organic = 0
        
        for month_data in monthly_data:
            month_organic = month_data.get("organicUsersAcquired") or month_data.get("organic_users_acquired") or 0
            cumulative_organic += month_organic
            organic_by_month.append({
                "month": month_data.get("month", 0),
                "organicUsers": month_organic,
                "cumulativeOrganic": cumulative_organic,
                "organicPercent": month_data.get("organicPercent") or month_data.get("organic_percent") or 0,
            })
        
        if organic_by_month:
            # Calculate year-by-year organic growth
            yearly_organic = []
            for year in range(1, 6):
                start_idx = (year - 1) * 12
                end_idx = year * 12
                year_data = organic_by_month[start_idx:end_idx] if len(organic_by_month) > start_idx else []
                
                if year_data:
                    year_organic = sum(m["organicUsers"] for m in year_data)
                    avg_organic_percent = sum(m["organicPercent"] for m in year_data) / len(year_data)
                    yearly_organic.append({
                        "year": year,
                        "organicUsers": year_organic,
                        "avgOrganicPercent": round(avg_organic_percent, 1),
                    })
            
            organic_progression = {
                "monthlyBreakdown": organic_by_month[:12] if len(organic_by_month) > 12 else organic_by_month,  # First year sample
                "yearlyTotals": yearly_organic,
                "totalOrganicOverPeriod": cumulative_organic,
                "peakMonthlyOrganic": max((m["organicUsers"] for m in organic_by_month), default=0),
            }
    
    return {
        "enabled": True,
        "summary": f"Organic growth contributed {organic_percent:.1f}% of total user acquisition with an effective K-factor of {k_factor:.2f}",
        
        # Core metrics
        "metrics": {
            "totalOrganicUsers": total_organic,
            "organicPercentOfTotal": round(organic_percent, 1),
            "effectiveKFactor": round(k_factor, 3),
            "organicGrowthRate": organic.get("organicGrowthRate") or organic.get("organic_growth_rate") or 0,
            "networkEffectMultiplier": organic.get("networkEffectMultiplier") or organic.get("network_effect_multiplier") or 1.0,
        },
        
        # Source breakdown
        "sourceBreakdown": {
            "wordOfMouth": organic.get("wordOfMouthUsers") or organic.get("word_of_mouth_users") or 0,
            "appStoreDiscovery": organic.get("appStoreDiscoveryUsers") or organic.get("app_store_discovery_users") or 0,
            "networkEffects": organic.get("networkEffectUsers") or organic.get("network_effect_users") or 0,
            "socialSharing": organic.get("socialSharingUsers") or organic.get("social_sharing_users") or 0,
            "contentVirality": organic.get("contentViralityUsers") or organic.get("content_virality_users") or 0,
        },
        
        # Revenue impact
        "revenueImpact": {
            "organicUsersInRevenue": organic_users,
            "estimatedOrganicRevenue": round(organic_revenue_contribution, 2),
            "organicRevenuePercent": round((organic_revenue_contribution / total_revenue * 100) if total_revenue > 0 else 0, 1),
            "costSavingsVsPaid": round(organic_users * 5.0, 2),  # Assuming $5 CAC saved per organic user
        },
        
        # Participation rates
        "participationRates": {
            "referralParticipation": round((organic.get("actualReferralParticipation") or organic.get("actual_referral_participation") or 0) * 100, 1),
            "sharingParticipation": round((organic.get("actualSharingParticipation") or organic.get("actual_sharing_participation") or 0) * 100, 1),
        },
        
        # Maturity impact
        "maturityImpact": {
            "earlyStageBoostApplied": organic.get("earlyStageBoostApplied") or organic.get("early_stage_boost_applied") or False,
            "maturityDampeningApplied": organic.get("maturityDampeningApplied") or organic.get("maturity_dampening_applied") or False,
            "seasonalAdjustmentsApplied": organic.get("seasonalAdjustmentsApplied") or organic.get("seasonal_adjustments_applied") or False,
        },
        
        # Progression data (if available)
        "progression": organic_progression,
        
        # Benchmarks
        "benchmarks": {
            "industryTypicalOrganicPercent": "20-40% Year 1, 50-70% Year 2, 60-80% Year 3+",
            "typicalKFactor": "0.25-0.60 for social/crypto platforms",
            "referenceApps": [
                {"name": "WhatsApp", "organicPercent": "70-80%", "kFactor": "0.6+"},
                {"name": "Instagram", "organicPercent": "60-70%", "note": "During growth phase"},
                {"name": "Dropbox", "referralContribution": "35%", "note": "From referral program alone"},
            ],
        },
    }


def extract_token_economics(
    result: Dict[str, Any],
    monthly_progression: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract and organize token economics data.
    
    Includes:
    - Inflation/deflation analysis
    - Yearly supply snapshots (Year 1-5)
    - Velocity metrics
    - Real yield metrics
    - Value accrual analysis
    - Recapture metrics
    - Rewards distribution
    """
    token_metrics = result.get("tokenMetrics") or result.get("token_metrics") or {}
    recapture = result.get("recapture") or {}
    rewards = result.get("rewards") or {}
    
    # Inflation data
    inflation = token_metrics.get("inflation") or {}
    
    # Vesting schedule from monthly progression
    vesting_schedule = None
    if monthly_progression:
        vesting_schedule = monthly_progression.get("vestingSchedule") or monthly_progression.get("vesting_schedule")
    
    # Supply distribution
    supply_distribution = {
        "circulatingSupply": inflation.get("circulatingSupply") or inflation.get("circulating_supply") or 0,
        "totalSupply": inflation.get("totalSupply") or inflation.get("total_supply") or 1_000_000_000,
        "monthlyEmission": inflation.get("monthlyEmission") or inflation.get("monthly_emission") or 0,
        "vestingUnlocks": inflation.get("vestingUnlocks") or inflation.get("vesting_unlocks") or 0,
        "totalMonthlyUnlocks": inflation.get("totalMonthlyUnlocks") or inflation.get("total_monthly_unlocks") or 0,
        "monthlyBurns": inflation.get("monthlyBurns") or inflation.get("monthly_burns") or 0,
        "monthlyBuybacks": inflation.get("monthlyBuybacks") or inflation.get("monthly_buybacks") or 0,
        "totalDeflationary": inflation.get("totalDeflationary") or inflation.get("total_deflationary") or 0,
        "netMonthlyInflation": inflation.get("netMonthlyInflation") or inflation.get("net_monthly_inflation") or 0,
        "isDeflationary": inflation.get("isDeflationary") or inflation.get("is_deflationary") or False,
    }
    
    # Add unlock breakdown if available
    unlocks_breakdown = inflation.get("monthlyUnlocksBreakdown") or inflation.get("monthly_unlocks_breakdown") or {}
    if unlocks_breakdown:
        supply_distribution["monthlyUnlocksBreakdown"] = unlocks_breakdown
    
    # ========================================================================
    # YEARLY SUPPLY SNAPSHOTS - Year 1-5 supply dynamics for slider
    # ========================================================================
    yearly_snapshots = inflation.get("yearlySnapshots") or inflation.get("yearly_snapshots") or []
    
    # Format yearly snapshots for report
    yearly_supply_dynamics = []
    for snapshot in yearly_snapshots:
        year = snapshot.get("year", 0)
        yearly_supply_dynamics.append({
            "year": year,
            "month": snapshot.get("month", year * 12),
            "status": snapshot.get("status", "Unknown"),
            "isDeflationary": snapshot.get("isDeflationary") or snapshot.get("is_deflationary") or False,
            "supply": {
                "rewardsEmission": snapshot.get("rewardsEmission") or snapshot.get("rewards_emission") or 0,
                "vestingUnlocks": snapshot.get("vestingUnlocks") or snapshot.get("vesting_unlocks") or 0,
                "totalUnlocks": snapshot.get("totalUnlocks") or snapshot.get("total_unlocks") or 0,
            },
            "deflationary": {
                "burns": snapshot.get("burns", 0),
                "buybacks": snapshot.get("buybacks", 0),
                "total": snapshot.get("totalDeflationary") or snapshot.get("total_deflationary") or 0,
            },
            "netChange": {
                "monthly": snapshot.get("netChange") or snapshot.get("net_change") or 0,
                "monthlyRate": snapshot.get("monthlyRate") or snapshot.get("monthly_rate") or 0,
                "annualRate": snapshot.get("annualRate") or snapshot.get("annual_rate") or 0,
            },
            "circulatingSupply": snapshot.get("circulatingSupply") or snapshot.get("circulating_supply") or 0,
        })
    
    # Summary of supply dynamics journey
    supply_dynamics_summary = None
    if yearly_supply_dynamics:
        year1 = yearly_supply_dynamics[0] if len(yearly_supply_dynamics) > 0 else {}
        year5 = yearly_supply_dynamics[4] if len(yearly_supply_dynamics) > 4 else {}
        
        supply_dynamics_summary = {
            "year1AnnualRate": year1.get("netChange", {}).get("annualRate", 0) if isinstance(year1.get("netChange"), dict) else 0,
            "year5AnnualRate": year5.get("netChange", {}).get("annualRate", 0) if isinstance(year5.get("netChange"), dict) else 0,
            "year5Status": year5.get("status", "Unknown"),
            "becomesDeflationary": year5.get("isDeflationary", False),
            "vestingCompletesAtMonth": 60,
            "totalSupplyFixed": True,
            "summary": (
                f"Token starts with {year1.get('netChange', {}).get('annualRate', 0):.1f}% annual supply growth in Year 1 "
                f"(vesting unlocks). By Year 5, vesting completes and token becomes "
                f"{'deflationary at ' + str(year5.get('netChange', {}).get('annualRate', 0)) + '% annually' if year5.get('isDeflationary') else 'near-neutral'}."
            ) if year1 and year5 else "Supply dynamics data not available.",
        }
    
    return {
        "vestingSchedule": vesting_schedule,
        "inflationAnalysis": {
            "annualNetInflationRate": inflation.get("annualNetInflationRate") or inflation.get("annual_net_inflation_rate") or 0,
            "emissionRate": inflation.get("emissionRate") or inflation.get("emission_rate") or 0,
            "dilutionRate": inflation.get("dilutionRate") or inflation.get("dilution_rate") or 0,
            "rewardsEmissionRate": inflation.get("rewardsEmissionRate") or inflation.get("rewards_emission_rate") or 0,
            "deflationStrength": inflation.get("deflationStrength") or inflation.get("deflation_strength") or "",
            "supplyHealthScore": inflation.get("supplyHealthScore") or inflation.get("supply_health_score") or 0,
            "monthsToMaxSupply": inflation.get("monthsToMaxSupply") or inflation.get("months_to_max_supply") or 60,
            "projectedYear1Inflation": inflation.get("projectedYear1Inflation") or inflation.get("projected_year1_inflation") or 0,
            "projectedYear5Supply": inflation.get("projectedYear5Supply") or inflation.get("projected_year5_supply") or 0,
            "tgeCirculating": inflation.get("tgeCirculating") or inflation.get("tge_circulating") or 114_833_333,
        },
        # NEW: Yearly supply dynamics for Year 1-5
        "yearlySupplyDynamics": yearly_supply_dynamics,
        "supplyDynamicsSummary": supply_dynamics_summary,
        "velocityMetrics": token_metrics.get("velocity") or {},
        "realYieldMetrics": token_metrics.get("realYield") or token_metrics.get("real_yield") or {},
        "valueAccrual": token_metrics.get("valueAccrual") or token_metrics.get("value_accrual") or {},
        "supplyDistribution": supply_distribution,
        "recaptureMetrics": {
            "totalRecaptured": recapture.get("totalRecaptured") or recapture.get("total_recaptured") or 0,
            "recaptureRate": recapture.get("recaptureRate") or recapture.get("recapture_rate") or 0,
            "burns": recapture.get("burns") or 0,
            "treasury": recapture.get("treasury") or 0,
            "staking": recapture.get("staking") or 0,
            "buybacks": recapture.get("buybacks") or 0,
            "effectiveBurnRate": recapture.get("effectiveBurnRate") or recapture.get("effective_burn_rate") or 0,
        },
        "rewardsMetrics": {
            "monthlyEmission": rewards.get("monthlyEmission") or rewards.get("monthly_emission") or 0,
            "emissionUsd": rewards.get("emissionUSD") or rewards.get("emission_usd") or 0,
            "allocationPercent": rewards.get("allocationPercent") or rewards.get("allocation_percent") or 0,
            "isDynamicAllocation": rewards.get("isDynamicAllocation") or rewards.get("is_dynamic_allocation") or False,
            "perUserMonthlyVcoin": rewards.get("perUserMonthlyVcoin") or rewards.get("per_user_monthly_vcoin") or 0,
            "perUserMonthlyUsd": rewards.get("perUserMonthlyUsd") or rewards.get("per_user_monthly_usd") or 0,
            "referralBonusDistributed": inflation.get("referralBonusDistributed") or inflation.get("referral_bonus_distributed") or 0,
            "pointsTokensDistributed": inflation.get("pointsTokensDistributed") or inflation.get("points_tokens_distributed") or 0,
            "stakingRewardsFromEmission": inflation.get("stakingRewardsFromEmission") or inflation.get("staking_rewards_from_emission") or 0,
            "userRewardsFromEmission": inflation.get("userRewardsFromEmission") or inflation.get("user_rewards_from_emission") or 0,
        },
    }


def generate_full_report(
    parameters: Dict[str, Any],
    result: Dict[str, Any],
    monthly_progression: Optional[Dict[str, Any]] = None,
    monte_carlo_result: Optional[Dict[str, Any]] = None,
    agent_based_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate a comprehensive full report with all simulation data.
    
    Args:
        parameters: Simulation parameters used
        result: Main simulation result (deterministic or selected percentile)
        monthly_progression: 60-month progression data if available
        monte_carlo_result: Monte Carlo simulation results if run
        agent_based_result: Agent-based simulation results if run
    
    Returns:
        Complete report dictionary with all sections
    """
    # Generate report sections
    executive_summary = generate_executive_summary(result, parameters, monthly_progression)
    risk_assessment = calculate_overall_risk_score(result)
    recommendations = aggregate_recommendations(result)
    benchmarks = generate_benchmarks(result)
    token_economics = extract_token_economics(result, monthly_progression)
    future_modules = extract_future_modules(result, parameters)
    five_year_projections = calculate_5_year_projections(result, parameters, monthly_progression)
    organic_growth = extract_organic_growth(result, monthly_progression)
    
    # NEW: Additional module extractions
    financial_summary = extract_financial_summary(result)
    core_modules = extract_core_modules(result)
    customer_acquisition = extract_customer_acquisition(result)
    prelaunch_modules = extract_prelaunch_modules(result)
    sensitivity_analysis = extract_sensitivity_analysis(result)
    staking_governance = extract_staking_governance(result)
    
    # Build the complete report
    report = {
        "metadata": {
            "generatedAt": datetime.now().isoformat(),
            "simulatorVersion": "2.0.0",
            "reportVersion": "1.1.0",  # Updated version for new sections
            "protocol": "ViWO Token Economy",
            "reportType": "comprehensive",
        },
        "executiveSummary": executive_summary,
        "parameters": parameters,
        "results": result,
        
        # === FINANCIAL OVERVIEW ===
        "financialSummary": financial_summary,
        
        # === REVENUE & MODULES ===
        "coreModules": core_modules,
        "futureModules": future_modules,
        
        # === GROWTH & ACQUISITION ===
        "customerAcquisition": customer_acquisition,
        "organicGrowth": organic_growth,
        "prelaunchModules": prelaunch_modules,
        
        # === TOKEN ECONOMICS ===
        "tokenEconomics": token_economics,
        "stakingGovernance": staking_governance,
        
        # === PROJECTIONS ===
        "fiveYearProjections": five_year_projections,
        
        # === RISK & ANALYSIS ===
        "riskAssessment": risk_assessment,
        "sensitivityAnalysis": sensitivity_analysis,
        "recommendations": recommendations,
        "benchmarks": benchmarks,
    }
    
    # Add monthly progression if available
    if monthly_progression:
        report["monthlyProgression"] = monthly_progression
    
    # Add Monte Carlo results if available
    if monte_carlo_result:
        report["monteCarloAnalysis"] = {
            "iterations": monte_carlo_result.get("iterations") or 0,
            "statistics": monte_carlo_result.get("statistics") or {},
            "distributions": {
                "revenueSummary": {
                    "p5": monte_carlo_result.get("percentiles", {}).get("p5", {}).get("totals", {}).get("revenue"),
                    "p50": monte_carlo_result.get("percentiles", {}).get("p50", {}).get("totals", {}).get("revenue"),
                    "p95": monte_carlo_result.get("percentiles", {}).get("p95", {}).get("totals", {}).get("revenue"),
                },
                "profitSummary": {
                    "p5": monte_carlo_result.get("percentiles", {}).get("p5", {}).get("totals", {}).get("profit"),
                    "p50": monte_carlo_result.get("percentiles", {}).get("p50", {}).get("totals", {}).get("profit"),
                    "p95": monte_carlo_result.get("percentiles", {}).get("p95", {}).get("totals", {}).get("profit"),
                },
            },
        }
    
    # Add Agent-based results if available
    if agent_based_result:
        report["agentBasedAnalysis"] = {
            "totalAgents": agent_based_result.get("totalAgents") or agent_based_result.get("total_agents") or 0,
            "agentBreakdown": agent_based_result.get("agentBreakdown") or agent_based_result.get("agent_breakdown") or {},
            "marketDynamics": agent_based_result.get("marketDynamics") or agent_based_result.get("market_dynamics") or {},
            "systemMetrics": agent_based_result.get("systemMetrics") or agent_based_result.get("system_metrics") or {},
            "flaggedBots": agent_based_result.get("flaggedBots") or agent_based_result.get("flagged_bots") or 0,
        }
    
    # Add 5A Policy results if present
    five_a = result.get("fiveA") or result.get("five_a")
    if five_a:
        report["fiveAPolicyAnalysis"] = {
            "enabled": five_a.get("enabled") or False,
            "avgCompoundMultiplier": five_a.get("avgCompoundMultiplier") or five_a.get("avg_compound_multiplier") or 1.0,
            "rewardRedistributionPercent": five_a.get("rewardRedistributionPercent") or five_a.get("reward_redistribution_percent") or 0,
            "usersWithBoost": five_a.get("usersWithBoost") or five_a.get("users_with_boost") or 0,
            "usersWithPenalty": five_a.get("usersWithPenalty") or five_a.get("users_with_penalty") or 0,
            "fairnessScore": five_a.get("fairnessScore") or five_a.get("fairness_score") or 0,
            "segmentBreakdown": five_a.get("segmentBreakdown") or five_a.get("segment_breakdown") or {},
        }
    
    # Generate checksum for data integrity
    report_json = json.dumps(report, sort_keys=True, default=str)
    checksum = hashlib.sha256(report_json.encode()).hexdigest()
    report["metadata"]["checksumSha256"] = checksum
    
    return report
