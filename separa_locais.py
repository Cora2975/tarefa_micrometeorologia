"""Separa os registros de um CSV em um arquivo para cada local.

Uso:
    python3 separa_locais.py

Opcionalmente, informe o CSV de entrada e a pasta de saída:
    python3 separa_locais.py dados.csv minha_pasta_de_saida
"""

import argparse
import csv
import re
from pathlib import Path


ARQUIVO_PADRAO = Path("ERA5Land_Micrometeorologia_Alunos.csv")
PASTA_SAIDA_PADRAO = Path("csv_por_local")
COLUNAS_LOCAL = ("region_id", "region_name")


def nome_seguro(texto: str) -> str:
    """Converte um texto em um nome de arquivo portável."""
    texto = texto.strip()
    texto = re.sub(r"[^\w.-]+", "_", texto, flags=re.UNICODE)
    return texto.strip("_.") or "local_sem_nome"


def separar_por_local(arquivo_entrada: Path, pasta_saida: Path) -> int:
    """Cria um CSV por combinação de ``region_id`` e ``region_name``."""
    if not arquivo_entrada.is_file():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {arquivo_entrada}")

    pasta_saida.mkdir(parents=True, exist_ok=True)
    arquivos_abertos = {}
    quantidade_por_local = {}

    try:
        with arquivo_entrada.open("r", encoding="utf-8-sig", newline="") as entrada:
            leitor = csv.DictReader(entrada)

            if not leitor.fieldnames:
                raise ValueError("O CSV de entrada não possui cabeçalho.")

            ausentes = set(COLUNAS_LOCAL) - set(leitor.fieldnames)
            if ausentes:
                raise ValueError(
                    "Colunas obrigatórias ausentes: " + ", ".join(sorted(ausentes))
                )

            for linha in leitor:
                local = tuple(linha[coluna].strip() for coluna in COLUNAS_LOCAL)
                region_id, region_name = local

                if not all(local):
                    raise ValueError(
                        f"Linha {leitor.line_num}: region_id ou region_name está vazio."
                    )

                if local not in arquivos_abertos:
                    nome_arquivo = (
                        f"{nome_seguro(region_id)}_{nome_seguro(region_name)}.csv"
                    )
                    caminho_saida = pasta_saida / nome_arquivo
                    arquivo_saida = caminho_saida.open("w", encoding="utf-8", newline="")
                    escritor = csv.DictWriter(arquivo_saida, fieldnames=leitor.fieldnames)
                    escritor.writeheader()
                    arquivos_abertos[local] = (arquivo_saida, escritor, caminho_saida)
                    quantidade_por_local[local] = 0

                _, escritor, _ = arquivos_abertos[local]
                escritor.writerow(linha)
                quantidade_por_local[local] += 1
    finally:
        for arquivo_saida, _, _ in arquivos_abertos.values():
            arquivo_saida.close()

    print(f"Foram criados {len(quantidade_por_local)} arquivos em: {pasta_saida}")
    for (region_id, region_name), total in quantidade_por_local.items():
        print(f"- {region_id} — {region_name}: {total} registros")

    return len(quantidade_por_local)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Separa um CSV em arquivos individuais por local."
    )
    parser.add_argument(
        "arquivo_entrada",
        nargs="?",
        type=Path,
        default=ARQUIVO_PADRAO,
        help=f"CSV de entrada (padrão: {ARQUIVO_PADRAO})",
    )
    parser.add_argument(
        "pasta_saida",
        nargs="?",
        type=Path,
        default=PASTA_SAIDA_PADRAO,
        help=f"Pasta para os CSVs separados (padrão: {PASTA_SAIDA_PADRAO})",
    )
    argumentos = parser.parse_args()
    separar_por_local(argumentos.arquivo_entrada, argumentos.pasta_saida)


if __name__ == "__main__":
    main()
