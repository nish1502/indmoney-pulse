import streamlit as st
import json
import os
import pandas as pd
from collections import Counter

# Page Config
st.set_page_config(page_title="AI-Powered Product Intelligence", layout="wide")

# Helper to load JSON safely
def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# DATA LOADING
reviews_data = load_json("output/v2c_classified_reviews.json")
trends_data = load_json("output/v3_trends.json")
impact_data = load_json("output/v3_impact.json")
report_text = ""
if os.path.exists("output/v3_weekly_pulse.md"):
    with open("output/v3_weekly_pulse.md", 'r', encoding='utf-8') as f:
        report_text = f.read()

# 1. HEADER & PRODUCT HEALTH
st.title("🤖 AI-Powered Product Intelligence Dashboard")

if reviews_data and trends_data and impact_data:
    # 0. Calculate Product Health (Simulated logic based on trend/impact)
    # Start at 100, deduct points for high-impact increasing issues
    health_score = 100
    impact_dict = {item[0]: item[1] for item in impact_data}
    
    for theme, info in trends_data.items():
        if info['change'] > 0:
            health_score -= (info['change'] * 2) # Penalize increasing problems
        elif info['change'] < 0:
            health_score += (abs(info['change']) * 0.5) # Reward improving themes
            
    health_score = min(max(int(health_score), 0), 100)
    
    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    with col_h1:
        st.metric("Overall Product Health", f"{health_score}%")
    with col_h2:
        st.metric("Total Reviews Captured", len(reviews_data))
    with col_h3:
        theme_counts = Counter([r["theme"] for r in reviews_data])
        top_theme = theme_counts.most_common(1)[0][0] if theme_counts else "N/A"
        st.metric("Top Volume Theme", top_theme)
    with col_h4:
        most_critical_theme = impact_data[0][0]
        st.metric("Most Critical Issue", most_critical_theme)

    st.markdown("---")

    # 1. SHARP EXECUTIVE SUMMARY
    top_impact_theme = impact_data[0][0]
    trend_val = trends_data.get(top_impact_theme, {}).get('change', 0)
    
    if trend_val > 0:
        summary_msg = f"❗ **ACTION REQUIRED:** {top_impact_theme} is escalating (+{abs(trend_val)}%). Immediate remediation needed for reported risk."
    else:
        summary_msg = f"💡 **ACTION:** While {top_impact_theme} remains critical, its frequency is declining (-{abs(trend_val)}%). Keep monitoring current fixes."
        
    st.info(f"**Executive Pulse:** {summary_msg}")

st.markdown("---")

# 2. PM PRIORITY BOARD (DOMINANT VIEW)
st.subheader("📋 PM Priority Board (Executive Focus)")

if reviews_data and trends_data and impact_data:
    # Use wider first column and decisive labels
    cols = st.columns([1.8, 1, 1])
    
    fix_now = []
    monitor = []
    improving = []
    
    top_impact_themes = [item[0] for item in impact_data[:3]]
    all_themes = sorted(trends_data.keys(), key=lambda x: impact_dict.get(x, 0), reverse=True)
    
    for theme in all_themes:
        change = trends_data.get(theme, {}).get("change", 0)
        is_top_impact = theme in top_impact_themes
        
        if change < 0:
            improving.append(theme)
        elif is_top_impact and change > 0:
            fix_now.append(theme)
        else:
            monitor.append(theme)
            
    with cols[0]:
        st.markdown("<h2 style='color: #FF4B4B;'>🚨 Fix Now</h2>", unsafe_allow_html=True)
        st.write("") 
        if fix_now:
            for theme in fix_now:
                score = impact_dict.get(theme, 0)
                change = trends_data.get(theme, {}).get('change', 0)
                # Dominate with larger text
                st.markdown(f"## {theme}")
                st.markdown(f"**Criticality:** High | Trending ↑ **{change}%** | Severity Score: **{score}**")
                st.write("") 
        else:
            st.write("*No high-risk escalations detected.*")
                
    with cols[1]:
        st.markdown("<h3 style='color: #FFBD45;'>⚠️ Monitor (Stable Risk)</h3>", unsafe_allow_html=True)
        if monitor:
            for theme in monitor:
                score = impact_dict.get(theme, 0)
                change = trends_data.get(theme, {}).get('change', 0)
                st.markdown(f"**{theme}**")
                st.write(f"Trend: → {change}% | Score: {score}")
                st.markdown("---")
                
    with cols[2]:
        st.markdown("<h3 style='color: #28A745;'>✅ Improving (Fix Working)</h3>", unsafe_allow_html=True)
        if improving:
            for theme in improving:
                score = impact_dict.get(theme, 0)
                change = trends_data.get(theme, {}).get('change', 0)
                st.markdown(f"**{theme}**")
                st.write(f"Trend: ↓ {abs(change)}% | Score: {score}")
                st.markdown("---")

st.markdown("---")

# 3. ANALYSIS & USER VOICES
col_left, col_right = st.columns([1.2, 1.5])

with col_left:
    st.subheader("📊 Theme Volume (%)")
    if theme_counts:
        df = pd.DataFrame(list(theme_counts.items()), columns=["Theme", "Count"])
        df = df.sort_values(by="Count", ascending=False)
        st.bar_chart(df.set_index("Theme"))

with col_right:
    st.subheader("💬 Voices from the Ground")
    # Show samples from Priority Board themes
    priority_order = fix_now + monitor + improving
    shown = 0
    for theme in priority_order:
        theme_samples = [r for r in reviews_data if r['theme'] == theme][:1]
        for r in theme_samples:
            if shown < 4:
                st.markdown(f"**[{r['theme']}]** {r['review'][:120]}...")
                st.markdown("---")
                shown += 1

st.markdown("---")

# 4. FULL REPORT PREVIEW
st.subheader("📄 Product Pulse Weekly Report")
if report_text:
    st.markdown(report_text)
else:
    st.write("Summary analysis pending next pipeline run.")

st.markdown("---")
st.caption("Auto-generated Intelligence Layer Powered by Gemini & Groq.")
