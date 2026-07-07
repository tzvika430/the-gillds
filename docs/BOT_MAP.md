# BOT MAP

Date: 2026-07-07

## Current Bot

Name:
@tzvikus_bot

File:
bot/src/bot.py

Size:
327 lines

Language:
Python

Framework:
pyTelegramBotAPI (telebot)


# Commands

## User Commands

/start
- Start bot

/time
- Show activity time

/balance
- Show user balance

/leaderboard
- Show ranking

/resources
- Show resources

/sell
- Sell resources

/market
- Marketplace

/buy
- Buy resources

/startsession
- Start earning session

/endsession
- End earning session


# Database

SQLite:

economy.db


Tables:

users

resources

market


# Main Modules

## User System

Functions:
- get_user
- update_time


## Economy

Functions:
- balance
- leaderboard


## Resources

Functions:
- get_resources
- resources_cmd


## Marketplace

Functions:
- buy_cmd
- sell_cmd
- market_cmd


## Sessions

Functions:
- start_session
- end_session


# Current Architecture

Single file:

bot.py


# Target Architecture

bot/

handlers/
- telegram commands

services/
- business logic

plugins/
- extensions

database/
- database layer


# Migration Status

Phase:
Analysis Complete


Next:
Modularization planning

