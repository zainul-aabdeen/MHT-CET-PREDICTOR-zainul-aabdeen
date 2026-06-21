import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.data_loader import data_loader
print('Total cap rows:', len(data_loader.cap_data))
print('Unique colleges:', data_loader.cap_data['college_name'].nunique())
print('Options categories count:', len(data_loader.options.get('categories', [])))
print('Options branches count:', len(data_loader.options.get('branches', [])))
