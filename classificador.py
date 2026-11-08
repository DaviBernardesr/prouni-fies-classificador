"""Classificador de elegibilidade ProUni/FIES por renda familiar per capita.

Fontes oficiais:
- ProUni: Lei 11.096/2005, art. 1º, §§ 1º e 2º (integral até 1,5 SM; parcial 50% até 3 SM)
- FIES: Lei 10.260/2001 (regras gerais) + Novo Fies (juros zero até 3 SM)
- FIES Social: Resolução FNDE nº 58/2024 e Portaria MEC nº 167/2024
  (até 0,5 SM per capita + CadÚnico ativo, financiamento de até 100%)

Valores de referência 2026 (salário mínimo = R$ 1.621,00):
- ProUni integral: renda per capita até 1,5 SM
- ProUni parcial (50%): renda per capita até 3 SM
- FIES regular, juros zero: renda per capita até 3 SM
- FIES Social: renda per capita até 0,5 SM + CadÚnico ativo
"""

from dataclasses import dataclass, field

SALARIO_MINIMO_2026 = 1621.00

LIMITE_PROUNI_INTEGRAL_SM = 1.5
LIMITE_PROUNI_PARCIAL_SM = 3.0
LIMITE_FIES_REGULAR_SM = 3.0
LIMITE_FIES_SOCIAL_SM = 0.5

ENEM_MEDIA_MINIMA = 450.0
ENEM_REDACAO_MINIMA = 1.0


@dataclass
class Candidato:
    renda_familiar_bruta: float
    numero_pessoas_familia: int
    media_enem: float = 0.0
    nota_redacao: float = 0.0
    cadunico_ativo: bool = False

    @property
    def renda_per_capita(self) -> float:
        return self.renda_familiar_bruta / self.numero_pessoas_familia

    @property
    def renda_per_capita_em_sm(self) -> float:
        return self.renda_per_capita / SALARIO_MINIMO_2026


@dataclass
class Resultado:
    renda_per_capita: float
    renda_per_capita_sm: float
    atende_enem: bool
    prouni_integral: bool = False
    prouni_parcial: bool = False
    fies_regular: bool = False
    fies_social: bool = False
    motivos: list = field(default_factory=list)

    def elegivel_algum_programa(self) -> bool:
        return any(
            [
                self.prouni_integral,
                self.prouni_parcial,
                self.fies_regular,
                self.fies_social,
            ]
        )


def classificar(candidato: Candidato) -> Resultado:
    renda_sm = candidato.renda_per_capita_em_sm
    atende_enem = (
        candidato.media_enem >= ENEM_MEDIA_MINIMA
        and candidato.nota_redacao > ENEM_REDACAO_MINIMA
    )

    resultado = Resultado(
        renda_per_capita=candidato.renda_per_capita,
        renda_per_capita_sm=renda_sm,
        atende_enem=atende_enem,
    )

    if not atende_enem:
        resultado.motivos.append(
            f"ENEM insuficiente (média {candidato.media_enem:.1f}, mínimo {ENEM_MEDIA_MINIMA}; "
            f"redação {candidato.nota_redacao:.1f}, mínimo acima de {ENEM_REDACAO_MINIMA})"
        )
        return resultado

    if renda_sm <= LIMITE_PROUNI_INTEGRAL_SM:
        resultado.prouni_integral = True
        resultado.motivos.append("Renda per capita dentro do limite para ProUni integral (até 1,5 SM)")
    elif renda_sm <= LIMITE_PROUNI_PARCIAL_SM:
        resultado.prouni_parcial = True
        resultado.motivos.append("Renda per capita dentro do limite para ProUni parcial 50% (até 3 SM)")
    else:
        resultado.motivos.append("Renda per capita acima do limite do ProUni (3 SM)")

    if candidato.cadunico_ativo and renda_sm <= LIMITE_FIES_SOCIAL_SM:
        resultado.fies_social = True
        resultado.motivos.append("Elegível ao FIES Social (renda até 0,5 SM + CadÚnico ativo)")

    if renda_sm <= LIMITE_FIES_REGULAR_SM:
        resultado.fies_regular = True
        resultado.motivos.append("Elegível ao FIES com juros zero (renda per capita até 3 SM, Novo Fies)")
    else:
        resultado.motivos.append("Renda per capita acima do limite do FIES (3 SM)")

    return resultado


def imprimir_resultado(resultado: Resultado) -> None:
    print(f"Renda per capita: R$ {resultado.renda_per_capita:.2f} ({resultado.renda_per_capita_sm:.2f} salários mínimos)")
    print(f"Atende critério ENEM: {'sim' if resultado.atende_enem else 'não'}")
    print(f"ProUni integral (100%): {'sim' if resultado.prouni_integral else 'não'}")
    print(f"ProUni parcial (50%): {'sim' if resultado.prouni_parcial else 'não'}")
    print(f"FIES regular: {'sim' if resultado.fies_regular else 'não'}")
    print(f"FIES Social: {'sim' if resultado.fies_social else 'não'}")
    print()
    for motivo in resultado.motivos:
        print(f"- {motivo}")
    print()
    print("Resultado final:", "ELEGÍVEL" if resultado.elegivel_algum_programa() else "NÃO ELEGÍVEL")


if __name__ == "__main__":
    candidato = Candidato(
        renda_familiar_bruta=4000.00,
        numero_pessoas_familia=4,
        media_enem=520.0,
        nota_redacao=600.0,
        cadunico_ativo=False,
    )
    resultado = classificar(candidato)
    imprimir_resultado(resultado)
