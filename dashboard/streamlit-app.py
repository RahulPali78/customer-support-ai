#!/usr/bin/env python3
"""
Customer Support AI Dashboard
Simple monitoring interface for the AI automation system
"""

import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, timedelta
import os

# Page config
st.set_page_config(
    page_title="CS AI Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Supabase credentials - use Streamlit secrets in production
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", "your-project-url"))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", "your-anon-key"))

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize
supabase = get_supabase()

# Sidebar
st.sidebar.title("🤖 CS AI Dashboard")
page = st.sidebar.radio("Navigate", ["📊 Overview", "📧 Email Queue", "🧠 Knowledge Base", "⚙️ Settings"])

if page == "📊 Overview":
    st.title("System Overview")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # Total emails today
        today = datetime.now().date()
        today_start = f"{today}T00:00:00"
        
        emails_today = supabase.table("emails").select("*", count="exact").gte("created_at", today_start).execute()
        total_today = emails_today.count if hasattr(emails_today, 'count') else 0
        
        # Auto-replied count
        auto_replied = supabase.table("emails").select("*", count="exact").eq("status", "auto_replied").gte("created_at", today_start).execute()
        auto_count = auto_replied.count if hasattr(auto_replied, 'count') else 0
        
        # Escalated count
        escalated = supabase.table("emails").select("*", count="exact").eq("status", "escalated").gte("created_at", today_start).execute()
        esc_count = escalated.count if hasattr(escalated, 'count') else 0
        
        # Avg confidence
        result = supabase.table("emails").select("confidence").limit(100).execute()
        confidences = [r['confidence'] for r in result.data if r.get('confidence')]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        
        col1.metric("Emails Today", total_today)
        col2.metric("Auto-Replied", auto_count)
        col3.metric("Escalated", esc_count)
        col4.metric("Avg Confidence", f"{avg_conf:.0%}")
        
    except Exception as e:
        st.error(f"Database connection error: {e}")
        st.info("Make sure Supabase credentials are set in .streamlit/secrets.toml")
    
    # Recent emails chart
    st.subheader("Recent Activity (Last 7 Days)")
    try:
        days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        result = supabase.table("emails").select("created_at, classification, status").gte("created_at", days_ago).execute()
        
        if result.data:
            df = pd.DataFrame(result.data)
            df['date'] = pd.to_datetime(df['created_at']).dt.date
            daily_counts = df.groupby(['date', 'classification']).size().unstack(fill_value=0)
            st.bar_chart(daily_counts)
        else:
            st.info("No data yet. Start ingesting emails to see charts.")
    except Exception as e:
        st.warning(f"Chart error: {e}")

elif page == "📧 Email Queue":
    st.title("Email Queue")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Status", ["All", "pending", "needs_review", "auto_replied", "escalated", "resolved"])
    with col2:
        class_filter = st.selectbox("Classification", ["All", "REFUND", "STATUS", "COMPLAINT", "GENERAL", "OTHER"])
    
    # Fetch emails
    try:
        query = supabase.table("emails").select("*").order("created_at", desc=True).limit(50)
        
        if status_filter != "All":
            query = query.eq("status", status_filter)
        if class_filter != "All":
            query = query.eq("classification", class_filter)
            
        result = query.execute()
        
        if result.data:
            for email in result.data:
                with st.expander(f"📧 {email['subject'][:60]}... | {email.get('classification', 'Unclassified')} | {email.get('status', 'Pending')}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**From:** {email.get('sender_name', 'Unknown')} <{email.get('sender_email', 'N/A')}>")
                        st.markdown(f"**Subject:** {email['subject']}")
                        st.markdown(f"**Received:** {email['received_at'][:16]}")
                        st.markdown("**Content:**")
                        st.text(email.get('body_text', 'No text content')[:500])
                    with col2:
                        st.markdown(f"**Classification:** `{email.get('classification', 'N/A')}`")
                        st.markdown(f"**Confidence:** {email.get('confidence', 'N/A'):.2%}" if email.get('confidence') else "**Confidence:** N/A")
                        st.markdown(f"**Status:** `{email.get('status', 'pending')}`")
                        if email.get('ai_response'):
                            st.markdown("---")
                            st.markdown("**AI Draft Response:**")
                            st.info(email['ai_response'][:300])
                        
                        # Action buttons
                        st.markdown("---")
                        if st.button("✅ Mark Resolved", key=f"resolve_{email['id']}"):
                            supabase.table("emails").update({"status": "resolved"}).eq("id", email['id']).execute()
                            st.rerun()
                        if st.button("📤 Escalate", key=f"escalate_{email['id']}"):
                            supabase.table("emails").update({"status": "escalated"}).eq("id", email['id']).execute()
                            st.rerun()
        else:
            st.info("No emails matching filters")
    except Exception as e:
        st.error(f"Error loading emails: {e}")

elif page == "🧠 Knowledge Base":
    st.title("Knowledge Base Documents")
    
    try:
        result = supabase.table("knowledge_documents").select("*").order("created_at", desc=True).execute()
        
        if result.data:
            for doc in result.data:
                with st.expander(f"📄 {doc['title']} | {doc.get('category', 'Uncategorized')}"):
                    st.markdown(f"**Category:** {doc.get('category', 'N/A')}")
                    st.markdown("**Content:**")
                    st.markdown(doc['content'])
                    st.caption(f"Created: {doc['created_at'][:10]}")
        else:
            st.info("No knowledge documents yet. Add them to the database to enable RAG responses.")
    except Exception as e:
        st.error(f"Error: {e}")
    
    # Add new document
    st.markdown("---")
    st.subheader("Add New Document")
    with st.form("add_doc"):
        title = st.text_input("Title")
        category = st.selectbox("Category", ["RETURNS", "SHIPPING", "PRODUCTS", "GENERAL", "OTHER"])
        content = st.text_area("Content", height=150)
        submit = st.form_submit_button("Add Document")
        
        if submit and title and content:
            try:
                supabase.table("knowledge_documents").insert({
                    "title": title,
                    "category": category,
                    "content": content
                }).execute()
                st.success("Document added!")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding document: {e}")

elif page == "⚙️ Settings":
    st.title("System Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Classification Thresholds")
        confidence_threshold = st.slider(
            "Auto-reply confidence threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.8,
            step=0.05
        )
        st.markdown(f"Current: **{confidence_threshold:.0%}**")
        st.caption("Emails with confidence below this will be escalated to human review.")
        
        st.subheader("Auto-Reply Rules")
        auto_status = st.checkbox("Auto-reply STATUS emails", value=True)
        auto_general = st.checkbox("Auto-reply GENERAL emails", value=True)
        auto_refund = st.checkbox("Auto-reply REFUND emails", value=False)
        auto_complaint = st.checkbox("Auto-reply COMPLAINT emails (dangerous)", value=False)
        
        if st.button("Save Settings"):
            st.success("Settings saved! (Note: In production, persist to database)")
    
    with col2:
        st.subheader("System Status")
        st.markdown("**Connected Services:**")
        st.markdown("✅ Supabase Database")
        st.markdown("✅ OpenAI API")
        st.markdown("⚠️ Gmail (OAuth required)")
        st.markdown("⚠️ Slack (OAuth required)")
        
        st.subheader("Quick Actions")
        if st.button("🔄 Run Email Check"):
            st.info("Triggering manual check... (In production: call n8n webhook)")
        if st.button("📊 Generate Report"):
            st.info("Downloading analytics... (In production: generate CSV/PDF)")
        
        st.markdown("---")
        st.subheader("About")
        st.caption("Customer Support AI v1.0")
        st.caption("Built with n8n + Supabase + OpenAI")