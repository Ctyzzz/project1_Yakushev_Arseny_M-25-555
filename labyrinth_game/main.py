#!/usr/bin/env python3
"""Точка входа в игру «Лабиринт сокровищ»."""

from labyrinth_game.constants import COMMANDS
from labyrinth_game.player_actions import (
    get_input,
    move_player,
    show_inventory,
    take_item,
    use_item,
)
from labyrinth_game.utils import (
    attempt_open_treasure,
    describe_current_room,
    show_help,
    solve_puzzle,
)


def process_command(game_state, command_line):
    """Разобрать и выполнить команду пользователя."""
    command_line = command_line.strip()
    if not command_line:
        return

    parts = command_line.split()
    verb = parts[0].lower()
    args = parts[1:]

    # Команды-направления (north, south, east, west)
    if verb in {"north", "south", "east", "west"}:
        move_player(game_state, verb)
        return

    match verb:
        case "go":
            if not args:
                print("Куда идти?")
                return
            direction = args[0].lower()
            move_player(game_state, direction)
        case "look":
            describe_current_room(game_state)
        case "inventory":
            show_inventory(game_state)
        case "take":
            if not args:
                print("Что вы хотите взять?")
                return
            item_name = " ".join(args)
            take_item(game_state, item_name)
        case "use":
            if not args:
                print("Что вы хотите использовать?")
                return
            item_name = " ".join(args)
            use_item(game_state, item_name)
        case "solve":
            if game_state["current_room"] == "treasure_room":
                attempt_open_treasure(game_state)
            else:
                solve_puzzle(game_state)
        case "help":
            show_help(COMMANDS)
        case "quit" | "exit":
            print("Вы решаете покинуть лабиринт. Игра окончена.")
            game_state["game_over"] = True
        case _:
            print("Неизвестная команда. Введите 'help' для списка команд.")


def main():
    """Запуск игры и основной игровой цикл."""
    game_state = {
        "player_inventory": [],
        "current_room": "entrance",
        "game_over": False,
        "steps_taken": 0,
    }

    print("Добро пожаловать в Лабиринт сокровищ!")
    print("Введите 'help', чтобы увидеть список команд.")
    describe_current_room(game_state)

    while not game_state["game_over"]:
        command_line = get_input("> ")
        if command_line is None:
            continue
        process_command(game_state, command_line)


if __name__ == "__main__":
    main()
