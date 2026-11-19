"""Verificações matemáticas do modelo, sem dependências externas."""
from modelo_bateria import (
    CENARIOS, ENERGIA_INICIAL_WH, FRACAO_RESERVA, HORIZONTE_H,
    DURACAO_EVENTO_S, POTENCIA_ESPERA_W, frequencia, consumo,
    energia, derivada, tempo_reserva, integrar_ponto_medio,
)


def verificar() -> None:
    contagem = 0
    tempos = []
    for c in CENARIOS:
        a, b = c['a'], c['b']
        t = tempo_reserva(a,b)
        tempos.append(t)
        assert 0 < t <= HORIZONTE_H
        assert abs(energia(0,a,b)-ENERGIA_INICIAL_WH) < 1e-12
        assert consumo(0,a,b) == 0
        assert abs(energia(t,a,b)-ENERGIA_INICIAL_WH*FRACAO_RESERVA) < 1e-10
        assert frequencia(HORIZONTE_H,a,b)*DURACAO_EVENTO_S/3600 <= 1
        assert abs(consumo(8,a,b)-integrar_ponto_medio(8,a,b)) < 1e-10
        contagem += 6
        for x in (1,4,8):
            h=0.00001
            aproximacao=(energia(x+h,a,b)-energia(x-h,a,b))/(2*h)
            assert abs(aproximacao-derivada(x,a,b)) < 1e-8
            assert abs(energia(x,a,b)+consumo(x,a,b)-ENERGIA_INICIAL_WH) < 1e-12
            assert energia(x+h,a,b) < energia(x,a,b)
            contagem += 3
    assert tempos[0] > tempos[1] > tempos[2]
    assert abs(tempo_reserva(0,0)-ENERGIA_INICIAL_WH*(1-FRACAO_RESERVA)/POTENCIA_ESPERA_W) < 1e-12
    assert tempo_reserva(7,1) < tempo_reserva(6,1)
    contagem += 3
    for a,b in ((-1,1),(1,-1),(400,0)):
        rejeitou=False
        try:
            tempo_reserva(a,b)
        except ValueError:
            rejeitou=True
        assert rejeitou
        contagem+=1
    print(f'{contagem} verificações aprovadas.')


if __name__=='__main__':
    verificar()
