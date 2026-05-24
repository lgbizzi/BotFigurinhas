"""Parser de códigos de figurinha para o Album Copa 2026.

Este módulo expõe :class:`CodigoParser`, responsável por normalizar entradas
brutas do usuário (texto livre, variações de separador, nomes de seleções) para
o formato canônico ``<CODIGO>-<numero>`` (ex.: ``BRA-1``, ``FWC-0``, ``CC-14``).
"""

import logging
import re

from unidecode import unidecode

from exceptions.domain_exceptions import CodigoInvalidoError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes privadas do módulo
# ---------------------------------------------------------------------------

_NOME_PARA_CODIGO: dict[str, str] = {
    "MEXICO": "MEX",
    "AFRICA DO SUL": "RSA",
    "COREIA DO SUL": "KOR",
    "REPUBLICA TCHECA": "CZE",
    "CANADA": "CAN",
    "BOSNIA E HERZEGOVINA": "BIH",
    "BOSNIA": "BIH",
    "CATAR": "QAT",
    "SUICA": "SUI",
    "BRASIL": "BRA",
    "MARROCOS": "MAR",
    "HAITI": "HAI",
    "ESCOCIA": "SCO",
    "ESTADOS UNIDOS": "USA",
    "PARAGUAI": "PAR",
    "AUSTRALIA": "AUS",
    "TURQUIA": "TUR",
    "ALEMANHA": "GER",
    "CURACAO": "CUW",
    "COSTA DO MARFIM": "CIV",
    "EQUADOR": "ECU",
    "HOLANDA": "NED",
    "JAPAO": "JPN",
    "SUECIA": "SWE",
    "TUNISIA": "TUN",
    "BELGICA": "BEL",
    "EGITO": "EGY",
    "IRA": "IRN",
    "IRAN": "IRN",
    "NOVA ZELANDIA": "NZL",
    "ESPANHA": "ESP",
    "CABO VERDE": "CPV",
    "ARABIA SAUDITA": "KSA",
    "URUGUAI": "URU",
    "FRANCA": "FRA",
    "SENEGAL": "SEN",
    "IRAQUE": "IRQ",
    "NORUEGA": "NOR",
    "ARGENTINA": "ARG",
    "ARGELIA": "ALG",
    "AUSTRIA": "AUT",
    "JORDANIA": "JOR",
    "PORTUGAL": "POR",
    "RD CONGO": "COD",
    "CONGO": "COD",
    "UZBEQUISTAO": "UZB",
    "COLOMBIA": "COL",
    "CROACIA": "CRO",
    "GANA": "GHA",
    "INGLATERRA": "ENG",
    "PANAMA": "PAN",
    "FIFA WORLD CUP HISTORY": "FWC",
    "COCA COLA": "CC",
    "COCA-COLA": "CC",
}

# Nomes compostos (com espaço) listados separadamente para ordenação por comprimento
# A ordenação é feita em tempo de uso para garantir que nomes mais longos têm prioridade.
_NOMES_COMPOSTOS: tuple[str, ...] = tuple(
    sorted(
        (nome for nome in _NOME_PARA_CODIGO if " " in nome or "-" in nome),
        key=len,
        reverse=True,
    )
)

_NOMES_SIMPLES: tuple[str, ...] = tuple(
    nome for nome in _NOME_PARA_CODIGO if nome not in _NOMES_COMPOSTOS
)

_CODIGOS_VALIDOS: frozenset[str] = frozenset(
    {
        "MEX", "RSA", "KOR", "CZE",
        "CAN", "BIH", "QAT", "SUI",
        "BRA", "MAR", "HAI", "SCO",
        "USA", "PAR", "AUS", "TUR",
        "GER", "CUW", "CIV", "ECU",
        "NED", "JPN", "SWE", "TUN",
        "BEL", "EGY", "IRN", "NZL",
        "ESP", "CPV", "KSA", "URU",
        "FRA", "SEN", "IRQ", "NOR",
        "ARG", "ALG", "AUT", "JOR",
        "POR", "COD", "UZB", "COL",
        "CRO", "GHA", "ENG", "PAN",
        "FWC", "CC",
    }
)

# (min_inclusivo, max_inclusivo)
_INTERVALOS: dict[str, tuple[int, int]] = {
    "FWC": (0, 19),
    "CC": (1, 14),
}
# Todos os demais códigos de seleção usam o intervalo padrão (1, 20)
_INTERVALO_SELECAO: tuple[int, int] = (1, 20)

# Regex para extrair (CODIGO, numero) do texto já normalizado.
# Aceita separador opcional (hífen ou espaço) entre o código e o número.
_REGEX_CODIGO: re.Pattern[str] = re.compile(r"^([A-Z]{2,5})[-\s]?(\d{1,3})$")


class CodigoParser:
    """Normaliza entradas brutas do usuário para o formato canônico de figurinha.

    O formato canônico é ``<CODIGO>-<numero>`` sem zeros à esquerda no número,
    por exemplo: ``BRA-1``, ``FWC-0``, ``CC-14``.

    O método público :meth:`normalizar` aplica a sequência de passos de
    normalização internos em ordem determinística e lança
    :class:`~exceptions.domain_exceptions.CodigoInvalidoError` para qualquer
    entrada irreconhecível ou fora do intervalo válido.

    Example::

        >>> parser = CodigoParser()
        >>> parser.normalizar("brasil 1")
        'BRA-1'
        >>> parser.normalizar("BRA-01")
        'BRA-1'
        >>> parser.normalizar("FWC 0")
        'FWC-0'
    """

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def resolver_selecao(self, entrada: str) -> str:
        """Resolve a country name or bare code to its canonical codigo_selecao.

        Accepts the same Portuguese names and accented variants recognised by
        :meth:`normalizar`, but does **not** require a sticker number.

        Args:
            entrada: Country name or code, e.g. ``"Brasil"``, ``"BRA"``,
                ``"Alemanha"``, ``"Costa do Marfim"``.

        Returns:
            Canonical ``codigo_selecao`` string, e.g. ``"BRA"``.

        Raises:
            CodigoInvalidoError: If the entry cannot be matched to any known
                selection in the Copa 2026 album.
        """
        texto = self._limpar(entrada)
        texto = self._normalizar_acentos(texto)

        if texto in _CODIGOS_VALIDOS:
            return texto

        for nome in _NOMES_COMPOSTOS:
            if texto == nome:
                return _NOME_PARA_CODIGO[nome]

        for nome in _NOMES_SIMPLES:
            if texto == nome:
                return _NOME_PARA_CODIGO[nome]

        raise CodigoInvalidoError(
            f"País não reconhecido: {entrada!r}. "
            "Use o nome em português, ex.: 'Brasil', 'Argentina', 'Alemanha', 'Costa do Marfim'."
        )

    def normalizar(self, entrada: str) -> str:
        """Recebe texto bruto do usuário e retorna o código canônico.

        Args:
            entrada: Texto bruto digitado pelo usuário, por exemplo
                ``"Brasil 1"``, ``"BRA-01"`` ou ``"fwc 0"``.

        Returns:
            Código canônico no formato ``<CODIGO>-<numero>``,
            por exemplo ``"BRA-1"`` ou ``"FWC-0"``.

        Raises:
            CodigoInvalidoError: Se a entrada for vazia, não reconhecível
                como código ou nome de seleção, contiver um código
                desconhecido, ou o número estiver fora do intervalo válido.
        """
        texto = self._limpar(entrada)
        texto = self._normalizar_acentos(texto)
        texto = self._resolver_nome(texto)
        codigo, numero = self._extrair_partes(texto)
        self._validar_codigo(codigo)
        self._validar_intervalo(codigo, numero)

        resultado = f"{codigo}-{numero}"
        logger.debug("Código normalizado: %r → %r", entrada, resultado)
        return resultado

    # ------------------------------------------------------------------
    # Passos privados
    # ------------------------------------------------------------------

    def _limpar(self, entrada: str) -> str:
        """Remove espaços nas extremidades e rejeita entradas vazias.

        Args:
            entrada: Texto bruto fornecido pelo usuário.

        Returns:
            Texto com strip aplicado.

        Raises:
            CodigoInvalidoError: Se a entrada (após strip) estiver vazia.
        """
        texto = entrada.strip()
        if not texto:
            raise CodigoInvalidoError("Entrada vazia: nenhum código foi fornecido.")
        return texto

    def _normalizar_acentos(self, texto: str) -> str:
        """Remove acentuação via unidecode e converte para maiúsculas.

        Args:
            texto: Texto após limpeza inicial.

        Returns:
            Texto sem acentos em letras maiúsculas.
        """
        return unidecode(texto).upper()

    def _resolver_nome(self, texto: str) -> str:
        """Substitui nomes completos de seleção pelo código oficial.

        Nomes compostos (com espaço ou hífen) têm prioridade sobre nomes
        simples, pois são verificados primeiro em ordem decrescente de
        comprimento para evitar correspondências parciais incorretas.

        Args:
            texto: Texto já sem acentos e em maiúsculas.

        Returns:
            Texto com o nome substituído pelo código, se reconhecido;
            caso contrário, o texto original é retornado sem alteração.
        """
        # Verifica nomes compostos primeiro (mais longos têm prioridade)
        for nome in _NOMES_COMPOSTOS:
            if texto.startswith(nome):
                sufixo = texto[len(nome):]
                return _NOME_PARA_CODIGO[nome] + sufixo

        # Verifica nomes simples
        for nome in _NOMES_SIMPLES:
            if texto.startswith(nome):
                sufixo = texto[len(nome):]
                return _NOME_PARA_CODIGO[nome] + sufixo

        return texto

    def _extrair_partes(self, texto: str) -> tuple[str, int]:
        """Extrai o código alfanumérico e o número de figurinha via regex.

        Padrão aceito: ``^([A-Z]{2,5})[-\\s]?(\\d{1,3})$``

        Args:
            texto: Texto normalizado, possivelmente já com o código resolvido.

        Returns:
            Tupla ``(codigo, numero)`` onde *codigo* é a string em maiúsculas
            e *numero* é o inteiro sem zeros à esquerda.

        Raises:
            CodigoInvalidoError: Se o texto não corresponder ao padrão esperado.
        """
        match = _REGEX_CODIGO.match(texto)
        if not match:
            raise CodigoInvalidoError(
                f"Formato inválido: {texto!r} não corresponde ao padrão "
                "'<CODIGO><numero>' (ex.: 'BRA-1', 'FWC0', 'CC 14')."
            )
        codigo = match.group(1)
        numero = int(match.group(2))  # int() remove zeros à esquerda automaticamente
        return codigo, numero

    def _validar_codigo(self, codigo: str) -> None:
        """Verifica se o código existe no conjunto de códigos válidos do álbum.

        Args:
            codigo: Código de seleção ou seção especial (ex.: ``"BRA"``, ``"FWC"``).

        Raises:
            CodigoInvalidoError: Se o código não pertencer a ``_CODIGOS_VALIDOS``.
        """
        if codigo not in _CODIGOS_VALIDOS:
            raise CodigoInvalidoError(
                f"Código desconhecido: {codigo!r} não existe no álbum Copa 2026. "
                f"Códigos válidos: {sorted(_CODIGOS_VALIDOS)}"
            )

    def _validar_intervalo(self, codigo: str, numero: int) -> None:
        """Verifica se o número da figurinha está dentro do intervalo permitido.

        Args:
            codigo: Código de seleção ou seção especial já validado.
            numero: Número inteiro da figurinha.

        Raises:
            CodigoInvalidoError: Se o número estiver fora do intervalo válido
                para o código fornecido.
        """
        minimo, maximo = _INTERVALOS.get(codigo, _INTERVALO_SELECAO)
        if not (minimo <= numero <= maximo):
            raise CodigoInvalidoError(
                f"Número fora do intervalo para {codigo!r}: recebido {numero}, "
                f"esperado entre {minimo} e {maximo} (inclusive)."
            )
