"""Вспомогательные функции: описание комнат, события, загадки, помощь."""

import math

from labyrinth_game.constants import (
    COMMANDS,
    EVENT_PROBABILITY,
    PUZZLE_ALTERNATIVES,
    RANDOM_EVENT_TYPES,
    ROOMS,
    ROOM_HALL,
    ROOM_LIBRARY,
    ROOM_TREASURE,
    ROOM_TRAP,
    TRAP_DEATH_MODULO,
    TRAP_DEATH_THRESHOLD,
)


def describe_current_room(game_state):
    """Вывести описание текущей комнаты, предметов и выходов."""
    room_name = game_state["current_room"]
    room = ROOMS[room_name]

    print(f"\n== {room_name.upper()} ==")
    print(room["description"])

    if room["items"]:
        print("Заметные предметы: " + ", ".join(room["items"]))

    exits = ", ".join(room["exits"].keys())
    print(f"Выходы: {exits}")

    if room.get("puzzle") is not None:
        print("Кажется, здесь есть загадка (используйте команду solve).")


def show_help(commands=COMMANDS):
    """Показать список доступных команд."""
    print("\nДоступные команды:")
    for cmd, description in commands.items():
        print(f"  {cmd.ljust(16)} - {description}")


def pseudo_random(seed, modulo):
    """Вернуть детерминированное псевдослучайное число в диапазоне [0, modulo)."""
    if modulo <= 0:
        raise ValueError("modulo must be positive")

    x = math.sin(seed * 12.9898) * 43758.5453
    fractional = x - math.floor(x)
    return int(math.floor(fractional * modulo))


def trigger_trap(game_state):
    """Симулировать срабатывание ловушки с потерей предмета или смертью."""
    print("Ловушка активирована! Пол начинает дрожать...")

    inventory = game_state["player_inventory"]
    if inventory:
        index = pseudo_random(game_state["steps_taken"], len(inventory))
        lost_item = inventory.pop(index)
        print(f"Вы пытаетесь удержаться равновесии и роняете: {lost_item}.")
        return

    roll = pseudo_random(game_state["steps_taken"], TRAP_DEATH_MODULO)
    if roll < TRAP_DEATH_THRESHOLD:
        print("Пол обрушился под вами. Вы падаете в темноту...")
        print("Вы погибли. Игра окончена.")
        game_state["game_over"] = True
    else:
        print("Плиты сходятся обратно. Вы чудом остались живы.")


def random_event(game_state):
    """Случайные события, происходящие при перемещении игрока."""
    seed = game_state["steps_taken"]

    # Шанс, что событие вообще произойдёт
    if pseudo_random(seed, EVENT_PROBABILITY) != 0:
        return

    event_type = pseudo_random(seed + 1, RANDOM_EVENT_TYPES)
    current_room = ROOMS[game_state["current_room"]]
    inventory = game_state["player_inventory"]

    if event_type == 0:
        # Находка монетки
        if "coin" not in current_room["items"]:
            current_room["items"].append("coin")
        print("Вы замечаете на полу блестящую монетку.")
    elif event_type == 1:
        # Испуг
        print("Вдалеке слышится странный шорох...")
        if "sword" in inventory:
            print("Вы крепче сжимаете меч, и шорох быстро затихает.")
    else:
        # Ловушка в trap_room без факела
        if (
            game_state["current_room"] == ROOM_TRAP
            and "torch" not in inventory
            and not game_state["game_over"]
        ):
            print("Под ногами что-то щёлкает... Кажется, это ловушка.")
            trigger_trap(game_state)


def _normalize_answer(text):
    """Привести ответ к нормальной форме: обрезка пробелов и lower()."""
    return text.strip().lower()


def _is_correct_answer(user_answer, expected_answer):
    """Проверить ответ пользователя с учётом альтернативных вариантов."""
    key = _normalize_answer(expected_answer)
    user = _normalize_answer(user_answer)
    allowed = PUZZLE_ALTERNATIVES.get(key, {key})
    return user in allowed


def solve_puzzle(game_state):
    """Решение загадки в текущей комнате."""
    room_name = game_state["current_room"]
    room = ROOMS[room_name]
    puzzle = room.get("puzzle")

    if puzzle is None:
        print("Загадок здесь нет.")
        return

    question, correct_answer = puzzle
    print(question)
    try:
        user_answer = input("Ваш ответ: ")
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из попытки ответить на загадку.")
        return

    if _is_correct_answer(user_answer, correct_answer):
        print("Верно! Вы успешно решили загадку.")
        room["puzzle"] = None  # нельзя решить дважды
        _give_puzzle_reward(room_name, game_state)
    else:
        print("Неверно. Попробуйте снова.")
        if room_name == ROOM_TRAP:
            trigger_trap(game_state)


def _give_puzzle_reward(room_name, game_state):
    """Выдать награду за решение загадки, зависящую от комнаты."""
    inventory = game_state["player_inventory"]

    if room_name == ROOM_HALL:
        if "bronze_key" not in inventory:
            inventory.append("bronze_key")
            print("Сундук приоткрывается, и вы находите бронзовый ключ.")
        else:
            print("Сундук оказывается пустым.")
    elif room_name == ROOM_TRAP:
        if "trap_amulet" not in inventory:
            inventory.append("trap_amulet")
            print(
                "Ловушка деактивируется. Вы находите маленький амулет "
                "и забираете его."
            )
    elif room_name == ROOM_LIBRARY:
        if "treasure_key" not in inventory:
            inventory.append("treasure_key")
            print("Между страницами свитка вы находите ключ от сокровищницы.")
    else:
        print("Вы чувствуете, что стали мудрее, но ничего не находите.")


def attempt_open_treasure(game_state):
    """Попытка открыть сундук с сокровищем — ключом или кодом."""
    if game_state["current_room"] != ROOM_TREASURE:
        print("Здесь нет сундука с сокровищами.")
        return

    room = ROOMS[ROOM_TREASURE]
    inventory = game_state["player_inventory"]

    if "treasure_chest" not in room["items"]:
        print("Сундук уже открыт.")
        return

    # Есть ли ключ?
    if "treasure_key" in inventory:
        print("Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        room["items"].remove("treasure_chest")
        print("В сундуке сияют сокровища! Вы победили!")
        game_state["game_over"] = True
        return

    # Попытка взломать кодом
    print(
        "Сундук заперт. У вас нет подходящего ключа.\n"
        "Можно попробовать ввести код, чтобы взломать замок."
    )
    try:
        choice = input("Ввести код? (да/нет): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nВы отступаете от сундука.")
        return

    if choice != "да":
        print("Вы отступаете от сундука.")
        return

    question, correct_answer = room["puzzle"]
    print(question)
    try:
        code = input("Код: ")
    except (KeyboardInterrupt, EOFError):
        print("\nВы отказываетесь вводить код.")
        return

    if _is_correct_answer(code, correct_answer):
        print("Код верный! Замок щёлкает, и сундук открывается.")
        room["items"].remove("treasure_chest")
        print("Внутри — сокровище. Вы победили!")
        game_state["game_over"] = True
    else:
        print("Код неверен. Замок остаётся запертым.")
