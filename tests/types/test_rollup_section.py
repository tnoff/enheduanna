from pydantic import ValidationError
from pytest import raises

from enheduanna.types.rollup_section import RollupSection

def test_validators():
    with raises(ValidationError) as e:
        RollupSection('Test', regex='foo')
    assert 'Regex requires groupBy be set' in str(e.value)

    with raises(ValidationError) as e:
        RollupSection('Test', groupBy='foo')
    assert 'GroupBy requires regex be set' in str(e.value)

    with raises(ValidationError) as e:
        RollupSection('Test', regex='foo', groupBy='bar')
    assert 'GroupBy field must be gathered in regex' in str(e.value)