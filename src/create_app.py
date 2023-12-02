from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.ability.routes import router as ability_router
from src.agent.routes import router as agent_router
from src.auth.routes import router as auth_router
from src.capital_transfer.routes import router as capital_transfer_router
from src.card.routes import router as card_router
from src.contract.routes import router as contract_router
from src.core.config import settings
from src.credit.routes import router as credit_router
from src.crypto.routes import router as crypto_router
from src.fee.routes import router as fee_router
from src.important_data.routes import router as important_data_router
from src.invoice.routes import router as invoice_router
from src.location.routes import router as location_router
from src.media.routes import router as media_router
from src.merchant.routes import router as merchant_router
from src.news.routes import router as news_router
from src.organization.routes import router as organization_router
from src.permission.routes import router as permission_router
from src.pos.routes import router as pos_router
from src.role.routes import router as role_router
from src.ticket.routes import router as ticket_router
from src.cooperation_request.routes import router as cooperation_request_router
from src.installments.routes import router as installments_router
from src.ticket_message.routes import router as ticket_message_router
from src.transaction.routes import router as transaction_router
from src.user.routes import router as user_router
from src.user_crypto.routes import router as user_crypto_router
from src.user_message.routes import router as user_message_router
from src.verify_phone.routes import router as verify_phone_router
from src.wallet.routes import router as wallet_router
from src.cash.routes import router as cash_router
from src.zibal.routes import router as zibal_router
from src.user_request.routes import router as user_request_router
from src.position_request.routes import router as position_request_router
from src.log.routes import router as log_router
from src.withdraw.routes import router as withdraw_router
from src.band_card.routes import router as band_card_router
from src.deposit.routes import router as deposit_router
from src.capital_transfer.routes import router as capital_transfer_router


# ---------------------------------------------------------------------------
def create_fastapi_app():
    app = FastAPI(
        title=settings.APP_NAME,
        openapi_url=settings.OPENAPI_URL,
        default_response_class=ORJSONResponse,
    )
    app.include_router(user_router)
    app.include_router(auth_router)
    app.include_router(role_router)
    app.include_router(permission_router)
    app.include_router(verify_phone_router)
    app.include_router(credit_router)
    app.include_router(ability_router)
    app.include_router(agent_router)
    app.include_router(capital_transfer_router)
    app.include_router(merchant_router)
    app.include_router(transaction_router)
    app.include_router(invoice_router)
    app.include_router(contract_router)
    app.include_router(fee_router)
    app.include_router(important_data_router)
    app.include_router(location_router)
    app.include_router(news_router)
    app.include_router(organization_router)
    app.include_router(user_message_router)
    app.include_router(ticket_router)
    app.include_router(ticket_message_router)
    app.include_router(pos_router)
    app.include_router(card_router)
    app.include_router(user_crypto_router)
    app.include_router(crypto_router)
    app.include_router(wallet_router)
    app.include_router(media_router)
    app.include_router(position_request_router)
    app.include_router(cash_router)
    app.include_router(user_request_router)
    app.include_router(installments_router)
    app.include_router(log_router)
    app.include_router(zibal_router)
    app.include_router(withdraw_router)
    app.include_router(deposit_router)
    app.include_router(band_card_router)
    app.include_router(capital_transfer_router)
    app.include_router(cooperation_request_router)
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
