import streamlit as st
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Récupérer les informations sensibles depuis les variables d'environnement
infura_url = os.getenv("INFURA_URL")  # URL Infura
private_key = os.getenv("PRIVATE_KEY")  # Clé privée
contract_address = Web3.to_checksum_address("0xefeb5e2c7ecd2bc7951bbc20961562405416d915")  # Adresse du contrat déployé

# Vérifier la connexion à Infura
web3 = Web3(Web3.HTTPProvider(infura_url))
if web3.is_connected():
    st.sidebar.success("✅ Connecté au réseau Polygon amoy testnet via Infura")
else:
    st.sidebar.error("❌ Échec de la connexion à Infura")
    st.stop()

# Obtenir l'adresse du portefeuille depuis la clé privée
if not private_key:
    st.error("🔒 Clé privée introuvable ! Veuillez l'ajouter au fichier `.env`.")
    st.stop()
account = Account.from_key(private_key)
portefeuille = account.address

# Affichage du portefeuille dans la barre latérale
st.sidebar.info(f"🔑 Adresse du portefeuille: {portefeuille}")

# Charger l'ABI du contrat
contract_abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "_portefeuille", "type": "address"},
            {"internalType": "uint256", "name": "_scoreCredit", "type": "uint256"},
            {"internalType": "uint256", "name": "_limiteExposition", "type": "uint256"},
            {"internalType": "uint256", "name": "_probabiliteDefaut", "type": "uint256"},
            {"internalType": "uint256", "name": "_pertesEnCasDeDefaut", "type": "uint256"},
            {"internalType": "uint256", "name": "_collaterale", "type": "uint256"}
        ],
        "name": "ajouterContrepartie",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "_portefeuille", "type": "address"},
            {"internalType": "uint256", "name": "_nouvelleExposition", "type": "uint256"}
        ],
        "name": "mettreAJourExposition",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "_portefeuille", "type": "address"}],
        "name": "calculerRisque",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "_portefeuille", "type": "address"}],
        "name": "calculerRatioCouverture",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "_portefeuille", "type": "address"}],
        "name": "calculerPertesAttendues",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "contreparties",
		"outputs": [
			{
				"internalType": "address",
				"name": "portefeuille",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "scoreCredit",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "limiteExposition",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "expositionCourante",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "collaterale",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "probabiliteDefaut",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "pertesEnCasDeDefaut",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Titre principal
st.title("Gestion des Risques Contreparties")

# Section Ajouter une Contrepartie
st.header("Ajouter une Contrepartie")
with st.expander("Détails sur la contrepartie"):
    score_credit = st.number_input("Score de Crédit", min_value=1, value=100)
    limite_exposition = st.number_input("Limite d'Exposition", min_value=1, value=1000)
    probabilite_defaut = st.number_input("Probabilité de Défaut (%)", min_value=1, max_value=100, value=10)
    pertes_defaut = st.number_input("Pertes en Cas de Défaut (%)", min_value=0, max_value=100, value=50)
    collaterale = st.number_input("Montant du Collatéral", min_value=0, value=500)

if st.button("Ajouter Contrepartie"):
    try:
        nonce = web3.eth.get_transaction_count(portefeuille)
        txn = contract.functions.ajouterContrepartie(
            portefeuille,
            int(score_credit),
            int(limite_exposition),
            int(probabilite_defaut),
            int(pertes_defaut),
            int(collaterale)
        ).build_transaction({
            "from": portefeuille,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": web3.to_wei("30", "gwei")
        })
        signed_txn = web3.eth.account.sign_transaction(txn, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        st.success(f"Contrepartie ajoutée avec succès! Transaction hash: {tx_hash.hex()}")
    except Exception as e:
        st.error(f"Erreur lors de l'ajout de la contrepartie: {e}")

# Section Mettre à Jour l'Exposition
st.header("Mettre à Jour l'Exposition")
nouvelle_exposition = st.number_input("Nouvelle Exposition", min_value=0, value=0)

if st.button("Mettre à Jour Exposition"):
    if nouvelle_exposition > limite_exposition:
        st.error(f"❌ Exposition dépasse la limite autorisée de {limite_exposition}!")
        try:
            nonce = web3.eth.get_transaction_count(portefeuille)
            txn = contract.functions.mettreAJourExposition(
                portefeuille,
                int(nouvelle_exposition)
            ).build_transaction({
                "from": portefeuille,
                "nonce": nonce,
                "gas": 200000,
                "gasPrice": web3.to_wei("30", "gwei")
            })
            signed_txn = web3.eth.account.sign_transaction(txn, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            st.success(f"Transaction envoyée mais refusée. Vous pouvez vérifier la transaction sur PolygonScan : [Voir Transaction](https://amoy.polygonscan.com/address/{contract_address})")
        except Exception as e:
            st.error(f"Erreur lors de la mise à jour de l'exposition: {e}")
    else:
        try:
            nonce = web3.eth.get_transaction_count(portefeuille)
            txn = contract.functions.mettreAJourExposition(
                portefeuille,
                int(nouvelle_exposition)
            ).build_transaction({
                "from": portefeuille,
                "nonce": nonce,
                "gas": 200000,
                "gasPrice": web3.to_wei("30", "gwei")
            })
            signed_txn = web3.eth.account.sign_transaction(txn, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            st.success(f"Exposition mise à jour avec succès! Transaction hash: {tx_hash.hex()}")
        except Exception as e:
            st.error(f"Erreur lors de la mise à jour de l'exposition: {e}")


# Section Calcul des Risques et Ratios
st.header("Calcul des Risques et Ratios")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Calculer Score de Risque"):
        try:
            risque = contract.functions.calculerRisque(portefeuille).call()
            st.write(f"📊 Score de Risque: {risque}")
        except Exception as e:
            st.error(f"Erreur lors du calcul du score de risque: {e}")

with col2:
    if st.button("Calculer Ratio de Couverture"):
        try:
            ratio_couverture = contract.functions.calculerRatioCouverture(portefeuille).call()
            st.write(f"📊 Ratio de Couverture: {ratio_couverture}%")
        except Exception as e:
            st.error(f"Erreur lors du calcul du ratio de couverture: {e}")

with col3:
    if st.button("Calculer Pertes Attendues"):
        try:
            pertes_attendues = contract.functions.calculerPertesAttendues(portefeuille).call()
            st.write(f"📊 Pertes Attendues: {pertes_attendues}")
        except Exception as e:
            st.error(f"Erreur lors du calcul des pertes attendues: {e}")

# Section Informations de la Contrepartie
st.header("Informations sur la Contrepartie")
if st.button("Afficher Informations"):
    try: 
        contrepartie_info = contract.functions.contreparties(portefeuille).call()
        if contrepartie_info[0] != "0x0000000000000000000000000000000000000000":
            st.json({
                "Portefeuille": contrepartie_info[0],
                "Score de Crédit": contrepartie_info[1],
                "Limite d'Exposition": contrepartie_info[2],
                "Exposition Courante": contrepartie_info[3],
                "Collateral": contrepartie_info[4],
                "Probabilité de Défaut": contrepartie_info[5],
                "Pertes en Cas de Défaut": contrepartie_info[6]
            })
        else:
            st.warning("Aucune contrepartie trouvée.")
    except Exception as e:
        st.error(f"Erreur : {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("💡 Utilisez toujours des réseaux de test pour les expérimentations.")
st.sidebar.markdown("---")
st.sidebar.write("🔗 [Documentation Solidity](https://soliditylang.org/)")

