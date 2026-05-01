import requests
from datetime import datetime, timezone

# APNI KEY YAHAN DAALO
API_KEY = "HZ5SB193VVPRG5VUBETYR35HPE33TTYXVT"

def get_eth_balance(address):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data['status'] == '1':
            return int(data['result']) / 1e18
    except:
        pass
    return 0

def get_transactions(address):
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={API_KEY}"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        if data['status'] == '1':
            return data['result']
    except:
        pass
    return []

def analyze_wallet(address):
    
    # Validate
    if not address or \
       not address.startswith('0x') or \
       len(address) != 42:
        return {
            'error': 'Invalid address. '
                    'Must start with 0x, '
                    '42 characters.'
        }
    
    # Fetch data
    eth_balance = get_eth_balance(address)
    transactions = get_transactions(address)
    total_tx = len(transactions)
    
    # Wallet age
    wallet_age_days = 0
    first_tx_date = "No transactions"
    
    if total_tx > 0:
        first_timestamp = int(
            transactions[0]['timeStamp']
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
    
    # Count tx types
    sent = 0
    received = 0
    failed = 0
    
    for tx in transactions:
        if tx['from'].lower() == \
           address.lower():
            sent += 1
        else:
            received += 1
        if tx.get('isError') == '1':
            failed += 1
    
    failed_rate = 0
    if total_tx > 0:
        failed_rate = (failed/total_tx)*100
    
    # Risk scoring
    risk_score = 0
    risk_flags = []
    risk_positives = []
    
    # Age check
    if wallet_age_days == 0:
        risk_score += 30
        risk_flags.append(
            "🔴 Brand new wallet"
        )
    elif wallet_age_days < 30:
        risk_score += 20
        risk_flags.append(
            f"🔴 Very new: "
            f"{wallet_age_days} days old"
        )
    elif wallet_age_days < 180:
        risk_score += 10
        risk_flags.append(
            f"🟡 Relatively new: "
            f"{wallet_age_days} days"
        )
    else:
        risk_positives.append(
            f"✅ Established wallet: "
            f"{wallet_age_days} days old"
        )
    
    # Transaction check
    if total_tx == 0:
        risk_score += 25
        risk_flags.append(
            "🔴 Zero transaction history"
        )
    elif total_tx < 10:
        risk_score += 15
        risk_flags.append(
            f"🟡 Very few transactions: "
            f"{total_tx}"
        )
    elif total_tx < 50:
        risk_score += 5
        risk_flags.append(
            f"🟡 Limited history: "
            f"{total_tx} transactions"
        )
    else:
        risk_positives.append(
            f"✅ Strong history: "
            f"{total_tx} transactions"
        )
    
    # Failed rate
    if failed_rate > 20:
        risk_score += 25
        risk_flags.append(
            f"🔴 High fail rate: "
            f"{failed_rate:.1f}%"
        )
    elif failed_rate > 10:
        risk_score += 10
        risk_flags.append(
            f"🟡 Elevated fail rate: "
            f"{failed_rate:.1f}%"
        )
    elif total_tx > 0:
        risk_positives.append(
            f"✅ Good success rate: "
            f"{100-failed_rate:.1f}%"
        )
    
    # Balance
    if eth_balance == 0 and total_tx > 0:
        risk_score += 10
        risk_flags.append(
            "🟡 Zero ETH balance"
        )
    elif eth_balance > 0:
        risk_positives.append(
            f"✅ Balance: "
            f"{eth_balance:.4f} ETH"
        )
    
    risk_score = min(risk_score, 100)
    
    if risk_score >= 60:
        risk_level = "🔴 HIGH RISK"
    elif risk_score >= 30:
        risk_level = "🟡 MEDIUM RISK"
    else:
        risk_level = "🟢 LOW RISK"
    
    return {
        'address': address,
        'eth_balance': round(eth_balance, 4),
        'total_transactions': total_tx,
        'sent_transactions': sent,
        'received_transactions': received,
        'failed_transactions': failed,
        'failed_rate': round(failed_rate, 1),
        'wallet_age_days': wallet_age_days,
        'first_transaction_date': first_tx_date,
        'risk_score': risk_score,
        'risk_level': risk_level,
        'risk_flags': risk_flags,
        'risk_positives': risk_positives
    }
