from LLM.openai import ask_llm
from helpers.utils import read_products_csv


def recommend_best_deal_with_ai(filename: str) -> tuple:
    """Original single recommendation function - kept for compatibility"""
    try:
        df = read_products_csv(filename)

        # Use the correct column names from your data
        df = df[df['rating'] >= 4.0]
        df = df.sort_values(by=['current_price'])

        products_text = "\n".join(
            f"{row['product_title']} : {row['current_price']}$, {row['rating']}"
            for _, row in df.iterrows()
        )

        prompt = f"""Here is a list of Amazon products:
{products_text}

Give me the best value-for-money product, with a short explanation (max 2 sentences).
"""

        result = ask_llm(prompt)
        product = df.iloc[0]['product_title'] if not df.empty else "No product found"
        return product, result

    except Exception as e:
        return "Error", f"An error occurred: {e}"


def get_ai_summary(filename: str) -> str:
    """Generate AI summary of all products"""
    try:
        df = read_products_csv(filename)
        
        if df.empty:
            return "No products found to summarize."
        
        # Calculate statistics
        avg_price = df['current_price'].mean()
        avg_rating = df['rating'].mean()
        avg_discount = df['discount_percent'].mean()
        total_products = len(df)
        high_rated = len(df[df['rating'] >= 4.0])
        
        # Top 3 best deals
        best_deals = df[df['rating'] >= 3.5].nlargest(3, 'discount_percent')
        deals_text = "\n".join([
            f"- {row['product_title'][:60]}: {row['discount_percent']:.1f}% off, Rating: {row['rating']}, Price: ${row['current_price']:.2f}"
            for _, row in best_deals.iterrows()
        ])
        
        prompt = f"""Analyze these search results for products:
- Total products found: {total_products}
- Average price: ${avg_price:.2f}
- Average rating: {avg_rating:.2f} stars
- Average discount: {avg_discount:.1f}%
- High-rated products (4+ stars): {high_rated}

Top 3 deals:
{deals_text}

Provide a brief market analysis (3-4 sentences) highlighting:
1. Price range and value proposition
2. Quality indicator (ratings)
3. Best deals available
4. Overall recommendation for this product category
"""
        
        summary = ask_llm(prompt, temperature=0.5)
        return summary
    
    except Exception as e:
        return f"Error generating summary: {e}"


def get_best_budget_option(filename: str) -> tuple:
    """Find the best budget option (lowest price with decent rating)"""
    try:
        df = read_products_csv(filename)
        
        # Filter products with minimum 3.5 rating
        df_filtered = df[df['rating'] >= 3.5].copy()
        
        if df_filtered.empty:
            return "N/A", "No products with acceptable rating found"
        
        # Find cheapest with good rating
        best_budget = df_filtered.loc[df_filtered['current_price'].idxmin()]
        
        prompt = f"""A customer is looking for a budget option for {best_budget['product_title']}.

Product details:
- Title: {best_budget['product_title']}
- Price: ${best_budget['current_price']:.2f}
- Original Price: ${best_budget['original_price']:.2f}
- Discount: {best_budget['discount_percent']:.1f}%
- Rating: {best_budget['rating']} stars ({int(best_budget['review_count'])} reviews)
- Seller: {best_budget.get('seller_name', 'Amazon')}

Explain why this is a good budget choice (2-3 sentences), focusing on value for money.
"""
        
        explanation = ask_llm(prompt)
        return best_budget['product_title'], explanation
    
    except Exception as e:
        return "Error", f"An error occurred: {e}"


def get_best_overall_product(filename: str) -> tuple:
    """Find the best overall product (rating + discount + price balance)"""
    try:
        df = read_products_csv(filename)
        
        if df.empty:
            return "N/A", "No products found"
        
        # Calculate deal score
        df['deal_score'] = (df['rating'] * 0.5 + (df['discount_percent'] / 20) * 0.3 + 
                           (1 - (df['current_price'] / df['current_price'].max())) * 0.2)
        
        best_product = df.loc[df['deal_score'].idxmax()]
        
        prompt = f"""A customer wants the BEST OVERALL product choice.

Top product recommendation:
- Title: {best_product['product_title']}
- Price: ${best_product['current_price']:.2f}
- Original Price: ${best_product['original_price']:.2f}
- Discount: {best_product['discount_percent']:.1f}%
- Rating: {best_product['rating']} stars ({int(best_product['review_count'])} reviews)
- Seller: {best_product.get('seller_name', 'Amazon')}

Provide a compelling reason why this is the best choice (2-3 sentences), highlighting quality, value, and customer satisfaction.
"""
        
        explanation = ask_llm(prompt)
        return best_product['product_title'], explanation
    
    except Exception as e:
        return "Error", f"An error occurred: {e}"


def compare_products(filename: str, num_products: int = 3) -> str:
    """Compare top products and provide insights"""
    try:
        df = read_products_csv(filename)
        
        if df.empty:
            return "No products to compare."
        
        # Get top products by deal score
        df['deal_score'] = (df['rating'] * 0.5 + (df['discount_percent'] / 20) * 0.3 + 
                           (1 - (df['current_price'] / df['current_price'].max())) * 0.2)
        
        top_products = df.nlargest(num_products, 'deal_score')
        
        comparison_text = "\n\n".join([
            f"Product {i+1}: {row['product_title'][:60]}\n"
            f"  Price: ${row['current_price']:.2f} (Original: ${row['original_price']:.2f})\n"
            f"  Discount: {row['discount_percent']:.1f}%\n"
            f"  Rating: {row['rating']} stars ({int(row['review_count'])} reviews)\n"
            f"  Seller: {row.get('seller_name', 'Amazon')}"
            for i, (_, row) in enumerate(top_products.iterrows())
        ])
        
        prompt = f"""Compare these {num_products} top products and provide insights:

{comparison_text}

Provide a detailed comparison (4-5 sentences):
1. Which is best overall and why
2. Which is best for budget
3. Which has best quality indicators
4. Key differences and recommendations
"""
        
        comparison = ask_llm(prompt, temperature=0.6)
        return comparison
    
    except Exception as e:
        return f"Error comparing products: {e}"
