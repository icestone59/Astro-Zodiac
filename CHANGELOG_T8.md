# CHANGELOG — T8 Validation Engine

## T8.1

Added deterministic Pattern Validation Engine.

### Added
- `validation_schema.py`
- `validation_question_bank.py`
- `validation_engine.py`
- `tests/test_validation_engine.py`
- `T8_VALIDATION_ENGINE_CONTRACT.md`

### Integrated concepts
- T6 Pattern Candidate input
- 5–8 custom MVP questions per supported pattern
- Frequency / Agreement / Behavioral Example response model
- Reverse scoring for positively worded items in P05 and P06
- Product scoring: Astrology 0–30, Self-report 0–35, Behavioral evidence 0–35
- Pattern Fit 0–100 with Low / Moderate / Strong bands
- `validated / explored / not_confirmed` state
- Minimum 5 scorable responses before final status

### Safety / research boundary
- No diagnosis
- No causal childhood inference
- No psychometric validity claim
- Custom questions only; named instruments are reference context, not reproduced instruments
