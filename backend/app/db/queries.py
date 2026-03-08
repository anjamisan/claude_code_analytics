from sqlalchemy import text
from app.db.connection import get_db

async def get_all_events(db):
    query = text("SELECT * FROM telemetry_events;")
    result = await db.execute(query)
    return result.fetchall()

async def insert_event(db, event_data):
    query = text("""
        INSERT INTO telemetry_events (event_type, user_id, timestamp, data)
        VALUES (:event_type, :user_id, :timestamp, :data);
    """)
    await db.execute(query, event_data)
    await db.commit()

async def get_event_by_id(db, event_id):
    query = text("SELECT * FROM telemetry_events WHERE id = :event_id;")
    result = await db.execute(query, {"event_id": event_id})
    return result.fetchone()

async def delete_event(db, event_id):
    query = text("DELETE FROM telemetry_events WHERE id = :event_id;")
    await db.execute(query, {"event_id": event_id})
    await db.commit()