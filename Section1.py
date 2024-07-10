import pandas as pd
import matplotlib.pyplot as plt
import json
import numpy as np

# Load the JSON file
with open('P1- BankStatements.json') as f:
    data = json.load(f)

# Extracting the transactions from the nested JSON structure
transactions = data['Account']['Transactions']['Transaction']

# Convert the list of transactions into a DataFrame
df = pd.DataFrame(transactions)

# Define the relevant columns based on the JSON structure
amount_column = 'amount'  # Column with transaction amounts
transaction_type_column = 'type'  # Column with transaction type (CREDIT/DEBIT)
balance_column = 'currentBalance'  # Column with current balance after transaction
timestamp_column = 'transactionTimestamp'  # Column with transaction timestamps

# Convert 'amount' and 'currentBalance' to numeric, handling any errors
df[amount_column] = pd.to_numeric(df[amount_column], errors='coerce')
df[balance_column] = pd.to_numeric(df[balance_column], errors='coerce')

# Drop rows where 'amount' or 'currentBalance' couldn't be converted to a number
df = df.dropna(subset=[amount_column, balance_column])

# Ensure 'transactionTimestamp' is converted to datetime, coercing errors
df[timestamp_column] = pd.to_datetime(df[timestamp_column], errors='coerce')

# Drop rows where 'transactionTimestamp' couldn't be converted to datetime
df = df.dropna(subset=[timestamp_column])

# Analyze for unusual or suspicious transactions
# Calculate the mean and standard deviation of transaction amounts
mean_amount = df[amount_column].mean()
std_amount = df[amount_column].std()

# Define thresholds for unusual transactions (e.g., 3 standard deviations from the mean)
upper_threshold = mean_amount + 3 * std_amount
lower_threshold = mean_amount - 3 * std_amount

# Identify transactions that are unusually high or low
unusual_transactions = df[(df[amount_column] > upper_threshold) | (df[amount_column] < lower_threshold)]

# Generate alerts for low balance
# Define a low balance threshold (e.g., below 1000)
low_balance_threshold = 1000
low_balance_alerts = df[df[balance_column] < low_balance_threshold]

# Generate alerts for high expenditure periods
# Calculate daily expenditure
df['date'] = df[timestamp_column].dt.date
daily_expenditure = df[df[transaction_type_column].str.upper() == 'DEBIT'].groupby('date')[amount_column].sum()

# Define a high expenditure threshold (e.g., spending more than 5000 in a day)
high_expenditure_threshold = 5000
high_expenditure_alerts = daily_expenditure[daily_expenditure > high_expenditure_threshold]

# Plot the unusual transactions
plt.figure(figsize=(12, 6))
plt.scatter(df[timestamp_column], df[amount_column], label='Transactions', alpha=0.5)
plt.scatter(unusual_transactions[timestamp_column], unusual_transactions[amount_column], color='red', label='Unusual Transactions')
plt.title('Transaction Amounts with Unusual Transactions Highlighted')
plt.xlabel('Date')
plt.ylabel('Amount (INR)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('unusual_transactions.png')  # Save the plot as an image
plt.show()

# Plot the daily expenditure with high expenditure alerts
plt.figure(figsize=(12, 6))
daily_expenditure.plot(kind='line', label='Daily Expenditure', color='blue')
plt.axhline(y=high_expenditure_threshold, color='red', linestyle='--', label='High Expenditure Threshold')
plt.scatter(high_expenditure_alerts.index, high_expenditure_alerts, color='red', label='High Expenditure Alerts')
plt.title('Daily Expenditure with High Expenditure Alerts')
plt.xlabel('Date')
plt.ylabel('Total Amount Spent (INR)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('high_expenditure_alerts.png')  # Save the plot as an image
plt.show()

# Display the analyzed data
print("Unusual or Suspicious Transactions:")
print(unusual_transactions)

print("\nLow Balance Alerts:")
print(low_balance_alerts[[timestamp_column, balance_column]])

print("\nHigh Expenditure Alerts:")
print(high_expenditure_alerts)
