"""
Основные функции.

Основные функции, участвующие в работе скрипта.
"""

import asyncio
import hashlib
import logging
import os
from typing import Dict, List, Union

import aiohttp
import requests

from script.help_functions import get_full_path, getea_api_url

TIMEOUT = 200
SUCCESS_CODE = 200
BLOCK_SIZE = 4096
NAME = 'name'
logger = logging.Logger('logger')


def get_page_json(url: str) -> Union[List[Dict], Dict, None]:
    """
    Получение json-контента страницы.

    :param url: str - ссылка на страницу
    :return: list | dict - содержимое страницы

    """
    res_content = None
    try:
        res = requests.get(url, timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        return res_content
    if res.status_code == SUCCESS_CODE:
        res_content = res.json()
    return res_content


def get_files_from_git(
    url: str,
    prev_path: str = '',
) -> List:
    """
    Получение списка файлов Git репозитория через API.

    :param url: str - ссылка API Git репозитория
    :param prev_path: str - путь до текущей директории
    :return: list - список словарей, состоящих из пути к файлу (name)
     и ссылки на файл (link)

    """
    files = []
    res_objects = get_page_json(url)
    if res_objects:
        for res_object in res_objects:
            full_path = get_full_path(prev_path, res_object[NAME])
            if res_object['type'] == 'file':
                files.append(
                    {
                        NAME: full_path,
                        'link': res_object['download_url'],
                    },
                )
            elif res_object['type'] == 'dir':
                new_url = '/'.join([url, res_object[NAME]])
                files.extend(get_files_from_git(new_url, full_path))
    return files


async def download_files(
    file_paths: List[Dict[str, str]],
    session: aiohttp.ClientSession,
) -> None:
    """
    Скачивание файлов из Git репозитория в папку path.

    :param file_paths: list - список словарей, состоящих из пути к файлу (name)
     и ссылки на файл (link)
    :param session: aiohttp.ClientSession - асинхронная сессия

    """
    for file_path in file_paths:
        async with session.get(file_path['link']) as res:
            if res.status == SUCCESS_CODE:
                os.makedirs(os.path.dirname(file_path[NAME]), exist_ok=True)

                with open(file_path[NAME], 'wb') as file_stream:
                    file_stream.write(await res.read())

                logger.info('{s} успешно загружен'.format(s=file_path[NAME]))
            else:
                logger.error('{s} не был загружен'.format(s=file_path[NAME]))


async def download_git_repo(file_paths_list: List[List]) -> None:
    """
    Скачивание Git репозитория в папку path.

    :param file_paths_list: list - список групп словарей,
     состоящих из пути к файлу (name) и ссылки на файл (link)

    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for files_parts in file_paths_list:
            tasks.append(download_files(files_parts, session))
        await asyncio.gather(*tasks)


def calculate_sha256_hash(file_path: str) -> str:
    """
    Расчёт хэша sha256 для файла file.

    :param file_path: str - путь к файлу
    :return: str - хэш файла

    """
    ans = None
    if os.path.exists(file_path):
        file_hash = hashlib.sha256()
        with open(file_path, 'rb') as file_stream:
            block = file_stream.read(BLOCK_SIZE)
            while block:
                file_hash.update(block)
                block = file_stream.read()
        ans = file_hash.hexdigest()
    return ans


def get_files(git_repo: str, save_folder: str) -> List[Dict]:
    """
    Получение списка файлов из репозитория Git со ссылками.

    :param git_repo: str - ссылка на репозиторий Git
    :param save_folder: str - папка для сохранения
    :return: list - список словарей, состоящих из пути к файлу (name)
     и ссылки на файл (link)
    """
    git_repo_api = getea_api_url(git_repo)
    file_paths = get_files_from_git(git_repo_api)
    logger.info('Список файлов получен.')

    if save_folder != '':
        for file_path in file_paths:
            file_path[NAME] = os.path.join(save_folder, file_path[NAME])
    return file_paths
