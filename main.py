from script.main import start_script


def main():
    """Базовая функция."""
    git_repo = 'https://gitea.radium.group/radium/project-configuration'
    save_folder = 'temp_folder'
    task_count = 3
    start_script(git_repo, save_folder, task_count)
