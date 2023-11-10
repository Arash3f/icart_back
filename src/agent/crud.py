from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ability.models import Ability
from src.agent.exception import AgentNotFoundException
from src.agent.models import Agent
from src.agent.schema import AgentUpdate
from src.database.base_crud import BaseCRUD


class AgentCRUD(BaseCRUD[Agent, None, AgentUpdate]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        agent_id: UUID,
    ) -> Type[Agent] | AgentNotFoundException:
        """
        ! Verify Agent Existence

        Parameters
        ----------
        db
            Target database connection
        agent_id
            Target Agent ID
        Returns
        -------
        obj
            Found Item

        Raises
        ------
        AgentNotFoundException
            Agent with this id not exist
        """
        obj = await db.get(entity=self.model, ident=agent_id)
        if not obj:
            raise AgentNotFoundException()

        return obj

    async def find_by_user_id(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
    ) -> Agent | AgentNotFoundException:
        """
        ! Find Agent by user id

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target Agent user ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        AgentNotFoundException
            Agent with this user_id not exist
        """
        response = await db.execute(
            select(self.model).where(self.model.user_id == user_id),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise AgentNotFoundException()

        return obj

    async def update_auto_data(self, *, db: AsyncSession) -> bool:
        """
        ! Update All Agent profit_rate

        Parameters
        ----------
        db
            Target database connection

        Returns
        -------
        res
            Result of operation
        """
        # * Find All Ability
        response = await db.execute(select(Ability))
        all_agent_ability_count = len(response.scalars().all())
        # * Find All Agent, is_main = False
        response = await db.execute(
            select(self.model).filter(
                self.model.is_main == False,
            ),
        )
        all_agents = response.scalars().all()

        mappings = []
        for agen in all_agents:
            # * Calculate interest rates
            agent_ability_count = len(agen.abilities)
            if agent_ability_count:
                new_profit_rate = (agent_ability_count * 100) / all_agent_ability_count
            else:
                new_profit_rate = 0
            # * Update Agent Is_Main field
            if new_profit_rate == 100:
                agen.is_main = True
            else:
                agen.is_main = False

            agen.profit_rate = new_profit_rate
            mappings.append(agent.__dict__)

        await db.run_sync(
            lambda session: session.bulk_update_mappings(
                mapper=self.model,
                mappings=mappings,
            ),
        )
        await db.commit()

        return True

    async def calculate_profit(
        self,
        *,
        db: AsyncSession,
        number_of_ability: int,
    ) -> float:
        """
        ! Calculate profit by number of active ability

        Parameters
        ----------
        db
            database connection
        number_of_ability
            number of active ability

        Returns
        -------
        profit_rate
            agent profit_rate
        """
        # * Find All Ability
        response = await db.execute(select(Ability))
        all_agent_ability_count = len(response.scalars().all())

        # * Calculate interest rates
        profit_rate = (number_of_ability * 100) / all_agent_ability_count

        return profit_rate


# ---------------------------------------------------------------------------
agent = AgentCRUD(Agent)
