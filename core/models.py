from dataclasses import dataclass, field
from typing import List

@dataclass
class Processo:
    pid: int
    tamanho: int

@dataclass
class Segmento:
    pid: int
    inicio: int
    tamanho: int

@dataclass
class MemoriaContigua:
    tamanho: int
    segmentos: List[Segmento] = field(default_factory=list)

@dataclass
class Pagina:
    numero: int
    frame: int

@dataclass
class TabelaPaginas:
    pid: int
    paginas: List[Pagina] = field(default_factory=list)
