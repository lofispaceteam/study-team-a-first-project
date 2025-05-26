import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.mark.anyio
async def test_get_promotions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/promotions")
        assert response.status_code == 200

    data = response.json()
    assert "promotions" in data
    assert isinstance(data["promotions"], list)
    assert len(data["promotions"]) == 1

    for promo in data["promotions"]:
        assert "product" in promo
        assert "original_price" in promo
        assert "discount_price" in promo
        assert isinstance(promo["product"], str)
        assert isinstance(promo["original_price"], int)
        assert isinstance(promo["discount_price"], int)
        assert promo["discount_price"] < promo["original_price"]