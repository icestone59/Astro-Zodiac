from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_runtime_files_exist():
    assert (ROOT / 'migration_runner.py').exists()
    assert (ROOT / 'render_start.sh').exists()
    assert (ROOT / 'T20_RENDER_RUNTIME_CONTRACT.md').exists()

def test_contract_is_safe_and_explicit():
    text = (ROOT / 'T20_RENDER_RUNTIME_CONTRACT.md').read_text(encoding='utf-8')
    assert 'DATABASE_URL' in text
    assert 'ASTRO_ZODIAC_PERSISTENCE=postgres' in text
    assert 'Do not commit' in text
