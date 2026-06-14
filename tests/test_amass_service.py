import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.amass_service import build_amass_command, extract_subdomains


def test_build_amass_command_uses_passive_mode():
    cmd = build_amass_command('example.com', mode='passive')
    assert cmd[:3] == ['amass', 'enum', '-passive']
    assert '-d' in cmd
    assert 'example.com' in cmd


def test_extract_subdomains_filters_duplicates():
    output = 'api.example.com\nwww.example.com\napi.example.com\n'
    domains = extract_subdomains(output)
    assert domains == ['api.example.com', 'www.example.com']
