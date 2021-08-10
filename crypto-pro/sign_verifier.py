from copy import copy
from typing import Optional

import settings
from Exceptions import NotSetCryptoProServerUrl, NoResponseReceived
from http_crypto import Request, Response
from settings import CRYPTOPRO_SERVER as URL


class SignVerifier:
    CRYPTOPRO_SERVER: Optional[str] = URL

    def __init__(self, content: bytes, sign: bytes) -> None:
        if not self.CRYPTOPRO_SERVER:
            raise NotSetCryptoProServerUrl

        self._response: Optional[Response] = None
        self._request: Request = Request(self.CRYPTOPRO_SERVER, content, sign)

    def is_valid(self) -> bool:
        """Проверка на то, является ли подпись валидной (действительной)"""
        if settings.VALIDATE_ON_CRYPTOPRO_SERVER:
            self._response = self._request.send()
            return self._response.status == Response.status_list['valid']
        else:
            print(
                'Внимание валидация файлов на CRYPTOPRO сервере отключена установите VALIDATE_ON_CRYPTOPRO_SERVER=True')
            return True

    @property
    def request(self) -> Request:
        """Возвращает объект запроса"""
        return copy(self._request)

    @property
    def response(self) -> Response:
        """Возвращает объект ответа"""
        if not self._response:
            raise NoResponseReceived

        return copy(self._response)

    @classmethod
    def set_cryptopro_url(cls, url: str) -> None:
        """Устанавливет URL сервера, к которому будут отправлены
        HTTP-запросы на проверку ЭЦП"""
        cls.CRYPTOPRO_SERVER = url
