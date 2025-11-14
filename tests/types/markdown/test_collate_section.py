from pydantic import ValidationError
from pytest import raises

from enheduanna.types.markdown.collate_section import CollateSection

def test_validators():
    with raises(ValidationError) as e:
        CollateSection('Test', regex='foo')
    assert 'Regex requires groupBy be set' in str(e.value)

    with raises(ValidationError) as e:
        CollateSection('Test', groupBy='foo')
    assert 'GroupBy requires regex be set' in str(e.value)

    with raises(ValidationError) as e:
        CollateSection('Test', regex='foo', groupBy='bar')
    assert 'GroupBy field must be gathered in regex' in str(e.value)