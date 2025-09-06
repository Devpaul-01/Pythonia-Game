import random
import time
import threading

from battlecharacters import (
    enemy_list, players_list, player_skills,
    attack, enemy_turn, perform_power_attack,
    use_health_potion, use_mana_potion,
    level_up, check, scale_enemy, flavor_texts, skill_recharge_worker
)

# ---- Main loop ----
while True:
    print("\n🎮 Welcome To The Battle Of Pythonia 🎮")

    # list players & skills
    print("\nHere are the players:")
    for p in players_list:
        print(f" - {p['name']} ({p['Class']}) HP:{p['health']}/{p['max_health']} ATK:{p['attack']} Skills:{p['player_class']}")

    player_choice = input("\nEnter the name of player you would like to choose: ").strip()
    print("\nHere are the opponents:")
    for e in enemy_list:
        print(f" - {e['name']} HP:{e['health']}/{e.get('max_health', e['health'])} Skills:{e.get('enemy_class', [])}")

    enemy_choice = input("\nEnter the name of opponent you would like to go against: ").strip()

    result = check(player_choice, enemy_choice)
    if not result:
        continue
    player, enemy = result

    # Player chooses one skill to bring to the battle
    print(f"\n{player['name']} available skills: {player['player_class']}")
    chosen_skill = input("Choose one skill to bring into this battle (type exact skill name): ").strip().lower()
    if chosen_skill not in [s.lower() for s in player.get("player_class", [])]:
        print(f"❌ Invalid skill selection. Choose a skill from your list next time.")
        continue
    player["chosen_skill"] = chosen_skill
    # initialize per-battle skill counters & timestamps
    player["skill_uses"] = 1
    player["max_skill_uses"] = 2
    player["last_skill_recharge"] = time.time()

    # ensure runtime flags exist (safe)
    player.setdefault("defense_active", False)
    player.setdefault("phase_shift", False)
    player.setdefault("strength_active", False)
    player.setdefault("charge_active", False)
    player.setdefault("rage_vulnerable", False)
    enemy.setdefault("turns", 0)
    enemy.setdefault("blocking", False)
    threading.Thread(target=skill_recharge_worker, args=(player, ), daemon=True).start()


    print(f"\n⚔️ Battle start: {player['name']} vs {enemy['name']} (Chosen skill: {player['chosen_skill']})")

    # Battle loop
    while player["health"] > 0 and enemy["health"] > 0:

        # status
        print(f"\n📊 {player['name']} | HP: {player['health']}/{player['max_health']} | Level: {player['level']} | EXP: {player['exp']} | Inventory: {player['inventory']}")
        print(f"Skill: {player.get('chosen_skill')} (uses: {player.get('skill_uses',0)}/{player.get('max_skill_uses',2)})")
        print("Actions: (a)ttack  (p)ower  (s)kill(use skill)  (i)nventory  (d)efend  (st)strength  (ch)charge")

        action = input("Choose action: ").strip().lower()

        # ---------- Player actions ----------
        if action in ["a", "attack"]:
            attack(player, enemy)

        elif action in ["p", "power"]:
            perform_power_attack(player, enemy)

        elif action in ["s", "skill"]:
            # use chosen skill (if available)
            if player.get("skill_uses", 0) > 0:
                # fetch skill function from dispatcher
                skill_func = player_skills.get(player["chosen_skill"])
                if skill_func:
                    skill_func(player, enemy)
                    # consume one use and start recharge timer
                    player["skill_uses"] -= 1
                    player["last_skill_recharge"] = time.time()
                else:
                    print("❌ Skill function not implemented.")
            else:
                print("⏳ Skill not ready yet. Wait for recharge.")

        elif action in ["i", "inventory"]:
            if not player["inventory"]:
                print("❌ No items.")
            else:
                print("Inventory:", player["inventory"])
                pick = input("Use (h)ealth or (m)ana potion? ").strip().lower()
                if pick == "h":
                    use_health_potion(player)
                elif pick == "m":
                    use_mana_potion(player)
                else:
                    print("❌ Invalid item choice.")

        elif action in ["d", "defend"]:
            player["defense_active"] = True
            print(f"🛡️ {player['name']} braces for the next attack (shield active).")

        elif action in ["st", "strength"]:
            # immediate buff to next attack
            player["strength_active"] = True
            print(f"💪 {player['name']} channels strength for the next attack (+5).")

        elif action in ["ch", "charge"]:
            player["charge_active"] = True
            print(f"⚡ {player['name']} charges up for the next attack (+10).")

        else:
            print("❌ Invalid action. Try again.")
            continue  # skip enemy turn if invalid

        # ---------- Enemy turn ----------
        if enemy["health"] > 0:
            print(f"\nThe {enemy['name']} {random.choice(flavor_texts)}")
            enemy_turn(player, enemy)

        # ---------- Check outcomes ----------
        if enemy["health"] <= 0:
            print(f"\n✅ {enemy['name']} defeated!")
            player["exp"] += 50
            level_up(player)
            break

        if player["health"] <= 0:
            print(f"\n💀 {player['name']} was defeated!")
            break

    # after match finished
    option = input("\nPlay again? (yes/exit): ").strip().lower()
    if option == "exit":
        print("👋 Thanks for playing Pythonia!")
        break
    elif option == "yes":
        # pick a new enemy and scale to player's level
        enemy = random.choice(enemy_list)
        scale_enemy(enemy, player["level"])
        # keep player's current HP and status but reset temporary flags:
        player["defense_active"] = False
        player["phase_shift"] = False
        player["strength_active"] = False
        player["charge_active"] = False
        player["rage_vulnerable"] = False
        continue
    else:
        print("❌ Invalid option, returning to main menu.")