import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.cluster import KMeans
from datetime import datetime, timedelta

def prepare_time_series_data(transactions):
    """
    Prepare transaction data for time series analysis.
    """
    # Convert transactions to DataFrame
    df = pd.DataFrame([{
        'date': t.date,
        'amount': t.amount if t.transaction_type == 'income' else -t.amount,
        'category': t.category,
        'type': t.transaction_type
    } for t in transactions])
    
    # Sort by date
    df = df.sort_values('date')
    
    # Set date as index
    df.set_index('date', inplace=True)
    
    # Resample to daily frequency and fill missing values
    daily_amounts = df['amount'].resample('D').sum().fillna(0)
    
    return daily_amounts

def generate_cash_flow_forecast(transactions, forecast_days=30):
    """
    Generate cash flow forecast using RandomForestRegressor.
    """
    if not transactions:
        return []
    
    # Prepare time series data
    daily_amounts = prepare_time_series_data(transactions)
    
    # Create features (last 7 days of cash flow)
    X = []
    y = []
    window_size = 7
    
    for i in range(len(daily_amounts) - window_size):
        X.append(daily_amounts.iloc[i:i+window_size].values)
        y.append(daily_amounts.iloc[i+window_size])
    
    X = np.array(X)
    y = np.array(y)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Generate forecast
    forecast = []
    last_window = daily_amounts.iloc[-window_size:].values
    
    for _ in range(forecast_days):
        prediction = model.predict([last_window])[0]
        forecast.append(prediction)
        last_window = np.roll(last_window, -1)
        last_window[-1] = prediction
    
    # Create forecast dates
    last_date = daily_amounts.index[-1]
    forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
    
    return [{
        'date': date.strftime('%Y-%m-%d'),
        'amount': amount
    } for date, amount in zip(forecast_dates, forecast)]

def get_expense_recommendations(transactions):
    """
    Generate expense recommendations using clustering and classification.
    """
    if not transactions:
        return []
    
    # Convert transactions to DataFrame
    df = pd.DataFrame([{
        'amount': t.amount,
        'category': t.category,
        'date': t.date
    } for t in transactions])
    
    # Group by category
    category_stats = df.groupby('category').agg({
        'amount': ['sum', 'mean', 'count']
    }).reset_index()
    
    category_stats.columns = ['category', 'total_amount', 'avg_amount', 'transaction_count']
    
    # Scale features
    scaler = StandardScaler()
    features = scaler.fit_transform(category_stats[['total_amount', 'avg_amount', 'transaction_count']])
    
    # Cluster categories
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(features)
    
    # Analyze clusters and generate recommendations
    recommendations = []
    
    for cluster_id in range(3):
        cluster_categories = category_stats[clusters == cluster_id]
        
        if len(cluster_categories) > 0:
            # High spending categories
            if cluster_categories['total_amount'].mean() > category_stats['total_amount'].mean():
                for _, category in cluster_categories.iterrows():
                    recommendations.append({
                        'category': category['category'],
                        'type': 'reduction',
                        'message': f"Consider reducing spending in {category['category']}. "
                                 f"Current monthly average: {category['avg_amount']:.2f}"
                    })
            
            # Low frequency categories
            if cluster_categories['transaction_count'].mean() < category_stats['transaction_count'].mean():
                for _, category in cluster_categories.iterrows():
                    recommendations.append({
                        'category': category['category'],
                        'type': 'monitoring',
                        'message': f"Monitor spending in {category['category']}. "
                                 f"Irregular transaction pattern detected."
                    })
    
    return recommendations

def predict_cash_flow_status(transactions):
    """
    Predict cash flow status using historical data.
    """
    if not transactions:
        return 'neutral'
    
    # Prepare daily cash flow data
    daily_amounts = prepare_time_series_data(transactions)
    
    # Calculate features
    features = {
        'avg_daily_amount': daily_amounts.mean(),
        'volatility': daily_amounts.std(),
        'trend': daily_amounts.iloc[-7:].mean() - daily_amounts.iloc[-14:-7].mean(),
        'positive_days_ratio': (daily_amounts > 0).mean()
    }
    
    # Simple rule-based prediction
    if features['trend'] > 0 and features['avg_daily_amount'] > 0:
        return 'positive'
    elif features['trend'] < 0 or features['avg_daily_amount'] < 0:
        return 'negative'
    else:
        return 'neutral' 