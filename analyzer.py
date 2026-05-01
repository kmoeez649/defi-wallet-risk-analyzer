import requests
from datetime import datetime, timezone

ETHERSCAN_API_KEY = "HZ5SB193VVPRG5VUBETYR35HPE33TTYXVT"
BASE_URL = "https://api.etherscan.io/v2/api?chainid=1"

def get_wallet_info(address):
    """Get basic wallet information"""
    
    # ETH Balance
    balance_url = (
        f"{BASE_URL}"
        f"?module=account"
        f"&action=balance"
        f"&address={address}"
        f"&tag=latest"
        f"&apikey={ETHERSCAN_API_KEY}"
    )
    
    balance_response = requests.get(
        balance_url
    ).json()
    
    eth_balance = 0
    if balance_response['status'] == '1':
        eth_balance = int(
            balance_response['result']
        ) / 1e18
    
    # Transaction History
    tx_url = (
        f"{BASE_URL}"
        f"?module=account"
        f"&action=txlist"
        f"&address={address}"
        f"&startblock=0"
        f"&endblock=99999999"
        f"&sort=asc"
        f"&apikey={ETHERSCAN_API_KEY}"
    )
    
    tx_response = requests.get(
        tx_url
    ).json()
    
    transactions = []
    if tx_response['status'] == '1':
        transactions = tx_response['result']
    
    return {
        'eth_balance': eth_balance,
        'transactions': transactions
    }

def analyze_wallet(address):
    """Main analysis function"""
    
    # Validate address
    if not address.startswith('0x') or \
       len(address) != 42:
        return {
            'error': 'Invalid wallet address. '
                    'Must start with 0x '
                    'and be 42 characters.'
        }
    
    # Get data
    wallet_data = get_wallet_info(address)
    transactions = wallet_data['transactions']
    eth_balance = wallet_data['eth_balance']
    
    # Basic stats
    total_tx = len(transactions)
    
    # Wallet age
    wallet_age_days = 0
    first_tx_date = "No transactions"
    
    if total_tx > 0:
        first_tx = transactions[0]
        first_timestamp = int(
            first_tx['timeStamp']
        )
        first_date = datetime.fromtimestamp(
            first_timestamp, 
            tz=timezone.utc
        )
        first_tx_date = first_date.strftime(
            "%B %d, %Y"
        )
        wallet_age_days = (
            datetime.now(timezone.utc) - 
            first_date
        ).days
    
    # Sent vs Received
    sent_count = 0
    received_count = 0
    failed_count = 0
    
    for tx in transactions:
        if tx['from'].lower() == \
           address.lower():
            sent_count += 1
        else:
            received_count += 1
            
        if tx['isError'] == '1':
            failed_count += 1
    
    # Failed transaction rate
    failed_rate = 0
    if total_tx > 0:
        failed_rate = (
            failed_count / total_tx
        ) * 100
    
    # Risk Score Calculation
    risk_score = 0
    risk_flags = []
    risk_positives = []
    
    # Flag 1: Very new wallet
    if wallet_age_days < 7:
        risk_score += 30
        risk_flags.append(
            "🔴 Wallet is less than "
            "7 days old — very new"
        )
    elif wallet_age_days < 30:
        risk_score += 15
        risk_flags.append(
            "🟡 Wallet is less than "
            "30 days old"
        )
    else:
        risk_positives.append(
            f"✅ Wallet age: "
            f"{wallet_age_days} days "
            f"— established"
        )
    
    # Flag 2: No transactions
    if total_tx == 0:
        risk_score += 20
        risk_flags.append(
            "🟡 No transaction history found"
        )
    elif total_tx < 5:
        risk_score += 10
        risk_flags.append(
            f"🟡 Very few transactions: "
            f"{total_tx}"
        )
    else:
        risk_positives.append(
            f"✅ Transaction history: "
            f"{total_tx} transactions"
        )
    
    # Flag 3: High failed rate
    if failed_rate > 20:
        risk_score += 25
        risk_flags.append(
            f"🔴 High failed transaction "
            f"rate: {failed_rate:.1f}%"
        )
    elif failed_rate > 10:
        risk_score += 10
        risk_flags.append(
            f"🟡 Elevated failed rate: "
            f"{failed_rate:.1f}%"
        )
    else:
        if total_tx > 0:
            risk_positives.append(
                f"✅ Low failed rate: "
                f"{failed_rate:.1f}%"
            )
    
    # Flag 4: Zero balance
    if eth_balance == 0 and total_tx > 0:
        risk_score += 10
        risk_flags.append(
            "🟡 Zero ETH balance"
        )
    elif eth_balance > 0:
        risk_positives.append(
            f"✅ ETH Balance: "
            f"{eth_balance:.4f} ETH"
        )
    
    # Cap at 100
    risk_score = min(risk_score, 100)
    
    # Risk Level
    if risk_score >= 60:
        risk_level = "🔴 HIGH RISK"
        risk_color = "red"
    elif risk_score >= 30:
        risk_level = "🟡 MEDIUM RISK"
        risk_color = "orange"
    else:
        risk_level = "🟢 LOW RISK"
        risk_color = "green"
    
    return {
        'address': address,
        'eth_balance': round(eth_balance, 4),
        'total_transactions': total_tx,
        'sent_transactions': sent_count,
        'received_transactions': received_count,
        'failed_transactions': failed_count,
        'failed_rate': round(failed_rate, 1),
        'wallet_age_days': wallet_age_days,
        'first_transaction_date': first_tx_date,
        'risk_score': risk_score,
        'risk_level': risk_level,
        'risk_color': risk_color,
        'risk_flags': risk_flags,
        'risk_positives': risk_positives
    }
