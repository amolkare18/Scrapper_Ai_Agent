import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_price_distribution_chart(df: pd.DataFrame):
    """Create histogram of price distribution"""
    fig = px.histogram(
        df,
        x='current_price',
        nbins=20,
        title='Price Distribution',
        labels={'current_price': 'Price ($)', 'count': 'Number of Products'},
        color_discrete_sequence=['#FF9900']
    )
    fig.update_layout(hovermode='x unified', height=400)
    return fig


def create_rating_breakdown_chart(df: pd.DataFrame):
    """Create rating distribution chart"""
    rating_bins = [0, 2, 3, 4, 5]
    rating_labels = ['0-2 ⭐', '2-3 ⭐', '3-4 ⭐', '4-5 ⭐']
    df_copy = df.copy()
    df_copy['rating_group'] = pd.cut(df_copy['rating'], bins=rating_bins, labels=rating_labels, include_lowest=True)
    
    rating_counts = df_copy['rating_group'].value_counts().sort_index()
    
    fig = px.bar(
        x=rating_counts.index,
        y=rating_counts.values,
        title='Rating Distribution',
        labels={'x': 'Rating Group', 'y': 'Number of Products'},
        color=rating_counts.values,
        color_continuous_scale='Viridis'
    )
    fig.update_layout(hovermode='x unified', height=400, showlegend=False)
    return fig


def create_discount_vs_price_chart(df: pd.DataFrame):
    """Create scatter plot of discount vs price"""
    fig = px.scatter(
        df,
        x='current_price',
        y='discount_percent',
        size='rating',
        hover_data=['product_title', 'rating'],
        title='Discount vs Price (bubble size = rating)',
        labels={'current_price': 'Price ($)', 'discount_percent': 'Discount (%)'},
        color='rating',
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(height=400)
    return fig


def create_top_products_chart(df: pd.DataFrame, n: int = 10):
    """Create bar chart of top rated products"""
    top_products = df.nlargest(n, 'rating')[['product_title', 'rating', 'current_price']].copy()
    top_products['product_title'] = top_products['product_title'].str[:50] + '...'
    
    fig = px.bar(
        top_products,
        x='rating',
        y='product_title',
        orientation='h',
        title=f'Top {n} Rated Products',
        labels={'rating': 'Rating ⭐', 'product_title': 'Product'},
        color='rating',
        color_continuous_scale='Greens'
    )
    fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
    return fig


def create_best_deals_chart(df: pd.DataFrame, n: int = 10):
    """Create bar chart of best deals (highest discount + good rating)"""
    df_copy = df[df['rating'] >= 3.5].copy()
    df_copy['deal_score'] = (df_copy['discount_percent'] * 0.6 + df_copy['rating'] * 10)
    
    best_deals = df_copy.nlargest(n, 'deal_score')[['product_title', 'discount_percent', 'current_price', 'rating']].copy()
    best_deals['product_title'] = best_deals['product_title'].str[:50] + '...'
    
    fig = px.bar(
        best_deals,
        x='discount_percent',
        y='product_title',
        orientation='h',
        title=f'Top {n} Best Deals (Discount + Rating)',
        labels={'discount_percent': 'Discount %', 'product_title': 'Product'},
        color='rating',
        color_continuous_scale='Reds'
    )
    fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
    return fig


def create_summary_metrics(df: pd.DataFrame) -> dict:
    """Generate summary statistics"""
    if df.empty:
        return {
            'total_products': 0,
            'avg_price': 0,
            'avg_rating': 0,
            'avg_discount': 0,
            'price_range': '0 - 0'
        }
    
    return {
        'total_products': len(df),
        'avg_price': f"${df['current_price'].mean():.2f}",
        'avg_rating': f"{df['rating'].mean():.2f} ⭐",
        'avg_discount': f"{df['discount_percent'].mean():.1f}%",
        'price_range': f"${df['current_price'].min():.2f} - ${df['current_price'].max():.2f}",
        'sponsored_count': df['is_sponsered'].sum(),
        'high_rated': len(df[df['rating'] >= 4.0])
    }


def create_seller_distribution(df: pd.DataFrame):
    """Create pie chart of sellers"""
    if 'seller_name' not in df.columns or df['seller_name'].empty:
        return None
    
    seller_counts = df['seller_name'].value_counts().head(10)
    
    fig = px.pie(
        values=seller_counts.values,
        names=seller_counts.index,
        title='Top Sellers Distribution',
        hole=0.3
    )
    fig.update_layout(height=400)
    return fig


def create_comparison_table(products_list: list) -> pd.DataFrame:
    """Create comparison table for selected products"""
    comparison_data = []
    for product in products_list:
        comparison_data.append({
            'Title': product.get('product_title', ''),
            'Price': f"${product.get('current_price', 0):.2f}",
            'Original Price': f"${product.get('original_price', 0):.2f}",
            'Discount': f"{product.get('discount_percent', 0):.1f}%",
            'Rating': f"{product.get('rating', 0):.1f} ⭐",
            'Reviews': product.get('review_count', 0),
            'Seller': product.get('seller_name', 'N/A')
        })
    
    return pd.DataFrame(comparison_data)
