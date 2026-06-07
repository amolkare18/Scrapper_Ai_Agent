import streamlit as st
import os
from controllers.scrapper_controller import search_products
from pipelines.data_pipeline import DataPipeline
from Agents.Agent_feedback import (
    recommend_best_deal_with_ai, 
    get_ai_summary, 
    get_best_budget_option,
    get_best_overall_product,
    compare_products
)
from helpers.visualizations import (
    create_price_distribution_chart,
    create_rating_breakdown_chart,
    create_discount_vs_price_chart,
    create_top_products_chart,
    create_best_deals_chart,
    create_summary_metrics,
    create_seller_distribution,
    create_comparison_table
)
from helpers.utils import export_to_json, export_to_excel, read_products_csv

# 🧱 Page configuration
st.set_page_config(
    page_title="🛍️ Amazon Product Scraper Pro",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-title {
        font-size: 3em;
        font-weight: bold;
        color: #FF9900;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# 🧱 Title
st.markdown('<div class="main-title">🛍️ Amazon Product Scraper Pro</div>', unsafe_allow_html=True)

# Session state for results persistence
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'filename' not in st.session_state:
    st.session_state.filename = None

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### ⚙️ Settings & Scraping")
    
    scrape_pages = st.slider("📄 Number of pages to scrape", 1, 5, 1)
    location = st.selectbox("🌍 Location/Country Code", ["in", "com", "co.uk", "ca", "de", "fr", "it", "es"])
    retry_attempts = st.slider("🔄 Retry attempts", 1, 5, 3)

# ==================== MAIN CONTENT ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Search", "📊 Dashboard", "🤖 AI Insights", "⚙️ Filters & Sort", "💾 Export"])

# ==================== TAB 1: SEARCH ====================
with tab1:
    st.markdown("### 🔎 Search for a Product")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        product_name = st.text_input("Enter the product name:", placeholder="e.g. MacBook, Headphones, iPhone...")
    with col2:
        search_button = st.button("🚀 Scrape", use_container_width=True)
    
    if search_button:
        if not product_name.strip():
            st.error("⚠️ Please enter a valid product name.")
        else:
            filename = f"{product_name}.csv"
            if os.path.exists(filename):
                os.remove(filename)
            pipeline = DataPipeline(csv_filename=filename)
            
            try:
                with st.spinner("🔄 Scraping Amazon... This may take a moment..."):
                    search_results = search_products(
                        product_name,
                        location=location,
                        retries=retry_attempts,
                        max_pages=scrape_pages,
                        data_pipeline=pipeline
                    )
                    pipeline.close_pipeline()
                
                st.session_state.search_results = search_results
                st.session_state.filename = filename
                
                if os.path.exists(filename):
                    df = read_products_csv(filename)
                    st.success(f"✅ Scraping completed! Found {len(df)} products.")
                    st.markdown("---")
                    st.markdown("### 📋 Scraped Products Preview")
                    
                    # Show first few products
                    display_cols = ['product_title', 'current_price', 'rating', 'discount_percent', 'seller_name']
                    available_cols = [col for col in display_cols if col in df.columns]
                    st.dataframe(df[available_cols].head(10), use_container_width=True)
                else:
                    st.warning("⚠️ No results found. Try a different search term.")
            
            except ValueError as ve:
                st.error(f"❌ Error: {ve}")
            except Exception as e:
                st.error(f"⚠️ Unexpected error: {e}")

# ==================== TAB 2: DASHBOARD ====================
with tab2:
    st.markdown("### 📊 Analytics Dashboard")
    
    if st.session_state.filename and os.path.exists(st.session_state.filename):
        df = read_products_csv(st.session_state.filename)
        
        if not df.empty:
            # Summary Metrics
            st.markdown("#### 📈 Key Metrics")
            metrics = create_summary_metrics(df)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📦 Total Products", metrics['total_products'])
            with col2:
                st.metric("💵 Avg Price", metrics['avg_price'])
            with col3:
                st.metric("⭐ Avg Rating", metrics['avg_rating'])
            with col4:
                st.metric("💰 Avg Discount", metrics['avg_discount'])
            
            # Additional metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Price Range", metrics['price_range'])
            with col2:
                st.metric("🎯 High-Rated", metrics['high_rated'])
            with col3:
                st.metric("📢 Sponsored", metrics['sponsored_count'])
            
            st.markdown("---")
            
            # Charts
            st.markdown("#### 📉 Visualizations")
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(create_price_distribution_chart(df), use_container_width=True)
            with col2:
                st.plotly_chart(create_rating_breakdown_chart(df), use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(create_discount_vs_price_chart(df), use_container_width=True)
            with col2:
                seller_chart = create_seller_distribution(df)
                if seller_chart:
                    st.plotly_chart(seller_chart, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(create_top_products_chart(df, 8), use_container_width=True)
            with col2:
                st.plotly_chart(create_best_deals_chart(df, 8), use_container_width=True)
        else:
            st.info("📭 No data available. Please scrape a product first.")
    else:
        st.info("📭 No data available. Please scrape a product first.")

# ==================== TAB 3: AI INSIGHTS ====================
with tab3:
    st.markdown("### 🤖 AI-Powered Insights")
    
    if st.session_state.filename and os.path.exists(st.session_state.filename):
        df = read_products_csv(st.session_state.filename)
        
        if not df.empty:
            # AI Insight Options
            insight_type = st.radio(
                "Choose an AI insight:",
                ["📊 Market Summary", "💎 Best Overall", "💰 Best Budget", "⚖️ Product Comparison", "🏆 Best Deal"],
                horizontal=True
            )
            
            if insight_type == "📊 Market Summary":
                st.markdown("#### Market Analysis")
                with st.spinner("🧠 AI is analyzing the market..."):
                    summary = get_ai_summary(st.session_state.filename)
                    st.markdown(f"```\n{summary}\n```")
            
            elif insight_type == "💎 Best Overall":
                st.markdown("#### Best Overall Product")
                with st.spinner("🧠 AI is finding the best product..."):
                    product, reason = get_best_overall_product(st.session_state.filename)
                    st.success(f"🌟 **{product}**")
                    st.info(f"**Why:** {reason}")
            
            elif insight_type == "💰 Best Budget":
                st.markdown("#### Best Budget Option")
                with st.spinner("🧠 AI is finding the best budget option..."):
                    product, reason = get_best_budget_option(st.session_state.filename)
                    st.success(f"💵 **{product}**")
                    st.info(f"**Why:** {reason}")
            
            elif insight_type == "⚖️ Product Comparison":
                st.markdown("#### Product Comparison")
                num_compare = st.slider("Number of products to compare", 2, 5, 3)
                with st.spinner(f"🧠 AI is comparing {num_compare} products..."):
                    comparison = compare_products(st.session_state.filename, num_compare)
                    st.markdown(f"```\n{comparison}\n```")
            
            elif insight_type == "🏆 Best Deal":
                st.markdown("#### Best Deal Recommendation")
                with st.spinner("🧠 AI is finding the best deal..."):
                    product, reason = recommend_best_deal_with_ai(st.session_state.filename)
                    st.success(f"🎯 **{product}**")
                    st.info(f"**Details:** {reason}")
        else:
            st.info("📭 No data available. Please scrape a product first.")
    else:
        st.info("📭 No data available. Please scrape a product first.")

# ==================== TAB 4: FILTERS & SORTING ====================
with tab4:
    st.markdown("### ⚙️ Advanced Filtering & Sorting")
    
    if st.session_state.filename and os.path.exists(st.session_state.filename):
        df = read_products_csv(st.session_state.filename)
        
        if not df.empty:
            df_filtered = df.copy()
            
            # Filters
            st.markdown("#### 🔍 Filters")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                price_range = st.slider(
                    "💵 Price Range",
                    float(df['current_price'].min()),
                    float(df['current_price'].max()),
                    (float(df['current_price'].min()), float(df['current_price'].max()))
                )
                df_filtered = df_filtered[
                    (df_filtered['current_price'] >= price_range[0]) &
                    (df_filtered['current_price'] <= price_range[1])
                ]
            
            with col2:
                rating_min = st.slider("⭐ Minimum Rating", 0.0, 5.0, 0.0)
                df_filtered = df_filtered[df_filtered['rating'] >= rating_min]
            
            with col3:
                sponsored_filter = st.radio("📢 Sponsored?", ["All", "Sponsored Only", "Non-Sponsored Only"])
                if sponsored_filter == "Sponsored Only":
                    df_filtered = df_filtered[df_filtered['is_sponsered'] == True]
                elif sponsored_filter == "Non-Sponsored Only":
                    df_filtered = df_filtered[df_filtered['is_sponsered'] == False]
            
            # Sorting
            st.markdown("#### 📊 Sorting")
            sort_by = st.selectbox(
                "Sort by:",
                ["Price (Low to High)", "Price (High to Low)", "Rating (High to Low)", 
                 "Discount (High to Low)", "Reviews (High to Low)"]
            )
            
            if sort_by == "Price (Low to High)":
                df_filtered = df_filtered.sort_values('current_price')
            elif sort_by == "Price (High to Low)":
                df_filtered = df_filtered.sort_values('current_price', ascending=False)
            elif sort_by == "Rating (High to Low)":
                df_filtered = df_filtered.sort_values('rating', ascending=False)
            elif sort_by == "Discount (High to Low)":
                df_filtered = df_filtered.sort_values('discount_percent', ascending=False)
            elif sort_by == "Reviews (High to Low)":
                df_filtered = df_filtered.sort_values('review_count', ascending=False)
            
            st.markdown("---")
            st.markdown(f"### 📋 Showing {len(df_filtered)} of {len(df)} products")
            
            # Display columns to show
            display_cols = ['product_title', 'current_price', 'rating', 'discount_percent', 'review_count', 'seller_name']
            available_cols = [col for col in display_cols if col in df_filtered.columns]
            
            st.dataframe(df_filtered[available_cols], use_container_width=True)
        else:
            st.info("📭 No data available. Please scrape a product first.")
    else:
        st.info("📭 No data available. Please scrape a product first.")

# ==================== TAB 5: EXPORT ====================
with tab5:
    st.markdown("### 💾 Export Data")
    
    if st.session_state.filename and os.path.exists(st.session_state.filename):
        df = read_products_csv(st.session_state.filename)
        
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # CSV Export
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=st.session_state.filename,
                    mime="text/csv"
                )
            
            with col2:
                # JSON Export
                try:
                    json_file = export_to_json(st.session_state.filename)
                    with open(json_file, 'r') as f:
                        json_data = f.read()
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_data,
                        file_name=json_file,
                        mime="application/json"
                    )
                except Exception as e:
                    st.error(f"Error exporting JSON: {e}")
            
            with col3:
                # Excel Export
                try:
                    excel_file = export_to_excel(st.session_state.filename)
                    with open(excel_file, 'rb') as f:
                        excel_data = f.read()
                    st.download_button(
                        label="📥 Download Excel",
                        data=excel_data,
                        file_name=excel_file,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Error exporting Excel: {e}")
            
            st.markdown("---")
            st.markdown("### 📊 Available Data Files")
            
            csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
            if csv_files:
                st.write("Found CSV files:")
                for file in csv_files:
                    size = os.path.getsize(file) / 1024  # Size in KB
                    st.write(f"- {file} ({size:.1f} KB)")
            else:
                st.info("No CSV files found.")
        else:
            st.info("📭 No data available. Please scrape a product first.")
    else:
        st.info("📭 No data available. Please scrape a product first.")
