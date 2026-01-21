# Library import
from . import PropertyInterface
from ..data_classes.primitive_data import PrimitiveData
from typing import Tuple
from dataclasses import dataclass

# Classes definition
class SignalLevel(PropertyInterface):
    # Class properties definition
    SUPPORTED_TECHNOLOGIES: Tuple[str] = (
        "GSM",
        "LTE",
        "WCDMA",
        "UNKNOWN"
    )

    def __init__(self,
        technology: str,
        rssi_raw: int | None,
        rssi_dbm: int | None,
        ber: int | None,
        rsrp: int | None,
        rsrq: int | None,
        sinr: int | None,
        signal_quality: int | None,
        timestamp: float
    ) -> None:
        # Instance properties assignment
        self.technology = PrimitiveData(
            data_type=str,
            minimum_length=1,
            maximum_length=None,
            possible_values=self.SUPPORTED_TECHNOLOGIES,
            content=technology
        )

        self.rssi_raw = PrimitiveData(
            data_type=None,
            minimum_length=None,
            maximum_length=None,
            possible_values=None,
            content=rssi_raw
        )

        self.rssi_dbm = PrimitiveData(
            data_type=None,
            minimum_length=None,
            maximum_length=None,
            possible_values=None,
            content=rssi_dbm
        )

        self.ber = PrimitiveData(
            data_type=int,
            minimum_length=None,
            maximum_length=None,
            possible_values=None,
            content=ber
        )

        self.rsrp = PrimitiveData(
            data_type=None,
            minimum_length=None,
            maximum_length=None,
            possible_values=None,
            content=rsrp
        )

        self.rsrq = PrimitiveData(
            data_type=None,
            minimum_length=None,
            maximum_length=None,
            possible_values=None,
            content=rsrq
        )

        self.sinr = PrimitiveData(
            data_type=None,
            minimum_length=None,
            maximum_length=None,
            possible_values=None,
            content=sinr
        )

        self.signal_quality = PrimitiveData(
            data_type=None,
            minimum_length=0,
            maximum_length=100,
            possible_values=None,
            content=signal_quality
        )

        self.timestamp = PrimitiveData(
            data_type=float,
            minimum_length=0,
            maximum_length=None,
            possible_values=None,
            content=timestamp
        )
    
    def to_dict(self) -> dict:
        return {
            "TECHNOLOGY":self.technology.content,
            "RSSI_RAW":self.rssi_raw.content,
            "RSSI_DBM":self.rssi_dbm.content,
            "BER":self.ber.content,
            "RSRP":self.rsrp.content,
            "RSRQ":self.rsrq.content,
            "SINR":self.sinr.content,
            "SIGNAL_QUALITY":self.signal_quality.content,
            "TIMESTAMP":self.timestamp.content
        }