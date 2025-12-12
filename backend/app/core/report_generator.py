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
        "riskLevel": risk_assessment["riskLevel"],
        "riskScore": risk_assessment["overallRiskScore"],
        "keyStrengths": strengths[:5],  # Top 5 strengths
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
    Uses monthly progression data if available, otherwise estimates from base result.
    """
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


def extract_token_economics(
    result: Dict[str, Any],
    monthly_progression: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract and organize token economics data.
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
        "monthlyBurns": inflation.get("monthlyBurns") or inflation.get("monthly_burns") or 0,
        "monthlyBuybacks": inflation.get("monthlyBuybacks") or inflation.get("monthly_buybacks") or 0,
        "netMonthlyInflation": inflation.get("netMonthlyInflation") or inflation.get("net_monthly_inflation") or 0,
        "isDeflationary": inflation.get("isDeflationary") or inflation.get("is_deflationary") or False,
    }
    
    # Add unlock breakdown if available
    unlocks_breakdown = inflation.get("monthlyUnlocksBreakdown") or inflation.get("monthly_unlocks_breakdown") or {}
    if unlocks_breakdown:
        supply_distribution["monthlyUnlocksBreakdown"] = unlocks_breakdown
    
    return {
        "vestingSchedule": vesting_schedule,
        "inflationAnalysis": {
            "annualNetInflationRate": inflation.get("annualNetInflationRate") or inflation.get("annual_net_inflation_rate") or 0,
            "emissionRate": inflation.get("emissionRate") or inflation.get("emission_rate") or 0,
            "deflationStrength": inflation.get("deflationStrength") or inflation.get("deflation_strength") or "",
            "supplyHealthScore": inflation.get("supplyHealthScore") or inflation.get("supply_health_score") or 0,
            "monthsToMaxSupply": inflation.get("monthsToMaxSupply") or inflation.get("months_to_max_supply") or 60,
            "projectedYear1Inflation": inflation.get("projectedYear1Inflation") or inflation.get("projected_year1_inflation") or 0,
            "projectedYear5Supply": inflation.get("projectedYear5Supply") or inflation.get("projected_year5_supply") or 0,
        },
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
    
    # Build the complete report
    report = {
        "metadata": {
            "generatedAt": datetime.now().isoformat(),
            "simulatorVersion": "2.0.0",
            "reportVersion": "1.0.0",
            "protocol": "ViWO Token Economy",
            "reportType": "comprehensive",
        },
        "executiveSummary": executive_summary,
        "parameters": parameters,
        "results": result,
        "tokenEconomics": token_economics,
        "fiveYearProjections": five_year_projections,
        "futureModules": future_modules,
        "riskAssessment": risk_assessment,
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
