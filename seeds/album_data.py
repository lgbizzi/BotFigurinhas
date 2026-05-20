"""Source-of-truth for the Copa 2026 sticker album structure.

This module is intentionally free of external dependencies — it contains only
plain Python data structures so that it can be imported safely in any context
(seeds, tests, documentation tools, etc.).

The exported constant :data:`ALBUM_GROUPS` is a list of :class:`AlbumGroup`
dataclasses, each describing one group (or special section) of the album.

Total sticker count: **995**
- 12 groups × 4 teams × 20 stickers = 960
- FWC section: numbers 0–19 = 20 stickers  (note: FWC-0 is included)
- CC section:  numbers 1–14 = 14 stickers

Example::

    from seeds.album_data import ALBUM_GROUPS

    for group in ALBUM_GROUPS:
        print(group.grupo, group.codigo_selecao, len(group.numeros))
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AlbumGroup:
    """Represents one team / special section in the album.

    Attributes:
        grupo: Group label (e.g. ``"A"``, ``"FWC"``, ``"CC"``).
        codigo_selecao: Short team code (e.g. ``"BRA"``, ``"FWC"``, ``"CC"``).
        nome_selecao: Full team / section name in Portuguese.
        numeros: Ordered list of sticker numbers for this entry.
    """

    grupo: str
    codigo_selecao: str
    nome_selecao: str
    numeros: tuple[int, ...]


def _team_range(start: int = 1, end: int = 20) -> tuple[int, ...]:
    """Return a tuple of integers from *start* to *end* inclusive.

    Args:
        start: First number (default 1).
        end: Last number inclusive (default 20).

    Returns:
        Tuple of integers ``[start, end]``.
    """
    return tuple(range(start, end + 1))


# ---------------------------------------------------------------------------
# Album data — one entry per team / section
# ---------------------------------------------------------------------------

ALBUM_GROUPS: tuple[AlbumGroup, ...] = (
    # ------------------------------------------------------------------
    # Grupo A
    # ------------------------------------------------------------------
    AlbumGroup("A", "MEX", "México", _team_range()),
    AlbumGroup("A", "RSA", "África do Sul", _team_range()),
    AlbumGroup("A", "KOR", "Coreia do Sul", _team_range()),
    AlbumGroup("A", "CZE", "República Tcheca", _team_range()),
    # ------------------------------------------------------------------
    # Grupo B
    # ------------------------------------------------------------------
    AlbumGroup("B", "CAN", "Canadá", _team_range()),
    AlbumGroup("B", "BIH", "Bósnia e Herzegovina", _team_range()),
    AlbumGroup("B", "QAT", "Catar", _team_range()),
    AlbumGroup("B", "SUI", "Suíça", _team_range()),
    # ------------------------------------------------------------------
    # Grupo C
    # ------------------------------------------------------------------
    AlbumGroup("C", "BRA", "Brasil", _team_range()),
    AlbumGroup("C", "MAR", "Marrocos", _team_range()),
    AlbumGroup("C", "HAI", "Haiti", _team_range()),
    AlbumGroup("C", "SCO", "Escócia", _team_range()),
    # ------------------------------------------------------------------
    # Grupo D
    # ------------------------------------------------------------------
    AlbumGroup("D", "USA", "Estados Unidos", _team_range()),
    AlbumGroup("D", "PAR", "Paraguai", _team_range()),
    AlbumGroup("D", "AUS", "Austrália", _team_range()),
    AlbumGroup("D", "TUR", "Turquia", _team_range()),
    # ------------------------------------------------------------------
    # Grupo E
    # ------------------------------------------------------------------
    AlbumGroup("E", "GER", "Alemanha", _team_range()),
    AlbumGroup("E", "CUW", "Curaçao", _team_range()),
    AlbumGroup("E", "CIV", "Costa do Marfim", _team_range()),
    AlbumGroup("E", "ECU", "Equador", _team_range()),
    # ------------------------------------------------------------------
    # Grupo F
    # ------------------------------------------------------------------
    AlbumGroup("F", "NED", "Holanda", _team_range()),
    AlbumGroup("F", "JPN", "Japão", _team_range()),
    AlbumGroup("F", "SWE", "Suécia", _team_range()),
    AlbumGroup("F", "TUN", "Tunísia", _team_range()),
    # ------------------------------------------------------------------
    # Grupo G
    # ------------------------------------------------------------------
    AlbumGroup("G", "BEL", "Bélgica", _team_range()),
    AlbumGroup("G", "EGY", "Egito", _team_range()),
    AlbumGroup("G", "IRN", "Irã", _team_range()),
    AlbumGroup("G", "NZL", "Nova Zelândia", _team_range()),
    # ------------------------------------------------------------------
    # Grupo H
    # ------------------------------------------------------------------
    AlbumGroup("H", "ESP", "Espanha", _team_range()),
    AlbumGroup("H", "CPV", "Cabo Verde", _team_range()),
    AlbumGroup("H", "KSA", "Arábia Saudita", _team_range()),
    AlbumGroup("H", "URU", "Uruguai", _team_range()),
    # ------------------------------------------------------------------
    # Grupo I
    # ------------------------------------------------------------------
    AlbumGroup("I", "FRA", "França", _team_range()),
    AlbumGroup("I", "SEN", "Senegal", _team_range()),
    AlbumGroup("I", "IRQ", "Iraque", _team_range()),
    AlbumGroup("I", "NOR", "Noruega", _team_range()),
    # ------------------------------------------------------------------
    # Grupo J
    # ------------------------------------------------------------------
    AlbumGroup("J", "ARG", "Argentina", _team_range()),
    AlbumGroup("J", "ALG", "Argélia", _team_range()),
    AlbumGroup("J", "AUT", "Áustria", _team_range()),
    AlbumGroup("J", "JOR", "Jordânia", _team_range()),
    # ------------------------------------------------------------------
    # Grupo K
    # ------------------------------------------------------------------
    AlbumGroup("K", "POR", "Portugal", _team_range()),
    AlbumGroup("K", "COD", "RD Congo", _team_range()),
    AlbumGroup("K", "UZB", "Uzbequistão", _team_range()),
    AlbumGroup("K", "COL", "Colômbia", _team_range()),
    # ------------------------------------------------------------------
    # Grupo L
    # ------------------------------------------------------------------
    AlbumGroup("L", "CRO", "Croácia", _team_range()),
    AlbumGroup("L", "GHA", "Gana", _team_range()),
    AlbumGroup("L", "ENG", "Inglaterra", _team_range()),
    AlbumGroup("L", "PAN", "Panamá", _team_range()),
    # ------------------------------------------------------------------
    # Special sections
    # ------------------------------------------------------------------
    # FWC: FIFA World Cup History — numbers 0 to 20 (21 stickers total, FWC-0 included)
    AlbumGroup("FWC", "FWC", "FIFA World Cup History", _team_range(0, 20)),
    # CC: Coca-Cola — numbers 1 to 14
    AlbumGroup("CC", "CC", "Coca-Cola", _team_range(1, 14)),
)

# ---------------------------------------------------------------------------
# Sanity check constant — must equal 995
# ---------------------------------------------------------------------------
TOTAL_FIGURINHAS: int = sum(len(g.numeros) for g in ALBUM_GROUPS)

# Raise immediately if the data is inconsistent so seeds / tests fail fast.
if TOTAL_FIGURINHAS != 995:
    raise AssertionError(
        f"album_data integrity check failed: expected 995 figurinhas, "
        f"got {TOTAL_FIGURINHAS}. Review the ALBUM_GROUPS constant."
    )
