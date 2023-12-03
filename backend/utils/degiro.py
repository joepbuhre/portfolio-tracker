import re
import locale
import pandas as pd

def extract_description(df: pd.DataFrame) -> pd.DataFrame:
    # Store the current locale
    original_locale = locale.getlocale()

    # Set the locale to Dutch
    locale.setlocale(locale.LC_NUMERIC, 'nl_NL')

    # Define a regular expression pattern to match the desired values
    pattern = r"(\d+)? @ ([\d\.,]+)?"

    # Apply the regex extraction and create new columns
    df[['quantity', 'share_price']] = df['description'].str.extract(pattern)

    # Convert the 'price' column to float using the Dutch locale
    df['share_price'] = df['share_price'].apply(lambda x: locale.atof(x) if pd.notnull(x) else x)

    # Restore the original locale
    locale.setlocale(locale.LC_NUMERIC, original_locale)

    # Display the resulting DataFrame
    return df
