from uuid import uuid4
import pandas as pd

def set_uuid(df: pd.DataFrame, column_name: str = 'id'):
    df.loc[:, column_name] = [str(uuid4()) for _ in range(len(df.index))]
    return df

def set_hash(df: pd.DataFrame, column_name: str = 'hash') -> pd.DataFrame:
    df['hash'] = df.apply(lambda x: hash(tuple(x)), axis=1)
    return df