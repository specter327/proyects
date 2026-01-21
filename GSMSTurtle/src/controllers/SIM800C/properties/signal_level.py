# Library import
import time
from ....contracts.properties.signal_level import SignalLevel
from ....contracts.properties import PropertyInterface


class Property(PropertyInterface):
    """
    SignalLevel property implementation for SIM800C devices
    """

    def __init__(self, controller: object) -> None:
        self.controller = controller

        if not self.controller.connection_status:
            raise RuntimeError("Controller is not connected with the device")

        if not self.controller.ATEngine:
            raise RuntimeError("ATEngine is not initialized")

    # -------------------------
    # Public API
    # -------------------------

    def read(self) -> SignalLevel:
        at = self.controller.ATEngine

        # Enviar comando
        at.send_at_command("AT+CSQ")

        start = time.time()
        TIMEOUT = 2.5

        rssi_raw = None
        rssi_dbm = None
        ber = None

        response = at.read_at_response()

        for line in response.content:
            if b"ERROR" in line:
                raise RuntimeError("AT+CSQ returned ERROR")

            # Payload real
            if line.startswith(b"+CSQ:"):
                try:
                    payload = line.split(b":", 1)[1].strip()
                    rssi_str, ber_str = payload.split(b",")

                    rssi_raw = int(rssi_str)
                    ber = int(ber_str)

                    if rssi_raw == 99:
                        rssi_dbm = None
                    else:
                        rssi_dbm = -113 + (rssi_raw * 2)

                except Exception:
                    raise RuntimeError(
                        f"Malformed +CSQ response: {line}"
                    )

            # Terminación formal del comando
            if line == b"OK":
                # No salimos antes de tiempo: esperamos
                # a ver si ya llegó el +CSQ
                if rssi_raw is not None:
                    break

        # -------------------------
        # Validación final
        # -------------------------

        if rssi_raw is None:
            raise RuntimeError(
                f"AT+CSQ did not return signal data. Raw responses: {response.content}"
            )

        # Calidad normalizada GSM (0–100)
        signal_quality = max(
            0,
            min(100, int((rssi_dbm + 113) * 100 / 62))
        ) if rssi_dbm is not None else 0

        return SignalLevel(
            technology="GSM",
            rssi_raw=rssi_raw,
            rssi_dbm=rssi_dbm,
            ber=ber,
            rsrp=None,
            rsrq=None,
            sinr=None,
            signal_quality=signal_quality,
            timestamp=time.time()
        )
