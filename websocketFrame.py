class WebsocketFrame:
    _fin = 0
    _rsv1 = 0
    _rsv2 = 0
    _rsv3 = 0
    _opcode = 0
    _payload_length = 0
    _payload_data = b''

    def populateFromWebsocketFrameMessage(self, data_in_bytes):
        self._parse_flags(data_in_bytes)
        self._parse_payload_length(data_in_bytes)
        self._maybe_parse_masking_key(data_in_bytes)
        self._parse_payload(data_in_bytes)

    def _parse_flags(self, data_in_bytes):
        first_byte = data_in_bytes[0]
        self._fin    = first_byte & 0b10000000
        self._rsv1   = first_byte & 0b01000000
        self._rsv2   = first_byte & 0b00100000
        self._rsv3   = first_byte & 0b00010000
        self._opcode = first_byte & 0b00001111

        second_byte = data_in_bytes[1]
        self._mask = second_byte & 0b10000000

    def _parse_payload_length(self, data_in_bytes):
        payload_length = (data_in_bytes[1]) & 0b01111111
        mask_key_start = 2
        if payload_length == 126:
            payload_length = int.from_bytes(
                (bytes(payload_length) + data_in_bytes[2:4]),
                byteorder='big')
            mask_key_start = 4
        elif payload_length == 127:
            payload_length = int.from_bytes(
                (bytes(payload_length) + data_in_bytes[2:9]),
                byteorder='big')
            mask_key_start = 10
        self._payload_length = payload_length
        self._mask_key_start = mask_key_start

    def _maybe_parse_masking_key(self, data_in_bytes):
        if not self._mask:
            return
        self._masking_key = data_in_bytes[
            self._mask_key_start:self._mask_key_start + 4]

    def _parse_payload(self, data_in_bytes):
        payload_data = b''
        if (self._payload_length == 0):
            return payload_data
        if self._mask:
            payload_start = self._mask_key_start + 4
            encoded_payload = data_in_bytes[payload_start:]
            decoded_payload = [
                byte ^ self._masking_key[i % 4]
                for i, byte in enumerate(encoded_payload)]
            payload_data = bytes(decoded_payload)
        else:
            payload_start = self._mask_key_start
            payload_data = data_in_bytes[payload_start:]
        self._payload_data = payload_data

    def get_payload_data(self):
        return self._payload_data

