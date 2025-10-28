# config/settings.py
import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Création des dossiers s'ils n'existent pas
DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PROCESSED_DATA_DIR.mkdir(exist_ok=True)

# Paramètres du modèle
MODEL_CONFIG = {
    "similarity_threshold": 0.3,
    "max_questions": 1000,
    "language": "french"
}

# URLs pour le web scraping (exemple)
DATA_SOURCES = {
    "formations_courte_durée": "https://www.ifoad-ujkz.net/formationenligne/course/index.php?categoryid=51",
    "filières": "https://www.ifoad-ujkz.net/formationenligne/course/index.php?categoryid=171",
    "Journaliste_numérique": "https://www.ifoad-ujkz.net/formationenligne/course/index.php?categoryid=56",
    "communication_numérique": "https://www.ifoad-ujkz.net/formationenligne/course/index.php?categoryid=58",
    "recrutement_licence_appliquee": "https://l.facebook.com/l.php?u=https%3A%2F%2Fwww.ujkz.bf%2Fwp-content%2Fuploads%2F2025%2F08%2FIFOAD-COMMUUNIQUE-N%C2%B0194-Recrutement-Licence-Appliquee-en-ligne-2025-2026.pdf%3Ffbclid%3DIwZXh0bgNhZW0CMTAAYnJpZBExcFpLU0VJRlBGRzRzS3FGdAEeTWLe4HKPViZD3gc0YzjWQ8eJKqrP42jH9UH33oi86ojOsqbSevNbkrt_47o_aem_Es-F63tMYdAUECKQDumMcg&h=AT2lprbWj4ndgki8ewcu3LltDRfKuQgmo9KIvEZQZ-fSYlWZ0Jqf4iz6DvkvMHRN2OR3LCU7mRCRbjV1OVDrcp3FkO2hACAGcECjUgYuXnBRRKZLcui7uF_6CNNJi2O7H0E4X1SzdRhmuerg&__tn__=-UK-R&c[0]=AT0pwoF4ZP477YMLiUKFTWbXNhYy0mJx_fA6GAzw-teFGcoeMKNsZ3WmeRHcIR904M8-GR2p3Tfltzv2a_loW-V3-cVuTtmPsqjP5-jnmiY9WDjdCQP1bSQa9C40bTlttod1iNYAuNw6PGIe9sMSRdy7HB0Gc16O97dr1oLYqsCsuGA4IGsRTXUeNjjOLaytS0RIray-BbOjmDopOOZCOiBrvA",
    "recrutement_master_data_science": "https://l.facebook.com/l.php?u=https%3A%2F%2Fwww.ujkz.bf%2Fwp-content%2Fuploads%2F2025%2F08%2FIFOAD-Communique-N%C2%B0211-Master-Data-Science-2025-2026.pdf%3Ffbclid%3DIwZXh0bgNhZW0CMTAAYnJpZBExcFpLU0VJRlBGRzRzS3FGdAEeG4etKR3Ie-QOq4njV55hCGtGml9iL7e_xbPdnYBEaSjD0TXp3OL6UH-RxMI_aem_3UBrDVj2yDmhgJNfzmpGVw&h=AT3WZtueEbQKLAoVh_iqXgmrQAC1xkuFk-knlnA-bmVIVPsgvWnzvfzQhdtBuFigvGK54p_RMI4uSYpPYl4GRjznVfXM_eIcZSgzSP7fcQIOgJKNOpCTnyVKfv_QkN24K1AIieA_ljjzLsxw&__tn__=-UK-R&c[0]=AT3cVpHVI3k-DZ6yLDJocP19ZiIdJPRS4kdr4FzkeAnoQdNGU8CFHq4ttL7Etew5-vEad2qp2RKmxE-Vk5l3GZbq7YK26EJX_olyVwzTS-TrWdhgqP8q4aMTglQl-tcd9H8qMOLXTtp18R6wmcMcIcCeLEFq-848IQUgvGA6wSkiV1jIB3NvWSq97XL81HhFf0tLzaYishzOjQW_70AjVVRzBA"
}