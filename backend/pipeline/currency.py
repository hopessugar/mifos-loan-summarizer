"""
Currency utilities for international loan contract analysis.

Maps currency codes (ISO 4217) to display symbols and locale-appropriate
formatting. Used across the backend to eliminate hardcoded Rs./INR references.
"""

# ISO 4217 currency code → display symbol
CURRENCY_SYMBOLS = {
    'INR': '₹',
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
    'CNY': '¥',
    'KES': 'KSh',
    'UGX': 'USh',
    'TZS': 'TSh',
    'NGN': '₦',
    'GHS': 'GH₵',
    'ZAR': 'R',
    'BRL': 'R$',
    'MXN': 'MX$',
    'AUD': 'A$',
    'CAD': 'C$',
    'CHF': 'CHF',
    'SEK': 'kr',
    'NOK': 'kr',
    'DKK': 'kr',
    'PLN': 'zł',
    'CZK': 'Kč',
    'HUF': 'Ft',
    'RUB': '₽',
    'TRY': '₺',
    'KRW': '₩',
    'THB': '฿',
    'IDR': 'Rp',
    'MYR': 'RM',
    'PHP': '₱',
    'VND': '₫',
    'PKR': 'Rs',
    'BDT': '৳',
    'LKR': 'Rs',
    'NPR': 'Rs',
    'MMK': 'K',
    'AED': 'د.إ',
    'SAR': '﷼',
    'EGP': 'E£',
    'XOF': 'CFA',
    'XAF': 'FCFA',
    'RWF': 'RF',
    'MWK': 'MK',
    'ZMW': 'ZK',
    'ETB': 'Br',
    'COP': 'COL$',
    'PEN': 'S/',
    'ARS': 'AR$',
    'CLP': 'CL$',
}


def get_currency_symbol(currency_code: str | None) -> str:
    """Get the display symbol for a currency code.
    
    Returns the symbol if known, otherwise returns the code itself
    (e.g., 'XYZ' → 'XYZ').
    """
    if not currency_code:
        return '$'
    return CURRENCY_SYMBOLS.get(currency_code.upper(), currency_code.upper())


def format_currency(value, currency_code: str | None) -> str:
    """Format a monetary value with the correct currency symbol.
    
    Examples:
        format_currency(50000, 'INR') → '₹50,000'
        format_currency(1000, 'USD')  → '$1,000'
        format_currency(500, 'KES')   → 'KSh 500'
    """
    if value is None:
        return '—'
    
    symbol = get_currency_symbol(currency_code)
    
    try:
        formatted_number = f'{float(value):,.0f}'
    except (ValueError, TypeError):
        formatted_number = str(value)
    
    # Some symbols conventionally have a space before the number
    space_before = currency_code and currency_code.upper() in {
        'KES', 'UGX', 'TZS', 'CHF', 'SEK', 'NOK', 'DKK',
        'XOF', 'XAF', 'RWF', 'MWK', 'ZMW', 'ETB',
    }
    
    if space_before:
        return f'{symbol} {formatted_number}'
    return f'{symbol}{formatted_number}'


def format_currency_precise(value, currency_code: str | None) -> str:
    """Like format_currency but keeps 2 decimal places."""
    if value is None:
        return '—'
    
    symbol = get_currency_symbol(currency_code)
    
    try:
        formatted_number = f'{float(value):,.2f}'
    except (ValueError, TypeError):
        formatted_number = str(value)
    
    space_before = currency_code and currency_code.upper() in {
        'KES', 'UGX', 'TZS', 'CHF', 'SEK', 'NOK', 'DKK',
        'XOF', 'XAF', 'RWF', 'MWK', 'ZMW', 'ETB',
    }
    
    if space_before:
        return f'{symbol} {formatted_number}'
    return f'{symbol}{formatted_number}'
