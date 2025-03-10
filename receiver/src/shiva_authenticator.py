from aiosmtpd.smtp import AuthResult, LoginPassword
from aiosmtpd.smtp import SMTP as SMTPServer
from aiosmtpd.smtp import Envelope as SMTPEnvelope
from aiosmtpd.smtp import Session as SMTPSession
import config


class Authenticator:
    def __call__(
        self,
        server: SMTPServer,
        session: SMTPSession,
        envelope: SMTPEnvelope,
        mechanism: str,
        auth_data,
    ) -> AuthResult:
        _config = config.get_config()
        resp = AuthResult(success=False, handled=False)
        if mechanism not in ("LOGIN", "PLAIN"):
            return resp
        if not isinstance(auth_data, LoginPassword):
            return resp

        username = auth_data.login
        password = auth_data.password
        if (
            username == _config["shiva"]["smpt_username"].encode()
            and password == _config["shiva"]["smtp_password"].encode()
        ):
            resp = AuthResult(success=True)

        return resp
