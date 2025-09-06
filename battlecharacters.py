import random
import time

# -------------------------
# Player & Enemy Data
# -------------------------
players_list = [
    {
        "name": "Hero",
        "Class": "Quick Strike",
        "health": 100,
        "max_health": 100,
        "Power_Attack": 3,
        "phase_shift": False,
        "attack": (10, 20),
        "inventory": ["Health potion", "Speed potion"],
        "level": 1,
        "crit_chance": 0.10,
        "crit_multiplier": 2.0,
        "exp": 0,
        "player_class": ["shieldblock", "fireball"],
        # runtime flags (start false)
        "defense_active": False,
        "strength_active": False,
        "charge_active": False,
        "rage_vulnerable": False
    },
    {
        "name": "Tank",
        "Class": "Shield Master",
        "health": 150,
        "max_health": 150,
        "Power_Attack": 3,
        "phase_shift": False,
        "attack": (5, 10),
        "inventory": ["Health potion", "Mana potion", "Speed potion"],
        "player_class": ["phaseshift", "heal"],
        "level": 1,
        "crit_chance": 0.05,
        "crit_multiplier": 1.5,
        "exp": 0,
        "defense_active": False,
        "strength_active": False,
        "charge_active": False,
        "rage_vulnerable": False
    },
    {
        "name": "Mage",
        "Class": "Fire Sorcerer",
        "health": 80,
        "max_health": 100,
        "Power_Attack": 3,
        "phase_shift": False,
        "attack": (15, 25),
        "inventory": ["Mana potion", "Health potion", "Speed potion"],
        "player_class": ["rageattack", "fireball"],
        "level": 1,
        "crit_chance": 0.20,
        "crit_multiplier": 2.1,
        "exp": 0,
        "defense_active": False,
        "strength_active": False,
        "charge_active": False,
        "rage_vulnerable": False
    }
]

enemy_list = [
    {"name": "Goblin", "health": 100, "attack": (5, 10), "max_health": 120, "enemy_class": ["quickjab", "dodge"], "turns": 0, "blocking": False},
    {"name": "Skeleton", "health": 90, "attack": (7, 12), "max_health": 100, "enemy_class": ["boneshield", "bonestrike"], "turns": 0, "blocking": False},
    {"name": "Orc", "health": 100, "attack": (10, 15), "max_health": 120, "enemy_class": ["smash", "rage"], "turns": 0, "blocking": False},
    {"name": "Dragon", "health": 120, "attack": (15, 25), "max_health": 140, "enemy_class": ["firebreath", "winggust"], "turns": 0, "blocking": False}
]

flavor_texts = [
    "growls and charges at you!",
    "prepares a heavy strike... 👀",
    "circles around, looking for an opening.",
    "swings wildly in rage!"
]

# -------------------------
# Utilities
# -------------------------
def check(player_name, enemy_name):
    """Find player and enemy dicts by name (case-insensitive)."""
    player = None
    enemy = None
    for p in players_list:
        if p["name"].lower() == player_name.lower():
            player = p
            break
    if not player:
        print("❌ Invalid player choice. Try again.")
        return None
    for e in enemy_list:
        if e["name"].lower() == enemy_name.lower():
            enemy = e
            break
    if not enemy:
        print("❌ Invalid enemy choice. Try again.")
        return None
    return player, enemy
def skill_recharge_worker(player):
    while True:
        now = time.time()
        last = player.get("last_skill_recharge", now)
        elapsed = now - last
        if elapsed >= 20 and player.get("skill_uses", 0) < player.get("max_skill_uses", 2):
            player["skill_uses"] = player.get("skill_uses", 0) + 1
            player["last_skill_recharge"] = now
            print(f"⚡ {player['name']}'s skill recharged! Uses: {player['skill_uses']}/{player.get('max_skill_uses',2)}")
        time.sleep(1)

# -------------------------
# Player Attack (player -> enemy)
# -------------------------
def attack(player, enemy):
    """
    Player attack. Respects:
      - strength_active (+5 damage flat)
      - charge_active (+10 damage flat)
      - critical chance (multiplier)
      - enemy blocking (halves damage)
    """
    base_min, base_max = player["attack"]
    damage = random.randint(base_min, base_max)

    # strength buff (one attack)
    if player.get("strength_active", False):
        damage += 5
        player["strength_active"] = False
        print(f"💪 {player['name']} uses Strength boost (+5 damage)!")

    # charge buff (one attack)
    if player.get("charge_active", False):
        damage += 10
        player["charge_active"] = False
        print(f"⚡ {player['name']} strikes with a charged attack (+10 damage)!")

    # critical
    if random.random() < player.get("crit_chance", 0):
        damage = int(damage * player.get("crit_multiplier", 2.0))
        print(f"💥 CRITICAL! {player['name']} deals {damage} damage!")

    # enemy blocking halves incoming damage
    if enemy.get("blocking", False):
        damage //= 2
        enemy["blocking"] = False
        print(f"🛡️ {enemy['name']} blocked the hit! Damage reduced to {damage}.")

    enemy["health"] -= damage
    enemy["health"] = max(0, enemy["health"])
    print(f"{player['name']} hits {enemy['name']} for {damage} damage. {enemy['name']} HP: {enemy['health']}/{enemy.get('max_health', '?')}")

    return damage

# -------------------------
# Enemy Attack (enemy -> player)
# -------------------------
def enemy_attack(enemy, player):
    base_min, base_max = enemy["attack"]
    damage = random.randint(base_min, base_max)

    # Phase shift evades completely
    if player.get("phase_shift", False):
        print(f"👻 {player['name']} phases out and avoids the attack!")
        player["phase_shift"] = False
        return

    # Player defense halves damage (shieldblock)
    if player.get("defense_active", False):
        damage = damage // 2
        player["defense_active"] = False
        print(f"🛡️ {player['name']} blocks! Incoming damage reduced to {damage}.")

    # Player vulnerability after rage (1.5x)
    if player.get("rage_vulnerable", False):
        damage = int(damage * 1.5)
        player["rage_vulnerable"] = False
        print(f"⚠️ {player['name']} is vulnerable after raging! Takes extra damage.")

    player["health"] -= damage
    player["health"] = max(0, player["health"])
    print(f"💥 {enemy['name']} hits {player['name']} for {damage} damage. {player['name']} HP: {player['health']}/{player['max_health']}")

    return damage

# -------------------------
# Special enemy attack (every 3 turns)
# -------------------------
def enemy_special_attack(player, enemy):
    damage = random.randint(enemy["attack"][0] + 5, enemy["attack"][1] + 10)
    print(f"⚡ {enemy['name']} unleashes a SPECIAL attack!")

    # phase shift
    if player.get("phase_shift", False):
        print(f"👻 {player['name']} phases out and avoids the special attack!")
        player["phase_shift"] = False
        return

    # defense reduces
    if player.get("defense_active", False):
        damage = damage // 2
        player["defense_active"] = False
        print(f"🛡️ {player['name']} blocks the special! Damage reduced to {damage}.")

    if player.get("rage_vulnerable", False):
        damage = int(damage * 1.5)
        player["rage_vulnerable"] = False
        print(f"⚠️ {player['name']} is vulnerable after raging! Takes extra damage.")

    player["health"] -= damage
    player["health"] = max(0, player["health"])
    print(f"💥 {enemy['name']} hits {player['name']} for {damage} special damage. {player['name']} HP: {player['health']}/{player['max_health']}")

# -------------------------
# Enemy turn AI (uses your logic)
# -------------------------
def enemy_turn(player, enemy):
    enemy["turns"] = enemy.get("turns", 0) + 1
    if random.random() < 0.3:
        enemy["blocking"] = True
        print(f"🛡️ {enemy['name']} prepares to block!")
    else:
        if enemy["turns"] % 3 == 0:
            enemy_special_attack(player, enemy)
        else:
            enemy_attack(enemy, player)

# -------------------------
# Power attack & potions
# -------------------------
def perform_power_attack(player, enemy):
    if player.get("Power_Attack", 0) <= 0:
        print("❌ No Power Attacks left!")
        return
    base_min, base_max = player["attack"]
    damage = random.randint(base_min + 8, base_max + 15)
    player["Power_Attack"] -= 1
    print(f"🔥 {player['name']} unleashes a Power Attack! ({player['Power_Attack']} left)")
    enemy["health"] -= damage
    enemy["health"] = max(0, enemy["health"])
    print(f"{enemy['name']} takes {damage} damage. HP left: {enemy['health']}")

def use_health_potion(player):
    if "Health potion" not in player["inventory"]:
        print("❌ No health potions available.")
        return
    heal = random.randint(20, 30)
    player["health"] = min(player["health"] + heal, player["max_health"])
    player["inventory"].remove("Health potion")
    print(f"🧪 {player['name']} healed {heal} HP! Now at {player['health']}/{player['max_health']}.")

def use_mana_potion(player):
    if "Mana potion" not in player["inventory"]:
        print("❌ No mana potions available.")
        return
    heal = random.randint(15, 25)
    player["health"] = min(player["health"] + heal, player["max_health"])
    player["inventory"].remove("Mana potion")
    print(f"🔮 {player['name']} restored {heal} HP with Mana Potion!")

# -------------------------
# Leveling & scaling
# -------------------------
def level_up(player):
    # simple exp table (you can expand)
    exp_req = {1: 100, 2: 200, 3: 400, 4: 800}
    while True:
        next_lv = player["level"] + 1
        if next_lv not in exp_req:
            break
        if player["exp"] >= exp_req[next_lv]:
            player["exp"] -= exp_req[next_lv]
            player["level"] = next_lv
            player["max_health"] += 10
            player["health"] = player["max_health"]
            old_min, old_max = player["attack"]
            player["attack"] = (old_min + 2, old_max + 3)
            print(f"🎉 {player['name']} leveled up to {player['level']}! Max HP: {player['max_health']}, Attack: {player['attack']}")
        else:
            break
    return player

def scale_enemy(enemy, player_level):
    base_min, base_max = enemy["attack"]
    enemy["attack"] = (base_min + player_level, base_max + player_level)
    enemy["health"] = enemy.get("max_health", enemy["health"]) + (player_level * 10)
    enemy["turns"] = 0
    enemy["blocking"] = False

# -------------------------
# Player class skills & small buffs
# -------------------------
def shieldblock(player, enemy):
    player["defense_active"] = True
    print(f"🛡️ {player['name']} raises their shield and will reduce the next hit.")

def fireball(player, enemy):
    damage = random.randint(20, 30)
    enemy["health"] -= damage
    enemy["health"] = max(0, enemy["health"])
    print(f"🔥 {player['name']} casts Fireball! {enemy['name']} takes {damage} damage. HP left: {enemy['health']}")

def phaseshift(player, enemy):
    player["phase_shift"] = True
    print(f"👻 {player['name']} phases out and will dodge the next attack!")

def heal(player, enemy):
    heal_amount = int(player["max_health"] * 0.25)
    player["health"] = min(player["health"] + heal_amount, player["max_health"])
    print(f"💊 {player['name']} heals for {heal_amount} HP. Now at {player['health']}/{player['max_health']}")

def rageattack(player, enemy):
    # immediate double-damage hit, but mark player vulnerable next enemy hit
    damage = random.randint(player["attack"][0], player["attack"][1]) * 2
    enemy["health"] -= damage
    enemy["health"] = max(0, enemy["health"])
    player["rage_vulnerable"] = True
    print(f"😡 {player['name']} rages and deals {damage} damage! (Vulnerable next turn)")

def strength_buff(player, enemy):
    player["strength_active"] = True
    print(f"💪 {player['name']} channels strength: next attack +5 damage.")

def charge_buff(player, enemy):
    player["charge_active"] = True
    print(f"⚡ {player['name']} charges up: next attack +10 damage.")

# Dispatcher (name -> function)
player_skills = {
    "shieldblock": shieldblock,
    "fireball": fireball,
    "phaseshift": phaseshift,
    "heal": heal,
    "rageattack": rageattack,
    # buffs (also usable via action commands)
    "strength": strength_buff,
    "charge": charge_buff
}  