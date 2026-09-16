"""Seed the database with mock data for development."""
import asyncio
from datetime import datetime, timezone

from app.database.engine import async_session
from app.database.models import LeagueModel, TeamModel, MatchModel, MatchEventModel, MatchStatisticModel
from app.providers.football_data.mock_provider import MockFootballProvider


async def seed():
    provider = MockFootballProvider()

    async with async_session() as db:
        leagues = await provider.get_leagues()
        for league in leagues:
            existing = await db.get(LeagueModel, league.id)
            if not existing:
                db.add(LeagueModel(
                    id=league.id,
                    provider_name=league.provider_name,
                    external_id=league.external_id,
                    name=league.name,
                    country=league.country,
                    season=league.season,
                ))

        teams = provider._teams
        for team in teams:
            existing = await db.get(TeamModel, team.id)
            if not existing:
                db.add(TeamModel(
                    id=team.id,
                    provider_name=team.provider_name,
                    external_id=team.external_id,
                    name=team.name,
                    short_name=team.short_name,
                ))

        await db.commit()

        matches = provider._matches
        for match in matches:
            existing = await db.get(MatchModel, match.id)
            if not existing:
                db.add(MatchModel(
                    id=match.id,
                    provider_name=match.provider_name,
                    external_id=match.external_id,
                    league_id=match.league.id,
                    home_team_id=match.home_team.id,
                    away_team_id=match.away_team.id,
                    status=match.status.value,
                    minute=match.minute,
                    added_time=match.added_time,
                    home_score=match.home_score,
                    away_score=match.away_score,
                    ht_home_score=match.ht_home_score,
                    ht_away_score=match.ht_away_score,
                    match_date=match.match_date,
                    venue=match.venue,
                    referee=match.referee,
                ))

        await db.commit()

        events = provider._events
        for match_id, event_list in events.items():
            for event in event_list:
                existing = await db.get(MatchEventModel, event.id)
                if not existing:
                    db.add(MatchEventModel(
                        id=event.id,
                        match_id=event.match_id,
                        provider_name=event.provider_name,
                        external_event_id=event.external_event_id,
                        event_type=event.event_type.value,
                        minute=event.minute,
                        added_time=event.added_time,
                        team_id=event.team_id,
                        player_name=event.player_name,
                        assist_player=event.assist_player,
                        detail=event.detail,
                    ))

        await db.commit()

        stats = provider._statistics
        for match_id, stat_list in stats.items():
            for stat in stat_list:
                existing = await db.get(MatchStatisticModel, stat.id)
                if not existing:
                    db.add(MatchStatisticModel(
                        id=stat.id,
                        match_id=stat.match_id,
                        stat_type=stat.stat_type,
                        home_value=stat.home_value,
                        away_value=stat.away_value,
                    ))

        await db.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
