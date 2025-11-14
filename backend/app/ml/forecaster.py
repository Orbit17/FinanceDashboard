import numpy as np
from datetime import datetime, timedelta

class CashFlowForecaster:
    def forecast(self, transactions, current_balance, days=90):
        income = sum(t['amount'] for t in transactions if t['amount'] > 0)
        expenses = abs(sum(t['amount'] for t in transactions if t['amount'] < 0))
        
        daily_income = income / 30
        daily_expenses = expenses / 30
        daily_net = daily_income - daily_expenses
        
        forecast_data = []
        balance = current_balance
        
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            balance += daily_net + np.random.normal(0, 10)
            
            forecast_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted': round(balance, 2),
                'upper': round(balance * 1.15, 2),
                'lower': round(balance * 0.85, 2)
            })
        
        return forecast_data
