<!-- Copie de lecture pour Projet ChatGPT. Source originale: sillage-specifications/README.md. Mise à jour manuelle requise après changement. -->

# Sillage — spécifications

**Objet.** Sillage définit une chaîne de développement assisté par IA sans accès de l'IA en écriture aux dépôts : lecture de miroirs privés, livraison par ZIP incrémental, vérification en copie temporaire, intégration locale contrôlée et publication signée selon une politique locale.

**Portée.** Contrats et comportements attendus uniquement. Ce dossier ne contient ni application, ni Skill installable, ni roadmap. Les données des exemples sont fictives. Les documents de conception destinés aux IA sont en **français** ; les fichiers techniques et les métadonnées du dépôt source sont en **anglais** selon [les standards](docs/developpement.md). Les contrats du **produit Sillage** restent distincts du protocole de **développement de Sillage**.

## Navigation

| Document | Contenu |
| --- | --- |
| [Architecture](docs/architecture.md) | Autorités, dépôts, flux, invariants |
| [Parcours et états](docs/parcours.md) | Traitement d'un paquet, cas de réussite/échec, traçabilité |
| [Compétences IA](docs/competences.md) | Trois Skills : concevoir, corriger, tester |
| [Installateur et contrôles](docs/installateur.md) | Format ZIP, contrôle préalable, copie candidate, isolation |
| [Synchronisation et diagnostics](docs/synchronisation.md) | Filewatcher, instantanés de travail, rapports, `LATEST` |
| [Signature et publication](docs/publication.md) | Règles d'engagement, commit signé, tag, push, incidents |
| [Contrats JSON](docs/contrats.md) | Versions, schémas, références croisées, exemples |
| [Standards de développement](docs/developpement.md) | Clean Code, SOLID pragmatique, séparation des responsabilités, nommage et Makefile du dépôt source |
| [Conventions Git/GitHub](docs/git-github.md) | `main`/`develop`, commits/tags signés, issues, PR, hooks, tests |
| [Conduite des phases](docs/conduite-phases.md) | P0, Makefile, SMART FR/EN vérifiée avant ouverture, validations croisées, mode transitoire et transmission |
| [Modèles de phase](templates/phase/SMART.fr.md) | SMART bilingue, prompt français, bilan anglais et transmission |
| [Modèles GitHub](templates/github/PULL_REQUEST.md) | PR de phase et issues parente/étapes (anglais) |
| [Références techniques](docs/references.md) | Liens officiels des mécanismes employés |

## Contrats de données

Tous les contrats sont en **JSON Schema Draft 2020-12**, avec le champ `schema_version: 1` ; le schéma de version inconnue est refusé, sans adaptation silencieuse.

| Schéma | Exemple |
| --- | --- |
| [Paquet](schemas/v1/package.schema.json) | [package.json](examples/v1/package.json) |
| [Politique de projet](schemas/v1/policy.schema.json) | [policy.json](examples/v1/policy.json) |
| [Instantané](schemas/v1/snapshot.schema.json) | [snapshot.json](examples/v1/snapshot.json) |
| [Rapport d'exécution](schemas/v1/run-report.schema.json) | [run-report.json](examples/v1/run-report.json) |
| [Contexte de correction](schemas/v1/correction-context.schema.json) | [correction-context.json](examples/v1/correction-context.json) |
| [État courant](schemas/v1/latest.schema.json) | [latest.json](examples/v1/latest.json) |

## Contrat distinct de préparation de phase

Le [manifeste de démarrage de phase v1](schemas/development/v1/phase-start.schema.json) et son [exemple fictif](examples/development/v1/phase-start.json) ne sont **pas** des contrats d’installation de code. Ils servent à un outil local Git/`gh` après validation et autorisation explicite ; ils ne contiennent aucune commande libre. Leurs documents bilingues et modèles de PR/issues sont dans `templates/`.

## Règles cardinales

1. Le **projet local** fait autorité sur le code réellement utilisé. L'IA ne possède aucun droit de publication ni d'écriture sur GitHub.
2. Le **miroir privé** expose une photographie traçable du code local de travail ; les propositions non installées utilisent des références séparées.
3. Le **dépôt de diagnostics** accueille rapports, journaux, documentation enrichie et pointeurs vers des commits exacts.
4. Le **dépôt public** ne reçoit que les changements autorisés et signés localement, jamais un simple instantané technique.
5. Un **paquet** est une archive de données déclaratives, jamais un script arbitraire à exécuter ; son identifiant est le SHA-256 du ZIP reçu.
6. Les contrôles sont **bornés, déterministes et proportionnés** : structure, lint, formatage, syntaxe et compilation pertinents ; **aucune exécution automatique de tests unitaires**, aucun E2E. La création et l'exécution manuelle de tests unitaires exigent un accord explicite. Le plafond des tentatives de correction et l'isolation vérifiable du préflight sont obligatoires.
7. **Aucune publication publique automatique par défaut** : une politique locale approuvée par le mainteneur est nécessaire.
8. Le **dépôt source de Sillage** utilise `main` et `develop`, des branches de phase, une PR par phase et des commits/fusions/tags personnellement signés. Son workflow n'est pas imposé aux projets utilisateurs.
9. À la fin de chaque conversation de phase, le dossier de conception est mis à jour et transmis avec les preuves réellement confirmées, sans réécrire les commits documentaires de mesure.

## Convention de lecture

- **DOIT / NE DOIT PAS** : exigence normative du contrat.
- **PEUT** : option compatible.
- *Proposition* : comportement conceptuel non implémenté.
- Les commits et SHA des exemples ne sont pas des preuves d'opérations réelles.
