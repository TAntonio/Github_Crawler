from src.managers.args_parse_manager import ArgsParseManager


def test_parse_input_arguments():
    manager = ArgsParseManager()
    json_payload = '{"keywords": ["python", "drf"], "proxies": ["1.1.1.1:8080"], "type": "Repositories"}'
    parsed = manager.parse_args(["-json_payload", json_payload])
    assert parsed.json_payload == json_payload
