# SLH INTEGRATION PLAN

Date: 2026-07-07

## Goal

Merge existing Telegram economy bot with SLH modular system.

Current:
Single file bot.py

Target:
Modular SLH Bot Platform


---

# Existing Components

## User System

Source:
bot.py

Keep:
- User registration
- Activity tracking
- Balance


## Economy

Source:
bot.py

Keep:
- Resources
- Marketplace
- Ranking


## Database

Current:
SQLite economy.db

Future:
Database service layer


---

# SLH Components To Integrate

## Admin System

Commands:
- status
- health
- logs
- backup
- monitor


## Agent System

Add:

Developer Agent
Tester Agent
Documentation Agent
Analyst Agent


## Plugin System

Create:

plugins/

Each feature becomes a plugin.


## Learning System

Integrate:

- courses
- progress
- tasks
- reports


---

# Migration Strategy

Phase 1:
Create modular structure.

Phase 2:
Move database logic.

Phase 3:
Move Telegram handlers.

Phase 4:
Add SLH commands.

Phase 5:
Testing.


---

# Rules

No direct rewrite.

Move one component at a time.

Every change:
- Backup
- Test
- Commit
- Document


END

