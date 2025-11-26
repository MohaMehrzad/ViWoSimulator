"""
Preset configurations for the simulator.

Updated with 2024-2025 industry benchmarks addressing all audit issues.
All presets now use realistic values for:
- CAC (Issue #2)
- Conversion rates (Issue #3)
- Token economics (Issue #5)
- Posts per user (Issue #8)
- Platform maturity (NEW)
"""

PRESETS = {
    "conservative": {
        "label": "Lean Bootstrap ($50K/yr)",
        "description": "Conservative growth with minimal spend, realistic for seed stage",
        "parameters": {
            "token_price": 0.03,
            "marketing_budget": 50000,
            "platform_maturity": "launch",
            "auto_adjust_for_maturity": True,
            "apply_retention": True,
            "include_compliance_costs": False,
            # User acquisition (Issue #2 - Realistic CAC)
            "north_america_budget_percent": 0.30,
            "global_low_income_budget_percent": 0.70,
            "cac_north_america_consumer": 80,
            "cac_global_low_income_consumer": 30,
            "high_quality_creator_cac": 5000,
            "high_quality_creators_needed": 2,
            "mid_level_creator_cac": 1000,
            "mid_level_creators_needed": 10,
            # Token economics (Issue #5 - Sustainable)
            "burn_rate": 0.02,
            "buyback_percent": 0.01,
            # Conversion & activity (Issues #3, #8)
            "verification_rate": 0.01,
            "posts_per_user": 0.4,
            "creator_percentage": 0.05,
            "posts_per_creator": 5,
            "ad_cpm_multiplier": 0.08,
            "reward_allocation_percent": 0.06,
            # Content (Issue #12)
            "enable_nft": False,
            "nft_mint_fee_vcoin": 25,
            "premium_content_volume_vcoin": 200,
            "content_sale_volume_vcoin": 100,
            # Identity (Issue #11)
            "monthly_sales": 0,
            "avg_profile_price": 15,
        }
    },
    "base": {
        "label": "Base Case ($150K/yr)",
        "description": "Balanced growth strategy for Series A",
        "parameters": {
            # Uses updated defaults from parameters.py
            "platform_maturity": "launch",
            "auto_adjust_for_maturity": True,
        }
    },
    "aggressive": {
        "label": "Growth Phase ($250K/yr)",
        "description": "Aggressive acquisition for growing platform",
        "parameters": {
            "token_price": 0.03,
            "marketing_budget": 250000,
            "platform_maturity": "growing",
            "auto_adjust_for_maturity": True,
            "apply_retention": True,
            "include_compliance_costs": False,  # Enable when needed
            # User acquisition
            "north_america_budget_percent": 0.40,
            "global_low_income_budget_percent": 0.60,
            "cac_north_america_consumer": 70,
            "cac_global_low_income_consumer": 22,
            "high_quality_creator_cac": 10000,
            "high_quality_creators_needed": 5,
            "mid_level_creator_cac": 2000,
            "mid_level_creators_needed": 25,
            # Token economics (Issue #5 - Sustainable max 15%)
            "burn_rate": 0.04,
            "buyback_percent": 0.03,
            # Conversion & activity
            "verification_rate": 0.02,
            "posts_per_user": 0.8,
            "creator_percentage": 0.08,
            "posts_per_creator": 8,
            "ad_cpm_multiplier": 0.25,
            "reward_allocation_percent": 0.10,
            # Advertising (Issue #7)
            "banner_cpm": 2.00,
            "video_cpm": 6.00,
            # Content
            "nft_mint_fee_vcoin": 30,
            "premium_content_volume_vcoin": 1500,
            "content_sale_volume_vcoin": 800,
            "verified_price": 5,
            "premium_price": 15,
            # Identity
            "monthly_sales": 3,
            "avg_profile_price": 40,
        }
    },
    "bull": {
        "label": "Year 2+ Scale ($400K/yr)",
        "description": "Established platform with strong brand",
        "parameters": {
            "token_price": 0.06,
            "marketing_budget": 400000,
            "platform_maturity": "established",
            "auto_adjust_for_maturity": True,
            "apply_retention": True,
            "include_compliance_costs": True,
            # User acquisition
            "north_america_budget_percent": 0.45,
            "global_low_income_budget_percent": 0.55,
            "cac_north_america_consumer": 60,
            "cac_global_low_income_consumer": 20,
            "high_quality_creator_cac": 12000,
            "high_quality_creators_needed": 8,
            "mid_level_creator_cac": 2500,
            "mid_level_creators_needed": 40,
            # Token economics (Issue #5 - Sustainable max 15%)
            "burn_rate": 0.05,
            "buyback_percent": 0.04,
            # Conversion & activity
            "verification_rate": 0.03,
            "posts_per_user": 1.0,
            "creator_percentage": 0.10,
            "posts_per_creator": 10,
            "ad_cpm_multiplier": 0.60,
            "reward_allocation_percent": 0.12,
            # Advertising (Issue #7 - Established rates)
            "banner_cpm": 8.00,
            "video_cpm": 25.00,
            # Content
            "enable_nft": True,
            "nft_mint_fee_vcoin": 35,
            "nft_mint_percentage": 0.01,
            "premium_content_volume_vcoin": 5000,
            "content_sale_volume_vcoin": 3000,
            "verified_price": 5,
            "premium_price": 15,
            # Identity (Issue #11)
            "monthly_sales": 15,
            "avg_profile_price": 80,
            # Exchange (Issue #4 - Higher for established)
            "exchange_user_adoption_rate": 0.10,
            "exchange_avg_monthly_volume": 200,
            "exchange_withdrawals_per_user": 0.8,
        }
    }
}
