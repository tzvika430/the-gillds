# PLAYER CHAT PLAN

Status: Researched, planned only — NOT implemented yet.
Date: 2026-07-16

## 1. Technical constraint (confirmed via Telegram official docs)

A bot cannot initiate a conversation with a user. A user must either
add the bot to a group or message it first. Source:
https://core.telegram.org/bots
"Bots can't start conversations with users. A user must either add
them to a group or send them a message first."

This means there is NO native Bot API way for the bot to open a real
private chat directly between two players. This is a Telegram
platform limitation, not a limitation of our code.

## 2. Feasible solution: relay through the bot

Since every player has already messaged the bot (via /start), the bot
already has permission to message any of them directly. This enables
a relay/postman pattern:

  Player A sends the bot a message intended for Player B.
  The bot forwards it to Player B, labeled as coming from Player A.
  Player B can reply the same way, relayed back through the bot.

This is NOT a native Telegram private chat between A and B — it is a
bot-mediated relay. From the player's perspective, it behaves like
messaging, just always passing through the bot.

## 3. Proposed commands (not yet implemented)

  /players           - lists active players (username or first name)
  /msg <id> <text>    - sends <text> to player <id>, relayed via bot

## 4. Fallback — shared group chat

Simpler alternative requiring no relay logic: create one shared
Telegram group, provide an invite link, all players join and talk
openly. Lower engineering effort, no privacy between players.

## 5. Status summary

Relay-through-bot is the recommended approach (real private messaging,
technically compliant with Telegram's rules). Shared group chat
remains a low-effort fallback if development time is limited.

END OF PLAYER CHAT PLAN
