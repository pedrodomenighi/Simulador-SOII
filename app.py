import streamlit as st
from core.models import Processo, MemoriaContigua
from core import contigua
from core.paginacao import MemoriaPaginada
from core.metrics import (
    uso_memoria_contigua, fragmentacao_externa,
    fragmentacao_interna, uso_memoria_paginacao, overhead_tabela_paginas
)
from ui.charts import memory_bar_html, frames_grid_html

st.set_page_config(page_title="Simulador de Memória", layout="wide")
st.title("Simulador de Gerenciamento de Memória")

# ---------- util de cenários ----------
def reset_contigua(tam):
    st.session_state.memoria_c = MemoriaContigua(tamanho=tam)
    st.session_state.step_c = 0
    st.session_state.log_c = []

def reset_paginacao(tp, frames):
    st.session_state.memoria_p = MemoriaPaginada(tamanho_pagina=tp, total_frames=frames)
    st.session_state.step_p = 0
    st.session_state.log_p = []

# ---------- Sidebar comum ----------
modo = st.sidebar.radio("Modo", ["Alocação Contígua", "Paginação"])


#   CONTÍGUA

if modo == "Alocação Contígua":
    # estado
    if "memoria_c" not in st.session_state:
        reset_contigua(128)

    tamanho_mem = st.sidebar.number_input("Tamanho da Memória (KB)", 32, 8192, st.session_state.memoria_c.tamanho)
    if st.sidebar.button("Aplicar tamanho"):
        reset_contigua(tamanho_mem)

    # criação/remoção manual
    st.sidebar.markdown("### Operações manuais")
    pid = st.sidebar.number_input("PID", 1, 999999, 1)
    tam_proc = st.sidebar.number_input("Tamanho Proc (KB)", 1, tamanho_mem, 16)
    algoritmo = st.sidebar.selectbox("Algoritmo", ["First-Fit", "Best-Fit", "Worst-Fit", "Circular-Fit"])

    c1, c2 = st.sidebar.columns(2)
    if c1.button("Alocar"):
        proc = Processo(pid, tam_proc)
        ok = False
        if algoritmo == "First-Fit": ok = contigua.first_fit(st.session_state.memoria_c, proc)
        elif algoritmo == "Best-Fit": ok = contigua.best_fit(st.session_state.memoria_c, proc)
        elif algoritmo == "Worst-Fit": ok = contigua.worst_fit(st.session_state.memoria_c, proc)
        elif algoritmo == "Circular-Fit": ok = contigua.circular_fit(st.session_state.memoria_c, proc)
        (st.sidebar.success if ok else st.sidebar.error)("Alocado!" if ok else "Sem espaço contíguo.")
        st.session_state.log_c.append(f"alloc P{pid} ({tam_proc}KB) via {algoritmo}: {'ok' if ok else 'falha'}")
    if c2.button("Remover"):
        contigua.remover_processo(st.session_state.memoria_c, pid)
        st.session_state.log_c.append(f"free P{pid}")


    # layout principal
    left, right = st.columns([2,1])

    with left:
        st.subheader("Memória (contígua)")
        st.markdown(memory_bar_html(st.session_state.memoria_c.tamanho, st.session_state.memoria_c.segmentos),
                    unsafe_allow_html=True)
        st.caption("Cada célula ≈ bloco proporcional do total")

        st.subheader("Tabela de segmentos")
        st.write([{"PID": s.pid, "Base": s.inicio, "Tamanho": s.tamanho} for s in st.session_state.memoria_c.segmentos])

    with right:
        st.subheader("Métricas")
        holes = contigua.espacos_livres(st.session_state.memoria_c)
        maior_buraco = max((t for _, t in holes), default=0)
        colA, colB, colC = st.columns(3)
        colA.metric("Uso (%)", f"{uso_memoria_contigua(st.session_state.memoria_c):.1f}")
        colB.metric("Frag. externa (%)", f"{fragmentacao_externa(st.session_state.memoria_c):.1f}")
        colC.metric("Maior buraco (KB)", f"{maior_buraco}")

        st.subheader("Log")
        st.code("\n".join(st.session_state.log_c[-12:]) or "(vazio)")


#   PAGINAÇÃO

else:
    if "memoria_p" not in st.session_state:
        reset_paginacao(4, 24)

    # parâmetros
    tamanho_pagina = st.sidebar.number_input("Tamanho da Página (KB)", 1, 1024, st.session_state.memoria_p.tamanho_pagina)
    total_frames   = st.sidebar.number_input("Número de Frames", 1, 4096, st.session_state.memoria_p.total_frames)
    if st.sidebar.button("Aplicar parâmetros"):
        reset_paginacao(tamanho_pagina, total_frames)

    # operações manuais
    st.sidebar.markdown("### Operações manuais")
    pid = st.sidebar.number_input("PID", 1, 999999, 1, key="pid_p")
    tam_proc = st.sidebar.number_input("Tamanho do Processo (KB)", 1, 1024 * 1024, 10, key="tam_p")

    c1, c2 = st.sidebar.columns(2)
    if c1.button("Alocar", key="alloc_p"):
        ok = st.session_state.memoria_p.alocar(Processo(pid, tam_proc))
        (st.sidebar.success if ok else st.sidebar.error)("Alocado!" if ok else "Frames insuficientes.")
        st.session_state.log_p.append(f"alloc P{pid} ({tam_proc}KB): {'ok' if ok else 'falha'}")
    if c2.button("Remover", key="rem_p"):
        st.session_state.memoria_p.remover(pid)
        st.session_state.log_p.append(f"free P{pid}")

    # layout principal
    left, right = st.columns([2,1])
    with left:
        st.subheader("Frames")
        # grid com 8 colunas por padrão; ajuste se quiser
        st.markdown(frames_grid_html(st.session_state.memoria_p.frames, cols=8), unsafe_allow_html=True)

        st.subheader("Tabela de páginas (selecionar PID)")
        pids = sorted(st.session_state.memoria_p.tabelas.keys())
        if pids:
            pid_sel = st.selectbox("PID", pids)
            tabela = st.session_state.memoria_p.tabelas.get(pid_sel, {})
            st.write([{"Página": p, "Frame": tabela[p]} for p in sorted(tabela.keys())])
        else:
            st.info("Nenhum processo alocado.")

    with right:
        st.subheader("Métricas")
        frames_ocup = st.session_state.memoria_p.frames_ocupados()
        uso = uso_memoria_paginacao(frames_ocup, st.session_state.memoria_p.total_frames)

        # fragmentação interna: soma das sobras por processo (apenas última página de cada proc)
        sobra_total_bytes = 0
        for pid_, tam_kb in st.session_state.memoria_p.tamanhos_proc.items():
            sobra_total_bytes += fragmentacao_interna(
                tam_kb * 1024, st.session_state.memoria_p.tamanho_pagina * 1024
            )
        overhead = overhead_tabela_paginas(st.session_state.memoria_p.paginas_alocadas_total())

        col1, col2, col3 = st.columns(3)
        col1.metric("Uso de memória (%)", f"{uso:.1f}")
        col2.metric("Frag. interna (KB)", f"{sobra_total_bytes // 1024}")
        col3.metric("Overhead Tabela (bytes)", f"{overhead}")

        st.subheader("Log")
        st.code("\n".join(st.session_state.log_p[-12:]) or "(vazio)")
