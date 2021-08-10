class SignVerifierException(Exception):
    def get_client_message(self):
        """Возвращает сообщение, которое будет отображено клиенту
        в случае вызова исключения"""
        raise NotImplementedError


class NotSetCryptoProServerUrl(SignVerifierException):
    def __init__(self, *args: object) -> None:
        super().__init__('Not set jinn url. '
                         'Please, call class method `set_cryptopro_url`', *args)

    def get_client_message(self):
        return 'Возникла ошибка при обработке ЭЦП. Пожалуйста, обратитесь к разработчикам'


class NoResponseReceived(SignVerifierException):
    def __init__(self, *args: object) -> None:
        super().__init__('No response received. '
                         'Please, call instance method `is_valid`', *args)

    def get_client_message(self):
        return 'Возникла ошибка при обработке ЭЦП. Пожалуйста, обратитесь к разработчикам'


class IncorrectInputData(SignVerifierException):
    def __init__(self, *args: object) -> None:
        super().__init__('Incorrect input data', *args)

    def get_client_message(self):
        return 'Переданы некорректные данные'


class ConnectionTimeout(SignVerifierException):
    def __init__(self, *args: object) -> None:
        super().__init__('Connection timeout', *args)

    def get_client_message(self):
        return 'Произошла ошибка сервера проверки подписи - обратитесь, пожалуйста, в службу технической поддержки'
