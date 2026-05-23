"""Source-of-truth for the Copa 2026 sticker album structure.

This module is intentionally free of external dependencies — it contains only
plain Python data structures so that it can be imported safely in any context
(seeds, tests, documentation tools, etc.).

The exported constant :data:`ALBUM_GROUPS` is a list of :class:`AlbumGroup`
dataclasses, each describing one group (or special section) of the album.

Total sticker count: **994**
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
        pagina: Physical album page where all stickers of this entry are located.
            For entries where the page varies per sticker number, use
            ``pagina_por_numero`` and leave this as the default ``0``.
        pagina_por_numero: Optional per-sticker-number page override.  When a
            sticker number is present in this mapping, its page takes precedence
            over ``pagina``.  Used by FWC and CC sections.
    """

    grupo: str
    codigo_selecao: str
    nome_selecao: str
    numeros: tuple[int, ...]
    pagina: int = 0
    pagina_por_numero: dict[int, int] = field(default_factory=dict)

    def get_pagina(self, numero: int) -> int:
        """Return the physical album page for the given sticker number.

        Checks ``pagina_por_numero`` first; falls back to ``pagina`` when the
        number is not explicitly mapped.

        Args:
            numero: Sticker number within this album group.

        Returns:
            Physical page number in the album.
        """
        return self.pagina_por_numero.get(numero, self.pagina)


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
    AlbumGroup("A", "MEX", "México", _team_range(), pagina=8),
    AlbumGroup("A", "RSA", "África do Sul", _team_range(), pagina=10),
    AlbumGroup("A", "KOR", "Coreia do Sul", _team_range(), pagina=12),
    AlbumGroup("A", "CZE", "República Tcheca", _team_range(), pagina=14),
    # ------------------------------------------------------------------
    # Grupo B
    # ------------------------------------------------------------------
    AlbumGroup("B", "CAN", "Canadá", _team_range(), pagina=16),
    AlbumGroup("B", "BIH", "Bósnia e Herzegovina", _team_range(), pagina=18),
    AlbumGroup("B", "QAT", "Catar", _team_range(), pagina=20),
    AlbumGroup("B", "SUI", "Suíça", _team_range(), pagina=22),
    # ------------------------------------------------------------------
    # Grupo C
    # ------------------------------------------------------------------
    AlbumGroup("C", "BRA", "Brasil", _team_range(), pagina=24),
    AlbumGroup("C", "MAR", "Marrocos", _team_range(), pagina=26),
    AlbumGroup("C", "HAI", "Haiti", _team_range(), pagina=28),
    AlbumGroup("C", "SCO", "Escócia", _team_range(), pagina=30),
    # ------------------------------------------------------------------
    # Grupo D
    # ------------------------------------------------------------------
    AlbumGroup("D", "USA", "Estados Unidos", _team_range(), pagina=32),
    AlbumGroup("D", "PAR", "Paraguai", _team_range(), pagina=34),
    AlbumGroup("D", "AUS", "Austrália", _team_range(), pagina=36),
    AlbumGroup("D", "TUR", "Turquia", _team_range(), pagina=38),
    # ------------------------------------------------------------------
    # Grupo E
    # ------------------------------------------------------------------
    AlbumGroup("E", "GER", "Alemanha", _team_range(), pagina=40),
    AlbumGroup("E", "CUW", "Curaçao", _team_range(), pagina=42),
    AlbumGroup("E", "CIV", "Costa do Marfim", _team_range(), pagina=44),
    AlbumGroup("E", "ECU", "Equador", _team_range(), pagina=46),
    # ------------------------------------------------------------------
    # Grupo F
    # ------------------------------------------------------------------
    AlbumGroup("F", "NED", "Holanda", _team_range(), pagina=48),
    AlbumGroup("F", "JPN", "Japão", _team_range(), pagina=50),
    AlbumGroup("F", "SWE", "Suécia", _team_range(), pagina=52),
    AlbumGroup("F", "TUN", "Tunísia", _team_range(), pagina=54),
    # ------------------------------------------------------------------
    # Grupo G
    # ------------------------------------------------------------------
    AlbumGroup("G", "BEL", "Bélgica", _team_range(), pagina=58),
    AlbumGroup("G", "EGY", "Egito", _team_range(), pagina=60),
    AlbumGroup("G", "IRN", "Irã", _team_range(), pagina=62),
    AlbumGroup("G", "NZL", "Nova Zelândia", _team_range(), pagina=64),
    # ------------------------------------------------------------------
    # Grupo H
    # ------------------------------------------------------------------
    AlbumGroup("H", "ESP", "Espanha", _team_range(), pagina=66),
    AlbumGroup("H", "CPV", "Cabo Verde", _team_range(), pagina=68),
    AlbumGroup("H", "KSA", "Arábia Saudita", _team_range(), pagina=70),
    AlbumGroup("H", "URU", "Uruguai", _team_range(), pagina=72),
    # ------------------------------------------------------------------
    # Grupo I
    # ------------------------------------------------------------------
    AlbumGroup("I", "FRA", "França", _team_range(), pagina=74),
    AlbumGroup("I", "SEN", "Senegal", _team_range(), pagina=76),
    AlbumGroup("I", "IRQ", "Iraque", _team_range(), pagina=78),
    AlbumGroup("I", "NOR", "Noruega", _team_range(), pagina=80),
    # ------------------------------------------------------------------
    # Grupo J
    # ------------------------------------------------------------------
    AlbumGroup("J", "ARG", "Argentina", _team_range(), pagina=82),
    AlbumGroup("J", "ALG", "Argélia", _team_range(), pagina=84),
    AlbumGroup("J", "AUT", "Áustria", _team_range(), pagina=86),
    AlbumGroup("J", "JOR", "Jordânia", _team_range(), pagina=88),
    # ------------------------------------------------------------------
    # Grupo K
    # ------------------------------------------------------------------
    AlbumGroup("K", "POR", "Portugal", _team_range(), pagina=90),
    AlbumGroup("K", "COD", "RD Congo", _team_range(), pagina=92),
    AlbumGroup("K", "UZB", "Uzbequistão", _team_range(), pagina=94),
    AlbumGroup("K", "COL", "Colômbia", _team_range(), pagina=96),
    # ------------------------------------------------------------------
    # Grupo L
    # ------------------------------------------------------------------
    AlbumGroup("L", "ENG", "Inglaterra", _team_range(), pagina=98),
    AlbumGroup("L", "CRO", "Croácia", _team_range(), pagina=100),
    AlbumGroup("L", "GHA", "Gana", _team_range(), pagina=102),
    AlbumGroup("L", "PAN", "Panamá", _team_range(), pagina=104),
    # ------------------------------------------------------------------
    # Special sections
    # ------------------------------------------------------------------
    # FWC: FIFA World Cup History — numbers 0 to 19 (20 stickers total, FWC-0 included)
    AlbumGroup(
        "FWC",
        "FWC",
        "FIFA World Cup History",
        _team_range(0, 19),
        pagina_por_numero={
            0: 0,
            1: 1, 2: 1, 3: 1, 4: 1,
            5: 2, 6: 2,
            7: 3, 8: 3,
            9: 106, 10: 106,
            11: 107, 12: 107, 13: 107,
            14: 108, 15: 108,
            16: 109, 17: 109, 18: 109, 19: 109,
        },
    ),
    # CC: Coca-Cola — numbers 1 to 14
    AlbumGroup(
        "CC",
        "CC",
        "Coca-Cola",
        _team_range(1, 14),
        pagina_por_numero={
            1: 112, 2: 112, 3: 112, 4: 112, 5: 112, 6: 112,
            7: 113, 8: 113, 9: 113, 10: 113, 11: 113, 12: 113, 13: 113, 14: 113,
        },
    ),
)

# ---------------------------------------------------------------------------
# Sanity check constant — must equal 994
# ---------------------------------------------------------------------------
TOTAL_FIGURINHAS: int = sum(len(g.numeros) for g in ALBUM_GROUPS)

# Raise immediately if the data is inconsistent so seeds / tests fail fast.
if TOTAL_FIGURINHAS != 994:
    raise AssertionError(
        f"album_data integrity check failed: expected 994 figurinhas, "
        f"got {TOTAL_FIGURINHAS}. Review the ALBUM_GROUPS constant."
    )
