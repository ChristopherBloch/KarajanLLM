#!/usr/bin/env python3
"""Test Aria API endpoints"""
import httpx
import json
import asyncio

API_BASE = "http://localhost:8000/api"


async def test_memories():
    """Test memory CRUD operations"""
    async with httpx.AsyncClient() as client:
        # Create memory
        print("Creating memory...")
        r = await client.post(f"{API_BASE}/memories", json={
            "key": "test_memory_1",
            "value": {"note": "This is a test", "count": 42},
            "category": "test"
        })
        print(f"  POST /memories: {r.status_code} - {r.text}")
        
        # Get memories
        print("\nGetting memories...")
        r = await client.get(f"{API_BASE}/memories")
        print(f"  GET /memories: {r.status_code} - {r.text[:200]}")
        
        # Get specific memory
        print("\nGetting specific memory...")
        r = await client.get(f"{API_BASE}/memories/test_memory_1")
        print(f"  GET /memories/test_memory_1: {r.status_code} - {r.text}")
        
        # Delete memory
        print("\nDeleting memory...")
        r = await client.delete(f"{API_BASE}/memories/test_memory_1")
        print(f"  DELETE /memories/test_memory_1: {r.status_code} - {r.text}")


async def test_thoughts():
    """Test thoughts endpoints"""
    async with httpx.AsyncClient() as client:
        # Create thought
        print("\nCreating thought...")
        r = await client.post(f"{API_BASE}/thoughts", json={
            "content": "Testing the API works correctly",
            "category": "test"
        })
        print(f"  POST /thoughts: {r.status_code} - {r.text}")
        
        # Get thoughts
        print("\nGetting thoughts...")
        r = await client.get(f"{API_BASE}/thoughts?limit=5")
        print(f"  GET /thoughts: {r.status_code} - {r.text[:200]}")


async def test_activities():
    """Test activity log endpoints"""
    async with httpx.AsyncClient() as client:
        # Create activity
        print("\nCreating activity...")
        r = await client.post(f"{API_BASE}/activities", json={
            "action": "test_run",
            "skill": "api_test",
            "details": {"test": True},
            "success": True
        })
        print(f"  POST /activities: {r.status_code} - {r.text}")
        
        # Get activities
        print("\nGetting activities...")
        r = await client.get(f"{API_BASE}/activities?limit=5")
        print(f"  GET /activities: {r.status_code} - {r.text[:200]}")


async def test_goals():
    """Test goals endpoints"""
    async with httpx.AsyncClient() as client:
        # Create goal
        print("\nCreating goal...")
        r = await client.post(f"{API_BASE}/goals", json={
            "goal_id": "test_goal_1",
            "title": "Test Goal",
            "description": "A test goal for API validation",
            "priority": 2
        })
        print(f"  POST /goals: {r.status_code} - {r.text}")
        
        # Get goals
        print("\nGetting goals...")
        r = await client.get(f"{API_BASE}/goals?limit=5")
        print(f"  GET /goals: {r.status_code} - {r.text[:200]}")


async def test_heartbeat():
    """Test heartbeat endpoints"""
    async with httpx.AsyncClient() as client:
        # Create heartbeat
        print("\nCreating heartbeat...")
        r = await client.post(f"{API_BASE}/heartbeat", json={
            "beat_number": 999,
            "status": "healthy",
            "details": {"test": True, "source": "api_test"}
        })
        print(f"  POST /heartbeat: {r.status_code} - {r.text}")
        
        # Get latest heartbeat
        print("\nGetting latest heartbeat...")
        r = await client.get(f"{API_BASE}/heartbeat/latest")
        print(f"  GET /heartbeat/latest: {r.status_code} - {r.text}")


async def main():
    print("=" * 60)
    print("Testing Aria API Endpoints")
    print("=" * 60)
    
    await test_memories()
    await test_thoughts()
    await test_activities()
    await test_goals()
    await test_heartbeat()
    
    print("\n" + "=" * 60)
    print("Tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
