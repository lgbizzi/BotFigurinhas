"""Unit tests for CodigoParser.normalizar — TDD (RED phase).

The implementation under test lives in ``services.codigo_parser`` and has NOT
been written yet.  All tests in this module are expected to fail with
``ModuleNotFoundError`` or ``ImportError`` until the Parser Specialist
implements ``services/codigo_parser.py``.

Test naming convention:
    test_normalizar_quando_<condição>_deve_<resultado>

Structure:
    - Arrange / Act / Assert separated by blank lines.
    - ``@pytest.mark.parametrize`` used for all tabular cases.
    - One assertion per test.
    - Zero business logic inside the test functions.
"""

import pytest

from exceptions.domain_exceptions import CodigoInvalidoError

# ---------------------------------------------------------------------------
# Import under test — will raise ModuleNotFoundError until implemented (RED).
# ---------------------------------------------------------------------------
from services.codigo_parser import CodigoParser  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def parser() -> CodigoParser:
    """Return a fresh :class:`CodigoParser` instance for each test."""
    return CodigoParser()


# ---------------------------------------------------------------------------
# 1. Formato canônico e variações de separador / zero à esquerda
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("BRA-1", "BRA-1"),
        ("BRA-01", "BRA-1"),
        ("BRA 1", "BRA-1"),
        ("BRA 01", "BRA-1"),
        ("BRA01", "BRA-1"),
    ],
)
def test_normalizar_quando_variacao_de_separador_ou_zero_deve_retornar_canonico(
    parser: CodigoParser,
    entrada: str,
    esperado: str,
) -> None:
    """Separator variants and leading zeros must all resolve to canonical form."""
    resultado = parser.normalizar(entrada)

    assert resultado == esperado


# ---------------------------------------------------------------------------
# 2. Case-insensitive
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("bra-1", "BRA-1"),
        ("Bra-1", "BRA-1"),
    ],
)
def test_normalizar_quando_entrada_em_lowercase_ou_mixedcase_deve_retornar_canonico(
    parser: CodigoParser,
    entrada: str,
    esperado: str,
) -> None:
    """Input in any letter case must resolve to the uppercase canonical code."""
    resultado = parser.normalizar(entrada)

    assert resultado == esperado


# ---------------------------------------------------------------------------
# 3. Nome completo → código (Brasil)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("Brasil 1", "BRA-1"),
        ("brasil 1", "BRA-1"),
        ("BRASIL 1", "BRA-1"),
        ("Brasil-1", "BRA-1"),
        ("Brasil01", "BRA-1"),
        ("Brasil-01", "BRA-1"),
    ],
)
def test_normalizar_quando_nome_completo_brasil_deve_retornar_codigo_bra(
    parser: CodigoParser,
    entrada: str,
    esperado: str,
) -> None:
    """Full team name 'Brasil' in any casing/format must map to 'BRA-<n>'."""
    resultado = parser.normalizar(entrada)

    assert resultado == esperado


# ---------------------------------------------------------------------------
# 4. Nomes sem acento → código correto
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("Franca 1", "FRA-1"),
        ("Alemanha 5", "GER-5"),
        ("Estados Unidos 3", "USA-3"),
        ("Costa do Marfim 2", "CIV-2"),
        ("Bosnia 1", "BIH-1"),
    ],
)
def test_normalizar_quando_nome_sem_acento_deve_mapear_para_codigo_correto(
    parser: CodigoParser,
    entrada: str,
    esperado: str,
) -> None:
    """Team names typed without diacritics must still resolve to the correct code."""
    resultado = parser.normalizar(entrada)

    assert resultado == esperado


# ---------------------------------------------------------------------------
# 5. Casos especiais — FWC
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("FWC-00", "FWC-0"),
        ("FWC00", "FWC-0"),
        ("FWC 00", "FWC-0"),
        ("FWC-0", "FWC-0"),
        ("FWC 0", "FWC-0"),
        ("FWC-1", "FWC-1"),
        ("FWC 19", "FWC-19"),
    ],
)
def test_normalizar_quando_codigo_fwc_valido_deve_retornar_canonico(
    parser: CodigoParser,
    entrada: str,
    esperado: str,
) -> None:
    """FWC stickers (0–19) must normalise correctly, including the FWC-0 edge case."""
    resultado = parser.normalizar(entrada)

    assert resultado == esperado


# ---------------------------------------------------------------------------
# 6. Casos especiais — CC
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("CC1", "CC-1"),
        ("CC-1", "CC-1"),
        ("CC 1", "CC-1"),
        ("CC01", "CC-1"),
        ("CC-14", "CC-14"),
    ],
)
def test_normalizar_quando_codigo_cc_valido_deve_retornar_canonico(
    parser: CodigoParser,
    entrada: str,
    esperado: str,
) -> None:
    """CC stickers (1–14) must normalise correctly."""
    resultado = parser.normalizar(entrada)

    assert resultado == esperado


# ---------------------------------------------------------------------------
# 7. Erros — deve lançar CodigoInvalidoError
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "entrada",
    [
        "BRA-0",    # abaixo do mínimo para seleções (1–20)
        "BRA-21",   # acima do máximo para seleções
        "XXX-1",    # código de seleção inexistente
        "",         # entrada vazia
        "FWC-20",   # FWC só vai até 19
        "CC-15",    # CC só vai até 14
        "CC-0",     # CC começa em 1
        "abc",      # sem número
    ],
)
def test_normalizar_quando_codigo_invalido_deve_lancar_codigo_invalido_error(
    parser: CodigoParser,
    entrada: str,
) -> None:
    """Invalid codes must raise CodigoInvalidoError — never return a value."""
    with pytest.raises(CodigoInvalidoError):
        parser.normalizar(entrada)


# ---------------------------------------------------------------------------
# 8. Mensagem de erro — CodigoInvalidoError deve ser subclasse de AlbumCopaError
# ---------------------------------------------------------------------------


def test_codigo_invalido_error_e_subclasse_de_album_copa_error() -> None:
    """CodigoInvalidoError must be catchable as AlbumCopaError."""
    from exceptions.domain_exceptions import AlbumCopaError

    assert issubclass(CodigoInvalidoError, AlbumCopaError)
