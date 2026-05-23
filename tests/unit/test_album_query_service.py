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
    pagina: int = 24,
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
        pagina: Physical album page number.

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
        pagina=pagina,
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


def test_faltantes_agrupados_quando_repo_retorna_lista_deve_retornar_grupos_ordenados(
    mock_figurinha_repository: MagicMock,
) -> None:
    """Two figurinhas from different groups produce two group tuples.

    Expected shape: [(group_header, [(nome_selecao, codigo_selecao, [Figurinha])]), ...]
    ordered by ascending pagina.
    """
    fig_a = _make_figurinha(
        id=1, grupo="B", codigo_selecao="QAT", nome_selecao="Catar",
        codigo_figurinha="QAT-1", pagina=20,
    )
    fig_b = _make_figurinha(
        id=2, grupo="L", codigo_selecao="ENG", nome_selecao="Inglaterra",
        codigo_figurinha="ENG-1", pagina=98,
    )
    mock_figurinha_repository.find_faltantes.return_value = [fig_a, fig_b]

    service = _make_service(mock_figurinha_repository)

    result = service.faltantes_agrupados(telegram_user_id=0)

    assert result == [
        ("Grupo B", [("Catar", "QAT", [fig_a])]),
        ("Grupo L", [("Inglaterra", "ENG", [fig_b])]),
    ]


def test_faltantes_agrupados_mesmo_grupo_agrupa_selecoes_no_mesmo_bloco(
    mock_figurinha_repository: MagicMock,
) -> None:
    """Two countries in the same group appear under a single group header."""
    fig_a = _make_figurinha(id=1, grupo="C", codigo_selecao="BRA", nome_selecao="Brasil",
                            numero=1, codigo_figurinha="BRA-1", pagina=24)
    fig_b = _make_figurinha(id=2, grupo="C", codigo_selecao="MAR", nome_selecao="Marrocos",
                            numero=1, codigo_figurinha="MAR-1", pagina=26)
    mock_figurinha_repository.find_faltantes.return_value = [fig_a, fig_b]

    service = _make_service(mock_figurinha_repository)

    result = service.faltantes_agrupados(telegram_user_id=0)

    assert len(result) == 1
    assert result[0][0] == "Grupo C"
    assert len(result[0][1]) == 2


def test_faltantes_agrupados_mesma_selecao_agrupa_figurinhas_juntas(
    mock_figurinha_repository: MagicMock,
) -> None:
    """Multiple figurinhas from the same country appear in a single country tuple."""
    fig_a = _make_figurinha(id=1, grupo="C", codigo_selecao="BRA", nome_selecao="Brasil",
                            numero=1, codigo_figurinha="BRA-1", pagina=24)
    fig_b = _make_figurinha(id=2, grupo="C", codigo_selecao="BRA", nome_selecao="Brasil",
                            numero=3, codigo_figurinha="BRA-3", pagina=24)
    mock_figurinha_repository.find_faltantes.return_value = [fig_a, fig_b]

    service = _make_service(mock_figurinha_repository)

    result = service.faltantes_agrupados(telegram_user_id=0)

    assert len(result) == 1
    assert result[0][1] == [("Brasil", "BRA", [fig_a, fig_b])]


def test_faltantes_agrupados_quando_lista_vazia_deve_retornar_lista_vazia(
    mock_figurinha_repository: MagicMock,
) -> None:
    """An empty list from the repository must produce an empty list."""
    mock_figurinha_repository.find_faltantes.return_value = []

    service = _make_service(mock_figurinha_repository)

    result = service.faltantes_agrupados(telegram_user_id=0)

    assert result == []


def test_faltantes_agrupados_fwc_split_early_e_late_em_grupos_separados(
    mock_figurinha_repository: MagicMock,
) -> None:
    """FWC stickers with pagina < 100 and pagina >= 100 appear as separate groups."""
    fwc_early = _make_figurinha(
        id=1, grupo="FWC", codigo_selecao="FWC",
        nome_selecao="FIFA World Cup History",
        numero=1, codigo_figurinha="FWC-1", pagina=1,
    )
    fwc_late = _make_figurinha(
        id=2, grupo="FWC", codigo_selecao="FWC",
        nome_selecao="FIFA World Cup History",
        numero=11, codigo_figurinha="FWC-11", pagina=107,
    )
    mock_figurinha_repository.find_faltantes.return_value = [fwc_early, fwc_late]

    service = _make_service(mock_figurinha_repository)

    result = service.faltantes_agrupados(telegram_user_id=0)

    assert len(result) == 2
    assert result[0][0] == "FWC"
    assert result[1][0] == "FWC"
    assert result[0][1][0][2] == [fwc_early]
    assert result[1][1][0][2] == [fwc_late]


def test_faltantes_agrupados_delega_chamada_ao_repositorio(
    mock_figurinha_repository: MagicMock,
) -> None:
    """faltantes_agrupados must call repository.find_faltantes() exactly once."""
    mock_figurinha_repository.find_faltantes.return_value = []

    service = _make_service(mock_figurinha_repository)
    service.faltantes_agrupados(telegram_user_id=0)

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

    result = service.repetidas(telegram_user_id=0)

    mock_figurinha_repository.find_repetidas.assert_called_once()
    assert result == [fig]


def test_repetidas_quando_repositorio_retorna_vazio_deve_retornar_lista_vazia(
    mock_figurinha_repository: MagicMock,
) -> None:
    """repetidas() must return an empty list when the repository returns none."""
    mock_figurinha_repository.find_repetidas.return_value = []

    service = _make_service(mock_figurinha_repository)

    result = service.repetidas(telegram_user_id=0)

    assert result == []


# ---------------------------------------------------------------------------
# repetidas_agrupadas
# ---------------------------------------------------------------------------


def test_repetidas_agrupadas_retorna_grupos_ordenados_por_pagina(
    mock_figurinha_repository: MagicMock,
) -> None:
    """Two figurinhas from different groups produce two group tuples in page order."""
    fig_a = _make_figurinha(
        id=1, grupo="C", codigo_selecao="BRA", nome_selecao="Brasil",
        codigo_figurinha="BRA-1", quantidade=2, pagina=24,
    )
    fig_b = _make_figurinha(
        id=2, grupo="L", codigo_selecao="ENG", nome_selecao="Inglaterra",
        codigo_figurinha="ENG-1", quantidade=3, pagina=98,
    )
    mock_figurinha_repository.find_repetidas.return_value = [fig_a, fig_b]

    service = _make_service(mock_figurinha_repository)

    result = service.repetidas_agrupadas(telegram_user_id=0)

    assert result == [
        ("Grupo C", [("Brasil", "BRA", [fig_a])]),
        ("Grupo L", [("Inglaterra", "ENG", [fig_b])]),
    ]


def test_repetidas_agrupadas_mesmo_grupo_agrupa_selecoes_juntas(
    mock_figurinha_repository: MagicMock,
) -> None:
    """Two countries in the same group appear under a single group header."""
    fig_a = _make_figurinha(id=1, grupo="C", codigo_selecao="BRA", nome_selecao="Brasil",
                            codigo_figurinha="BRA-2", quantidade=2, pagina=24)
    fig_b = _make_figurinha(id=2, grupo="C", codigo_selecao="MAR", nome_selecao="Marrocos",
                            codigo_figurinha="MAR-1", quantidade=2, pagina=26)
    mock_figurinha_repository.find_repetidas.return_value = [fig_a, fig_b]

    service = _make_service(mock_figurinha_repository)

    result = service.repetidas_agrupadas(telegram_user_id=0)

    assert len(result) == 1
    assert result[0][0] == "Grupo C"
    assert len(result[0][1]) == 2


def test_repetidas_agrupadas_quando_lista_vazia_deve_retornar_lista_vazia(
    mock_figurinha_repository: MagicMock,
) -> None:
    """An empty repository response must produce an empty list."""
    mock_figurinha_repository.find_repetidas.return_value = []

    service = _make_service(mock_figurinha_repository)

    result = service.repetidas_agrupadas(telegram_user_id=0)

    assert result == []


def test_repetidas_agrupadas_delega_chamada_ao_repositorio(
    mock_figurinha_repository: MagicMock,
) -> None:
    """repetidas_agrupadas() must call repository.find_repetidas() exactly once."""
    mock_figurinha_repository.find_repetidas.return_value = []

    service = _make_service(mock_figurinha_repository)
    service.repetidas_agrupadas(telegram_user_id=0)

    mock_figurinha_repository.find_repetidas.assert_called_once()


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

    result = service.progresso(telegram_user_id=0)

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

    result = service.progresso(telegram_user_id=0)

    assert result.total_album == 0


# ---------------------------------------------------------------------------
# progresso_detalhado
# ---------------------------------------------------------------------------


def _setup_progresso_detalhado_mocks(
    mock_figurinha_repository: MagicMock,
    *,
    contagem: list | None = None,
    faltantes: list | None = None,
    cc_faltantes: list | None = None,
) -> None:
    """Configure all mocks needed by progresso_detalhado() with safe defaults.

    ``paises_completos`` is now computed by the service from ``contagem``
    (selections with faltantes == 0), so there is no corresponding repository
    mock to set up.
    """
    from models.progresso import Progresso  # noqa: PLC0415

    mock_figurinha_repository.get_progresso.return_value = Progresso(
        total_album=670, tipos_possuidos=100, total_exemplares=200
    )
    mock_figurinha_repository.get_selecoes_faltantes_contagem.return_value = (
        contagem if contagem is not None else []
    )
    mock_figurinha_repository.find_faltantes.return_value = (
        faltantes if faltantes is not None else []
    )
    mock_figurinha_repository.get_cc_faltantes.return_value = (
        cc_faltantes if cc_faltantes is not None else []
    )


def test_progresso_detalhado_deve_delegar_get_progresso_ao_repositorio(
    mock_figurinha_repository: MagicMock,
) -> None:
    """progresso_detalhado() must call repository.get_progresso() exactly once.

    The delegated call to get_progresso is required because the base progress
    counters (total_album, tipos_possuidos, total_exemplares) originate there.
    """
    _setup_progresso_detalhado_mocks(mock_figurinha_repository)

    service = _make_service(mock_figurinha_repository)
    service.progresso_detalhado(telegram_user_id=0)

    mock_figurinha_repository.get_progresso.assert_called_once()


def test_progresso_detalhado_deve_delegar_get_selecoes_faltantes_contagem_ao_repositorio(
    mock_figurinha_repository: MagicMock,
) -> None:
    """progresso_detalhado() must call repository.get_selecoes_faltantes_contagem() once.

    This single call provides all per-selection data: the service derives
    top3_proximos, top3_distantes, and paises_completos from the result.
    """
    _setup_progresso_detalhado_mocks(mock_figurinha_repository)

    service = _make_service(mock_figurinha_repository)
    service.progresso_detalhado(telegram_user_id=0)

    mock_figurinha_repository.get_selecoes_faltantes_contagem.assert_called_once()


def test_progresso_detalhado_deve_delegar_find_faltantes_ao_repositorio(
    mock_figurinha_repository: MagicMock,
) -> None:
    """progresso_detalhado() must call repository.find_faltantes() exactly once.

    The service filters brilhantes from the full faltantes list returned here
    instead of delegating that business rule to a dedicated repository method.
    """
    _setup_progresso_detalhado_mocks(mock_figurinha_repository)

    service = _make_service(mock_figurinha_repository)
    service.progresso_detalhado(telegram_user_id=0)

    mock_figurinha_repository.find_faltantes.assert_called_once()


def test_progresso_detalhado_deve_delegar_get_cc_faltantes_ao_repositorio(
    mock_figurinha_repository: MagicMock,
) -> None:
    """progresso_detalhado() must call repository.get_cc_faltantes() exactly once."""
    _setup_progresso_detalhado_mocks(mock_figurinha_repository)

    service = _make_service(mock_figurinha_repository)
    service.progresso_detalhado(telegram_user_id=0)

    mock_figurinha_repository.get_cc_faltantes.assert_called_once()


def test_progresso_detalhado_deve_retornar_progresso_com_paises_completos(
    mock_figurinha_repository: MagicMock,
) -> None:
    """progresso_detalhado() must derive paises_completos from contagem in the service.

    contagem contains one selection with faltantes==0 (complete) and one with
    faltantes==3 (incomplete).  The returned Progresso must carry
    paises_completos == 1.
    """
    _setup_progresso_detalhado_mocks(
        mock_figurinha_repository,
        contagem=[("Brasil", 0), ("Argentina", 3)],
    )

    service = _make_service(mock_figurinha_repository)
    result = service.progresso_detalhado(telegram_user_id=0)

    assert result.paises_completos == 1


def test_progresso_detalhado_deve_retornar_progresso_com_brilhantes_faltantes(
    mock_figurinha_repository: MagicMock,
) -> None:
    """progresso_detalhado() must extract brilhantes from find_faltantes() result.

    find_faltantes returns two Figurinha objects: one A-L numero=1 sticker
    (qualifies as brilhante) and one FWC sticker (also a brilhante).  Both
    codes must appear in result.brilhantes_faltantes.
    """
    bra1 = _make_figurinha(
        codigo_figurinha="BRA-1", grupo="A", codigo_selecao="BRA", numero=1, quantidade=0
    )
    fwc3 = _make_figurinha(
        codigo_figurinha="FWC-3", grupo="FWC", codigo_selecao="FWC", numero=3, quantidade=0
    )
    _setup_progresso_detalhado_mocks(mock_figurinha_repository, faltantes=[bra1, fwc3])

    service = _make_service(mock_figurinha_repository)
    result = service.progresso_detalhado(telegram_user_id=0)

    assert "BRA-1" in result.brilhantes_faltantes and "FWC-3" in result.brilhantes_faltantes


def test_progresso_detalhado_deve_retornar_progresso_com_cc_faltantes(
    mock_figurinha_repository: MagicMock,
) -> None:
    """progresso_detalhado() must populate cc_faltantes from the repository list.

    The mock returns ["CC-2", "CC-5"]; these codes must appear in
    result.cc_faltantes.
    """
    _setup_progresso_detalhado_mocks(mock_figurinha_repository, cc_faltantes=["CC-2", "CC-5"])

    service = _make_service(mock_figurinha_repository)
    result = service.progresso_detalhado(telegram_user_id=0)

    assert "CC-2" in result.cc_faltantes and "CC-5" in result.cc_faltantes
