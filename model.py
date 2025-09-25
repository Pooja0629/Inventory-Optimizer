from prophet import Prophet
import pandas as pd
import numpy as np

def get_forecast(component_data, periods=90):
    """
    Generates a forecast using Facebook Prophet for the given component data.
    Returns forecast VALUES (yhat) as numpy array for calculations.
    """
    try:
        # Prepare data for Prophet
        prophet_df = component_data[['Date', 'Units_Used']].copy()
        prophet_df = prophet_df.rename(columns={'Date': 'ds', 'Units_Used': 'y'})
        
        # Remove any NaN values
        prophet_df = prophet_df.dropna()
        
        if len(prophet_df) < 2:
            # Not enough data for forecasting, return simple average
            avg_demand = component_data['Units_Used'].mean()
            return np.array([avg_demand] * periods)
        
        # Initialize and fit the model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.95,
            seasonality_mode='multiplicative'
        )
        
        model.fit(prophet_df)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=periods, freq='D')
        
        # Generate forecast
        forecast_df = model.predict(future)
        
        # Return only the future forecast values (yhat) as numpy array
        future_forecast = forecast_df.tail(periods)['yhat'].values
        
        # Ensure no negative forecasts (inventory can't be negative)
        future_forecast = np.maximum(future_forecast, 0)
        
        return future_forecast
        
    except Exception as e:
        print(f"Error in get_forecast: {e}")
        # Fallback: return average demand
        avg_demand = component_data['Units_Used'].mean()
        return np.array([avg_demand] * periods)
