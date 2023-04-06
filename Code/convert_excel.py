import pandas as pd

def convert_excel_to_txt():
    with open('/Users/ellataira/Library/Mobile Documents/com~apple~CloudDocs/Desktop/'
              'is4200/homework--5-ellataira/qrel.txt', 'w') as file:
        pd.read_excel(
            '/Users/ellataira/Library/Mobile Documents/com~apple~'
            'CloudDocs/Desktop/is4200/homework--5-ellataira/Results/all_manual_rankings.xlsx').to_string(file, index=False)


convert_excel_to_txt()