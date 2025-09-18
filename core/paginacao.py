from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .models import Processo

@dataclass
class Frame:
    idx: int
    pid: Optional[int] = None
    pagina: Optional[int] = None  # número da página lógica

@dataclass
class MemoriaPaginada:
    tamanho_pagina: int         # em KB (ou outra unidade consistente)
    total_frames: int
    frames: List[Frame] = field(default_factory=list)
    tabelas: Dict[int, Dict[int, int]] = field(default_factory=dict)  # pid -> (pag -> frame_idx)
    tamanhos_proc: Dict[int, int] = field(default_factory=dict)       # pid -> tamanho (KB)

    def __post_init__(self):
        if not self.frames:
            self.frames = [Frame(i) for i in range(self.total_frames)]

    def _frames_livres(self) -> List[Frame]:
        return [f for f in self.frames if f.pid is None]

    def _num_paginas(self, tamanho_proc_kb: int) -> int:
        tp = max(1, self.tamanho_pagina)
        return (tamanho_proc_kb + tp - 1) // tp

    def alocar(self, proc: Processo) -> bool:
        paginas = self._num_paginas(proc.tamanho)
        livres = self._frames_livres()
        if len(livres) < paginas:
            return False
        # alocar páginas nas primeiras 'paginas' livres
        self.tabelas.setdefault(proc.pid, {})
        for p, frame in zip(range(paginas), livres[:paginas]):
            frame.pid = proc.pid
            frame.pagina = p
            self.tabelas[proc.pid][p] = frame.idx
        self.tamanhos_proc[proc.pid] = proc.tamanho
        return True

    def remover(self, pid: int) -> None:
        for fr in self.frames:
            if fr.pid == pid:
                fr.pid = None
                fr.pagina = None
        self.tabelas.pop(pid, None)
        self.tamanhos_proc.pop(pid, None)

    def paginas_alocadas_total(self) -> int:
        return sum(len(tbl) for tbl in self.tabelas.values())

    def frames_ocupados(self) -> int:
        return sum(1 for f in self.frames if f.pid is not None)
