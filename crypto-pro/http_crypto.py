import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from copy import copy

import requests

from Exceptions import ConnectionTimeout
from data_cleaner import DataCleaner


class ValidationStatusConst:
    CONFIRMED = "Подпись верна"
    DENIED = "Подпись неверна"
    SOS = (
        "Недостаточно информации для определения статуса ни одной из имеющихся подписей, "
        "возможно в случае, если не найдены сертификаты авторов либо для них недоступны "
        "полные и актуальные СОС"
    )
    PARTIALLY_VALID = "Часть подписей действительна, часть – нет"
    NOT_CHECKED = "Подпись не проверялась"


class Response:
    status_list: Dict[str, str] = {
        "valid": ValidationStatusConst.CONFIRMED,
        "invalid": ValidationStatusConst.DENIED,
        "unknown": ValidationStatusConst.SOS,
        "partiallyValid": ValidationStatusConst.PARTIALLY_VALID,
    }

    def __init__(self, raw_text: str) -> None:
        try:
            self.response = json.loads(raw_text)[0]
            self.info_signer = self.response['SignerCertificateInfo']['SubjectName'].split(',')
            self.info_org = self.response['SignerCertificateInfo']['IssuerName'].split(',')
        except KeyError:
            self.response = json.loads(raw_text)

    @property
    def status(self) -> str:
        """Возвращает статус проверки ЭЦП"""
        if self.response.get('Result'):
            return self.status_list.get('valid')
        else:
            return self.status_list.get('invalid')

    @property
    def validation_date(self) -> datetime:
        """Возвращает дату проверки ЭЦП"""
        return datetime.now()

    @property
    def message(self) -> Optional[str]:
        return self.response.get('Message')

    @property
    def serial_number(self) -> Optional[str]:
        """Возвращает идентфикатор ЭЦП"""
        try:
            return self.response['SignerCertificateInfo']['SerialNumber']
        except KeyError:
            return self.response.get('Message')

    @property
    def thumbprint(self) -> Optional[str]:
        """Возвращает отпечаток ЭЦП"""
        try:
            return self.response['SignerCertificateInfo']['Thumbprint']
        except KeyError:
            return self.response.get('Message')

    @property
    def validity_before_date(self) -> Optional[datetime]:
        """Возвращает дату с которой сертификат действителен"""
        try:
            return datetime.strptime(self.response['SignerCertificateInfo']['NotBefore'], "%Y-%m-%dT%H:%M:%S")
        except KeyError:
            return self.response.get('Message')

    @property
    def validity_after_date(self):
        """Возвращает дату с которой сертификат действителен"""
        try:
            return datetime.strptime(self.response['SignerCertificateInfo']['NotAfter'], "%Y-%m-%dT%H:%M:%S")
        except KeyError:
            return self.response.get('Message')

    @property
    def snils_signer(self) -> Optional[str]:
        """Возвращает СНИЛС подписанта ЭЦП"""
        try:
            return self.info_signer[11][7:]
        except AttributeError:
            return self.response.get('Message')

    @property
    def inn_signer(self) -> Optional[str]:
        """Возвращает ИНН подписанта ЭЦП"""
        try:
            return self.info_signer[12][5:]
        except AttributeError:
            return self.response.get('Message')

    @property
    def ogrn_signer(self) -> Optional[str]:
        """Возвращает ОГРН подписанта ЭЦП"""
        try:
            return self.info_signer[10][6:]
        except AttributeError:
            return self.response.get('Message')

    @property
    def subject_org(self) -> Optional[str]:
        """Получить информацию об организации-подписанте"""
        try:
            return self.info_signer[8][3:]
        except AttributeError:
            return self.response.get('Message')

    @property
    def signer(self) -> Optional[str]:
        """Возвращает ФИО подписанта"""
        try:
            return self.info_signer[2][3:]
        except AttributeError:
            return self.response.get('Message')

    @property
    def position_signer(self) -> Optional[str]:
        """Возвращает должность подписанта"""
        try:
            return self.info_signer[9][3:]
        except AttributeError:
            return self.response.get('Message')

    @property
    def issuer_org(self) -> Optional[str]:
        """Получить информацию об организации, выпустившую ЭЦП"""
        try:
            return self.info_org[1][3:]
        except AttributeError:
            return self.response.get('Message')

    @property
    def signing_date(self) -> Optional[datetime]:
        """Возвращает дату подписания документа"""
        try:
            return datetime.strptime(self.response['SignatureInfo']['LocalSigningTime'],
                                     "%Y-%m-%dT%H:%M:%S") + timedelta(
                hours=3)
        except KeyError:
            return self.response.get('Message')

    @property
    def email_signer(self) -> Optional[str]:
        """Возвращает email подписанта"""
        try:
            return self.info_signer[13][3:]
        except AttributeError:
            return self.response.get('Message')

    @property
    def ogrn_org(self) -> Optional[str]:
        """Возвращает ОГРН организации, выпустившую ЭЦП"""
        try:
            return self.info_org[6][6:]
        except AttributeError:
            return self.response.get('Message')

    @property
    def email_org(self) -> Optional[str]:
        """Возвращает email организации, выпустившую ЭЦП"""
        try:
            return self.info_org[7][3:]
        except AttributeError:
            return self.response.get('Message')


class Request:

    def __init__(self, url: str, content: bytes, sign: bytes) -> None:
        self.url: str = url
        self.cleaner: DataCleaner = DataCleaner(content, sign)

        self._headers: Dict[str, str] = self._prepare_headers()
        self._body: dict = self._prepare_body()

    def send(self) -> Response:
        """Отправляет HTTP запрос на CRYPTOPRO сервер для проверки ЭЦП"""
        try:
            response: requests.Response = requests.post(
                f"{self.url}/rest/api/signatures", headers=self._headers, data=json.dumps(self._body), timeout=10
            )
        except requests.exceptions.ConnectTimeout:
            raise ConnectionTimeout()
        return Response(response.text)

    @property
    def headers(self) -> Dict[str, str]:
        """Возвращает заголовки HTTP запроса"""
        return copy(self._headers)

    @property
    def body(self) -> dict:
        """Возвращает тело HTTP запроса"""
        return self._body

    def _prepare_body(self) -> dict:
        """Подготавливает тело запроса"""

        return {
            "SignatureType": 5,
            "Content": self.cleaner.clean_sign(),
            "Source": self.cleaner.clean_content()
        }

    @staticmethod
    def _prepare_headers() -> Dict[str, str]:
        """Подготавливает заголовки для построения запроса"""
        return {
            "Content-Type": 'application/json',
            "Cache-Control": 'no-cache'
        }
