from collections import OrderedDict
from uuid import uuid4
from faker import Faker
from datetime import timedelta
from models.leads import Lead, LeadStage
from db.sql import get_session
from sqlmodel import delete
from utils.logger import logger

fake = Faker()
BATCH_SIZE = 500

def generate_fake_leads(n=50):
    leads = []
    for _ in range(n):
        created_at = fake.date_time_between(start_date="-1y", end_date="now", tzinfo=None)
        updated_at = created_at + timedelta(days=fake.random_int(min=0, max=30))
        last_contacted_at = created_at + timedelta(days=fake.random_int(min=0, max=60)) if fake.boolean() else None
        
        lead = Lead(
            id=uuid4(),
            name=fake.name(),
            email=fake.unique.email(),
            company_name=fake.company(),
            engaged=fake.random_choices(elements=OrderedDict([(True, 0.7), (False, 0.3)]), length=1)[0],
            stage=fake.enum(LeadStage),
            last_contacted_at=last_contacted_at,
            created_at=created_at,
            updated_at=updated_at
        )
        leads.append(lead)
    return leads

async def seed_leads(n=1000, clear_existing=False):
    try:
        session_gen = get_session()
        session = await session_gen.__anext__()

        if True:
            if clear_existing:
                statement = delete(Lead)
                await session.execute(statement)
                await session.commit()
            
            _n = n
            while _n > 0:
                leads = generate_fake_leads(min(_n, BATCH_SIZE))
                session.add_all(leads)
                await session.commit()

                _n = _n - BATCH_SIZE
                
                logger.info(f"Seeded batch with {BATCH_SIZE} leads successfully!")
            logger.info(f"Seeded all {n} leads successfully!")
    except Exception as e:
        logger.error(f"Exception in seed_leads ==> {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_leads(n=532, clear_existing=True))
