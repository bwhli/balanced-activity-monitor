import json
from typing import Optional

from pydantic import BaseModel, validator


class Log(BaseModel):

    address: str
    block_number: int
    block_timestamp: int
    data: str
    indexed: str
    log_index: int
    method: str
    transaction_hash: str

    @validator("indexed")
    @classmethod
    def validate_indexed(cls, data):
        return cls._convert_hex_to_int(data)

    @validator("data")
    @classmethod
    def validate_data(cls, data):
        return cls._convert_hex_to_int(data)

    @staticmethod
    def _convert_hex_to_int(data):
        data = json.loads(data)
        formatted_data = []
        for element in data:
            if element[:2] == "0x" and element != "0x":
                formatted_data.append(int(element, 16))
            else:
                formatted_data.append(element)
        return formatted_data


class Tx(BaseModel):
    block_number: int
    block_timestamp: int
    data: str
    from_address: str
    hash: str
    method: str
    status: str
    to_address: str
    type: str
    value: str
    value_decimal: int

    @validator("data")
    @classmethod
    def validate_indexed(cls, data):
        return json.loads(data)
