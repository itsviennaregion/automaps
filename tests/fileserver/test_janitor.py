import os

from automaps.fileserver import DownloadPathJanitor


def prepare_tmp(path):
    (path / "downloads").mkdir()
    path = path / "downloads"
    for i in range(48):
        if i == 0:
            p = path / f"map{i:02d}.py"
            p.touch()
        else:
            p2 = path / f"map{i:02d}.py"
            p2.touch()
            os.utime(
                p2,
                (
                    p.stat().st_atime - 3600 * i - 1000,
                    p.stat().st_mtime - 3600 * i - 1000,
                ),
            )

    for i in range(48):
        if i == 0:
            p = path / f"map{i:02d}.pdf"
            p.touch()
        else:
            p2 = path / f"map{i:02d}.pdf"
            p2.touch()
            os.utime(
                p2,
                (
                    p.stat().st_atime - 3600 * i - 1000,
                    p.stat().st_mtime - 3600 * i - 1000,
                ),
            )

    return path


def test_download_path(tmp_path):
    tmp_path = prepare_tmp(tmp_path)
    j = DownloadPathJanitor(tmp_path.as_posix())
    assert list(j._find_all_files()) == [
        x for x in tmp_path.iterdir() if x.suffix == ".pdf"
    ]


def test_old_files(tmp_path):
    tmp_path = prepare_tmp(tmp_path)

    j = DownloadPathJanitor(tmp_path.as_posix())
    assert len(list(j._find_old_files())) == 40
    assert all(x.suffix == ".pdf" for x in j._find_old_files())

    j = DownloadPathJanitor(tmp_path.as_posix(), max_seconds=3600 * 8)
    assert len(list(j._find_old_files())) == 40

    j = DownloadPathJanitor(tmp_path.as_posix(), max_seconds=0)
    assert len(list(j._find_old_files())) == 48

    j = DownloadPathJanitor(tmp_path.as_posix(), max_seconds=3600 * 49)
    assert len(list(j._find_old_files())) == 0


def test_delete_files(tmp_path):
    tmp_path = prepare_tmp(tmp_path)
    j = DownloadPathJanitor(tmp_path.as_posix())
    j._delete_files(j._find_old_files())
    assert len(list(tmp_path.iterdir())) == 48 + 8

    tmp_path = prepare_tmp(tmp_path)
    j = DownloadPathJanitor(tmp_path.as_posix(), max_seconds=0)
    j._delete_files(j._find_old_files())
    assert len(list(tmp_path.iterdir())) == 48 + 0

    tmp_path = prepare_tmp(tmp_path)
    j = DownloadPathJanitor(tmp_path.as_posix(), max_seconds=3600 * 49)
    j._delete_files(j._find_old_files())
    assert len(list(tmp_path.iterdir())) == 48 + 48


def test_clean(tmp_path):
    tmp_path = prepare_tmp(tmp_path)
    j = DownloadPathJanitor(tmp_path.as_posix())
    j.clean()
    assert len(list(tmp_path.iterdir())) == 48 + 8
