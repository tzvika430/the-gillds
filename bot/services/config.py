BASE_RATE = 0.003858
DB_PATH = "/data/data/com.termux/files/home/SLH-DEV/database/economy.db"
RESOURCE_RATES = {"water": 1/1000, "coal": 1/3000, "copper": 1/6000, "gold": 1/30000}
RESOURCE_EMOJI = {"water": "💧", "coal": "⚫", "copper": "🟠", "gold": "🥇", "wheat": "🌾", "soil": "🟤", "wood": "🪵", "stones": "🪨"}
ALL_RESOURCE_IDX = {"water": 1, "coal": 2, "copper": 3, "gold": 4, "wheat": 6, "soil": 7, "wood": 8, "stones": 9}
WORKER_RATE = 1/50
WORKER_TO_RESOURCE = {
    'soldier': None, 'commander': None, 'general': None, 'spy': None,
    'soldier': None,
    'commander': None,
    'general': None,"farmer": "wheat", "lumberjack": "wood", "water_drawer": "water", "coal_miner": "coal", "copper_miner": "copper", "gold_miner": "gold"}
FARMER_BYPRODUCTS = {"soil": 0.5, "stones": 0.5}
HIRE_COST = {"soldier": 2, "commander": 10, "general": 30, "spy": 8, "dragon": 50, "wardog": 25, "farmer": 1, "lumberjack": 1, "water_drawer": 1, "coal_miner": 2, "copper_miner": 3, "gold_miner": 5}
BUILDING_CAPACITY = {"straw_house": 4, "brick_house": 4, "barracks": 4, "spy_house": 4, "sawmill": 4}
WORKER_BUILDING = {"soldier": "barracks", "commander": "barracks", "general": "barracks", "spy": "spy_house", "dragon": "fortress", "wardog": "fortress", "farmer": "straw_house", "lumberjack": "sawmill", "water_drawer": "brick_house", "coal_miner": "brick_house", "copper_miner": "brick_house", "gold_miner": "brick_house"}
BUILDING_COST = {
    'barracks': {'soil': 200, 'stones': 200, 'wood': 100, 'copper': 50},
    'spy_house': {'soil': 300, 'stones': 200, 'wood': 150, 'gold': 50},
    'straw_house': {'wheat': 100, 'soil': 100, 'wood': 50, 'water': 20},
    'brick_house': {'soil': 200, 'stones': 200, 'wood': 100, 'water': 50},
    'sawmill': {'wood': 100, 'wheat': 50, 'soil': 50, 'coal': 50},
}

# ================ PREDATOR EVENT ================
PREDATOR_DAILY_THRESHOLD_PLAYERS = 10
PREDATOR_WEEKLY_SECONDS = 604800
PREDATOR_DAILY_SECONDS = 86400
TIGER_EAT_COUNT = 2
LION_EAT_COUNT = 1
PREDATOR_PROTECTED_TYPE = "farmer"
PREDATOR_PROTECTED_MIN = 1
# Future: soldier types reduce predation chance (not yet implemented, no soldier types exist yet)
# soldier: -1%, commander: -2%, general: -4%
SOLDIER_RISK_REDUCTION = {"soldier": 0.01, "commander": 0.02, "general": 0.04}

DEFAULT_BUILDING_CAPACITY = 4

NPC_BUY_RATE = 500

SOLDIER_REQUIREMENTS = {'commander': ('soldier', 6), 'general': ('commander', 3), 'spy': None}

DAILY_CONSUMPTION = {
    "water": {
        "farmer": 1, "lumberjack": 1, "water_drawer": 0.5,
        "coal_miner": 1, "copper_miner": 1, "gold_miner": 1,
        "soldier": 1, "commander": 2, "general": 3,
        "spy": 2
    },
    "gold": {
        "commander": 1, "general": 2,
        "spy": 1
    }
}

FORTRESS_COST = {"soil": 500, "stones": 500, "wood": 300, "gold": 100, "copper": 100}

UNIT_SCORE = {"soldier": 1, "commander": 2, "general": 3, "wardog": 4, "dragon": 5}
