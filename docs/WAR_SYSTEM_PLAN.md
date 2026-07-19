
## 3. Combat outcome

- Winner takes 10% of each of the loser's resources (8 physical resource
  types only — water, coal, copper, gold, wheat, soil, wood, stones).
  Gild itself is NOT part of this transfer.
- Protection rule: if taking 10% of a specific resource type would leave
  the loser below the amount needed to build the BASIC building
  (straw_house specifically, not any building), that resource type is
  not deducted from the loser.
- Even when a resource type is protected from the loser, the winner
  still receives their full 10% share of it (calculated from the loser's
  pre-battle amount), regardless of whether it was actually deducted.
- Winner additionally receives a flat +1 Gild reward for winning
  (independent of the resource percentage transfer above). This is a
  new, permanent Gild income source not tied to player-to-player trade.

## 4. Related economy fix — NPC resource purchase (implementable now,
     independent of the soldier system)

Problem identified: Gild currently only enters a player's wallet via the
10 Gild starting grant or by another player buying from their market
listing. This makes Gild scarce and creates full dependency on other
players being active buyers, which hurts retention especially early on
when there are few players.

Decision: players may buy any producible resource directly from the
game system (NPC), bypassing the player market, at a fixed rate:
  1 Gild = 200 units of any resource that can normally be produced.
This is a straightforward Gild-sink-relief valve: it does not directly
solve the Gild-earning problem (still need Gild to spend), but ensures
a player can always progress even with zero other active players,
as long as they already hold any Gild.

## 5. Status summary

- Combat rules (sections 1-3): documented only, NOT implemented.
  Blocked on soldier system existing.
- NPC resource purchase (section 4): documented, technically
  implementable immediately — does not depend on soldiers.
  Awaiting decision on implementation timing.

END OF WAR SYSTEM PLAN
