"""Unit tests for MovimentacaoService.

Covers the ``registrar`` public method with a fully mocked repository
collaborator.  No database connection is used.

Tested class (not yet implemented — RED phase):
    services.movimentacao_service.MovimentacaoService
"""

import pytest
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_service(mock_movimentacao_repository: MagicMock):
    """Instantiate MovimentacaoService with an injected mock repository.

    The import is deferred so collection succeeds in the RED phase, when the
    module does not yet exist.

    Args:
        mock_movimentacao_repository: Mock standing in for MovimentacaoRepository.

    Returns:
        A :class:`MovimentacaoService` instance wired with the provided mock.
    """
    from services.movimentacao_service import MovimentacaoService  # noqa: PLC0415

    return MovimentacaoService(movimentacao_repository=mock_movimentacao_repository)


# ---------------------------------------------------------------------------
# MovimentacaoService.registrar
# ---------------------------------------------------------------------------


class TestMovimentacaoServiceRegistrar:
    """Tests for ``MovimentacaoService.registrar``."""

    def test_registrar_entrada_deve_criar_movimentacao_com_tipo_entrada(
        self,
        mock_movimentacao_repository: MagicMock,
        user_info: dict,
    ):
        """registrar with tipo='ENTRADA' must persist a Movimentacao with tipo='ENTRADA'."""
        service = _make_service(mock_movimentacao_repository)

        service.registrar(
            figurinha_id=1,
            tipo="ENTRADA",
            quantidade=3,
            entrada_bruta="BRA-1",
            telegram_user_id=user_info["telegram_user_id"],
            telegram_username=user_info["telegram_username"],
        )

        mock_movimentacao_repository.insert.assert_called_once()
        assert mock_movimentacao_repository.insert.call_args.kwargs["tipo"] == "ENTRADA"

    def test_registrar_saida_deve_criar_movimentacao_com_tipo_saida(
        self,
        mock_movimentacao_repository: MagicMock,
        user_info: dict,
    ):
        """registrar with tipo='SAIDA' must persist a Movimentacao with tipo='SAIDA'."""
        service = _make_service(mock_movimentacao_repository)

        service.registrar(
            figurinha_id=1,
            tipo="SAIDA",
            quantidade=2,
            entrada_bruta="BRA-1",
            telegram_user_id=user_info["telegram_user_id"],
            telegram_username=user_info["telegram_username"],
        )

        mock_movimentacao_repository.insert.assert_called_once()
        assert mock_movimentacao_repository.insert.call_args.kwargs["tipo"] == "SAIDA"

    def test_registrar_deve_propagar_telegram_user_id_corretamente(
        self,
        mock_movimentacao_repository: MagicMock,
        user_info: dict,
    ):
        """The telegram_user_id received must be forwarded unchanged to the repository."""
        service = _make_service(mock_movimentacao_repository)

        service.registrar(
            figurinha_id=1,
            tipo="ENTRADA",
            quantidade=1,
            entrada_bruta="BRA-1",
            telegram_user_id=user_info["telegram_user_id"],
            telegram_username=user_info["telegram_username"],
        )

        assert mock_movimentacao_repository.insert.call_args.kwargs["telegram_user_id"] == user_info["telegram_user_id"]

    def test_registrar_deve_propagar_telegram_username_corretamente(
        self,
        mock_movimentacao_repository: MagicMock,
        user_info: dict,
    ):
        """The telegram_username received must be forwarded unchanged to the repository."""
        service = _make_service(mock_movimentacao_repository)

        service.registrar(
            figurinha_id=1,
            tipo="ENTRADA",
            quantidade=1,
            entrada_bruta="BRA-1",
            telegram_user_id=user_info["telegram_user_id"],
            telegram_username=user_info["telegram_username"],
        )

        assert mock_movimentacao_repository.insert.call_args.kwargs["telegram_username"] == user_info["telegram_username"]

    def test_registrar_deve_propagar_entrada_bruta_sem_modificacao(
        self,
        mock_movimentacao_repository: MagicMock,
        user_info: dict,
    ):
        """The raw input string must be stored in the Movimentacao without any transformation."""
        service = _make_service(mock_movimentacao_repository)
        raw_input = "  BRA-1  "

        service.registrar(
            figurinha_id=1,
            tipo="ENTRADA",
            quantidade=1,
            entrada_bruta=raw_input,
            telegram_user_id=user_info["telegram_user_id"],
            telegram_username=user_info["telegram_username"],
        )

        assert mock_movimentacao_repository.insert.call_args.kwargs["entrada_bruta"] == raw_input

    def test_registrar_quando_repositorio_lanca_excecao_deve_propagar_sem_silenciar(
        self,
        mock_movimentacao_repository: MagicMock,
        user_info: dict,
    ):
        """Any exception raised by the repository must propagate to the caller unmodified."""
        service = _make_service(mock_movimentacao_repository)
        mock_movimentacao_repository.insert.side_effect = RuntimeError("db failure")

        with pytest.raises(RuntimeError, match="db failure"):
            service.registrar(
                figurinha_id=1,
                tipo="ENTRADA",
                quantidade=1,
                entrada_bruta="BRA-1",
                telegram_user_id=user_info["telegram_user_id"],
                telegram_username=user_info["telegram_username"],
            )
