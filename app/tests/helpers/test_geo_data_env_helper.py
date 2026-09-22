"""Unit tests for GeoDataEnvHelper."""

from helpers.GeoDataEnvHelper import sanitize_geo_data_env


def test_proj_lib_without_proj_db_is_removed(tmp_path, monkeypatch):
    """The field failure: VTP's PROJ4-era data dir has no proj.db."""
    stale = tmp_path / "PROJ4-data"
    stale.mkdir()
    (stale / "epsg").write_text("old proj4 table")
    monkeypatch.setenv('PROJ_LIB', str(stale))

    removed = sanitize_geo_data_env()

    assert ('PROJ_LIB', str(stale)) in removed
    import os
    assert 'PROJ_LIB' not in os.environ


def test_proj_lib_with_proj_db_is_kept(tmp_path, monkeypatch):
    good = tmp_path / "proj"
    good.mkdir()
    (good / "proj.db").write_text("sqlite")
    monkeypatch.setenv('PROJ_LIB', str(good))

    removed = sanitize_geo_data_env()

    assert removed == []
    import os
    assert os.environ['PROJ_LIB'] == str(good)


def test_gdal_data_gdal1_layout_is_removed(tmp_path, monkeypatch):
    """GDAL 1.x csv-table layout (VTP) lacks gdalvrt.xsd."""
    stale = tmp_path / "GDAL-data"
    stale.mkdir()
    (stale / "gcs.csv").write_text("old tables")
    monkeypatch.setenv('GDAL_DATA', str(stale))

    removed = sanitize_geo_data_env()

    assert ('GDAL_DATA', str(stale)) in removed


def test_gdal_data_modern_layout_is_kept(tmp_path, monkeypatch):
    good = tmp_path / "gdal"
    good.mkdir()
    (good / "gdalvrt.xsd").write_text("<xsd/>")
    monkeypatch.setenv('GDAL_DATA', str(good))

    assert sanitize_geo_data_env() == []


def test_nonexistent_directory_is_removed(monkeypatch):
    monkeypatch.setenv('PROJ_DATA', r'Q:\no\such\place')
    removed = sanitize_geo_data_env()
    assert ('PROJ_DATA', r'Q:\no\such\place') in removed


def test_unset_variables_stay_unset(monkeypatch):
    monkeypatch.delenv('PROJ_LIB', raising=False)
    monkeypatch.delenv('PROJ_DATA', raising=False)
    monkeypatch.delenv('GDAL_DATA', raising=False)

    assert sanitize_geo_data_env() == []
    import os
    assert 'PROJ_LIB' not in os.environ
    assert 'GDAL_DATA' not in os.environ
