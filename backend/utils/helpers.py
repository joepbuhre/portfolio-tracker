from itertools import product
from typing import List
from uuid import uuid4
import pandas as pd
from hashlib import sha256

def set_uuid(df: pd.DataFrame, column_name: str = 'id'):
    df.loc[:, column_name] = [str(uuid4()) for _ in range(len(df.index))]
    return df

def set_hash(df: pd.DataFrame, column_name: str = 'hash') -> pd.DataFrame:
    df['hash'] = df.apply(lambda x: sha256(tuple(x)), axis=1)
    return df

def cross_apply(*lists: List):
    return list(map(list, product(*lists)))