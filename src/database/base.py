# ? All models that should be considered in db with alembic migrations
from src.database.base_class import Base
from src.user.models import User
from src.verify_phone.models import VerifyPhone
from src.permission.models import Permission
from src.role.models import Role, RolePermission
from src.agent.models import Agent, AgentAbility, AgentLocation
from src.ability.models import Ability
from src.capital_transfer.models import CapitalTransferEnum
from src.contract.models import Contract
from src.location.models import Location
from src.news.models import News
from src.organization.models import Organization
from src.position_request.models import PositionRequest
from src.user_message.models import UserMessage
from src.wallet.models import Wallet
from src.credit.models import Credit
from src.merchant.models import Merchant
from src.important_data.models import ImportantData
from src.fee.models import Fee
from src.transaction.models import Transaction, TransactionRow
from src.invoice.models import Invoice
from src.ticket.models import Ticket
from src.ticket_message.models import TicketMessage
from src.pos.models import Pos
from src.card.models import Card
from src.user_crypto.models import UserCrypto
from src.deposit.models import Deposit
from src.crypto.models import Crypto
from src.cash.models import Cash
from src.user_request.models import UserRequest
from src.installments.models import Installments
from src.band_card.models import BankCard
from src.withdraw.models import Withdraw
from src.log.models import Log
