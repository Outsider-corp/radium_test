"""
Вспомогательные функции.

Несколько вспомогательных функций для работы скрипта.
"""
import os
from typing import List


def getea_api_url(git_pero: str) -> str:
    """
    Получение ссылки API для Gitea репозитория.

    :param git_pero: str - ссылка на Gitea репозиторий
    :return: str - ссылка API на содержимое репозитория

    """
    start_link = 'https:/'
    add_link = 'api/v1/repos'
    git_link_parts = git_pero.split('/')
    if git_pero.startswith(start_link):
        git_link_parts.insert(3, add_link)
    else:
        git_link_parts.insert(1, add_link)
        git_link_parts.insert(0, start_link)
    if git_link_parts[-1].endswith('.git'):
        git_link_parts[-1] = git_link_parts[-1][:-4]
    git_link_parts.append('contents')
    return '/'.join(git_link_parts)


def split_list(lst: List, parts_count: int = 0) -> List[List]:
    """
    Разбиение списка на равные части.

    :param lst: list - список, который нужно разбить на части
    :param parts_count: int - количество частей
    :return: list - список, состоящий из частей

    """
    if parts_count:
        part_size = len(lst) // parts_count
        files_parts = []
        for ind in range(parts_count):
            start = part_size * ind
            end = part_size * (ind + 1)
            files_parts.append(lst[start:end])
        if end < len(lst):
            files_parts[-1].extend(lst[end:])
    else:
        files_parts = [[part] for part in lst]
    return files_parts


def get_full_path(prev_path: str, new_path: str) -> str:
    """
    Получение полного пути к файлу.

    :param prev_path: str - путь к рабочей папке
    :param new_path: str - относительный путь
    :return: str - полный путь к файлу
    """
    if prev_path != '':
        new_path = os.path.join(prev_path, new_path)
    return new_path
