import ast
import json

# ============================================================ 1) SSOT: face a face + a matriz como desenhada
P = "04_Dados_SSOT_e_Scripts/cabecote_ex030.json"
d = json.load(open(P, encoding="utf-8"))
d["encosto_na_extrusora"] = {
    "decisao_do_usuario": "encosta face a face (2026-09-12) - a face do flange do cabeçote encosta na face "
                          "da extrusora; o piloto Ø105 × 3,00 é centragem",
    "o_que_Isso_muda_na_matriz": "nada na posição da matriz. A posição axial da matriz é definida pela "
                                 "escada interna do cabeçote (fundo do bolso + degrau), medida com "
                                 "interferência 0,0000 mm³ no assento; o que a decisão fixa é onde o "
                                 "CONJUNTO cabeçote+matriz para em relação à máquina.",
    "exigencia_na_maquina": "se a junta fecha na face do flange (d = 92,00), a face da extrusora precisa de "
                            "um rebaixo que receba o piloto de 3,00 mm (Ø > 105,00); sem ele a junta fica "
                            "aberta 3,00 mm, e é o rebaixo que define se a traseira da matriz (d = 95,00) "
                            "entra ou não na máquina",
    "correcao_de_afirmacao_anterior": "eu escrevi que, com encosto face a face, a protrusão da matriz cairia "
                                      "de 14,00 para 11,00 mm e o NC dos cartuchos viraria +0,250 mm. Isso "
                                      "estava errado: só seria assim se a referência axial da matriz fosse a "
                                      "face do flange, e a medição mostra que ela é o degrau/fundo do bolso "
                                      "do próprio cabeçote. A protrusão continua 14,00 mm e o NC "
                                      "(-2,750 mm, sai com Z >= 99,75) continua de pé.",
}
d["matriz_copo_desenhada_no_dxf"] = {
    "o_que_e": "a seção do cabeçote no DXF já contém a Matriz 1 Copo montada, com cotas de PROJETO - não "
               "as medidas do STEP. Foi o que o usuário apontou, e a geometria confirma.",
    "medido_no_dxf": {
        "banda_da_matriz": "H r = 47,48/47,52 sobre d = 25,00..95,00 existe em DUAS camadas: `contorno` (o "
                           "bolso do cabeçote) e `SL35` (geometria de seção) - linha a linha com o bolso, "
                           "Ø95,00 desenhado, não Ø93,00",
        "segundo_estagio": "H r = 45,00 em d = 14,00..25,00 (11,00 = o furo do cabeçote) E outra em "
                           "d = 14,00..31,00 (17,00) - o estágio desenhado para dentro da matriz é 6,00 mm "
                           "mais comprido que o furo que o recebe",
        "unica_aresta_vertical_na_faixa": "V d = 25,00 de r = 44,98 a 47,48 (a quina do degrau do cabeçote); "
                                          "não há outra aresta vertical entre r 36 e 54 no trecho",
        "face_de_entrada": "V d = 95,00 em SL35, de r = 0,02 a 47,48 - a face de entrada da matriz desenhada "
                           "no plano mais traseiro do cabeçote (o 'face a face')",
    },
    "consequencia": "os 11,00 mm que eu lia como comprimento do degrau do cabeçote são também o canal da "
                    "fenda, que é peça separada do copo - o corte do DXF mostra os dois estágios lado a "
                    "lado nessa faixa. No STEP medido: banda 69,909 e estágio 10,80 (total 80,70), ou seja, "
                    "o corpo medido é 0,091 + 0,20 mm mais curto que o desenhado (70 + 11 = 81,00).",
    "limitacao_deste_arquivo": "o DXF extraído do DWG tem SÓ geometria: 0 entidades DIMENSION e 0 textos, "
                                "então os NÚMEROS escritos no desenho não são legíveis aqui. O que o arquivo "
                                "permite é medir as linhas acima. O DWG é AutoCAD 2016 com seções "
                                "comprimidas e o leitor .NET não roda neste ambiente (pede OpenSSL 1.1).",
}
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("1) SSOT do cabeçote: encosto face a face + a matriz desenhada no DXF, com a correcao registrada")

# ================================================= 2) verificador: um item [G] para o encosto escolhido
P = "04_Dados_SSOT_e_Scripts/verificar_interface_cabecote.py"
s = open(P, encoding="utf-8").read()
ant = '    pend = [l for l in linhas if l["status"] == "PENDENTE_CONFIRMACAO"]'
nvo = '''    print("\\n[G] encosto do conjunto na extrusora (decisão 'encosta face a face')\\n" + "-" * 70)
    # O que e medido no solido: o piloto protrai atras da face do flange exatamente a altura que a decisao
    # exige que a máquina rebaixe. O que fica pendente: se a face da extrusora TEM esse rebaixo.
    # O que e medido no solido: onde a casca externa cai de 0220 para 0105 - a face real do flange - e o
    # quanto o piloto protrai atras dela. (Nao uso CORPO[][1] direto: os aneis tem sobreposicao de 1 mm
    # para o booleano ser robusto, e a face DESNHADA esta em Z = 3,00, nao em 2,00.)
    face_flange = None
    for zt in [round(0.05 * i, 3) for i in range(0, 121)]:
        fat = head.intersect(cil_z(500.0, zt - 0.0025, zt + 0.0025))
        if not fat.Solids():
            continue
        rr = max(maior(fat).BoundingBox().xlen, maior(fat).BoundingBox().ylen) / 2.0
        if rr > 100.0:
            face_flange = zt
            break
    protr_piloto = round(face_flange - CORPO[2][1], 3) if face_flange is not None else float("nan")
    print(f"   face do flange no sólido: Z = {n2(face_flange)} | piloto de Z = {n2(CORPO[2][1])} a "
          f"{n2(CORPO[2][2])} | protrusão do piloto: {n2(protr_piloto)} mm")
    checar("Piloto protrai atrás da face do flange (o rebaixo que a máquina precisa ter)",
           protr_piloto, dados["corpo"]["piloto_traseiro"]["altura_mm"], un="mm",
           obs="face do flange e fim do piloto medidos no sólido por varredura de seções de 0,05 mm")
    alerta("Rebaixo na face da extrusora para receber o piloto (decisão 'face a face')",
           round(protr_piloto, 3),
           "com a junta fechando na face do flange (d = 92,00), a face da máquina precisa de %s mm de "
           "rebaixo em Ø > %s; sem ele a junta fica aberta %s mm. A posição axial da matriz NÃO muda "
           % (n2(protr_piloto), n2(2 * CORPO[2][0]), n2(protr_piloto)) +
           "com isso: ela vem do degrau/fundo do bolso do cabeçote (interferência 0,0000 mm³ no assento), "
           "então a protrusão continua 14,00 mm e o NC dos cartuchos também.")
    print()

    pend = [l for l in linhas if l["status"] == "PENDENTE_CONFIRMACAO"]'''
assert s.count(ant) == 1, "ancora do resumo"
s = s.replace(ant, nvo)
open(P, "w", encoding="utf-8").write(s)
ast.parse(s)
print("2) verificador de interface: bloco [G] com 1 conformidade medida e 1 pendencia de máquina")

# ============================ 3) portao: o desenho 2D entra na cadeia de estudos (3,7 s, deterministicos)
P = "04_Dados_SSOT_e_Scripts/verificar_cadeia.py"
s = open(P, encoding="utf-8").read()
ant = '                  "medir_perfis_matrizes_x_cabecote.py --json --md"]'
nvo = ('                  "medir_perfis_matrizes_x_cabecote.py --json --md",\n'
       '                  "gerar_desenho_2d_cabecote_matriz.py"]  # o PDF 2D: 3,7 s, so le os STEP')
assert s.count(ant) == 1, "CADEIA_ESTUDOS"
s = s.replace(ant, nvo)
open(P, "w", encoding="utf-8").write(s)
ast.parse(s)
print("3) portao passa a regerar o desenho 2D no --com-estudos")
