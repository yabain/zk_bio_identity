# Manual d'installation et d'utilisation

## 1. Pré-requis

### Côté Frappe / ERPNext
- site Frappe ou ERPNext v15+
- module RH actif si tu veux `Employee`, `Employee Checkin`, `Attendance`, `Shift Type`, `Auto Attendance`
- accès administrateur au site
- possibilité d'installer une app custom depuis GitHub sur Frappe Cloud

### Côté poste local
- Windows recommandé pour le scanner ZKTeco USB
- Python 3.10+
- accès internet sortant vers ton site Frappe Cloud
- SDK / driver officiel ZKTeco correspondant à ton modèle

## 2. Installation de l'app sur Frappe Cloud

1. Pousse ce dépôt sur GitHub.
2. Dans Frappe Cloud, ouvre le Bench qui héberge ton site.
3. Ajoute l'app custom depuis le dépôt GitHub.
4. Installe l'app sur le site.
5. Lance la migration du site si nécessaire.

Une fois installée, l'app crée automatiquement :
- les rôles `Biometric Manager` et `Biometric Operator`
- les champs biométriques ajoutés sur `User`
- le Workspace public `ZK Bio Identity`
- le document `ZK Bio Settings` s'il n'existe pas

## 3. Configuration initiale côté site

### 3.1 Attribuer les rôles
Attribue au moins un des rôles suivants aux opérateurs :
- `Biometric Manager`
- `Biometric Operator`

### 3.2 Ouvrir les réglages
Va dans :
- `ZK Bio Identity` → `ZK Bio Settings`

Renseigne :
- `default_device` : périphérique par défaut
- `auto_create_employee_checkin` : activé si tu veux générer le pointage automatiquement après identification réussie
- `checkin_mode` : `Alternating`, `Always IN`, ou `Always OUT`
- `heartbeat_timeout_seconds` : durée après laquelle un device est considéré offline

## 4. Création d'un utilisateur API dédié à l'agent

Crée un utilisateur technique, par exemple :
- `biometric.agent@tondomaine.com`

Attribue-lui :
- `Biometric Manager`

Génère :
- API Key
- API Secret

Ces deux valeurs seront utilisées dans `agent_local/config.yaml`.

## 5. Installation du driver / SDK ZKTeco

### 5.1 Windows
1. Télécharge le SDK officiel ZKFinger pour Windows depuis le centre de téléchargement ZKTeco.
2. Décompresse l'archive.
3. Installe le driver fourni.
4. Branche le scanner USB.
5. Vérifie que Windows détecte correctement le périphérique.
6. Repère le chemin du DLL principal utilisé par le SDK.

Exemple de chemin fréquent à adapter :
- `C:\ZKTeco\ZKFingerSDK\lib\zkfp.dll`

### 5.2 macOS
Je ne recommande pas le support natif macOS pour cette V1.

La procédure conseillée est :
1. créer une VM Linux sur le Mac
2. faire le passthrough USB du scanner vers la VM
3. installer le SDK Linux ZKTeco dans la VM
4. lancer l'agent dans la VM au lieu de macOS

## 6. Installation de l'agent local

### 6.1 Préparer l'environnement
Dans `agent_local/` :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Sous Windows PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 6.2 Créer le fichier de configuration
Copie `config.example.yaml` vers `config.yaml`, puis remplis :

- `site_url`
- `api_key`
- `api_secret`
- `device_id`
- `device_name`
- `provider`
- `sdk_library_path` si mode ZKTeco réel

### 6.3 Mode simulation
Pour valider tout le flux sans matériel :

```yaml
provider: mock
```

### 6.4 Démarrer l'agent
```bash
python main.py --config config.yaml
```

## 7. Vérification de la connexion

Ouvre la page :
- `ZK Bio Identity` → `Connect Device`

Tu dois voir :
- le device
- son dernier heartbeat
- son statut online/offline
- si le scanner est détecté ou non

## 8. Enrôlement d'une empreinte

1. Ouvre `Add Fingerprint`.
2. Choisis un utilisateur.
3. Choisis le device.
4. Clique `Start Enrollment`.
5. L'agent reçoit une session `Enroll`.
6. L'utilisateur pose son doigt.
7. L'empreinte est enregistrée dans `Biometric Credential`.
8. Les champs biométriques du `User` sont mis à jour automatiquement.

## 9. Identification d'un utilisateur

1. Ouvre `Identify User`.
2. Choisis le device.
3. Clique `Start Identification`.
4. L'agent reçoit une session `Identify`.
5. L'utilisateur pose son doigt.
6. Si l'utilisateur existe :
   - la page affiche son profil
   - un `Employee Checkin` peut être créé automatiquement si l'option est activée
7. Sinon :
   - la page affiche `Utilisateur inexistant`

## 10. Pointage RH

Le module n'essaie pas de remplacer Frappe HR.

Il s'appuie sur :
- `Employee`
- `Employee Checkin`
- `Attendance`
- `Shift Type`
- `Auto Attendance`

Le comportement recommandé :
- l'identification biométrique trouve le `User`
- le `User` lié à un `Employee` produit un `Employee Checkin`
- Frappe HR calcule ensuite la présence à partir des checkins

## 11. Bonnes pratiques

- lier chaque employé à son `User`
- garder un device dédié pour chaque point de capture
- utiliser un compte API dédié à l'agent
- tester d'abord en mode `mock`
- valider ensuite le SDK réel sur ton modèle ZKTeco exact
- sauvegarder le site avant toute montée en production

## 12. Dépannage rapide

### Device non visible dans Frappe
- vérifier l'URL du site
- vérifier l'API key / secret
- vérifier que l'agent tourne
- vérifier que le rôle de l'utilisateur API permet les appels

### Scanner non détecté
- vérifier le driver ZKTeco
- vérifier le chemin de la DLL / SO
- tester le scanner avec la démo fournie dans le SDK officiel

### L'identification ne marche pas
- vérifier qu'au moins une empreinte est enrôlée
- vérifier que le provider a bien rechargé les templates
- vérifier l'implémentation du wrapper dans `zkteco_sdk_provider.py` pour le SDK exact utilisé

### Les pointages ne se créent pas
- vérifier que le `User` est lié à un `Employee`
- vérifier que `auto_create_employee_checkin` est activé
- vérifier que le doctype `Employee Checkin` existe sur le site
