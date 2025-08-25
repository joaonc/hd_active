import pytest

from hd_active.utils import ASSETS_ROOT, PROJECT_ROOT, get_asset, is_truthy


class TestGlobals:
    def test_project_root(self):
        assert PROJECT_ROOT.name == 'hd_active'

    def test_assets_root(self):
        assert ASSETS_ROOT.name == 'assets'


class TestGetAsset:
    @pytest.mark.parametrize('path', ['images/hard_drive_icon.png'])
    def test_exists(self, path):
        asset = get_asset(path)
        assert asset.exists()


class TestIsTruthy:
    @pytest.mark.parametrize('value', [True, 'True', 'true', 'YeS', 'ON', 1, 1.1, -1])
    def test_true(self, value):
        assert is_truthy(value) is True

    @pytest.mark.parametrize('value', [False, 'False', 'false', 'NO', 'OfF', 0, 0.0])
    def test_false(self, value):
        assert is_truthy(value) is False

    @pytest.mark.parametrize('value', ['foo', object()])
    def test_undetermined(self, value):
        with pytest.raises(ValueError):
            is_truthy(value)
