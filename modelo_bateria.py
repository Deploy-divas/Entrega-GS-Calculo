"""Modelo didático de autonomia do chaveiro AUdi.

Todos os parâmetros são hipotéticos, não medições. Python 3.10+.
Execute: python modelo_bateria.py. Instale matplotlib para os gráficos.
"""
import json
import math
from pathlib import Path

# Energia nominal hipotética e fator de disponibilidade adotado pelo modelo.
ENERGIA_NOMINAL_WH = 1.85
FATOR_DISPONIVEL = 0.80
ENERGIA_INICIAL_WH = ENERGIA_NOMINAL_WH * FATOR_DISPONIVEL
FRACAO_RESERVA = 0.10
POTENCIA_ESPERA_W = 0.06
POTENCIA_ATIVA_W = 0.60
DURACAO_EVENTO_S = 12.0
HORIZONTE_H = 24.0
CENARIOS = (
    {'nome': 'Leve', 'a': 2.0, 'b': 0.2, 'cor': '#24776B'},
    {'nome': 'Moderado', 'a': 6.0, 'b': 1.0, 'cor': '#B07812'},
    {'nome': 'Intenso', 'a': 10.0, 'b': 3.0, 'cor': '#A73E52'},
)


def energia_por_evento() -> float:
    """Retorna a energia incremental (Wh/evento), descontando a espera."""
    return (POTENCIA_ATIVA_W - POTENCIA_ESPERA_W) * DURACAO_EVENTO_S / 3600


def frequencia(t: float, a: float, b: float) -> float:
    """Frequência média suavizada de eventos por hora; t em horas."""
    return a + b * t


def potencia(t: float, a: float, b: float) -> float:
    """P(t), potência média em W, para aparelho ainda em operação."""
    return POTENCIA_ESPERA_W + energia_por_evento() * frequencia(t, a, b)


def consumo(t: float, a: float, b: float) -> float:
    """Integral analítica de P(u) de 0 a t: energia acumulada em Wh."""
    k = energia_por_evento()
    return (POTENCIA_ESPERA_W + k * a) * t + k * b * t ** 2 / 2


def energia(t: float, a: float, b: float) -> float:
    """E(t) sem truncamento; usar somente até o instante de reserva."""
    return ENERGIA_INICIAL_WH - consumo(t, a, b)


def derivada(t: float, a: float, b: float) -> float:
    """E'(t) = -P(t), em Wh/h (equivalente a W)."""
    return -potencia(t, a, b)


def tempo_reserva(a: float, b: float) -> float:
    """Resolve C(T) = E0*(1-r) para a primeira raiz não negativa.

    Usa forma estável da raiz da equação A*T²+B*T-D=0.
    A função rejeita taxas negativas e ocupação impossível no horizonte.
    """
    if a < 0 or b < 0:
        raise ValueError('Este estudo considera a e b não negativos.')
    if frequencia(HORIZONTE_H, a, b) * DURACAO_EVENTO_S / 3600 > 1:
        raise ValueError('Eventos excedem 100% do tempo no horizonte.')
    coef_a = energia_por_evento() * b / 2
    coef_b = POTENCIA_ESPERA_W + energia_por_evento() * a
    disponivel = ENERGIA_INICIAL_WH * (1 - FRACAO_RESERVA)
    if coef_a == 0:
        return disponivel / coef_b
    return 2 * disponivel / (coef_b + math.sqrt(coef_b ** 2 + 4 * coef_a * disponivel))


def integrar_ponto_medio(t: float, a: float, b: float, n: int = 1000) -> float:
    """Verifica a integral por uma soma de áreas de retângulos médios."""
    passo = t / n
    acumulado = 0.0
    for i in range(n):
        acumulado += potencia((i + 0.5) * passo, a, b) * passo
    return acumulado


def calcular_resultados() -> dict:
    """Calcula cenários, limites laterais e sensibilidade de uma hora de uso."""
    saida = {'premissas': {
        'origem': 'Todos os números são hipotéticos; não houve ensaio físico.',
        'energia_nominal_Wh': ENERGIA_NOMINAL_WH,
        'fator_disponivel': FATOR_DISPONIVEL,
        'energia_inicial_Wh': ENERGIA_INICIAL_WH,
        'reserva_Wh': ENERGIA_INICIAL_WH * FRACAO_RESERVA,
        'potencia_espera_W': POTENCIA_ESPERA_W,
        'potencia_ativa_W': POTENCIA_ATIVA_W,
        'duracao_evento_s': DURACAO_EVENTO_S,
        'k_Wh_por_evento': energia_por_evento(),
        'horizonte_h': HORIZONTE_H,
    }, 'cenarios': []}
    for c in CENARIOS:
        a, b = c['a'], c['b']
        t = tempo_reserva(a, b)
        if t > HORIZONTE_H:
            raise ValueError('Raiz fora do domínio de simulação adotado.')
        limites = []
        for epsilon in (1.0, 0.1, 0.01, 0.001):
            limites.append({'epsilon_h': epsilon,
                            'energia_Wh': energia(t - epsilon, a, b)})
        saida['cenarios'].append({
            'nome': c['nome'], 'a': a, 'b': b,
            'tempo_reserva_h': t,
            'derivada_8h_Wh_por_h': derivada(8, a, b),
            'consumo_8h_Wh': consumo(8, a, b),
            'energia_8h_Wh': energia(8, a, b),
            'taxa_media_0a8_Wh_por_h': (energia(8, a, b) - energia(0, a, b)) / 8,
            'erro_integral_Wh': abs(consumo(8, a, b) - integrar_ponto_medio(8, a, b)),
            'ocupacao_final_horizonte': (
                frequencia(HORIZONTE_H, a, b) * DURACAO_EVENTO_S / 3600
            ),
            'limite_esquerda': limites,
        })
    # Sensibilidade no cenário moderado: +1 evento/h na frequência inicial.
    a, b = 6.0, 1.0
    t = tempo_reserva(a, b)
    dt_da = -energia_por_evento() * t / potencia(t, a, b)
    saida['sensibilidade'] = {
        'dT_da_h_por_evento_por_h': dt_da,
        'T_a6_h': t, 'T_a7_h': tempo_reserva(7, b),
        'efeito_exato_h': tempo_reserva(7, b) - t,
    }
    return saida


def gerar_graficos(pasta: Path) -> None:
    """Gera PNGs com matplotlib; gráficos param no instante de reserva."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False})
    specs = (
        ('energia', 'Energia restante', 'Energia (Wh)', energia),
        ('taxa', 'Velocidade de descarga', "E’(t) (Wh/h)", derivada),
        ('consumo', 'Energia consumida acumulada', 'Consumo (Wh)', consumo),
    )
    for arquivo, titulo, eixo, funcao in specs:
        fig, ax = plt.subplots(figsize=(9, 4.5), layout='constrained')
        for c in CENARIOS:
            t_final = tempo_reserva(c['a'], c['b'])
            ts = [t_final * i / 250 for i in range(251)]
            ys = [funcao(t, c['a'], c['b']) for t in ts]
            ax.plot(ts, ys, color=c['cor'], linewidth=2.4, label=c['nome'])
            ax.plot([ts[-1]], [ys[-1]], 'o', color=c['cor'])
        if arquivo == 'energia':
            reserva_wh = ENERGIA_INICIAL_WH * FRACAO_RESERVA
            ax.axhline(reserva_wh, color='#555555', linestyle='--',
                       label=f'Reserva: {reserva_wh:.3f} Wh'.replace('.', ','))
        ax.set(title=titulo, xlabel='Tempo ligado (h)', ylabel=eixo)
        ax.grid(alpha=0.2)
        ax.legend(loc='best')
        fig.savefig(pasta / f'{arquivo}.png', dpi=200)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 4.5), layout='constrained')
    ts = [i * 8 / 200 for i in range(201)]
    ys = [potencia(t, 6, 1) for t in ts]
    ax.plot(ts, ys, color='#24776B', linewidth=2.4)
    ax.fill_between(ts, ys, color='#24776B', alpha=0.2)
    ax.set(title='Integral: área sob a potência média (cenário moderado)',
           xlabel='Tempo ligado (h)', ylabel='Potência média (W)', ylim=(0, 0.10))
    ax.text(0.6, 0.025, f'Área de 0 a 8 h = {consumo(8, 6, 1):.4f} Wh')
    ax.grid(alpha=0.2)
    fig.savefig(pasta / 'integral.png', dpi=200)
    plt.close(fig)


def executar() -> None:
    """Salva resultados, série temporal e gráficos ao lado do programa."""
    pasta = Path(__file__).resolve().parent/'resultados'
    pasta.mkdir(exist_ok=True)
    dados = calcular_resultados()
    with (pasta/'resultados.json').open('w',encoding='utf-8') as f:
        json.dump(dados,f,indent=4,ensure_ascii=False)
    with (pasta/'serie_temporal.csv').open('w',encoding='utf-8') as f:
        f.write('cenario;tempo_h;energia_Wh;consumo_Wh;potencia_W\n')
        for c in CENARIOS:
            t_final=tempo_reserva(c['a'],c['b'])
            for i in range(101):
                t=t_final*i/100
                f.write(f"{c['nome']};{t:.8f};{energia(t,c['a'],c['b']):.8f};"
                        f"{consumo(t,c['a'],c['b']):.8f};{potencia(t,c['a'],c['b']):.8f}\n")
    for c in dados['cenarios']:
        print(f"{c['nome']}: reserva após {c['tempo_reserva_h']:.2f} h; "
              f"consumo em 8 h = {c['consumo_8h_Wh']:.4f} Wh")
    try:
        gerar_graficos(pasta)
    except ImportError:
        print('Resultados numéricos salvos. Instale matplotlib para gerar gráficos.')
    else:
        print('Gráficos e resultados salvos em:',pasta)


if __name__ == '__main__':
    executar()
