"""Domain-level exceptions for the Album Copa 2026 project.

All custom exceptions inherit from :class:`AlbumCopaError` so callers can
catch the entire hierarchy with a single ``except AlbumCopaError`` clause
when broad error handling is appropriate.
"""


class AlbumCopaError(Exception):
    """Exceção base do projeto."""


class CodigoInvalidoError(AlbumCopaError):
    """Código de figurinha não reconhecido ou fora do intervalo válido."""


class FigurinhaNaoEncontradaError(AlbumCopaError):
    """Figurinha com o código fornecido não existe no banco."""


class QuantidadeInsuficienteError(AlbumCopaError):
    """Operação de remoção resultaria em quantidade negativa.

    Attributes:
        codigo: The sticker code that triggered the error.
        saldo_atual: Current quantity available for the sticker.
        quantidade_solicitada: Quantity that was requested for removal.
    """

    def __init__(self, codigo: str, saldo_atual: int, quantidade_solicitada: int) -> None:
        """Initialise the exception with contextual balance information.

        Args:
            codigo: The sticker code that triggered the error.
            saldo_atual: Current quantity available for the sticker.
            quantidade_solicitada: Quantity that was requested for removal.
        """
        self.codigo = codigo
        self.saldo_atual = saldo_atual
        self.quantidade_solicitada = quantidade_solicitada
        super().__init__(
            f"Saldo insuficiente para {codigo}: "
            f"disponível={saldo_atual}, solicitado={quantidade_solicitada}"
        )
