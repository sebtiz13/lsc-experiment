# Plan d'Implémentation pour les Scripts de Payload

## Objectif
Créer des scripts Python pour décoder et encoder les payloads du smart power strip, avec un système de test complet.

## Structure du Projet
```
smart_plug_payload/
├── decode_payload.py      # Script de décodage
├── encode_payload.py      # Script d'encodage  
├── test_payloads.py       # Tests complets
├── plan.md                # Ce fichier
└── README.md              # Documentation
```

## Analyse de la Structure du Payload

### Format de Base
- Payload encodé en base64
- Structure binaire avec champs spécifiques
- Support des cycles multiples dans un seul payload

### Structure d'un Cycle Unique (12 octets)
- **Octet 0**: Numéro de socket (1-3) + flag d'activation (bit 7)
  - Bit 7: 0 = désactiver, 1 = activer
  - Bits 0-2: numéro de socket (1-3)
- **Octets 1-2**: Heure de début (minutes depuis minuit, little-endian)
- **Octets 3-4**: Heure de fin (minutes depuis minuit, little-endian)
- **Octet 5**: Jours de répétition (bitmap)
  - Bit 0 = Dimanche, Bit 1 = Lundi, ..., Bit 6 = Samedi
  - 0x00 = une seule fois
- **Octets 6-7**: Durée d'ouverture (minutes, little-endian)
- **Octets 8-9**: Durée de fermeture (minutes, little-endian)
- **Octets 10-11**: Réservé/unknown (souvent 0x0001)

### Structure Multi-Cycles
- **En-tête**: 2 octets indiquant le nombre de cycles
- **Données**: Concatenation des payloads de cycles individuels

## Plan de Développement

### Étape 1: Script de Décodage (`decode_payload.py`)

#### Fonctions Principales
```python
def decode_payload(base64_payload: str) -> list[dict]:
    """Décode un payload base64 en information lisible"""
    # 1. Décodage base64
    # 2. Analyse de l'en-tête pour les multi-cycles
    # 3. Pour chaque cycle, extraire les informations
    # 4. Retourner une liste de dictionnaires

def minutes_to_time(minutes: int) -> str:
    """Convertit les minutes en format HH:MM"""
    # Gestion du dépassement pour les heures traversant minuit

def decode_repeat_days(bitmap: int) -> str:
    """Convertit le bitmap des jours en noms de jours"""
    # Mapping des bits vers les noms de jours

def format_duration(minutes: int) -> str:
    """Formate la durée en minutes vers un format lisible"""
    # Gestion des heures et minutes
```

#### Interface CLI
```python
def main():
    # Interface en ligne de commande pour décoder les payloads
    # Support des arguments et de l'entrée standard
```

### Étape 2: Script d'Encodage (`encode_payload.py`)

#### Fonctions Principales
```python
def encode_payload(cycles: list[dict]) -> str:
    """Encode les informations de cycle en payload base64"""
    # 1. Validation des cycles d'entrée
    # 2. Pour chaque cycle, convertir les informations
    # 3. Créer l'en-tête pour les multi-cycles
    # 4. Concatenation des données
    # 5. Encodage base64

def time_to_minutes(time_str: str) -> int:
    """Convertit HH:MM en minutes depuis minuit"""
    # Gestion du format 24h

def days_to_bitmap(days: str) -> int:
    """Convertit les noms de jours en bitmap"""
    # Mapping des noms de jours vers les bits

def duration_to_minutes(duration_str: str) -> int:
    """Convertit la durée lisible en minutes"""
    # Analyse des formats comme "1h", "30min", "1h30min"
```

#### Interface CLI
```python
def main():
    # Interface en ligne de commande pour encoder les payloads
    # Support des arguments et de l'entrée standard
```

### Étape 3: Script de Tests (`test_payloads.py`)

#### Structure des Tests
```python
import unittest
from decode_payload import decode_payload
from encode_payload import encode_payload

class TestPayloadEncodingDecoding(unittest.TestCase):
    """Suite de tests pour l'encodage et le décodage des payloads"""

    def test_single_cycle_payloads(self):
        """Test tous les exemples de cycles uniques"""
        # Cas de test basés sur project.md
        # Vérification du décodage
        # Test de round-trip (encode → decode → encode)

    def test_multi_cycle_payloads(self):
        """Test les exemples de payloads multi-cycles"""
        # Cas de test pour 2 et 3 cycles
        # Vérification de la structure multi-cycles

    def test_time_edge_cases(self):
        """Test les cas particuliers de temps"""
        # Heures traversant minuit
        # Plages de temps complètes

    def test_repeat_days(self):
        """Test les différents motifs de jours de répétition"""
        # Une seule fois, jours individuels, combinaisons

    def test_durations(self):
        """Test les différents formats de durée"""
        # Minutes, heures, formats mixtes
```

#### Cas de Test Spécifiques
- Tous les exemples de project.md
- Payloads multi-cycles
- Cas limites (minuit, durées complexes)
- Tests de round-trip

### Étape 4: Gestion des Erreurs

#### Dans le Décodeur
- Payload base64 invalide
- Longueur de payload incorrecte
- Valeurs de socket invalides
- Heures invalides
- Formats de durée invalides

#### Dans l'Encodeur
- Données d'entrée manquantes
- Numéros de socket invalides
- Formats de temps invalides
- Formats de durée invalides
- Jours de répétition invalides

## Calendrier d'Implémentation

1. **Analyse et Conception** (En cours)
   - Compréhension complète de la structure du payload
   - Création du plan détaillé

2. **Implémentation du Décodeur**
   - Fonctions de base (décodage, conversion de temps)
   - Support des cycles uniques
   - Support des multi-cycles
   - Interface CLI

3. **Implémentation de l'Encodeur**
   - Fonctions de base (encodage, conversion de temps)
   - Validation des entrées
   - Interface CLI

4. **Création des Tests**
   - Tests unitaires pour les fonctions individuelles
   - Tests d'intégration pour les cycles complets
   - Tests de régression avec tous les exemples

5. **Tests et Debugging**
   - Exécution de tous les tests
   - Correction des problèmes identifiés
   - Optimisation des performances

6. **Documentation**
   - Création du README.md
   - Commentaires dans le code
   - Exemples d'utilisation

## Exigences Techniques

- Python 3.8+
- Pas de dépendances externes (utilisation de la bibliothèque standard)
- Code modulaire et bien documenté
- Tests complets avec bonne couverture
- Gestion robuste des erreurs

## Livrables

1. Script de décodage fonctionnel
2. Script d'encodage fonctionnel
3. Suite de tests complète
4. Documentation claire
5. Exemples d'utilisation

## Validation

Le projet sera considéré comme réussi lorsque:
- Tous les exemples de project.md sont correctement décodés
- Tous les exemples peuvent être ré-encodés pour produire les payloads originaux
- Tous les tests passent
- La documentation est complète et claire