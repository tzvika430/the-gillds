BASE_RATE = 0.003858
DB_PATH = "/data/data/com.termux/files/home/SLH-DEV/database/economy.db"
RESOURCE_RATES = {"water": 1/1000, "coal": 1/3000, "copper": 1/6000, "gold": 1/30000}
RESOURCE_EMOJI = {"water": "💧", "coal": "⚫", "copper": "🟠", "gold": "🥇", "wheat": "🌾", "soil": "🟤", "wood": "🪵", "stones": "🪨"}
ALL_RESOURCE_IDX = {"water": 1, "coal": 2, "copper": 3, "gold": 4, "wheat": 6, "soil": 7, "wood": 8, "stones": 9}
WORKER_RATE = 1/100
WORKER_TO_RESOURCE = {"farmer": "wheat", "lumberjack": "wood", "water_drawer": "water", "coal_miner": "coal", "copper_miner": "copper", "gold_miner": "gold"}
FARMER_BYPRODUCTS = {"soil": 0.3, "stones": 0.3}
HIRE_COST = {"farmer": 1, "lumberjack": 1, "water_drawer": 1, "coal_miner": 2, "copper_miner": 3, "gold_miner": 5}
BUILDING_CAPACITY = {"straw_house": 4, "brick_house": 4}
WORKER_BUILDING = {"farmer": "straw_house", "water_drawer": "brick_house", "coal_miner": "brick_house", "copper_miner": "brick_house", "gold_miner": "brick_house"}
BUILDING_COST = {
    'straw_house': {'wheat': 100, 'soil': 100, 'wood': 50},
    'brick_house': {'soil': 100, 'stones': 100, 'wood': 100},
    'sawmill': {'wood': 50, 'wheat': 50, 'soil': 50},
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
