import gzip
import json
import tempfile

import pytest

import json_lines


def jl_bytes(data):
    return '\n'.join(json.dumps(x) for x in data).encode('utf8')


def test_reader_path(tmpdir):
    data = [{'a': 1}, {'b': 2}]
    p = tmpdir.join('myfile.jl')
    p.write(jl_bytes(data))

    with json_lines.open_file(str(p)) as f:
        assert list(json_lines.reader(f)) == data


def test_reader_file(tmpdir):
    data = [{'a': 1}, {'b': 2}]
    p = tmpdir.join('myfile.jl')
    p.write(jl_bytes(data))

    with open(str(p), 'rb') as f:
        assert list(json_lines.reader(f)) == data


def test_reader_gzip_file(tmpdir):
    data = [{'a': 1}, {'b': 2}]
    p = tmpdir.join('myfile.jl')
    with gzip.open(str(p), 'wb') as gzip_f:
        gzip_f.write(jl_bytes(data))

    with gzip.open(str(p), 'rb') as f:
        assert list(json_lines.reader(f)) == data


def test_reader_gzip_path(tmpdir):
    data = [{'a': 1}, {'b': 2}]
    p = tmpdir.join('myfile.jl.gz')
    with gzip.open(str(p), 'wb') as gzip_f:
        gzip_f.write(jl_bytes(data))

    with json_lines.open_file(str(p)) as f_:
        assert list(json_lines.reader(f_)) == data


def test_reader_broken_fail(tmpdir):
    p = tmpdir.join('myfile.jl.gz')
    p.write(b'somedata')

    with json_lines.open_file(str(p)) as f_:
        with pytest.raises(Exception):
            _ = list(json_lines.reader(f_))


def test_reader_broken_json_fail(tmpdir):
    p = tmpdir.join('myfile.jl.gz')
    with gzip.open(str(p), 'wb') as gzip_f:
        gzip_f.write(b'{"a": 1}\n{[]')

    with json_lines.open_file(str(p)) as f_:
        with pytest.raises(Exception):
            _ = list(json_lines.reader(f_))


def test_reader_broken(tmpdir):
    p = tmpdir.join('myfile.jl.gz')
    data = [{'a': 1}]
    with gzip.open(str(p), 'wb') as gzip_f:
        gzip_f.write(jl_bytes(data * 1000))
    with open(str(p), 'rb') as f_:
        contents = f_.read()
    with open(str(p), 'wb') as f_:
        f_.write(contents[:-10])

    with json_lines.open_file(str(p)) as f_:
        read_data = list(json_lines.reader(f_, broken=True))
        assert read_data[:900] == data * 900


def test_reader_broken_json(tmpdir):
    p = tmpdir.join('myfile.jl.gz')
    with gzip.open(str(p), 'wb') as gzip_f:
        gzip_f.write(b'{"a": 1}\n{[]')

    with json_lines.open_file(str(p)) as f_:
        read_data = list(json_lines.reader(f_, broken=True))
        assert read_data == [{'a': 1}]


def test_reader_broken_fuzz(tmpdir):
    p = tmpdir.join('myfile.jl.gz')
    data = [{'a': 1}]
    with gzip.open(str(p), 'wb') as gzip_f:
        gzip_f.write(jl_bytes(data * 1000))

    with open(str(p), 'rb') as f_:
        contents = f_.read()
    for cut in range(1, min(1000, len(contents))):
        with open(str(p), 'wb') as f_:
            f_.write(contents[:-cut])
        with json_lines.open_file(str(p)) as f_:
            read_data = list(json_lines.reader(f_, broken=True))
            assert isinstance(read_data, list)

