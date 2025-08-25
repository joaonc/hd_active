import os
from pathlib import Path

from invoke import Collection, Exit, task

os.environ.setdefault('INVOKE_RUN_ECHO', '1')  # Show commands by default


PROJECT_ROOT = Path(__file__).parent
PROJECT_NAME = PROJECT_ROOT.name
PROJECT_SOURCE_RELATIVE_DIR = 'src'
PROJECT_SOURCE_DIR = PROJECT_ROOT / PROJECT_SOURCE_RELATIVE_DIR
"""Source code for the whole project."""
SOURCE_DIR = PROJECT_SOURCE_DIR / PROJECT_NAME
"""Source code for the this project's package."""
ASSETS_DIR = PROJECT_ROOT / 'assets'

# Requirements files
REQUIREMENTS_MAIN = 'main'
REQUIREMENTS_FILES = {
    REQUIREMENTS_MAIN: 'requirements',
    'dev': 'requirements-dev',
    'docs': 'requirements-docs',
}
"""
Requirements files.
Order matters as most operations with multiple files need ``requirements.txt`` to be processed
first.
Add new requirements files here.
"""

REQUIREMENTS_TASK_HELP = {
    'requirements': '`.in` file. Full name not required, just the initial name after the dash '
    f'(ex. "dev"). For main file use "{REQUIREMENTS_MAIN}". Available requirements: '
    f'{", ".join(REQUIREMENTS_FILES)}.'
}

VERSION_FILES = [
    PROJECT_ROOT / 'pyproject.toml',
    SOURCE_DIR / '__init__.py',
]
"""
Files that contain the package version.
This version needs to be updated with each release.
"""

UI_FILES = tuple((ASSETS_DIR / 'ui').glob("**/*.ui"))
"""
Qt ``.ui`` files.
"""

QRC_FILES = tuple(ASSETS_DIR.glob("**/*.qrc"))
"""
Qt ``.qrc`` resource files.
"""

# region Executable build configs
BUILD_SPEC_FILE = ASSETS_DIR / 'pyinstaller.spec'
BUILD_WORK_DIR = PROJECT_ROOT / 'build'
BUILD_WORK_APP_DIR = BUILD_WORK_DIR / 'app'
"""See ``BUILD_DIST_APP_DIR`` for more info."""
BUILD_DIST_DIR = PROJECT_ROOT / 'dist'
BUILD_DIST_APP_DIR = BUILD_DIST_DIR / 'app'
"""
Directory where the executable is built.

There are two types of distributions: package and executable (app).

To build the package, ``flit`` is used and at the time of writing it doesn't offer an option to
specify the output directory and it's always ``dist`` (``BUILD_DIST_DIR``)

To build the executable, ``pyinstaller`` is used and it does allow to specify the output directory.

To avoid mixing the files when creating both types of distributions, the package files will be in
``BUILD_DIST_DIR`` and the executable files in ``BUILD_DIST_APP_DIR``.
"""
# endregion


def _csstr_to_list(csstr: str) -> list[str]:
    """
    Convert a comma-separated string to list.
    """
    return [s.strip() for s in csstr.split(',')]


def _get_requirements_file(requirements: str, extension: str) -> str:
    """
    Return the full requirements file name (with extension).

    :param requirements: The requirements file to retrieve. Can be the whole filename
        (no extension), ex `'requirements-dev'` or just the initial portion, ex `'dev'`.
        Use `'main'` for the `requirements` file.
    :param extension: Requirements file extension. Can be either `'in'` or `'txt'`.
    """
    filename = REQUIREMENTS_FILES.get(requirements, requirements)
    if filename not in REQUIREMENTS_FILES.values():
        raise Exit(f'`{requirements}` is an unknown requirements file.')

    return f'{filename}.{extension.lstrip(".")}'


def _get_requirements_files(requirements: str | None, extension: str) -> list[str]:
    extension = extension.lstrip('.')
    if requirements is None:
        requirements_files = list(REQUIREMENTS_FILES)
    else:
        requirements_files = _csstr_to_list(requirements)

    # Get full filename+extension and sort by the order defined in `REQUIREMENTS_FILES`
    filenames = [
        _get_requirements_file(r, extension) for r in REQUIREMENTS_FILES if r in requirements_files
    ]

    return filenames


def _get_os_name():
    """User-friendly OS name (lowercased)."""
    import platform

    system = platform.system().lower()
    return {'darwin': 'mac'}.get(system, system)


def _get_build_app_files() -> tuple[Path, Path]:
    import hd_active

    version = hd_active.__version__

    # Assumes the distribution directory is empty prior to creating the app
    files = [f for f in BUILD_DIST_APP_DIR.glob('*') if f.is_file() and f.suffix.lower() != '.zip']
    if not files:
        raise Exit(f'App file not found in {BUILD_DIST_APP_DIR}')
    if len(files) > 1:
        raise Exit(
            f'One file expected in the distribution folder {BUILD_DIST_APP_DIR}.\n'
            f'{len(files)} files found:\n' + '\n'.join(str(file) for file in files)
        )
    app_file = files[0]
    zip_file = BUILD_DIST_APP_DIR / f'{app_file.stem}_{version}_{_get_os_name()}.zip'

    return app_file, zip_file


def _get_project_version() -> str:
    import re

    pattern = re.compile('''^[ _]*version[ _]*[:=] *['"](.*)['"]''', re.MULTILINE)
    versions = {}
    for file in VERSION_FILES:
        with open(file) as f:
            text = f.read()
        match = pattern.search(text)
        if not match:
            raise Exit(f'Could not find version in `{file.relative_to(PROJECT_ROOT)}`.')
        versions[file] = match.group(1)

    if len(set(versions.values())) != 1:
        raise Exit(
            'Version mismatch in files that contain versions.\n'
            + (
                '\n'.join(
                    f'{file.relative_to(PROJECT_ROOT)}: {version}'
                    for file, version in versions.items()
                )
            )
        )

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


def _update_project_version(version: str):
    regex = r'''^([ _]*version[ _]*[:=] *['"])(.*)(['"].*)$'''
    for file in VERSION_FILES:
        _re_sub_file(file, regex, version)


def _get_release_name_and_tag(version: str) -> tuple[str, str]:
    """
    Generate release name and tag based on the version.

    :return: Tuple with release name (ex 'v1.2.3') and tag (ex '1.2.3').
    """
    return f'v{version}', version


def _get_version_from_release_name(release_name: str) -> str:
    if not release_name.startswith('v'):
        raise Exit(f'Invalid release name: {release_name}')
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


def _module_path_from_file(file: Path, base_dir: Path) -> str:
    if file.is_file():
        _dir = file.parent
    elif file.is_dir():
        _dir = file
    else:
        raise Exit(f'File {file} is not a file or directory.')

    return str(_dir.relative_to(base_dir)).replace(os.sep, '.').strip('.')


def _update_imports():
    """
    Update the relative imports in the project to absolute imports.

    When being used as a package, this project works with relative imports, but as an app built
    with PyInstaller, relative imports do not work.
    """
    import shutil

    # Copy code to build dir
    build_source_dir = BUILD_WORK_APP_DIR / PROJECT_SOURCE_DIR.relative_to(PROJECT_ROOT)
    shutil.copytree(
        PROJECT_SOURCE_DIR, build_source_dir, ignore=shutil.ignore_patterns('__pycache__')
    )

    # Update imports
    for root, dirs, files in os.walk(build_source_dir):
        root_path = Path(root)
        module = _module_path_from_file(root_path, build_source_dir.parent)
        for file in files:
            file_path = root_path / file

            regex_replace = [
                (r'''^( *from[ ]+)(\.)( .*)''', module),  # from . import <module>
                (
                    r'''^( *from[ ]+)(\.{2})(.*)''',
                    '.'.join(module.split('.')[:-1]) + '.',
                ),
                (
                    r'''^( *from[ ]+)(\.{1})(.*)''',
                    module + '.',
                ),
            ]
            for regex in regex_replace:
                _re_sub_file(file_path, regex[0], regex[1])


def _get_branch(c):
    """Returns the current branch."""
    return c.run('git branch --show-current').stdout.strip()


def _get_default_branch(c):
    """Returns the default branch (usually ``main``)."""
    return c.run('gh repo view --json defaultBranchRef --jq .defaultBranchRef.name').stdout.strip()


def _commit(c, message: str):

    # Commit
    c.run('git add ' + ' '.join(f'"{file}"' for file in VERSION_FILES))
    c.run(f'git commit -m "{message}"')

    # Push current branch
    branch = _get_branch(c)
    c.run(f'git push origin {branch}')


def _create_pr(c, title: str, description: str):
    """
    Creates a PR in GitHub and merges it after checks pass.

    If checks fail, the PR will remain open and will need to be dealt with manually.
    """
    # Create PR
    default_branch = _get_default_branch(c)
    branch = _get_branch(c)
    c.run(
        f'gh pr create --title "{title}" --body "{description}" '
        f'--head {branch} --base {default_branch}'
    )

    # Merge PR after checks pass
    c.run(f'gh pr merge {branch} --squash --auto')


@task
def build_clean(c):
    """
    Delete files created from previous builds (`build` and `dist` folders).
    """
    import shutil

    # From building the package and/or executable
    for d in [BUILD_WORK_DIR, BUILD_DIST_DIR]:
        shutil.rmtree(d, ignore_errors=True)

    # From building the package
    shutil.rmtree(PROJECT_ROOT / f'{PROJECT_NAME}.egg-info', ignore_errors=True)


@task(
    help={
        'version': 'Version in semantic versioning format (ex 1.5.0). '
        'If `version` is set, then `bump` cannot be used.',
        'bump': 'Portion of the version to increase, can be "major", "minor", or "patch".\n'
        'If `bump` is set, then `version` cannot be used.',
        'mode': 'What do do after the files are updated:\n"nothing": do nothing and the changes '
        'are not committed (default).\n"commit": commit and push the changes with the message '
        '"bump version".\n"pr": Commit, push, create and merge PR after checks pass.',
        'yes': 'Don\'t ask confirmation to create new branch if necessary.',
    },
)
def build_version(c, version: str = '', bump: str = '', mode: str = 'nothing', yes: bool = False):
    """
    Updates the files that contain the project version to the new version.

    Optionally, commit the changes, create a PR and merge it after checks pass.
    """
    from packaging.version import Version

    mode = mode.strip().lower()
    if mode not in ['nothing', 'commit', 'pr']:
        raise Exit('Invalid `mode` choice.')

    v1 = Version(_get_project_version())
    if version and bump:
        raise Exit('Either `version` or `bump` can be set, not both.')
    if not (version or bump):
        try:
            bump = {'1': 'major', '2': 'minor', '3': 'patch'}[
                input(
                    f'Current version is `{v1}`, which portion to bump?'
                    '\n1 - Major\n2 - Minor\n3 - Patch\n> '
                )
            ]
        except KeyError:
            raise Exit('Invalid choice')

    if version:
        v2 = Version(version)
        if v2 <= v1:
            raise Exit(f'New version `{v2}` needs to be greater than the existing version `{v1}`.')
    else:
        try:
            v2 = _get_next_version(v1, bump.strip().lower())
        except AttributeError:
            raise Exit('Invalid `bump` choice.')

    # Verify branch is not default
    branch = _get_branch(c)
    default_branch = _get_default_branch(c)
    if branch == default_branch:
        branch_ok = False
        if yes or input(
            f'Current branch `{branch}` is the default branch, create new branch? [Y/n] '
        ).strip().lower() in ['', 'y', 'yes']:
            c.run(f'git checkout -b release-{v2}')
            branch_ok = True
        if not branch_ok:
            raise Exit(f'Cannot make changes in the default branch `{branch}`.')

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
        _commit(c, f'bump version to {v2}')
    if mode == 'pr':
        pr_title = f'Release {v2}'
        print(f'Create and merge PR `{pr_title}`.')
        _create_pr(c, pr_title, f'Preparing for release {v2}')


@task(
    build_clean,
    help={
        'no_spec': f'Do not use the spec file `{BUILD_SPEC_FILE.relative_to(PROJECT_ROOT)}` and '
        f'create one in the `{BUILD_WORK_DIR.relative_to(PROJECT_ROOT)}` directory with defaults.',
        'no_zip': 'Do not create a ZIP file, which can be used to upload to a GitHub release.',
    },
)
def build_app(c, no_spec: bool = False, no_zip: bool = False):
    """
    Build the executable (app) file(s).
    """
    _update_imports()

    # Build executable
    if no_spec:
        build_source_dir = BUILD_WORK_APP_DIR / PROJECT_SOURCE_DIR.relative_to(PROJECT_ROOT)
        build_input_file = build_source_dir / PROJECT_NAME / 'main.py'
        c.run(
            f'pyinstaller '
            f'--onefile "{build_input_file}" --distpath "{BUILD_DIST_APP_DIR}" '
            f'--workpath "{BUILD_WORK_APP_DIR}" --specpath "{BUILD_WORK_APP_DIR}"'
        )
    else:
        c.run(
            f'pyinstaller "{BUILD_SPEC_FILE}" '
            f'--distpath "{BUILD_DIST_APP_DIR}" --workpath "{BUILD_WORK_APP_DIR}"'
        )

    app_file, zip_file = _get_build_app_files()

    # Zip file
    if no_zip:
        print('ZIP file not created.')
    else:
        import zipfile

        with zipfile.ZipFile(zip_file, 'w') as f:
            f.write(app_file, arcname=app_file.name)

    print(f'App files created in {BUILD_DIST_APP_DIR}')


@task(
    help={
        'no_upload': 'Do not upload to Pypi.',
        'yes': 'Don\'t request confirmation to publish to Pypi.',
    },
)
def build_publish(c, no_upload: bool = False, yes: bool = False):
    """
    Build package and publish (upload) to Pypi.

    Output in `dist` folder.
    """
    # Create distribution files (source and wheel)
    c.run('flit build')
    # Upload to pypi
    if not no_upload:
        if (
            yes
            or input(f'Publishing version `{_get_project_version()}` to Pypi. Press Y to confirm. ')
            .strip()
            .lower()
            == 'y'
        ):
            c.run('flit publish')
        else:
            print('Package not published to Pypi.')


@task(
    help={
        'notes': 'Release notes.',
        'notes_file': 'Read release notes from file. Ignores the `-notes` parameter.',
        'yes': 'Don\'t request confirmation to create the release.',
    },
)
def build_release(
    c,
    notes: str = '',
    notes_file: str = '',
    yes: bool = False,
):
    """
    Create a release and tag in GitHub from the current project version.

    Does not upload artifacts (executable/zip) to the release. Use `build.upload` for that.
    """
    from packaging.version import Version

    if notes and notes_file:
        raise Exit('Both `--notes` and `--notes-file` are specified. Only one can be specified.')

    if not notes and not notes_file and not yes:
        response = input('No release notes or notes file specified, continue? [Y/n]')
        response = response.strip().lower() or 'y'
        if response not in ['yes', 'y']:
            raise Exit('No release notes specified.')

    # Check that there's no release with the current version
    version = Version(_get_project_version())
    latest_release, latest_tag, _ = _get_latest_release(c)
    latest_version = Version(_get_version_from_release_name(latest_release))
    if str(latest_version) != latest_tag:
        raise Exit(
            f'Invalid format in latest release or tag: Release: {latest_release}, Tag: {latest_tag}'
        )

    if latest_version >= version:
        raise Exit(
            f'Release/tag version being created ({version}) needs to be greater than the current '
            f'latest release version ({latest_version}).'
        )

    # Create release (zip file not uploaded)
    new_release, new_tag = _get_release_name_and_tag(str(version))
    command = f'gh release create "{new_tag}" --title "{new_release}" --generate-notes'
    if notes:
        command += f' --notes "{notes}"'
    if notes_file:
        notes_file_path = Path(notes_file)
        command += f' --notes-file "{notes_file_path.resolve(strict=True)}"'

    if (
        yes
        or input(f'Creating GitHub release `{new_release}`. Press Y to confirm. ').strip().lower()
        == 'y'
    ):
        c.run(command)
        print('GitHub release created. Upload artifacts with `build.upload`.')
    else:
        print('GitHub release not created.')


@task(
    help={
        'label': 'The label that will be displayed in GitHub next to the artifact. The special '
        'strings "auto" and "none" mean that the label is to be autogenerated (OS specific) or no '
        'label is attached, respectively. Any other string is what\'s used as label. Use the '
        '`--dry` option to see the label without uploading the artifact.'
    },
)
def build_upload(c, label: str = 'none'):
    """
    Upload asset to the GitHub release in the manifest file.
    The artifact being uploaded is the Zip file with the executable binary for the current OS.
    The release the artifact is uploaded to is specified in the manifest file inside the Zip file.

    The following must already exist:
      * The artifact (`inv build.exe`).
      * The release in GitHub (`inv build.release`).
    """
    from packaging.version import Version

    import hd_active

    _, zip_file = _get_build_app_files()
    app_version = Version(hd_active.__version__)

    if not zip_file.exists():
        raise Exit(
            f'Zip file not found: {zip_file}\n'
            'Rebuild the app with `inv build.dist` and without the `--no-zip` option.'
        )

    # Verify asset is being uploaded to the correct GH release
    latest_release, latest_tag, assets = _get_latest_release(c)
    latest_version = Version(_get_version_from_release_name(latest_release))
    if app_version != latest_version:
        raise Exit(
            f'App version `{app_version}` does not match '
            f'the latest release in GitHub `{latest_version}`.`'
        )

    # Verify asset does not yet exist in the GH release
    asset = next((asset for asset in assets if asset['name'] == zip_file.name), None)
    if asset:
        raise Exit(
            f'File `{zip_file.name}` already exists in release `{latest_release}`.\n'
            'To re-upload, the file needs to be deleted from the release first.'
        )

    # Create label
    if label.lower() == 'auto':
        label = f'#{_get_os_name().title()}'
    elif label.lower() == 'none':
        label = ''
    else:
        label = f'#{label}'

    # Upload file
    print(
        f'Uploading `{zip_file.name}` to release `{latest_release}`'
        + (f' with label `{label}`' if label else '')
    )
    command = f'gh release upload "{latest_tag}" "{zip_file}{label}"'

    c.run(command)


@task
def build_run(c):
    """
    Run the built package.
    """
    os_name = _get_os_name()

    if os_name == 'windows':
        exes = list(BUILD_DIST_APP_DIR.glob('**/*.exe'))
        if len(exes) == 0:
            raise Exit('No executable found.')
        elif len(exes) > 1:
            raise Exit('Multiple executables found.')
        c.run(str(exes[0]))
    elif os_name == 'mac':
        app_file, _, _ = _get_build_app_files()
        c.run(str(app_file))
    elif os_name == 'linux':
        raise Exit('Running on Linux not yet implemented.')
    else:
        raise Exit(f'Running on {os_name.title()} is not supported.')


@task(
    help={
        'file': '`.ui` file to be converted to `.py`. `.ui` extension not required. '
        'Can be a comma separated list. If not supplied, all files will be converted. '
        f'Available files: {", ".join(p.stem for p in UI_FILES)}.'
    }
)
def ui_py(c, file=None):
    """
    Convert Qt `.ui` files into `.py`.
    """
    if file:
        file_stems = [
            (_f2[:-3] if _f2.lower().endswith('.ui') else _f2)
            for _f2 in [_f1.strip() for _f1 in file.split(',')]
        ]
    else:
        file_stems = [p.stem for p in UI_FILES]

    for file_stem in file_stems:
        try:
            file_path_in = next(p for p in UI_FILES if p.stem == file_stem)
        except StopIteration:
            raise Exit(
                f'File "{file}" not found. Available files: {", ".join(p.stem for p in UI_FILES)}'
            )

        file_path_out = SOURCE_DIR / 'ui/forms' / f'ui_{file_stem}.py'

        c.run(f'pyside6-uic {file_path_in} -o {file_path_out} --from-imports')


@task(
    help={
        'file': '`.qrc` file to be converted to `.py`. `.qrc` extension not required. '
        'Can be a coma separated list of filenames. If not supplied, all files will be converted. '
        f'Available files: {", ".join(p.stem for p in QRC_FILES)}.'
    }
)
def ui_rc(c, file=None):
    """
    Convert Qt `.qrc` files into `.py`.
    """
    if file:
        file_stems = [
            (_f2[:-4] if _f2.lower().endswith('.qrc') else _f2)
            for _f2 in [_f1.strip() for _f1 in file.split(',')]
        ]
    else:
        file_stems = [p.stem for p in QRC_FILES]

    for file_stem in file_stems:
        try:
            file_path_in = next(p for p in QRC_FILES if p.stem == file_stem)
        except StopIteration:
            raise Exit(
                f'File "{file}" not found. Available files: {", ".join(p.stem for p in QRC_FILES)}'
            )

        file_path_out = SOURCE_DIR / 'ui/forms' / f'{file_stem}_rc.py'

        c.run(f'pyside6-rcc {file_path_in} -o {file_path_out}')


@task(
    help={
        'file': f'`.ui` file to be edited. Available files: {", ".join(p.stem for p in UI_FILES)}.'
    }
)
def ui_edit(c, file):
    """
    Edit a file in QT Designer.
    """
    file_stem = file[:-3] if file.lower().endswith('.ui') else file
    try:
        ui_file_path = next(p for p in UI_FILES if p.stem == file_stem)
    except StopIteration:
        raise Exit(
            f'File "{file}" not found. Available files: {", ".join(p.stem for p in UI_FILES)}'
        )

    c.run(f'pyside6-designer {ui_file_path}', asynchronous=True)


@task
def lint_black(c, path='.'):
    c.run(f'black {path}')


@task
def lint_flake8(c, path='.'):
    c.run(f'flake8 {path}')


@task
def lint_isort(c, path='.'):
    c.run(f'isort {path}')


@task
def lint_mypy(c, path='.'):
    c.run(f'mypy {path}')


@task
def lint_all(c):
    """
    Run all linters.
    Config for each of the tools is in ``pyproject.toml`` and ``setup.cfg``.
    """
    lint_isort(c)
    lint_black(c)
    lint_flake8(c)
    lint_mypy(c, 'src')
    lint_mypy(c, 'tests')
    print('Done')


@task
def test_unit(c):
    """
    Run unit tests.
    """
    c.run('python -m pytest')


@task(help=REQUIREMENTS_TASK_HELP)
def pip_compile(c, requirements=None):
    """
    Compile requirements file(s).
    """
    for filename in _get_requirements_files(requirements, 'in'):
        c.run(f'pip-compile {filename}')


@task(help=REQUIREMENTS_TASK_HELP)
def pip_sync(c, requirements=None):
    """
    Synchronize environment with requirements file.
    """
    c.run(f'pip-sync {" ".join(_get_requirements_files(requirements, "txt"))}')


@task(
    help=REQUIREMENTS_TASK_HELP | {'package': 'Package to upgrade. Can be a comma separated list.'}
)
def pip_package(c, requirements, package):
    """
    Upgrade package.
    """
    packages = [p.strip() for p in package.split(',')]
    for filename in _get_requirements_files(requirements, 'in'):
        c.run(f'pip-compile --upgrade-package {" --upgrade-package ".join(packages)} {filename}')


@task(help=REQUIREMENTS_TASK_HELP)
def pip_upgrade(c, requirements):
    """
    Try to upgrade all dependencies to their latest versions.
    """
    for filename in _get_requirements_files(requirements, 'in'):
        c.run(f'pip-compile --upgrade {filename}')


@task
def precommit_install(c):
    """
    Install pre-commit into the git hooks, which will cause pre-commit to run on automatically.
    This should be the first thing to do after cloning this project and installing requirements.
    """
    c.run('pre-commit install')


@task
# `upgrade` instead of `update` to maintain similar naming to `pip-compile upgrade`
def precommit_upgrade(c):
    """
    Upgrade pre-commit config to the latest repos' versions.
    """
    c.run('pre-commit autoupdate')


@task(help={'hook': 'Name of hook to run. Default is to run all.'})
def precommit_run(c, hook=None):
    """
    Manually run pre-commit hooks.
    """
    hook = hook or '--all-files'
    c.run(f'pre-commit run {hook}')


@task
def docs_serve(c):
    """
    Start documentation local server.
    """
    c.run('mkdocs serve')


@task
def docs_deploy(c):
    """
    Publish documentation to GitHub Pages at https://joaonc.github.io/hd_active
    """
    c.run('mkdocs gh-deploy')


@task
def docs_clean(c):
    """
    Delete documentation website static files.
    """
    import shutil

    shutil.rmtree(PROJECT_ROOT / 'site', ignore_errors=True)


ns = Collection()  # Main namespace

test_collection = Collection('test')
test_collection.add_task(test_unit, 'unit')

build_collection = Collection('build')
build_collection.add_task(build_clean, 'clean')
build_collection.add_task(build_version, 'version')
build_collection.add_task(build_app, 'app')
build_collection.add_task(build_release, 'release')
build_collection.add_task(build_run, 'run')
build_collection.add_task(build_upload, 'upload')
build_collection.add_task(build_publish, 'publish')

lint_collection = Collection('lint')
lint_collection.add_task(lint_all, 'all')
lint_collection.add_task(lint_black, 'black')
lint_collection.add_task(lint_flake8, 'flake8')
lint_collection.add_task(lint_isort, 'isort')
lint_collection.add_task(lint_mypy, 'mypy')

pip_collection = Collection('pip')
pip_collection.add_task(pip_compile, 'compile')
pip_collection.add_task(pip_package, 'package')
pip_collection.add_task(pip_sync, 'sync')
pip_collection.add_task(pip_upgrade, 'upgrade')

precommit_collection = Collection('precommit')
precommit_collection.add_task(precommit_run, 'run')
precommit_collection.add_task(precommit_install, 'install')
precommit_collection.add_task(precommit_upgrade, 'upgrade')

docs_collection = Collection('docs')
docs_collection.add_task(docs_serve, 'serve')
docs_collection.add_task(docs_deploy, 'deploy')
docs_collection.add_task(docs_clean, 'clean')

ui_collection = Collection('ui')
ui_collection.add_task(ui_py, 'py')
ui_collection.add_task(ui_rc, 'rc')
ui_collection.add_task(ui_edit, 'edit')

ns.add_collection(build_collection)
ns.add_collection(lint_collection)
ns.add_collection(pip_collection)
ns.add_collection(precommit_collection)
ns.add_collection(test_collection)
ns.add_collection(docs_collection)
ns.add_collection(ui_collection)
