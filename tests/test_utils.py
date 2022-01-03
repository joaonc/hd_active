import pytest

from hd_active.utils import get_asset


class TestGetAsset:
    @pytest.mark.parametrize('path', ['drive-harddisk-usb_36212_32px.png'])
    def test_exists(self, path):
        asset = get_asset(path)
        assert asset.exists()
