import pickle
import os

class TransactionCategorizer:
    def __init__(self):
        self.rules = {
            'Groceries': ['whole foods', 'trader joe', 'safeway', 'kroger', 'walmart', 'grocery'],
            'Dining': ['restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'pizza', 'chipotle'],
            'Transportation': ['uber', 'lyft', 'gas', 'parking', 'metro', 'transit'],
            'Entertainment': ['netflix', 'spotify', 'hulu', 'movie', 'theater', 'concert'],
            'Utilities': ['electric', 'water', 'internet', 'phone', 'verizon', 'at&t'],
            'Shopping': ['amazon', 'target', 'best buy', 'mall', 'clothing'],
            'Healthcare': ['pharmacy', 'doctor', 'medical', 'hospital', 'cvs', 'walgreens'],
            'Income': ['salary', 'paycheck', 'deposit', 'transfer in', 'direct dep']
        }
    
    def predict(self, description):
        desc_lower = description.lower()
        for category, keywords in self.rules.items():
            if any(kw in desc_lower for kw in keywords):
                return {'category': category, 'confidence': 0.85}
        return {'category': 'Other', 'confidence': 0.65}
    
    def save(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
    
    def load(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                loaded = pickle.load(f)
                self.rules = loaded.rules
