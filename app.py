import streamlit as st
from analyzer import analyze_wallet

# Page config
st.set_page_config(
    page_title="DeFi Wallet Risk Analyzer",
    page_icon="🔍",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0a0a0a;
    }
    .stTextInput > div > div > input {
        background-color: #161616;
        color: #d8d0c0;
        border: 1px solid #2a2a2a;
    }
    .risk-box {
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
# 🔍 DeFi Wallet Risk Analyzer
**Analyze any Ethereum wallet instantly**
""")

st.markdown("---")

# Input
wallet_address = st.text_input(
    "Enter Ethereum Wallet Address",
    placeholder="0x742d35Cc6634C0532...",
    help="Must start with 0x, 42 characters"
)

analyze_button = st.button(
    "🔍 Analyze Wallet",
    type="primary",
    use_container_width=True
)

# Analysis
if analyze_button and wallet_address:
    
    with st.spinner(
        "Analyzing wallet... "
        "fetching blockchain data..."
    ):
        result = analyze_wallet(
            wallet_address.strip()
        )
    
    # Error check
    if 'error' in result:
        st.error(result['error'])
    
    else:
        # Risk Score — Big Display
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Risk Score",
                f"{result['risk_score']}/100"
            )
        
        with col2:
            st.metric(
                "Risk Level",
                result['risk_level']
            )
        
        with col3:
            st.metric(
                "Wallet Age",
                f"{result['wallet_age_days']} days"
            )
        
        st.markdown("---")
        
        # Two columns for stats
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 📊 Wallet Stats")
            st.write(
                f"**ETH Balance:** "
                f"{result['eth_balance']} ETH"
            )
            st.write(
                f"**Total Transactions:** "
                f"{result['total_transactions']}"
            )
            st.write(
                f"**Sent:** "
                f"{result['sent_transactions']}"
            )
            st.write(
                f"**Received:** "
                f"{result['received_transactions']}"
            )
            st.write(
                f"**Failed:** "
                f"{result['failed_transactions']} "
                f"({result['failed_rate']}%)"
            )
            st.write(
                f"**First Transaction:** "
                f"{result['first_transaction_date']}"
            )
        
        with col_right:
            # Risk Flags
            if result['risk_flags']:
                st.markdown("### ⚠️ Risk Flags")
                for flag in result['risk_flags']:
                    st.write(flag)
            
            # Positive Signals
            if result['risk_positives']:
                st.markdown(
                    "### ✅ Positive Signals"
                )
                for pos in result['risk_positives']:
                    st.write(pos)
        
        st.markdown("---")
        
        # Disclaimer
        st.caption(
            "⚠️ This analysis is for "
            "informational purposes only. "
            "Not financial advice. "
            "Always do your own research."
        )

elif analyze_button and not wallet_address:
    st.warning(
        "Please enter a wallet address"
    )

# Footer
st.markdown("---")
st.markdown(
    "Built by Moeez Khan | "
    "FinTech & AI Automation | "
    "[GitHub] https://github.com/kmoeez649"
)
