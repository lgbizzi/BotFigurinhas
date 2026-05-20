"""Unit tests for FigurinhaService.

Covers the ``adicionar`` and ``remover`` public methods with fully mocked
repository and service collaborators.  No database connection is used.

Tested class (not yet implemented — RED phase):
    services.figurinha_service.FigurinhaService
"""

import pytest
from unittest.mock import MagicMock, call

from exceptions.domain_exceptions import (
    FigurinhaNaoEncontradaError,
    QuantidadeInsuficienteError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_service(mock_figurinha_repository: MagicMock, mock_movimentacao_service: MagicMock):
    """Instantiate FigurinhaService with injected collaborators.

    The import is deferred so collection succeeds in the RED phase, when the
    module does not yet exist.

    Args:
        mock_figurinha_repository: Mock standing in for FigurinhaRepository.
        mock_movimentacao_service: Mock standing in for MovimentacaoService.

    Returns:
        A :class:`FigurinhaService` instance wired with the provided mocks.
    """
    from services.figurinha_service import FigurinhaService  # noqa: PLC0415

    codigo_parser = MagicMock(name="CodigoParser")
    return FigurinhaService(
        figurinha_repository=mock_figurinha_repository,
        movimentacao_service=mock_movimentacao_service,
        codigo_parser=codigo_parser,
    ), codigo_parser


# ---------------------------------------------------------------------------
# FigurinhaService.adicionar
# ---------------------------------------------------------------------------


class TestFigurinhaServiceAdicionar:
    """Tests for ``FigurinhaService.adicionar``."""

    def test_adicionar_quando_figurinha_com_quantidade_zero_deve_retornar_quantidade_um(
        self,
        mock_figurinha_repository: MagicMock,
        mock_movimentacao_repository: MagicMock,
        sample_figurinha,
        user_info: dict,
    ):
        """Sticker starts at 0; adding 1 must persist and return quantity 1."""
        mock_movimentacao_service = MagicMock(name="MovimentacaoService")
        service, codigo_parser = _make_service(mock_figurinha_repository, mock_movimentacao_service)

        sample_figurinha.quantidade = 0
        codigo_parser.normalizar.return_value = sample_figurinha.codigo_figurinha
        mock_figurinha_repository.find_by_codigo.return_value = sample_figurinha
        mock_figurinha_repository.update_quantidade.return_value = None

        result = service.adicionar(
            entrada_bruta="BRA-1",
            quantidade=1,
            telegram_user_id=user_info["telegram_user_id"],
            telegram_username=user_info["telegram_username"],
        )

        assert result.quantidade == 1

    def test_adicionar_quando_n_figurinhas_deve_incrementar_corretamente(
        self,
        mock_figurinha_repository: MagicMock,
        mock_movimentacao_repository: MagicMock,
        sample_figurinha,
        user_info: dict,
    ):
        """Adding N to an existing stock of M must yield M+N."""
        mock_movimentacao_service = MagicMock(name="MovimentacaoService")
        service, codigo_parser = _make_service(mock_figurinha_repository, mock_movimentacao_service)

        sample_figurinha.quantidade = 3
        codigo_parser.normalizar.return_value = sample_figurinha.codigo_figurinha
        mock_figurinha_repository.find_by_codigo.return_value = sample_figurinha
        mock_figurinha_repository.update_quantidade.return_value = None

        result = service.adicionar(
            entrada_bruta="BRA-1",
            quantidade=4,
            telegram_user_id=user_info["telegram_user_id"],
            telegram_username=user_info["telegram_username"],
        )

        assert result.quantidade == 7

    def test_adicionar_deve_chamar_movimentacao_service_com_tipo_entrada(
        self,
        mock_figurinha_repository: MagicMock,
        mock_movimentacao_repository: MagicMock,
        sample_figurinha,
        user_info: dict,
    ):
        """``adicionar`` must delegate movement registration with tipo='ENTRADA'."""
        mock_movimentacao_service = MagicMock(name="MovimentacaoService")
        service, codigo_parser = _make_service(mock_figurinha_repository, mock_movimentacao_service)

        sample_figurinha.quantidade = 0
        codigo_parser.normalizar.return_value = sample_figurinha.codigo_figurinha
        mock_figurinha_repository.find_by_codigo.return_value = sample_figurinha

        service.adicionar(
            entrada_bruta="BRA-1",
            quantidade=2,
            telegram_user_id=user_info["telegram_user_id"],
            telegram_username=user_info["telegram_username"],
        )

        mock_movimentacao_service.registrar.assert_called_once()
        assert mock_movimentacao_service.registrar.call_args.kwargs["tipo"] == "ENTRADA"

    def test_adicionar_quando_codigo_invalido_deve_lancar_figurinha_nao_encontrada_error(
        self,
        mock_figurinha_repository: MagicMock,
        mock_movimentacao_repository: MagicMock,
        user_info: dict,
    ):
        """Unknown sticker code must raise ``FigurinhaNaoEncontradaError``."""
        mock_movimentacao_service = MagicMock(name="MovimentacaoService")
        service, codigo_parser = _make_service(mock_figurinha_repository, mock_movimentacao_service)

        codigo_parser.normalizar.return_value = "BRA-999"
        mock_figurinha_repository.find_by_codigo.return_value = None

        with pytest.raises(FigurinhaNaoEncontradaError):
            service.adicionar(
                entrada_bruta="BRA-999",
                quantidade=1,
                telegram_user_id=user_info["telegram_user_id"],
                telegram_username=user_info["telegram_username"],
            )

    def test_adicionar_quando_quantidade_zero_deve_lancar_value_error(
        self,
        mock_figurinha_repository: MagicMock,
        mock_movimentacao_repository: MagicMock,
        user_info: dict,
    ):
        """quantidade=0 is semantically invalid and must raise ``ValueError``."""
        mock_movimentacao_service = MagicMock(name="MovimentacaoService")
        service, _ = _make_service(mock_figurinha_repository, mock_movimentacao_service)

        with pytest.raises(ValueError):
            service.adicionar(
                entrada_bruta="BRA-1",
                quantidade=0,
                telegram_user_id=user_info["telegram_user_id"],
                telegram_username=user_info["telegram_username"],
            )

    def test_adicionar_quando_quantidade_negativa_deve_lancar_value_error(
        self,
        mock_figurinha_repository: MagicMock,
        mock_movimentacao_repository: MagicMock,
        user_info: dict,
    ):
        """Negative quantidade must raise ``ValueError`` before any DB call."""
        mock_movimentacao_service = MagicMock(name="MovimentacaoService")
        service, _ = _make_service(mock_figurinha_repository, mock_movimentacao_service)

        with pytest.raises(ValueError):
            service.adicionar(
                entrada_bruta="BRA-1",
                quantidade=-5,
                telegram_user_id=user_info["telegram_user_id"],
                telegram_username=user_info["telegram_username"],
            )


# ---------------------------------------------------------------------------
# FigurinhaService.remover
# ---------------------------------------------------------------------------


class TestFigurinhaServiceRemover:
    """Tests for ``FigurinhaService.remover``."""

    def test_remover_quando_quantidade_suficiente_deve_decrementar_corretamente(
        self,
        mock_figurinha_repository: MagicMock,
        mock_movimentacao_repository: MagicMock,
        sample_figurinha,
        user_info: dict,
    ):
        """Removing K from a stock of N > K must yield N-K."""
        mock_movimentacao_service = MagicMock(name="MovimentacaoService")
        service, codigo_parser = _make_service(mock_figurinha_repository, mock_movimentacao_service)

        sample_figurinha.quantidade = 5
        codigo_parser.normalizar.return_value = sample_figurinha.codigo_figurinha
        mock_figurinha_repository.find_by_codigo.return_value = sample_figurinha

        result = service.remover(
            entrada_bruta="BRA-1",
            quantidade=3,
            telegram_user_id=user_info["telegram_user_id"],
            telegram_username=user_info["telegram_username"],
        )

        assert result.quantidade == 2

    def test_remover_quando_quantidade_exata_deve_resultar_em_zero(
        self,
        mock_figurinha_repository: MagicMock,
        mock_movimentacao_repository: MagicMock,
        sample_figurinha,
        user_info: dict,
    ):
        """Removing exactly N from a stock of N must leave quantity at 0."""
        mock_movimentacao_service = MagicMock(name="MovimentacaoService")
        service, codigo_parser = _make_service(mock_figurinha_repository, mock_movimentacao_service)

        sample_figurinha.quantidade = 4
        codigo_parser.normalizar.return_value = sample_figurinha.codigo_figurinha
        mock_figurinha_repository.find_by_codigo.return_value = sample_figurinha

        result = service.remover(
            entrada_bruta="BRA-1",
            quantidade=4,
            telegram_user_id=user_info["telegram_user_id"],
            telegram_username=user_info["telegram_username"],
        )

        assert result.quantidade == 0

    def test_remover_quando_quantidade_insuficiente_deve_lancar_quantidade_insuficiente_error(
        self,
        mock_figurinha_repository: MagicMock,
        mock_movimentacao_repository: MagicMock,
        sample_figurinha,
        user_info: dict,
    ):
        """Removing more than the available stock must raise ``QuantidadeInsuficienteError``."""
        mock_movimentacao_service = MagicMock(name="MovimentacaoService")
        service, codigo_parser = _make_service(mock_figurinha_repository, mock_movimentacao_service)

        sample_figurinha.quantidade = 2
        codigo_parser.normalizar.return_value = sample_figurinha.codigo_figurinha
        mock_figurinha_repository.find_by_codigo.return_value = sample_figurinha

        with pytest.raises(QuantidadeInsuficienteError) as exc_info:
            service.remover(
                entrada_bruta="BRA-1",
                quantidade=5,
                telegram_user_id=user_info["telegram_user_id"],
                telegram_username=user_info["telegram_username"],
            )

        assert exc_info.value.saldo_atual == 2

    def test_remover_deve_chamar_movimentacao_service_com_tipo_saida(
        self,
        mock_figurinha_repository: MagicMock,
        mock_movimentacao_repository: MagicMock,
        sample_figurinha,
        user_info: dict,
    ):
        """``remover`` must delegate movement registration with tipo='SAIDA'."""
        mock_movimentacao_service = MagicMock(name="MovimentacaoService")
        service, codigo_parser = _make_service(mock_figurinha_repository, mock_movimentacao_service)

        sample_figurinha.quantidade = 10
        codigo_parser.normalizar.return_value = sample_figurinha.codigo_figurinha
        mock_figurinha_repository.find_by_codigo.return_value = sample_figurinha

        service.remover(
            entrada_bruta="BRA-1",
            quantidade=3,
            telegram_user_id=user_info["telegram_user_id"],
            telegram_username=user_info["telegram_username"],
        )

        mock_movimentacao_service.registrar.assert_called_once()
        assert mock_movimentacao_service.registrar.call_args.kwargs["tipo"] == "SAIDA"

    def test_remover_quando_codigo_invalido_deve_lancar_figurinha_nao_encontrada_error(
        self,
        mock_figurinha_repository: MagicMock,
        mock_movimentacao_repository: MagicMock,
        user_info: dict,
    ):
        """Unknown sticker code must raise ``FigurinhaNaoEncontradaError``."""
        mock_movimentacao_service = MagicMock(name="MovimentacaoService")
        service, codigo_parser = _make_service(mock_figurinha_repository, mock_movimentacao_service)

        codigo_parser.normalizar.return_value = "BRA-999"
        mock_figurinha_repository.find_by_codigo.return_value = None

        with pytest.raises(FigurinhaNaoEncontradaError):
            service.remover(
                entrada_bruta="BRA-999",
                quantidade=1,
                telegram_user_id=user_info["telegram_user_id"],
                telegram_username=user_info["telegram_username"],
            )
