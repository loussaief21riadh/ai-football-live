import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from contextlib import asynccontextmanager


class TestLifespanStartup:
    @pytest.mark.asyncio
    async def test_lifespan_starts_sync_service(self):
        mock_sync = AsyncMock()
        mock_provider = MagicMock()

        with patch("app.providers.football.factory.create_football_provider", return_value=mock_provider):
            with patch("app.main.DataSyncService") as MockSync:
                MockSync.return_value = mock_sync

                from app.main import lifespan

                @asynccontextmanager
                async def _test_lifespan(app):
                    async with lifespan(app):
                        yield

                async with _test_lifespan(None):
                    MockSync.assert_called_once_with(mock_provider)
                    mock_sync.start.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_lifespan_stops_sync_service_on_shutdown(self):
        mock_sync = AsyncMock()
        mock_provider = MagicMock()

        with patch("app.providers.football.factory.create_football_provider", return_value=mock_provider):
            with patch("app.main.DataSyncService") as MockSync:
                MockSync.return_value = mock_sync

                from app.main import lifespan

                @asynccontextmanager
                async def _test_lifespan(app):
                    async with lifespan(app):
                        yield

                async with _test_lifespan(None):
                    pass

                mock_sync.stop.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_provider_selected_by_configuration(self):
        mock_sync = AsyncMock()
        mock_provider = MagicMock()

        with patch("app.providers.football.factory.create_football_provider", return_value=mock_provider) as mock_create:
            with patch("app.main.DataSyncService") as MockSync:
                MockSync.return_value = mock_sync

                from app.main import lifespan

                @asynccontextmanager
                async def _test_lifespan(app):
                    async with lifespan(app):
                        yield

                async with _test_lifespan(None):
                    mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_service_started_exactly_once(self):
        mock_sync = AsyncMock()
        mock_provider = MagicMock()

        with patch("app.providers.football.factory.create_football_provider", return_value=mock_provider):
            with patch("app.main.DataSyncService") as MockSync:
                MockSync.return_value = mock_sync

                from app.main import lifespan

                @asynccontextmanager
                async def _test_lifespan(app):
                    async with lifespan(app):
                        yield

                async with _test_lifespan(None):
                    assert mock_sync.start.await_count == 1

    @pytest.mark.asyncio
    async def test_lifespan_exception_during_start_still_stops(self):
        mock_sync = AsyncMock()
        mock_sync.start.side_effect = RuntimeError("start failed")
        mock_provider = MagicMock()

        with patch("app.providers.football.factory.create_football_provider", return_value=mock_provider):
            with patch("app.main.DataSyncService") as MockSync:
                MockSync.return_value = mock_sync

                from app.main import lifespan

                @asynccontextmanager
                async def _test_lifespan(app):
                    async with lifespan(app):
                        yield

                with pytest.raises(RuntimeError, match="start failed"):
                    async with _test_lifespan(None):
                        pass

    @pytest.mark.asyncio
    async def test_app_has_lifespan_configured(self):
        from app.main import app
        assert app.router.lifespan_context is not None
