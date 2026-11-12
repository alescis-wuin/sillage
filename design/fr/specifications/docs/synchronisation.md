<!-- Copie de lecture pour Projet ChatGPT. Source originale: sillage-specifications/docs/synchronisation.md. Mise à jour manuelle requise après changement. -->

# Sillage — synchronisation et diagnostics privés

[Accueil](../README.md) · [Architecture](architecture.md) · [Contrats](contrats.md)

## Première version : synchronisation manuelle

La version initiale fonctionne avec **un projet pilote et un hôte effectivement supporté**, sans service permanent. `sync` et `status` sont disponibles manuellement. Le watcher, l'enregistrement multi-projets et `register`/`unregister`/`pause`/`resume` décrits ci-dessous restent **différés**, pas des prérequis des premières phases.

Une synchronisation manuelle : capture les octets et modes autorisés du véritable répertoire local, publie un commit technique du miroir `work`, puis publie un snapshot et une entrée de navigation des diagnostics **après confirmation du push de `work`**. Si le réseau échoue, l'état local devient `pending`/`degraded` avec journal de reprise idempotent : aucune référence distante non vérifiée n'est annoncée comme actuelle.

Les chemins sont filtrés par règles de type `.gitignore` ; les fichiers non suivis sont capturés seulement par liste blanche. Secrets, clés, caches, builds et fichiers temporaires sont exclus. Le miroir n'est pas une copie complète de tout le disque local.

## Extension différée : surveillance facultative

Un watcher local, s'il est développé ultérieurement, pourra utiliser `register`, `unregister`, `pause`, `resume`, `sync` et `status`, un **debounce** et un scan de réconciliation. Les événements manuels ne déclenchent **ni compilation ni tests ni conversation IA ni commit public**. L'installateur doit éviter les captures intermédiaires pendant ses écritures, sans imposer la création d'un service en V1.

## Calcul de l'instantané

Un snapshot représente les octets et modes autorisés du répertoire de travail, même lorsque `HEAD` ne reflète pas les modifications non commitées. Il contient `source_head`, `source_dirty`, la liste des chemins et leurs empreintes, et `mirror_commit` confirmé.

`snapshot_id` = SHA-256 de la représentation JSON UTF-8 canonique (sans espaces, clés triées, sans horodatage ni taille) de la liste triée par chemin des objets `{path, sha256, mode}` pour **l'ensemble des fichiers inclus**. Chemins POSIX normalisés NFC. Ce n'est ni le SHA du ZIP ni celui d'un commit Git.

Le miroir `work` expose uniquement le dernier état local **réellement confirmé**. Les commits `proposals/<package-id-sans-prefixe>` correspondent aux candidates effectivement reconstruites, même si leur préflight échoue ; ils ne remplacent jamais le `work` réel sans installation. L'historique technique reste distinct de l'historique Git officiel.

## Dépôt de diagnostics

```text
diagnostics/
├── AI_START_HERE.md       # navigation, y compris rejets précoces
├── LATEST.md              # seulement après un véritable run compatible
├── latest.json            # schéma v1 ; pas de valeur fictive d'amorçage
├── snapshots/<id>.json    # snapshot identifié et SHA work confirmé
├── runs/<run-id>/
│   ├── report.json        # seulement si base_snapshot vérifiable
│   ├── rejection.md       # sinon : diagnostic minimal, jamais un faux report
│   ├── correction-context.json  # après confirmation du commit de report
│   └── logs/*.log         # journaux ciblés, filtrés et bornés
└── index/
    ├── TREE.txt
    └── docs/...           # documentation enrichie facultative, différée
```

Pour un rejet sans base fiable, `rejection.md` contient les identifiants réellement calculables (`package_id`, `run_id`), la catégorie, le motif filtré, les informations manquantes et aucune fausse référence Git. Il peut être consulté depuis une nouvelle conversation après publication confirmée ; sinon il demeure en attente locale. Ce fichier **n'est pas la cible de `latest_run`** et n'exige pas de nouveau schéma JSON. Voir l'[exemple fictif de rejet](../examples/v1/rejection.md).

Les rapports des runs valides distinguent `candidate.commit` (éventuellement `null`), `local.status`, `publication.status` et les états de synchronisation. Un `correction-context.json` référence un **commit de diagnostics déjà confirmé**, ses logs et la base réelle de correction ; l'absence de commit testé ne doit pas être comblée fictivement.

Les journaux sont filtrés (secrets, tokens, chemins sensibles), bornés et épinglés à leur `run_id`/`package_id`. `LATEST.md` dérive de `latest.json` ; les références de `latest.json` ne changent qu'après vérification des écritures distantes réelles. Si le miroir et les diagnostics divergent, indiquer `degraded` et le dernier point cohérent connu.

Les documents d'index enrichi peuvent devenir périmés ; indiquer leur snapshot source. Le code réellement capturé prime sur une prose dérivée. Les pointeurs Git LFS sont possibles à long terme mais hors du parcours v1 de référence.

## Convergence et reprise

Les écritures vers `work`, diagnostics et dépôt public sont **non atomiques entre dépôts**. Un journal local conserve séparément les opérations accomplies, à reprendre et impossibles, sans service permanent. Une nouvelle `sync` ou reprise explicite poursuit les publications idempotentes.

**Un échec de push privé n'annule jamais une installation locale réellement réussie.** Le résultat de code reste `installed`, et la publication du miroir/des diagnostics devient `pending` ou `degraded`. La recherche d'un run exige des SHAs épinglés : ne pas sélectionner arbitrairement un `latest` incohérent.
