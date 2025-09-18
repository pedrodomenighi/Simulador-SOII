# core/metrics.py
from .models import MemoriaContigua

def uso_memoria_contigua(mem: MemoriaContigua) -> float:
    usado = sum(s.tamanho for s in mem.segmentos)
    return 0.0 if mem.tamanho == 0 else 100.0 * usado / mem.tamanho

def fragmentacao_externa(mem: MemoriaContigua) -> float:
    # 1 - (maior_buraco / livre_total)
    livre_total = 0
    maior = 0
    # holes = (inicio, tam) – reaproveita cálculo rápido aqui p/ não criar dependência circular
    usados = sorted(mem.segmentos, key=lambda s: s.inicio)
    pos = 0
    for seg in usados:
        if seg.inicio > pos:
            tam = seg.inicio - pos
            livre_total += tam
            maior = max(maior, tam)
        pos = seg.inicio + seg.tamanho
    if pos < mem.tamanho:
        tam = mem.tamanho - pos
        livre_total += tam
        maior = max(maior, tam)
    if livre_total == 0:
        return 0.0
    return max(0.0, (1.0 - maior / livre_total) * 100.0)

def fragmentacao_interna(total_bytes_alocados: int, tamanho_pagina: int) -> int:
    """
    Retorna a soma das sobras dentro das páginas alocadas (em bytes).
    Ex.: se última página usa só 2 KiB de uma página de 4 KiB, sobra = 2 KiB.
    """
    if tamanho_pagina <= 0 or total_bytes_alocados <= 0:
        return 0
    paginas = (total_bytes_alocados + tamanho_pagina - 1) // tamanho_pagina
    usado_ultima = total_bytes_alocados % tamanho_pagina
    if usado_ultima == 0:
        usado_ultima = tamanho_pagina
    sobra_ultima = tamanho_pagina - usado_ultima
    # páginas cheias não têm sobra interna
    return 0 if paginas == 0 else sobra_ultima

def uso_memoria_paginacao(frames_ocupados: int, total_frames: int) -> float:
    return 0.0 if total_frames == 0 else 100.0 * frames_ocupados / total_frames

def overhead_tabela_paginas(num_paginas_alocadas: int, bytes_por_entrada: int = 8) -> int:
    return num_paginas_alocadas * bytes_por_entrada
