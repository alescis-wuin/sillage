<!-- Copie de lecture pour Projet ChatGPT. Source originale: sillage-specifications/templates/phase/PROMPT.fr.md. Mise à jour manuelle requise après changement. -->

# Mandat de conception — phase PXX

Prends pour référence la roadmap et les spécifications françaises jointes, la fiche SMART française et les références GitHub de `CONTEXT.json`. Lis le code **au SHA confirmé** en lecture seule ; ne suppose pas que des changements locaux non poussés sont accessibles.

Exécute exclusivement le périmètre du lot et ses deux étapes. Respecte les règles de code modulaire, le nommage anglais du code et des ressources Git, les conventions de commit et les règles de signature personnelle. Tu ne disposes d'aucune autorisation Git/GitHub en écriture ; propose les commandes ou le paquet déclaratif pour l'outil local, sans effectuer de fusion ni signer au nom du mainteneur.

Les contrôles statiques, lint, formatage en mode contrôle, syntaxe et compilation pertinents sont admis selon la politique locale ; aucun test unitaire ne peut être créé ou exécuté sans accord explicite distinct, jamais automatiquement. Aucun E2E. Ne répète pas les contrôles réussis sur des entrées identiques. Respecte les bornes de correction et ne prétends pas à une isolation non vérifiée.

Termine la conversation par un bilan factuel des travaux, références SHA vérifiées, critères satisfaits/non satisfaits, décisions validées, limites et mises à jour nécessaires du dossier de conception (roadmap, spécifications, transmission). Ne présente pas la PR comme fusionnée avant vérification réelle.
