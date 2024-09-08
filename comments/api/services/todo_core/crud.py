from httpx import AsyncClient
from fastapi import Depends, HTTPException, status


class TodoCoreCRUD:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get(self, resource: str, item_id: int = None, params: dict = None):
        url = f"{self.base_url}/{resource}/"
        if item_id:
            url += f"{item_id}/"
        async with AsyncClient() as client:
            response = await client.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    async def create(self, resource: str, data: dict):
        url = f"{self.base_url}/{resource}/"
        async with AsyncClient() as client:
            response = await client.post(url, json=data)
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    async def update(self, resource: str, item_id: int, data: dict):
        url = f"{self.base_url}/{resource}/{item_id}/"
        async with AsyncClient() as client:
            response = await client.put(url, json=data)
        if response.status_code in (200, 204):
            return response.json() if response.content else {}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    async def delete(self, resource: str, item_id: int):
        url = f"{self.base_url}/{resource}/{item_id}/"
        async with AsyncClient() as client:
            response = await client.delete(url)
        if response.status_code == 204:
            return {"detail": "Item deleted successfully"}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
