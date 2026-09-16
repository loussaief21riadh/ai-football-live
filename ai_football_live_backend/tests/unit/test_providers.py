import pytest

from app.providers.football_data.mock_provider import MockFootballProvider
from app.providers.ai.mocks.mock_provider import MockAIProvider
from app.providers.cache.memory_provider import InMemoryCacheProvider


class TestMockFootballProvider:
    @pytest.mark.asyncio
    async def test_get_live_matches(self):
        provider = MockFootballProvider()
        matches = await provider.get_live_matches()
        assert len(matches) > 0
        for match in matches:
            assert match.status.value in ("live", "halftime")

    @pytest.mark.asyncio
    async def test_get_leagues(self):
        provider = MockFootballProvider()
        leagues = await provider.get_leagues()
        assert len(leagues) == 3
        assert leagues[0].name == "Premier League"

    @pytest.mark.asyncio
    async def test_get_match_by_internal_id(self):
        provider = MockFootballProvider()
        match = await provider.get_match_by_internal_id(1)
        assert match is not None
        assert match.id == 1
        assert match.home_team.name == "Arsenal"

    @pytest.mark.asyncio
    async def test_get_match_not_found(self):
        provider = MockFootballProvider()
        match = await provider.get_match_by_internal_id(999)
        assert match is None


class TestMockAIProvider:
    @pytest.mark.asyncio
    async def test_generate_live_match(self):
        provider = MockAIProvider()
        import json
        user_prompt = json.dumps({
            "match": {"home_team": {"name": "Arsenal"}, "away_team": {"name": "Chelsea"}},
            "calculated_metrics": {"score_line": "2 - 1", "status": "live"},
        })
        result = await provider.generate("system", user_prompt)
        data = json.loads(result)
        assert "interpretation" in data
        assert "key_insights" in data
        assert "data_references" in data
        assert "2 - 1" in data["interpretation"]

    @pytest.mark.asyncio
    async def test_get_provider_name(self):
        provider = MockAIProvider()
        assert provider.get_provider_name() == "mock"


class TestInMemoryCacheProvider:
    @pytest.mark.asyncio
    async def test_set_and_get(self):
        cache = InMemoryCacheProvider()
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self):
        cache = InMemoryCacheProvider()
        result = await cache.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self):
        cache = InMemoryCacheProvider()
        await cache.set("key1", "value1")
        await cache.delete("key1")
        result = await cache.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_exists(self):
        cache = InMemoryCacheProvider()
        await cache.set("key1", "value1")
        assert await cache.exists("key1")
        assert not await cache.exists("nonexistent")

    @pytest.mark.asyncio
    async def test_ttl_expiration(self):
        cache = InMemoryCacheProvider()
        await cache.set("key1", "value1", ttl_seconds=1)
        result = await cache.get("key1")
        assert result == "value1"
