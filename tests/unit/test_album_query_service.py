"""Unit tests for AlbumQueryService.

Agent: Tests Analyst

Tests the ``faltantes_agrupados``, ``repetidas``, and ``progresso`` public
methods with fully mocked repository collaborators.  No database connection
is used.

Tested class (not yet implemented — RED phase):
    services.album_query_service.AlbumQueryService

Test naming convention:
    test_<method>_<condition>_deve_<expected_result>

Structure:
    - Arrange / Act / Assert blocks separated by blank lines.
    - One assertion per test function where possible.
    - Zero business logic (no ``if``, ``for``, or computed values) inside tests.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from models.figurinha import Figurinha


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_figurinha(
    *,
    id: int = 1,
    grupo: str = "A",
    codigo_selecao: str = "BRA",
    nome_selecao: str = "Brasil",
    numero: int = 1,
    codigo_figurinha: str = "BRA-1",
    quantidade: int = 0,
) -> Figurinha:
    """Build a Figurinha with sensible defaults for testing.

    Args:
        id: Primary key.
        grupo: Album group label.
        codigo_selecao: Short team code.
        nome_selecao: Full team name.
        numero: Sticker number.
        codigo_figurinha: Canonical sticker code.
        quantidade: Quantity owned.

    Returns:
        A populated :class:`Figurinha` instance.
    """
    now = datetime.now(tz=timezone.utc)
    return Figurinha(
        id=id,
        grupo=grupo,
        codigo_selecao=codigo_selecao,
        nome_selecao=nome_selecao,
        numero=numero,
        codigo_figurinha=codigo_figurinha,
        quantidade=quantidade,
        created_at=now,
        updated_at=now,
    )


def _make_service(mock_repo: MagicMock):
    """Instantiate AlbumQueryService with an injected mock repository.

    The import is deferred so collection succeeds in the RED phase, when
    the module does not yet exist.

    Args:
        mock_repo: Mock standing in for FigurinhaRepository.

    Returns:
        A :class:`AlbumQueryService` instance wired with the provided mock.
    """
    from services.album_query_service import AlbumQueryService  # noqa: PLC0415

    return AlbumQueryService(figurinha_repository=mock_repo)


# ---------------------------------------------------------------------------
# faltantes_agrupados
# ---------------------------------------------------------------------------


def test_faltantes_agrupados_quando_repo_retorna_lista_deve_agrupar_por_grupo_e_selecao(
    mock_figurinha_repository: MagicMock,
) -> None:
    """Two figurinhas with different grupo/selecao are grouped into a nested dict.

    Expected shape: {grupo: {nome_selecao: [Figurinha]}}
    """
    fig_a = _make_figurinha(
        id=1,
        grupo="A",
        codigo_selecao="QAT",
        nome_selecao="Qatar",
        numero=1,
        codigo_figurinha="QAT-1",
        quantidade=0,
    )
    fig_b = _make_figurinha(
        id=2,
        grupo="B",
        codigo_selecao="ENG",
        nome_selecao="Inglaterra",
        numero=1,
        codigo_figurinha="ENG-1",
        quantidade=0,
    )
    mock_figurinha_repository.find_faltantes.return_value = [fig_a, fig_b]

    service = _make_service(mock_figurinha_repository)

    result = service.faltantes_agrupados()

    assert result == {
        "A": {"Qatar": [fig_a]},
        "B": {"Inglaterra": [fig_b]},
    }


def test_faltantes_agrupados_mesmo_grupo_duas_selecoes_deve_agrupar_corretamente(
    mock_figurinha_repository: MagicMock,
) -> None:
    """Two figurinhas in the same grupo but different selecao produce two sub-keys."""
    fig_a = _make_figurinha(
        id=1,
        grupo="C",
        codigo_selecao="BRA",
        nome_selecao="Brasil",
        numero=1,
        codigo_figurinha="BRA-1",
        quantidade=0,
    )
    fig_b = _make_figurinha(
        id=2,
        grupo="C",
        codigo_selecao="ARG",
        nome_selecao="Argentina",
        numero=1,
        codigo_figurinha="ARG-1",
        quantidade=0,
    )
    mock_figurinha_repository.find_faltantes.return_value = [fig_a, fig_b]

    service = _make_service(mock_figurinha_repository)

    result = service.faltantes_agrupados()

    assert set(result["C"].keys()) == {"Brasil", "Argentina"}


def test_faltantes_agrupados_quando_lista_vazia_deve_retornar_dict_vazio(
    mock_figurinha_repository: MagicMock,
) -> None:
    """An empty list from the repository must produce an empty nested dict."""
    mock_figurinha_repository.find_faltantes.return_value = []

    service = _make_service(mock_figurinha_repository)

    result = service.faltantes_agrupados()

    assert result == {}


def test_faltantes_agrupados_delega_chamada_ao_repositorio(
    mock_figurinha_repository: MagicMock,
) -> None:
    """faltantes_agrupados must call repository.find_faltantes() exactly once."""
    mock_figurinha_repository.find_faltantes.return_value = []

    service = _make_service(mock_figurinha_repository)
    service.faltantes_agrupados()

    mock_figurinha_repository.find_faltantes.assert_called_once()


# ---------------------------------------------------------------------------
# repetidas
# ---------------------------------------------------------------------------


def test_repetidas_deve_delegar_chamada_ao_repositorio(
    mock_figurinha_repository: MagicMock,
) -> None:
    """repetidas() must delegate to repository.find_repetidas() and return its result."""
    fig = _make_figurinha(quantidade=3)
    mock_figurinha_repository.find_repetidas.return_value = [fig]

    service = _make_service(mock_figurinha_repository)

    result = service.repetidas()

    mock_figurinha_repository.find_repetidas.assert_called_once()
    assert result == [fig]


def test_repetidas_quando_repositorio_retorna_vazio_deve_retornar_lista_vazia(
    mock_figurinha_repository: MagicMock,
) -> None:
    """repetidas() must return an empty list when the repository returns none."""
    mock_figurinha_repository.find_repetidas.return_value = []

    service = _make_service(mock_figurinha_repository)

    result = service.repetidas()

    assert result == []


# ---------------------------------------------------------------------------
# progresso
# ---------------------------------------------------------------------------


def test_progresso_deve_delegar_chamada_ao_repositorio(
    mock_figurinha_repository: MagicMock,
) -> None:
    """progresso() must delegate to repository.get_progresso() and return its result."""
    from models.progresso import Progresso  # noqa: PLC0415

    expected = Progresso(total_album=100, tipos_possuidos=40, total_exemplares=80)
    mock_figurinha_repository.get_progresso.return_value = expected

    service = _make_service(mock_figurinha_repository)

    result = service.progresso()

    mock_figurinha_repository.get_progresso.assert_called_once()
    assert result is expected


def test_progresso_quando_repositorio_retorna_zeros_deve_repassar(
    mock_figurinha_repository: MagicMock,
) -> None:
    """progresso() must pass through a Progresso with all-zero values."""
    from models.progresso import Progresso  # noqa: PLC0415

    expected = Progresso(total_album=0, tipos_possuidos=0, total_exemplares=0)
    mock_figurinha_repository.get_progresso.return_value = expected

    service = _make_service(mock_figurinha_repository)

    result = service.progresso()

    assert result.total_album == 0
