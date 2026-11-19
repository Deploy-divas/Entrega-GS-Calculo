# AUdi — modelagem da autonomia energética

**Global Solution 2026.2 · CitizenTech · Differentiated Problem Solving**

O AUdi é um chaveiro assistivo que identifica objetos por NFC e reproduz descrições em áudio. Este projeto usa limites, derivadas, taxas de variação e integrais para estudar como a frequência de uso influencia o consumo de energia e o tempo até a reserva da bateria.

## Integrantes

| Integrante | RM |
|---|---:|
| Amanda Silva da Mata | 572585 |
| Beatriz Mantovani da Cruz | 573824 |
| Laura Sampaio Neves | 570802 |

## Arquivos da entrega

| Arquivo | Conteúdo |
|---|---|
| `relatorio-tecnico-AUdi.pdf` | Relatório técnico com o problema, as premissas, o desenvolvimento matemático, os gráficos, a análise dos resultados e a conclusão. |
| `modelo_bateria.py` | Cálculo dos cenários e geração dos gráficos e dados. |
| `verificar_modelo.py` | Verificações matemáticas e numéricas do modelo. |
| `requirements.txt` | Dependência necessária para gerar os gráficos. |
| `resultados/` | Quatro gráficos PNG, resultados em JSON e série temporal em CSV. |

## Como executar

Com Python 3.10 ou superior, execute os comandos na pasta do projeto:

```bash
python -m pip install -r requirements.txt
python modelo_bateria.py
python verificar_modelo.py
```

Em sistemas nos quais o comando é `python3`, substitua `python` por `python3`. O programa grava os arquivos gerados em `resultados/`. A verificação apresenta **51 condições aprovadas** quando executada normalmente, sem a opção `-O` do Python.

## Modelo matemático

A energia inicial útil adotada é **1,48 Wh**, calculada a partir de uma energia nominal de 1,85 Wh e de um fator de disponibilidade de 80%. A reserva corresponde a **10% da energia útil inicial**, ou **0,148 Wh**. O consumo em espera é representado por 0,06 W. Cada identificação com áudio dura 12 segundos e utiliza potência média de 0,60 W durante o evento.

Se `t` é o tempo ligado em horas, a frequência média de eventos é `f(t) = a + bt`. O gasto adicional por evento é `k = (0,60 − 0,06) × 12/3600 = 0,0018 Wh`. Assim:

- **Potência média:** `P(t) = 0,06 + k(a + bt)`.
- **Energia consumida:** `C(t) = (0,06 + ka)t + (kb/2)t²`, obtida pela integral de `P(t)`.
- **Energia restante:** `E(t) = 1,48 − C(t)`.
- **Taxa instantânea de descarga:** `E′(t) = −P(t)`.
- **Tempo até a reserva:** `T` é a solução de `E(T) = 0,148 Wh`.

O relatório desenvolve essas relações, apresenta o limite da energia ao se aproximar da reserva e compara a taxa média com a taxa instantânea de descarga.

## Resultados

| Cenário | Frequência média `f(t)` (eventos/h) | Consumo em 8 h | Tempo até a reserva |
|---|---|---:|---:|
| Leve | `2 + 0,2t` | 0,52032 Wh | 19,83 h |
| Moderado | `6 + t` | 0,62400 Wh | 15,69 h |
| Intenso | `10 + 3t` | 0,79680 Wh | 12,05 h |

Os três cenários mostram como o aumento da frequência de identificação antecipa a chegada à reserva. Os gráficos apresentam a energia restante, a taxa de descarga, o consumo acumulado e a integral da potência no cenário moderado. As curvas terminam no instante de reserva de cada cenário.

Os parâmetros energéticos e os padrões de uso são **premissas de simulação**. Os resultados permitem comparar os cenários e orientar o planejamento de um aviso de recarga; a autonomia do dispositivo físico deverá ser confirmada por medições do protótipo.

## Referência

FIAP. *Desafio CitizenTech — Global Solution 2026.2*, Engenharia de Software, seção de Differentiated Problem Solving.
