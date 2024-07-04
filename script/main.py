"""
Скрипт для нахождения хэшей файлов из репозитория Git.

Скрипт позволяет асинхронно скачивать файлы из репозитория Git
и высчитывать хэш sha256 у этих файлов. Хэши сохраняются в json файл.
"""

import asyncio
import json
import os

from script import main_functions as mf
from script.help_functions import split_list


def start_script(git_repo: str, save_folder: str, task_count: int) -> None:
    """
    Основная функция скрипта.

    :param git_repo: str - ссылка на Git репозиторий
    :param save_folder: str - путь к папке сохранения
    :param task_count: int - количество задач

    """
    file_paths = mf.get_files(git_repo, save_folder)

    # Скачивание репозитория (асинхронно)
    file_paths_groups = split_list(file_paths, task_count)
    asyncio.get_event_loop().run_until_complete(
        mf.download_git_repo(file_paths_groups),
    )

    # Подсчёт хэша файлов
    files_hashes = {}
    for file_abs_path in file_paths:
        files_hashes[file_abs_path[mf.NAME]] = (
            mf.calculate_sha256_hash(file_abs_path[mf.NAME])
        )

    with open(os.path.join('../hashes.json'), 'w') as file_stream:
        json.dump(files_hashes, file_stream)
    mf.logger.info('Хэши файлов успешно посчитаны.')
