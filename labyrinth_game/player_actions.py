"""Действия игрока: ввод, перемещение, инвентарь, использование предметов."""

from labyrinth_game.constants import ROOMS, ROOM_TREASURE
from labyrinth_game.utils import describe_current_room, random_event


def get_input(prompt="> "):
    """Безопасно запросить ввод у пользователя."""
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"


def show_inventory(game_state):
    """Показать содержимое инвентаря игрока."""
    inventory = game_state["player_inventory"]
    if not inventory:
        print("Ваш инвентарь пуст.")
        return

    print("В вашем инвентаре: " + ", ".join(inventory))


def move_player(game_state, direction):
    """Переместить игрока в указанном направлении, если есть выход."""
    room_name = game_state["current_room"]
    room = ROOMS[room_name]
    exits = room["exits"]

    direction = direction.lower()
    if direction not in exits:
        print("Нельзя пойти в этом направлении.")
        return

    next_room = exits[direction]
    inventory = game_state["player_inventory"]

    # Особая логика при входе в treasure_room
    if next_room == ROOM_TREASURE and "rusty_key" not in inventory:
        print("Дверь заперта. Нужен ключ, чтобы пройти дальше.")
        return

    if next_room == ROOM_TREASURE and "rusty_key" in inventory:
        print("Вы используете найденный ключ, чтобы открыть путь "
              "в комнату сокровищ.")

    game_state["current_room"] = next_room
    game_state["steps_taken"] += 1

    describe_current_room(game_state)
    random_event(game_state)


def take_item(game_state, item_name):
    """Поднять предмет из комнаты и добавить его в инвентарь."""
    room_name = game_state["current_room"]
    room = ROOMS[room_name]

    if item_name == "treasure_chest":
        print("Вы не можете поднять сундук, он слишком тяжёлый.")
        return

    if item_name not in room["items"]:
        print("Такого предмета здесь нет.")
        return

    room["items"].remove(item_name)
    game_state["player_inventory"].append(item_name)
    print(f"Вы подняли: {item_name}")


def use_item(game_state, item_name):
    """Использовать предмет из инвентаря."""
    inventory = game_state["player_inventory"]

    if item_name not in inventory:
        print("У вас нет такого предмета.")
        return

    if item_name == "torch":
        print("Вы поднимаете факел. В комнате становится светлее.")
    elif item_name == "sword":
        print("Вы сжимаете меч и чувствуете прилив уверенности.")
    elif item_name == "bronze_box":
        print("Вы открываете бронзовую шкатулку.")
        if "rusty_key" not in inventory:
            inventory.append("rusty_key")
            print("Внутри вы находите ржавый ключ.")
        else:
            print("Но внутри вы ничего нового не находите.")
    else:
        print("Вы не знаете, как использовать этот предмет.")
