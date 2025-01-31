from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from django.conf import settings

class WebpayService:
    def __init__(self):
        self.tx = Transaction()

        if settings.WEBPAY_ENV == "TEST":
            self.tx.configure_for_testing()
        else:
            self.tx.configure_for_production(settings.WEBPAY_API_KEY, settings.WEBPAY_COMMERCE_CODE)

    def iniciar_pago(self, monto, orden_compra, url_retorno, url_final):
        response = self.tx.create(
            buy_order=orden_compra,
            session_id="session_" + orden_compra,
            amount=monto,
            return_url=url_retorno
        )
        return response

    def confirmar_pago(self, token_ws):
        return self.tx.commit(token_ws)

    def obtener_estado(self, token_ws):
        return self.tx.status(token_ws)
