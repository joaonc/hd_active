from pathlib import Path
from typing import Annotated

import typer

from admin import PROJECT_ROOT, SOURCE_DIR
from admin.utils import DryAnnotation, logger, run

BUILD_DIST_DIR = PROJECT_ROOT / 'dist'
VERSION_FILES = [
    PROJECT_ROOT / 'pyproject.toml',
    SOURCE_DIR / '__init__.py',
]
"""
Files that contain the package version.
This version needs to be updated with each release.
"""

app = typer.Typer()


def _update_project_version(version: str):
    regex = r'''^([ _]*version[ _]*[:=] *['"])(.*)(['"].*)$'''
    for file in VERSION_FILES:
        _re_sub_file(file, regex, version)


def _get_project_version() -> str:
    import re

    pattern = re.compile('''^[ _]*version[ _]*[:=] *['"](.*)['"]''', re.MULTILINE)
    versions = {}
    for file in VERSION_FILES:
        with open(file) as f:
            text = f.read()
        match = pattern.search(text)
        if not match:
            logger.error(f'Could not find version in `{file.relative_to(PROJECT_ROOT)}`.')
            raise typer.Exit(1)
        versions[file] = match.group(1)

    if len(set(versions.values())) != 1:
        logger.error(
            'Version mismatch in files that contain versions.\n'
            + (
                '\n'.join(
                    f'{file.relative_to(PROJECT_ROOT)}: {version}'
                    for file, version in versions.items()
                )
            )
        )
        raise typer.Exit(1)

    return list(versions.values())[0]


def _get_next_version(current_version, part):
    from packaging.version import Version

    version = Version(str(current_version))

    if part == 'major':
        new_version = Version(f'{version.major + 1}.0.0')
    elif part == 'minor':
        new_version = Version(f'{version.major}.{version.minor + 1}.0')
    elif part == 'patch':
        new_version = Version(f'{version.major}.{version.minor}.{version.micro + 1}')
    else:
        raise ValueError('`part` must be "major", "minor", or "patch"')

    return new_version


def _re_sub_file(file: str | Path, regex: str, repl: str, save: bool = True) -> str:
    """
    Regex search/replace text in a file.

    :param file: File to update.
    :param regex: Regex pattern, as a string.
        The regex needs to return 3 capturing groups: text before, text to replace, text after
        (per line).
    :param repl: Text to replace with.
    :param save: Whether to save the file with the new text.
    :return: Updated text.
    """
    import re

    pattern = re.compile(regex, re.MULTILINE)
    with open(file) as f:
        text = f.read()
    new_text = pattern.sub(lambda match: f'{match.group(1)}{repl}{match.group(3)}', text)

    if save:
        with open(file, 'w') as f:
            f.write(new_text)

    return new_text


def _get_release_name_and_tag(version: str) -> tuple[str, str]:
    """
    Generate release name and tag based on the version.

    :return: Tuple with release name (ex 'v1.2.3') and tag (ex '1.2.3').
    """
    return f'v{version}', version


def _get_version_from_release_name(release_name: str) -> str:
    if not release_name.startswith('v'):
        logger.error(f'Invalid release name: {release_name}')
        raise typer.Exit(1)
    return release_name[1:]


def _get_latest_release(c) -> tuple[str, str, list[dict]]:
    """
    Retrieves the latest release from GitHub.

    :return: Tuple with: release name (ex 'v1.2.3'), tag (ex '1.2.3') and list of assets uploaded.
    """
    import json

    release_info_json = c.run('gh release view --json name,tagName,assets').stdout.strip()
    release_info = json.loads(release_info_json)
    return release_info['name'], release_info['tagName'], release_info['assets']


def _get_branch():
    """Returns the current branch."""
    return run(False, 'git', 'branch', '--show-current')


def _get_default_branch():
    """Returns the default branch (usually ``main``)."""
    return run(
        False, 'gh', 'repo', 'view', '--json', 'defaultBranchRef', '--jq', '.defaultBranchRef.name'
    )


def _commit(message: str, dry: bool):
    # Commit
    run(dry, 'git', 'add', *VERSION_FILES)
    run(dry, 'git', 'commit', '-m', message)

    # Push current branch
    branch = _get_branch()
    run(dry, 'git', 'push', 'origin', branch)


def _create_pr(title: str, description: str, dry: bool):
    """
    Creates a PR in GitHub and merges it after checks pass.

    If checks fail, the PR will remain open and will need to be dealt with manually.
    """
    # Create PR
    default_branch = _get_default_branch()
    branch = _get_branch()
    run(
        dry,
        'gh',
        'pr',
        'create',
        '--title',
        title,
        '--body',
        description,
        '--head',
        branch,
        '--base',
        default_branch,
    )

    # Merge PR after checks pass
    run(dry, 'gh', 'pr', 'merge', 'branch', '--squash', '--auto')


@app.command(name='clean')
def build_clean():
    import shutil

    shutil.rmtree(BUILD_DIST_DIR, ignore_errors=True)


@app.command(name='version')
def build_version(
    version: Annotated[
        str,
        typer.Option(
            help='Version in semantic versioning format (ex 1.5.0). '
            'If `version` is set, then `bump` cannot be used.',
            show_default=False,
        ),
    ] = '',
    bump: Annotated[
        str,
        typer.Option(
            help='Portion of the version to increase, can be "major", "minor", or "patch". '
            'If `bump` is set, then `version` cannot be used.',
            show_default=False,
        ),
    ] = '',
    mode: Annotated[
        str,
        typer.Option(
            help='What do do after the files are updated:\n'
            '`nothing`: do nothing and the changes are not committed (default).\n'
            '`commit`: commit and push the changes with the message "bump version".\n'
            '`pr`: Commit, push, create and merge PR after checks pass.'
        ),
    ] = 'nothing',
    yes: Annotated[
        bool,
        typer.Option(
            help='Don\'t ask confirmation to create new branch if necessary.',
            show_default=False,
        ),
    ] = False,
    dry: DryAnnotation = False,
):
    """
    Updates the files that contain the project version to the new version.

    Optionally, commit the changes, create a PR and merge it after checks pass.
    """
    from packaging.version import Version

    mode = mode.strip().lower()
    if mode not in ['nothing', 'commit', 'pr']:
        logger.error('Invalid `mode` choice.')
        raise typer.Exit(1)

    v1 = Version(_get_project_version())
    if version and bump:
        logger.error('Either `version` or `bump` can be set, not both.')
        raise typer.Exit(1)
    if not (version or bump):
        try:
            bump = {'1': 'major', '2': 'minor', '3': 'patch'}[
                input(
                    f'Current version is `{v1}`, which portion to bump?'
                    '\n1 - Major\n2 - Minor\n3 - Patch\n> '
                )
            ]
        except KeyError:
            logger.error('Invalid choice')
            raise typer.Exit(1)

    if version:
        v2 = Version(version)
        if v2 <= v1:
            logger.error(
                f'New version `{v2}` needs to be greater than the existing version `{v1}`.'
            )
            raise typer.Exit(1)
    else:
        try:
            v2 = _get_next_version(v1, bump.strip().lower())
        except AttributeError:
            logger.error('Invalid `bump` choice.')
            raise typer.Exit(1)

    # Verify branch is not default
    branch = _get_branch()
    default_branch = _get_default_branch()
    if branch == default_branch:
        branch_ok = False
        if yes or input(
            f'Current branch `{branch}` is the default branch, create new branch? [Y/n] '
        ).strip().lower() in ['', 'y', 'yes']:
            run(dry, 'git', 'checkout', '-b', f'release-{v2}')
            branch_ok = True
        if not branch_ok:
            logger.error(f'Cannot make changes in the default branch `{branch}`.')
            raise typer.Exit(1)

    # Update files to new version
    _update_project_version(str(v2))
    print(
        f'New version is `{v2}`. Modified files :\n'
        + '\n'.join(f'  {file.relative_to(PROJECT_ROOT)}' for file in VERSION_FILES)
    )

    # Commit/push/pr
    if mode == 'nothing':
        print('Files not committed, PR not created.')
    if mode in ['commit', 'pr']:
        print('Commit and push changes.')
        _commit(f'bump version to {v2}', dry)
    if mode == 'pr':
        pr_title = f'Release {v2}'
        print(f'Create and merge PR `{pr_title}`.')
        _create_pr(pr_title, f'Preparing for release {v2}', dry)


if __name__ == '__main__':
    app()
