import os
from unittest.mock import AsyncMock, mock_open, patch, call, ANY

import pytest
import aiohttp

from script.help_functions import getea_api_url, get_full_path, split_list
from script.main import start_script
from script.main_functions import get_page_json, get_files_from_git, \
    download_files, download_git_repo, calculate_sha256_hash, get_files


def test_getea_api_url():
    assert (getea_api_url('https://gitea.radium.group/radium/monitoring') ==
            'https://gitea.radium.group/api/v1/repos/radium/monitoring/contents'
            )

    assert (getea_api_url('gitea.radium.group/radium/userhash.git') ==
            'https://gitea.radium.group/api/v1/repos/radium/userhash/contents'
            )
    assert (getea_api_url(
        'https://gitea.radium.group/radium/project-configuration') ==
            'https://gitea.radium.group/api/v1/'
            'repos/radium/project-configuration/contents'
            )


def test_split_list():
    assert split_list([], 2) == [[], []]

    assert split_list([1, 2, 3, 4, 5]) == [[1], [2], [3], [4], [5]]

    assert split_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4, 5]]

    assert (split_list([1, 2, 3, 4, 5, 6], 6) ==
            [[1], [2], [3], [4], [5], [6]]
            )


def test_get_full_path():
    assert get_full_path('', 'one') == 'one'

    assert get_full_path('one', 'two') == os.path.join('one',
                                                       'two',
                                                       )


def test_get_page_json():
    assert get_page_json('https://nocontent.ru') is None

    assert get_page_json('gitea.radium.group/api/v1/'
                         'repos/radium/project-configuration/content') is None

    test3_answer = [{'name': 'cookiecutter.json',
                     'path': 'cookiecutter-python/cookiecutter.json',
                     'sha': '4b32200430cd081ce24c9004206f68a52ef0dae5',
                     'last_commit_sha':
                         'd89a5842c19a5524c135761845639428c2c8508f',
                     'type': 'file', 'size': 554, 'encoding': None,
                     'content': None, 'target': None,
                     'url': 'https://gitea.radium.group/api/v1/repos/'
                            'radium/project-configuration/contents/'
                            'cookiecutter-python/cookiecutter.json?ref=master',
                     'html_url': 'https://gitea.radium.group/radium/'
                                 'project-configuration/src/branch/master/'
                                 'cookiecutter-python/cookiecutter.json',
                     'git_url': 'https://gitea.radium.group/api/v1/repos/'
                                'radium/project-configuration/git/blobs/4'
                                'b32200430cd081ce24c9004206f68a52ef0dae5',
                     'download_url': 'https://gitea.radium.group/radium/'
                                     'project-configuration/raw/branch/'
                                     'master/cookiecutter-python/'
                                     'cookiecutter.json',
                     'submodule_git_url': None, '_links': {
            'self': 'https://gitea.radium.group/api/v1/repos/radium/'
                    'project-configuration/contents/cookiecutter-python/'
                    'cookiecutter.json?ref=master',
            'git': 'https://gitea.radium.group/api/v1/repos/radium/'
                   'project-configuration/git/blobs/'
                   '4b32200430cd081ce24c9004206f68a52ef0dae5',
            'html': 'https://gitea.radium.group/radium/'
                    'project-configuration/src/branch/master/'
                    'cookiecutter-python/cookiecutter.json',
        },
                     },
                    {'name': '{{ cookiecutter.project_slug }}',
                     'path': 'cookiecutter-python/'
                             '{{ cookiecutter.project_slug }}',
                     'sha': 'f5938adce4b64ee661163a5518f05c5fc4bcb846',
                     'last_commit_sha':
                         '26791c096a89eb75fee0e22d0c651a0292d07b7a',
                     'type': 'dir', 'size': 0, 'encoding': None,
                     'content': None,
                     'target': None,
                     'url': 'https://gitea.radium.group/api/v1/repos/'
                            'radium/project-configuration/contents/'
                            'cookiecutter-python/%7B%7B%20cookiecutter.'
                            'project_slug%20%7D%7D?ref=master',
                     'html_url': 'https://gitea.radium.group/'
                                 'radium/project-configuration/src/'
                                 'branch/master/cookiecutter-python/'
                                 '%7B%7B%20cookiecutter.project_slug%20%7D%7D',
                     'git_url': 'https://gitea.radium.group/api/v1/'
                                'repos/radium/project-configuration/git/'
                                'blobs/f5938adce4b64ee661163a5518f05c5fc4bcb846',
                     'download_url': None, 'submodule_git_url': None,
                     '_links': {
                         'self': 'https://gitea.radium.group/api/v1/repos/'
                                 'radium/project-configuration/contents/'
                                 'cookiecutter-python/%7B%7B%20cookiecutter.'
                                 'project_slug%20%7D%7D?ref=master',
                         'git': 'https://gitea.radium.group/api/v1/repos/'
                                'radium/project-configuration/git/blobs/'
                                'f5938adce4b64ee661163a5518f05c5fc4bcb846',
                         'html': 'https://gitea.radium.group/radium/'
                                 'project-configuration/src/branch/master/'
                                 'cookiecutter-python/%7B%7B%20cookiecutter.'
                                 'project_slug%20%7D%7D'
                     },
                     },
                    ]

    assert get_page_json(
        ('https://gitea.radium.group/api/v1/repos/radium/project-'
         'configuration/contents/'
         'cookiecutter-python')
    ) == test3_answer


def test_get_files_from_git_with_mocks():
    url = 'mock.com'
    with patch('script.main_functions.get_page_json',
               return_value=[{'name': '1',
                              'type': 'file',
                              'download_url': 'url'},
                             ]
               ) as mock_get_files_from_git1:
        res1 = get_files_from_git(url)
        assert res1 == [{
            'name': '1',
            'link': 'url'
        },
        ]
        mock_get_files_from_git1.assert_called_once_with(url)

    with patch('script.main_functions.get_page_json'
               ) as mock_get_files_from_git2:
        mock_get_files_from_git2.side_effect = lambda x: [{'name': '3',
                                                           'type': 'file',
                                                           'download_url':
                                                               'url3'},
                                                          ] if x.endswith(
            'folder1') else [{'name': '2',
                              'type': 'file',
                              'download_url':
                                  'url2'},
                             {'name': 'folder1',
                              'type': 'dir',
                              'download_url':
                                  'f_url'},
                             ]
        res2 = get_files_from_git(url)
        assert res2 == [
            {
                'name': '2',
                'link': 'url2'
            },
            {
                'name': os.path.join('folder1', '3'),
                'link': 'url3'
            },
        ]

        expected_calls = [
            call(url),
            call(f'{url}/folder1'),
        ]
        mock_get_files_from_git2.assert_has_calls(expected_calls)


@pytest.mark.asyncio
async def test_download_files():
    file_path = [
        {
            'name': os.path.join('cookiecutter-python',
                                 '{{ cookiecutter.project_slug }}',
                                 'cookiecutter.json'),
            'link': 'https://gitea.radium.group/radium/project-configuration/raw'
                    '/branch/master/cookiecutter-python/'
                    '{{ cookiecutter.project_slug }}/README.md'
        },
        {
            'name': os.path.join('ccookiecutter-python',
                                 '{{ cookiecutter.project_slug }}',
                                 'cookiecutter.json'),
            'link': 'https://gitea.radium.group/radium/project-configuration/raw'
                    '/branch/master/ccookiecutter-python/'
                    '{{ cookiecutter.project_slug }}/README.md'
        },
    ]
    file_content = (b'# {{cookiecutter.project_name}}\n\n'
                    b'{{cookiecutter.description}}\n')
    with (patch('os.makedirs') as mock_makedirs,
          patch('builtins.open', mock_open()) as mock_file):
        async with aiohttp.ClientSession() as session:
            await download_files(file_path, session)

        mock_makedirs.assert_called_once_with(os.path.dirname(
            file_path[0]['name']), exist_ok=True,
        )
        mock_file().write.assert_called_once_with(file_content)


@pytest.mark.asyncio
async def test_download_git_repo():
    files_parts_list = [[1, 2], [3, 4, 5]]

    with patch('script.main_functions.download_files') as mock_download_files:
        await download_git_repo(files_parts_list)

        expected_calls = [
            call([1, 2], ANY),
            call([3, 4, 5], ANY),
        ]
        mock_download_files.assert_has_calls(expected_calls)


def test_calculate_sha256_hash():
    mock_files = ['__empty', '__one']
    with open('__empty', 'w'):
        pass
    with open('__one', 'w') as f_stream:
        f_stream.write('some text')
    assert (calculate_sha256_hash('__empty') ==
            'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')

    assert (calculate_sha256_hash('__one') ==
            'b94f6f125c79e3a5ffaa826f584c10d52ada669e6762051b826b55776d05aed2')

    assert (calculate_sha256_hash('-!..!.-&?')) is None

    for file_path in mock_files:
        os.remove(file_path)


def test_get_files():
    git_mock = 'mock.com/rep'
    with patch('script.main_functions.get_files_from_git', return_value=[
        {
            'name': '2',
            'link': 'url2'
        },
        {
            'name': os.path.join('folder1', '3'),
            'link': 'url3'
        },
    ]
               ) as mock_get_files_from_git1:
        assert get_files(git_mock, 'mf') == [
            {
                'name': os.path.join('mf', '2'),
                'link': 'url2'},
            {
                'name': os.path.join('mf', 'folder1', '3'),
                'link': 'url3'
            },
        ]
        mock_get_files_from_git1.assert_called_once_with('https://mock.com/'
                                                         'api/v1/repos/rep'
                                                         '/contents',
                                                         )
    with patch('script.main_functions.get_files_from_git',
               return_value=[],
               ) as mock_get_files_from_git2:
        assert get_files(git_mock, '') == []
        mock_get_files_from_git2.assert_called_once_with('https://mock.com/'
                                                         'api/v1/repos/rep'
                                                         '/contents',
                                                         )


def test_start_script():
    git_repo = 'mock.com'
    save_folder = 'mock_folder'
    task_count = 2

    with (patch('script.main_functions.get_files') as mock_get_files,
          patch('script.main_functions.download_git_repo',
                new_callable=AsyncMock,
                ) as mock_download_git_repo,
          patch('script.main_functions.'
                'calculate_sha256_hash',
                ) as mock_calculate_sha256_hash,
          patch('builtins.open', mock_open()),
          patch('json.dump') as mock_json):
        file_paths = [
            {'name': 'a', 'link': 'url1'},
            {'name': 'b', 'link': 'url2'}
        ]
        mock_get_files.return_value = file_paths
        mock_calculate_sha256_hash.return_value = b'test_content'
        start_script(git_repo, save_folder, task_count)

        mock_get_files.assert_called_once_with(git_repo, save_folder)
        mock_download_git_repo.assert_awaited_once_with([
            [{'name': 'a', 'link': 'url1'}],
            [{'name': 'b', 'link': 'url2'}],
        ]
        )
        calculate_sha256_hash_calls = [
            call('a'),
            call('b'),
        ]
        mock_calculate_sha256_hash.assert_has_calls(calculate_sha256_hash_calls)
        sha256_content = {'a': b'test_content',
                          'b': b'test_content',
                          }
        mock_json.assert_called_once_with(sha256_content, ANY)


