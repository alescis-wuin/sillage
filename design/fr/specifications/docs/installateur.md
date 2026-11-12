<!-- Copie de lecture pour Projet ChatGPT. Source originale: sillage-specifications/docs/installateur.md. Mise à jour manuelle requise après changement. -->

# Sillage — installateur local fixe et contrôles

[Accueil](../README.md) · [Parcours](parcours.md) · [Contrats](contrats.md) · [Standards](developpement.md)

## Interface et autorité

L'installateur est **indépendant des ZIP** et des Skills. Il reçoit des chemins explicites, utilise une politique locale approuvée et ne crée aucun commit public sans autorisation distincte :

```text
apply-package --project <chemin-local> --bundle <livraison.zip>
```

Cette commande est une interface attendue, **pas un programme livré** dans le dossier de spécifications. L'installateur de ZIP du produit n'est pas le préparateur local de phase décrit dans [Conduite des phases](conduite-phases.md).

## Format ZIP v1

```text
livraison.zip
├── manifest.json
├── patches/change.diff  # uniquement si référencé par le manifeste
└── payload/...          # uniquement si référencé par le manifeste
```

- `manifest.json` est contrôlé avec [`package.schema.json`](../schemas/v1/package.schema.json). Il déclare la base `snapshot_id`/`mirror_commit`, les opérations et les empreintes de charge utile. `supersedes` et `fixes_run_id` sont facultatifs et n'autorisent aucune opération supplémentaire.
- Chaque patch Git unifié cible exclusivement les chemins déclarés ; chaque fichier complet doit correspondre à son empreinte déclarée.
- **Seuls** `manifest.json` et les fichiers `payload.file` explicitement déclarés sont autorisés ; les répertoires implicites ne deviennent pas du code exécutable. Le manifeste n'accepte pas de commandes shell ni de privilèges.
- `package_id` = SHA-256 des **octets exacts du ZIP reçu**, calculé hors manifeste. Les membres supplémentaires, liens, archives à chemins dangereux, collisions, doublons, décompression excessive et entrées non régulières sont refusés.

## Contrôles obligatoires

1. **Archive et manifeste** : schéma/version, chemins relatifs canoniques, structure, nombre/tailles plafonnés, absence de symlink et de membre non déclaré, collisions Unicode/casse, sécurité de l'extraction.
2. **Intégrité et base** : SHA-256 des charges, `before_sha256`/`after_sha256`, unicité des changements, conformité de `snapshot_id` et `mirror_commit` aux octets de l'état local observé.
3. **Candidate isolée** : reconstituer **une candidate exacte par paquet** sur copie éphémère, y appliquer patch/fichiers sans hooks ni filtres Git non autorisés, vérifier les octets obtenus et enregistrer l'identifiant de l'arbre réellement testé ; `proposals/*` ne remplace jamais `work`.
4. **Préflight local** : exécuter uniquement les vérifications statiques, syntaxiques et de compilation applicables du profil `standard` connu **hors ZIP**, avec bornes de temps, isolation et absence d'appels transitifs aux tests unitaires. `full` n'est jamais implicite. En cas de contrôles requis indisponibles, refuser `ready`.
5. **Installation consentie** : recueillir une approbation locale, recontrôler le contenu de base juste avant écriture, préserver l'index et les modifications étrangères, sauvegarder les chemins ciblés et restaurer lorsque c'est sûr ; consigner tout état partiel sans annoncer `installed`.

## Isolation vérifiable (préflight de code non fiable)

Une compilation ou une commande de build peut exécuter du code arbitraire. Le simple fait de lancer une commande dans un sous-répertoire temporaire **ne constitue pas une isolation**.

Le mécanisme retenu sur l'hôte pilote DOIT assurer et démontrer :

- Une copie candidate distincte du dépôt de travail réel, sans accès en écriture au projet original ; confinement des chemins accessibles, y compris via liens, chemins relatifs et variables d'environnement.
- Aucun secret ou identifiant d'écriture Git/GitHub injecté (`HOME`, variables de configuration Git, agent SSH, fichiers de credentials, tokens, sockets), aucun accès à une clé de signature du mainteneur.
- Hooks Git, filtres, scripts d'installation et exécutions implicites non autorisés neutralisés ; les commandes de vérification ne peuvent pas modifier les dépôts privés/publics par des droits récupérés sur l'hôte.
- Accès réseau désactivé par défaut pour les commandes candidates lorsque possible ; toute exception nécessaire est définie et contrôlée hors ZIP, sans accès aux identifiants de publication.
- Contrôles de frontières non destructifs sur l'environnement réellement retenu, avec résultats enregistrés (ex. tentative d'écriture sur un chemin témoin interdit, absence de credentials exposés **sans lire de secrets réels**). Le mécanisme doit être réellement disponible sur l'OS pilote.

**Si une commande obligatoire ne peut pas être exécutée avec ces garanties, son résultat est `blocked` ou `unavailable` et l'installation ne reçoit pas `ready`.** Ne pas prétendre à une isolation par simple configuration déclarative. La validation de la sécurité de cette frontière est distincte de la compilation du code candidat.

Le v1 refuse les symlinks, sous-modules, Git SHA-256, changements de mode non représentables et fichiers non réguliers. Les nouveaux fichiers ont le mode `100644`. Les évolutions LFS et multi-OS ne sont pas des conditions de la première version.

## Politique de vérification et tests

| Catégorie | Exécution automatique normale |
| --- | --- |
| Structure ZIP, schéma, intégrité et base | Obligatoire |
| Lint, formatage **en mode contrôle**, syntaxe, compilation, analyse statique pertinente | Autorisée si configurée, isolée et applicable |
| Tests unitaires | **Interdite**, même ciblée ou transitive |
| Tests E2E | **Interdite** ; aucune suite E2E prévue |
| Profil `full` | Jamais implicitement exécuté ; autorisation distincte, sans pouvoir d'imposer des tests unitaires |

La création **et** l'exécution manuelle d'un test unitaire nécessitent une nécessité avérée et une approbation explicite du mainteneur. L'exécution approuvée ne devient pas un hook ni un préflight automatique. Les commandes composites (`make build`, scripts du langage) doivent être examinées pour exclure des tests transitifs ; si cette propriété est incertaine, **bloquer** la commande en exécution automatique.

`policy.schema.json` v1 décrit des listes de commandes `argv` sans catégorie sémantique et impose une liste non vide pour `standard` et `full`. En conséquence, **le schéma seul ne peut pas garantir** l'interdiction des tests unitaires ni représenter un projet sans aucune commande. L'exécuteur DOIT refuser une configuration automatique non auditée ; un projet sans contrôle pertinent exige une évolution **versionnée** du contrat, pas une commande factice. L'[exemple de politique](../examples/v1/policy.json) ne contient aucun test unitaire.

Ne jamais relancer une vérification déjà réussie sur la même candidate et les mêmes paramètres sans obligation ou doute concret. Une correction automatique ne peut pas dépasser le plafond local défini dans [Compétences IA](competences.md) ; une nouvelle tentative doit viser la cause et comporter un changement pertinent.

## Verdicts et diagnostics

- `ready` : intégrité et **tous les contrôles requis** réussis sur la candidate exacte, dans une isolation vérifiée.
- `failed` : contrôle réellement exécuté et échoué.
- `blocked` : archive/base non valide, autorisation insuffisante ou contrôle obligatoire impossible à sécuriser/exécuter.
- `unverified` : vérification facultative non exécutée/indisponible ; **ne pas assimiler à `ready`**.

Un ZIP rejeté avant base fiable donne `runs/<run-id>/rejection.md`, **pas** un faux `run-report`. Un rapport v1 n'est créé que si les champs requis sont connus. Les diagnostics sont publiés après confirmation de leurs références et mis en attente localement si le réseau est indisponible. Un échec de push des diagnostics ou du miroir **n'annule pas** une installation locale réellement réussie ; `installed` et `pending`/`degraded` sont des dimensions distinctes.
