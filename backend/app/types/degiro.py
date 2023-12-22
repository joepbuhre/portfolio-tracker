from enum import Enum



from enum import Enum

from sqlalchemy import Transaction, desc

class TransactionType(int, Enum):
    SELL_SHARES = 1  # Verkoop 3 @ 91,02 USD
    BUY_SHARES = 2  # Koop 2 @ 35,495 EUR
    FLATEX_INTEREST = 3  # Flatex Interest
    FLATEX_INTEREST_INCOME = 4  # Flatex Interest Income
    CURRENCY_EXCHANGE_OUTFLOW = 5  # Levantamento de divisa
    CURRENCY_EXCHANGE_INFLOW = 6  # Crédito de divisa
    CURRENCY_EXCHANGE = 7  # Crédito de divisa
    DEGIRO_TRANSACTION_COMISSION = 8  # Comissão de transação
    DEGIRO_CONNECTIVITY_COST = 9  # Custo de Conectividade DEGIRO 2021
    DEGIRO_CASH_SWEEP = 10  # Degiro Cash Sweep Transfer | #Flatex Cash Sweep Transfer
    DEPOSIT = 11  # Overboeking
    WITHDRAWAL = 12  # Withdrawal
    DIVIDEND = 13  # Dividendo
    DIVIDEND_TAX = 14  # Imposto sobre dividendo
    UNKNOWN = 15

def categorize_transaction(description: str):
    description_lower = description.lower()

    if "koop" in description_lower:
        return TransactionType.BUY_SHARES

    if "verkoop" in description_lower:
        return TransactionType.SELL_SHARES

    if "dividend" in description_lower:
        if "belasting" in description_lower:
            return TransactionType.DIVIDEND_TAX
        else:
            return TransactionType.DIVIDEND

    if "transactiekosten" in description_lower or "aansluitingskosten" in description_lower:
        return TransactionType.DEGIRO_TRANSACTION_COMISSION

    if "valuta" in description_lower:
        if "creditering" in description_lower:
            return TransactionType.CURRENCY_EXCHANGE_INFLOW
        elif "debitering" in description_lower:
            return TransactionType.CURRENCY_EXCHANGE_OUTFLOW
        else:
            return TransactionType.UNKNOWN

    if "interest income" in description_lower:
        return TransactionType.FLATEX_INTEREST_INCOME

    if "interest" in description_lower:
        return TransactionType.FLATEX_INTEREST

    if "cash sweep transfer" in description_lower:
        return TransactionType.DEGIRO_CASH_SWEEP
    
    if "ideal" in description_lower:
        return TransactionType.DEPOSIT

    if "reservation" in description_lower:
        return TransactionType.UNKNOWN

    return TransactionType.UNKNOWN
