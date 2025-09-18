from .models import Processo, Segmento, MemoriaContigua

def first_fit(mem: MemoriaContigua, proc: Processo) -> bool:
    livre = espacos_livres(mem)
    for inicio, tam in livre:
        if tam >= proc.tamanho:
            mem.segmentos.append(Segmento(proc.pid, inicio, proc.tamanho))
            return True
    return False

def best_fit(mem: MemoriaContigua, proc: Processo) -> bool:
    livre = espacos_livres(mem)
    melhor = min((esp for esp in livre if esp[1] >= proc.tamanho), default=None, key=lambda x: x[1])
    if melhor:
        mem.segmentos.append(Segmento(proc.pid, melhor[0], proc.tamanho))
        return True
    return False

def worst_fit(mem: MemoriaContigua, proc: Processo) -> bool:
    livre = espacos_livres(mem)
    pior = max((esp for esp in livre if esp[1] >= proc.tamanho), default=None, key=lambda x: x[1])
    if pior:
        mem.segmentos.append(Segmento(proc.pid, pior[0], proc.tamanho))
        return True
    return False

def circular_fit(mem: MemoriaContigua, proc: Processo, last_index=[0]) -> bool:
    livre = espacos_livres(mem)
    if not livre:
        return False
    n = len(livre)
    for i in range(n):
        idx = (last_index[0] + i) % n
        inicio, tam = livre[idx]
        if tam >= proc.tamanho:
            mem.segmentos.append(Segmento(proc.pid, inicio, proc.tamanho))
            last_index[0] = idx + 1
            return True
    return False

def remover_processo(mem: MemoriaContigua, pid: int):
    mem.segmentos = [s for s in mem.segmentos if s.pid != pid]

def espacos_livres(mem: MemoriaContigua):
    usados = sorted(mem.segmentos, key=lambda s: s.inicio)
    livre = []
    pos = 0
    for seg in usados:
        if seg.inicio > pos:
            livre.append((pos, seg.inicio - pos))
        pos = seg.inicio + seg.tamanho
    if pos < mem.tamanho:
        livre.append((pos, mem.tamanho - pos))
    return livre
