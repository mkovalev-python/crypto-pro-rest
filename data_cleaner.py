from base64 import b64encode
from functools import reduce
from typing import List


class DataCleaner:
    def __init__(self, content: bytes, sign: bytes) -> None:
        self._sign: bytes = sign
        self._content: bytes = content

    def clean_content(self) -> str:
        """Возвращает преобразованное содержимое"""
        return b64encode(self._content).decode('utf-8')

    def clean_sign(self) -> str:
        """Возвращает преобазованную (без лишних мета-данных) подпись"""
        try:
            string = self._sign.decode('utf-8')
            string = reduce(lambda a, b: a.replace(b, ''), self.get_sign_replacement(), string)
        except UnicodeDecodeError:
            string = b64encode(self._sign).decode('utf-8')
        return string

    @staticmethod
    def get_sign_replacement() -> List[str]:
        """Возвращает список строк, которые необходимо вырезать в теле подписи"""
        return [
            '-----BEGIN CMS-----',
            '----- BEGIN PKCS7 SIGNED -----',
            '----- END PKCS7 SIGNED -----',
            '-----END CMS-----',
            '\r\n',
            '\n'
        ]
