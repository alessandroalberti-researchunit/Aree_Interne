"""
Scarica i documenti SNAI da politichecoesione.governo.it
nella struttura DOCS/ del progetto.

Esecuzione:
    python script/download_docs.py

Dipendenze: requests (pip install requests)

URL verificate al: 2026-06-18
"""

import os
import time
import requests

BASE_URL = "https://www.politichecoesione.governo.it"
ER_URL   = "https://politicheterritoriali.regione.emilia-romagna.it"
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "DOCS")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; research/1.0)"
}

# ---------------------------------------------------------------------------
# Mappa: (percorso_locale_relativo_a_DOCS, url_completa)
# ---------------------------------------------------------------------------
DOCUMENTI = [

    # ── Documenti generali SNAI 21-27 ──────────────────────────────────────
    (
        "openkit_guida-alla-lettura.pdf",
        BASE_URL + "/media/3186/openkit_guida-alla-lettura.pdf",
    ),
    (
        "mappa-ai-2020-nota-tecnica-nuvap.pdf",
        BASE_URL + "/media/2831/20220214-mappa-ai-2020-nota-tecnica-nuvap_rev.pdf",
    ),
    (
        "elenco_aree_snai_14-20-e-21-27.pdf",
        BASE_URL + "/media/zhyl2mkl/elenco_aree_snai_14-20-e-21-27_20261805.pdf",
    ),
    (
        "snai-criteri-selezione-aree-21-27.pdf",
        BASE_URL + "/media/2810/snai-criteri-per-la-selezione-delle-aree-da-sostenere-nel-ciclo-21-27.pdf",
    ),
    (
        "estratto-snai-accordo-partenariato-2021-2027.pdf",
        BASE_URL + "/media/uvap0nnt/estratto_snai_accordo-di-partenariato_2021-2027.pdf",
    ),

    # ── PSNAI e allegati ───────────────────────────────────────────────────
    # Fonte: /documenti-ed-esiti-istituzionali/documenti-strategici-di-inquadramento/
    #        programmazione-2021-2027/piano-strategico-nazionale-delle-aree-interne-2021-2027-psnai-e-allegati/
    (
        "PSNAI_2021-2027.pdf",
        BASE_URL + "/media/jhld12qn/psnai_finale_30072025_clean_ministro.pdf",
    ),
    (
        "01_contributo-cnel-demografia-aree-interne.pdf",
        BASE_URL + "/media/ihnf1qaq/1_contributo-cnel-demografia-delle-aree-interne-e-condizioni-per-uninversione-di-tendenza.pdf",
    ),
    (
        "02_contributo-censis-gruppi-omogenei.pdf",
        BASE_URL + "/media/5xpdha4t/2_contributo-censis-individuazione-e-analisi-di-gruppi-omogenei-di-territori.pdf",
    ),
    (
        "03_report-consultazione-PSNAI.pdf",
        BASE_URL + "/media/kvudrmu3/3_report-finale-della-consultazione-piano-strategico-nazionale-delle-aree-interne.pdf",
    ),
    (
        "04_linee-guida-requisito-associativo.pdf",
        BASE_URL + "/media/k1ahol2s/4_evoluzione-del-requisito-associativo-nella-snai-linee-guida-2021-2027.pdf",
    ),
    (
        "05_linee-guida-mobilita-MIT.pdf",
        BASE_URL + "/media/q0khs3u1/5_mit_le-aree-interne-e-la-mobilita_linee-guida-per-gli-interventi-nelle-aree-progetto.pdf",
    ),
    (
        "06_linee-guida-scuola-MIM.pdf",
        BASE_URL + "/media/w1pjo1lc/6_mim_la-buona-scuola_linee-guida-per-le-aree-interne.pdf",
    ),
    (
        "07_linee-guida-salute.pdf",
        BASE_URL + "/media/zkyjq2ti/7_la-salute-nelle-aree-interne_linee-guida-per-gli-interventi-nelle-aree-progetto.pdf",
    ),
    (
        "08_elenco-aree-comuni-con-riperimetrazioni.xlsx",
        BASE_URL + "/media/kvhb4wx3/8_elenco-delle-aree-e-dei-comuni-interessati-integrata-con-le-riperimetrazioni-richieste-dalle-amministrazioni-regionali-_corretto.xlsx",
    ),
    (
        "09_indice-strategie-di-area.pdf",
        BASE_URL + "/media/tuhlgb0d/9_indice-per-lelaborazione-delle-strategie-di-area.pdf",
    ),
    (
        "09a_format-2-allegato-indice.xlsx",
        BASE_URL + "/media/qeuhe2d2/9a_format-2-allegato-indice.xlsx",
    ),
    (
        "09b_format-3-allegato-indice.xlsx",
        BASE_URL + "/media/2xygxu5j/9b_format-3-allegato-indice.xlsx",
    ),
    (
        "10_scheda-intervento.xlsx",
        BASE_URL + "/media/01ad31dx/10_-scheda-intervento_rev.xlsx",
    ),
    (
        "11_relazione-annuale-2023.pdf",
        BASE_URL + "/media/ofddm2e1/11_relazione-annuale-al-31122023.pdf",
    ),

    # ── Documentazione regionale — Rapporti istruttoria ────────────────────
    (
        "Documentazione Regionale/Nord/rapporto-istruttoria_pa-bolzano.pdf",
        BASE_URL + "/media/3102/rapporto-istruttoria_pa-bolzano.pdf",
    ),
    (
        "Documentazione Regionale/Nord/rapporto-istruttoria_pa-trento.pdf",
        BASE_URL + "/media/3103/rapporto-istruttoria_pa-trento.pdf",
    ),
    (
        "Documentazione Regionale/Nord/rapporto-istruttoria_emilia-romagna.pdf",
        BASE_URL + "/media/3105/rapporto-istruttoria_regione-emilia-romagna.pdf",
    ),
    (
        "Documentazione Regionale/Nord/rapporto-istruttoria_friuli-venezia-giulia.pdf",
        BASE_URL + "/media/3106/rapporto-istruttoria_regione-friuli-venezia-giulia.pdf",
    ),
    (
        "Documentazione Regionale/Nord/rapporto-istruttoria_liguria.pdf",
        BASE_URL + "/media/3109/rapporto-istruttoria_regione-liguria.pdf",
    ),
    (
        "Documentazione Regionale/Nord/rapporto-istruttoria_lombardia.pdf",
        BASE_URL + "/media/3093/rapporto-istruttoria_regione-lombardia.pdf",
    ),
    (
        "Documentazione Regionale/Nord/rapporto-istruttoria_piemonte.pdf",
        BASE_URL + "/media/3096/rapporto-istruttoria_regione-piemonte.pdf",
    ),
    (
        "Documentazione Regionale/Nord/rapporto-istruttoria_valle-daosta.pdf",
        BASE_URL + "/media/3107/rapporto-istruttoria_regione-valle-daosta.pdf",
    ),
    (
        "Documentazione Regionale/Nord/rapporto-istruttoria_veneto.pdf",
        BASE_URL + "/media/3101/rapporto-istruttoria_regione-veneto.pdf",
    ),
    (
        "Documentazione Regionale/Centro/rapporto-istruttoria_lazio.pdf",
        BASE_URL + "/media/3092/rapporto-istruttoria_regione-lazio.pdf",
    ),
    (
        "Documentazione Regionale/Centro/rapporto-istruttoria_marche.pdf",
        BASE_URL + "/media/3094/rapporto-istruttoria_regione-marche.pdf",
    ),
    (
        "Documentazione Regionale/Centro/rapporto-istruttoria_toscana.pdf",
        BASE_URL + "/media/3099/rapporto-istruttoria_regione-toscana.pdf",
    ),
    (
        "Documentazione Regionale/Centro/rapporto-istruttoria_umbria.pdf",
        BASE_URL + "/media/3100/rapporto-istruttoria_regione-umbria.pdf",
    ),
    (
        "Documentazione Regionale/Sud/rapporto-istruttoria_abruzzo.pdf",
        BASE_URL + "/media/3090/rapporto-istruttoria_regione-abruzzo.pdf",
    ),
    (
        "Documentazione Regionale/Sud/rapporto-istruttoria_basilicata.pdf",
        BASE_URL + "/media/3091/rapporto-istruttoria_regione-basilicata.pdf",
    ),
    (
        "Documentazione Regionale/Sud/rapporto-istruttoria_calabria.pdf",
        BASE_URL + "/media/3104/rapporto-istruttoria_regione-calabria.pdf",
    ),
    (
        "Documentazione Regionale/Sud/rapporto-istruttoria_campania.pdf",
        BASE_URL + "/media/3108/rapporto-istruttoria_regione-campania.pdf",
    ),
    (
        "Documentazione Regionale/Sud/rapporto-istruttoria_molise.pdf",
        BASE_URL + "/media/3095/rapporto-istruttoria_regione-molise.pdf",
    ),
    (
        "Documentazione Regionale/Sud/rapporto-istruttoria_puglia.pdf",
        BASE_URL + "/media/3097/rapporto-istruttoria_regione-puglia.pdf",
    ),
    (
        "Documentazione Regionale/Sud/rapporto-istruttoria_sardegna.pdf",
        BASE_URL + "/media/3098/rapporto-istruttoria_regione-sardegna.pdf",
    ),
    (
        "Documentazione Regionale/Sud/rapporto-istruttoria_sicilia.pdf",
        BASE_URL + "/media/3089/rapporto-istruttoria_regione-sicilia.pdf",
    ),

    # ── Documentazione regionale — Dossier SNAI ────────────────────────────
    # (Emilia-Romagna non ha dossier; al suo posto ci sono i file APQ — vedi TODO sotto)
    (
        "Documentazione Regionale/Nord/snai-dossier_pa-bolzano.pdf",
        BASE_URL + "/media/3162/snai-dossier-pa-bolzano.pdf",
    ),
    (
        "Documentazione Regionale/Nord/snai-dossier_pa-trento.pdf",
        BASE_URL + "/media/3163/snai-dossier-pa-trento.pdf",
    ),
    (
        "Documentazione Regionale/Nord/snai-dossier_friuli-venezia-giulia.pdf",
        BASE_URL + "/media/3169/snai-dossier-regionale-friuli-venezia-giulia.pdf",
    ),
    (
        "Documentazione Regionale/Nord/snai-dossier_liguria.pdf",
        BASE_URL + "/media/3171/snai-dossier-regionale-liguria.pdf",
    ),
    (
        "Documentazione Regionale/Nord/snai-dossier_lombardia.pdf",
        BASE_URL + "/media/3172/snai-dossier-regionale-lombardia.pdf",
    ),
    (
        "Documentazione Regionale/Nord/snai-dossier_piemonte.pdf",
        BASE_URL + "/media/3175/snai-dossier-regionale-piemonte.pdf",
    ),
    (
        "Documentazione Regionale/Nord/snai-dossier_valle-daosta.pdf",
        BASE_URL + "/media/3181/snai-dossier-regionale-valle-daosta.pdf",
    ),
    (
        "Documentazione Regionale/Nord/snai-dossier_veneto.pdf",
        BASE_URL + "/media/3182/snai-dossier-regionale-veneto.pdf",
    ),
    (
        "Documentazione Regionale/Centro/snai-dossier_lazio.pdf",
        BASE_URL + "/media/3170/snai-dossier-regionale-lazio.pdf",
    ),
    (
        "Documentazione Regionale/Centro/snai-dossier_marche.pdf",
        BASE_URL + "/media/3173/snai-dossier-regionale-marche.pdf",
    ),
    (
        "Documentazione Regionale/Centro/snai-dossier_toscana.pdf",
        BASE_URL + "/media/3179/snai-dossier-regionale-toscana.pdf",
    ),
    (
        "Documentazione Regionale/Centro/snai-dossier_umbria.pdf",
        BASE_URL + "/media/3180/snai-dossier-regionale-umbria.pdf",
    ),
    (
        "Documentazione Regionale/Sud/snai-dossier_abruzzo.pdf",
        BASE_URL + "/media/3164/snai-dossier-regionale-abruzzo.pdf",
    ),
    (
        "Documentazione Regionale/Sud/snai-dossier_basilicata.pdf",
        BASE_URL + "/media/3165/snai-dossier-regionale-basilicata.pdf",
    ),
    (
        "Documentazione Regionale/Sud/snai-dossier_calabria.pdf",
        BASE_URL + "/media/3166/snai-dossier-regionale-calabria.pdf",
    ),
    (
        "Documentazione Regionale/Sud/snai-dossier_campania.pdf",
        BASE_URL + "/media/3167/snai-dossier-regionale-campania.pdf",
    ),
    (
        "Documentazione Regionale/Sud/snai-dossier_molise.pdf",
        BASE_URL + "/media/3174/snai-dossier-regionale-molise.pdf",
    ),
    (
        "Documentazione Regionale/Sud/snai-dossier_puglia.pdf",
        BASE_URL + "/media/3176/snai-dossier-regionale-puglia.pdf",
    ),
    (
        "Documentazione Regionale/Sud/snai-dossier_sardegna.pdf",
        BASE_URL + "/media/3177/snai-dossier-regionale-sardegna.pdf",
    ),
    (
        "Documentazione Regionale/Sud/snai-dossier_sicilia.pdf",
        BASE_URL + "/media/3178/snai-dossier-regionale-siciliana.pdf",
    ),

    # ── APQ Emilia-Romagna ─────────────────────────────────────────────────
    # Gli APQ (Accordi di Programma Quadro) sono su politicheterritoriali.regione.emilia-romagna.it
    (
        "Documentazione Regionale/Nord/Emilia-Romagna/APQ_Appennino-Emiliano.pdf",
        ER_URL + "/politiche-territoriali/snai/allegati/apq_appennino_emiliano/@@download/file",
    ),
    (
        "Documentazione Regionale/Nord/Emilia-Romagna/APQ_Basso-Ferrarese.pdf",
        ER_URL + "/politiche-territoriali/snai/allegati/apq_basso_ferrarese/@@download/file",
    ),
    (
        "Documentazione Regionale/Nord/Emilia-Romagna/APQ_Appennino-Piacentino-Parmense.pdf",
        ER_URL + "/politiche-territoriali/snai/allegati/apq_app_piacentino_parmense/@@download/file",
    ),
    (
        "Documentazione Regionale/Nord/Emilia-Romagna/APQ_Alta-Valmarecchia.pdf",
        ER_URL + "/politiche-territoriali/snai/allegati/apq_alta_val_marecchia/@@download/file",
    ),
]


def download(dest_rel, url, skip_existing=True):
    dest = os.path.join(BASE_DIR, dest_rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    if skip_existing and os.path.exists(dest):
        print(f"  SKIP (exists): {dest_rel}")
        return

    print(f"  GET  {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=256 * 1024):
                f.write(chunk)
        size_kb = os.path.getsize(dest) / 1024
        print(f"       → {dest_rel}  ({size_kb:.0f} KB)")
    except Exception as e:
        print(f"  ERRORE: {e}")


def main():
    print(f"Destinazione: {BASE_DIR}\n")
    for dest_rel, url in DOCUMENTI:
        download(dest_rel, url)
        time.sleep(0.5)   # cortesia verso il server
    print("\nFatto.")


if __name__ == "__main__":
    main()
