<!-- Copie de lecture pour Projet ChatGPT. Source originale: sillage-specifications/docs/conduite-phases.md. Mise à jour manuelle requise après changement. -->

# Sillage — conduite des lots de conception et transmission entre conversations

[Accueil](../README.md) · [Git et GitHub](git-github.md) · [Manifeste de préparation](../schemas/development/v1/phase-start.schema.json)

## Distinction essentielle

Ce protocole encadre **le développement de Sillage**. Il ne constitue pas une fonction de l'installateur des projets utilisateurs et ne modifie ni le manifeste ZIP v1 du produit, ni les autorisations Git d'un projet géré. La roadmap détermine les objectifs, périmètres et critères des phases ; le présent document détermine **comment** les mener. Les quatre phases fonctionnelles et leurs huit étapes restent définies dans la roadmap séparée ; **P0** les précède sans constituer une cinquième phase fonctionnelle.

## P0 — pré-phase d'amorçage, un lot limité

**Objectif :** préparer un dépôt source GitHub et son équivalent local utilisables sans dépendre de Sillage encore non développé.

**Inclus :** créer le dépôt et `main`/`develop`, configurer les protections compatibles avec les commits de merge personnellement signés, vérifier Git/`gh` et l'identité de signature, installer les conventions de nommage, l'arborescence et la documentation initiales, modèles GitHub et labels, hooks locaux statiques, **Makefile minimal obligatoire**, accès GitHub en lecture seule pour l'IA, modèles SMART/transmission et préparateur local minimal de phase.

**Exclus :** synchroniseur de projets utilisateurs, miroir `work`, installateur ZIP de code, signature des projets utilisateurs, filewatcher, services permanents, tests unitaires/E2E automatiques, CI/CD, prise en charge multi-OS et orchestration générale.

**Validation observable :** dépôt et branches confirmés ; signatures personnelles de commit, tag et merge vérifiées avec la clé autorisée (sur dépôt temporaire ou opérations approuvées) ; protections GitHub testées au regard d'un merge local signé ; **Make disponible et cibles Make existantes effectivement exécutées, avec échecs non masqués** ; hooks contrôlés sur un exemple conforme et un exemple volontairement invalide, sans lancer de test unitaire ; préparateur rejetant les manifestes incohérents avant toute écriture ; modèles utilisables ; lecture par l'IA d'un SHA exact ; navigation vers les spécifications FR. Un droit, une protection ou une commande non disponible est signalé, jamais supposé fonctionnel.

**Outillage de P0 :** suivre [les règles du Makefile source](developpement.md#makefile-du-dépôt-source-obligatoire-en-p0). Les cibles `help`, `hooks-install` et, après disponibilité de l'outil, `phase-start` restent des points d'entrée minces ; `check`, `lint`, `format-check`, `syntax` et `build` n'existent que pour des vérifications réelles. Pas de tests unitaires ou E2E automatiques, même par appel transitif.

**Anti-doublons :** P0 configure le **dépôt source de Sillage** ; la synchronisation miroir/diagnostics des utilisateurs appartient à P1, le préflight des ZIP utilisateurs à P2, leurs corrections à P3 et leur publication officielle à P4. Aucun de ces composants n'est développé en P0.

## Fiche SMART adaptée, sans T

Chaque lot P1–P4 possède une fiche française de référence pour l'IA et une **traduction anglaise sémantiquement équivalente** pour le dépôt :

- **S — Spécifique :** résultat exact, responsabilités et livrables identifiables.
- **M — Mesurable :** critères d'acceptation observables, éléments de preuve et états attendus.
- **A — Atteignable :** prérequis techniques réellement satisfaits et moyens disponibles.
- **R — Pertinent/réaliste :** contribution au jalon, décisions et limites de la phase.
- **Périmètre et hors périmètre** : sections obligatoires et distinctes, ajoutées aux critères SMART.

**T est volontairement exclu** : aucune date butoir ni échéance fictive n'est créée. Les commits documentaires permettent de mesurer une durée calendaire *a posteriori*, mais ne remplacent pas un suivi des heures réellement travaillées.

Les deux versions possèdent les mêmes IDs de critères (`AC01`, `AC02`, etc.), le même périmètre et les mêmes exclusions. La structure peut être contrôlée mécaniquement ; l'équivalence de sens nécessite une comparaison humaine/IA **approuvée par le mainteneur avant le premier commit SMART**, puis revérifiée avant le bilan si l'une des fiches a changé. Le contrôle de structure ou de JSON seul ne garantit pas le sens. Le texte français, remis aux IA, reste l'autorité de conception ; l'anglais validé est le livrable officiel du dépôt.

## Nouvelle conversation par phase

À l'ouverture de chaque lot, fournir à l'IA : documentation de conception en **français** (roadmap et spécifications), SMART FR, prompt dédié FR, état validé des décisions, références GitHub des issues, SHA exact de `develop` et accès au dépôt source **en lecture seule**. Les fichiers non publiés doivent être fournis explicitement : le connecteur GitHub ne voit pas les commits locaux non poussés.

Un dossier de transfert succinct est suffisant :

```text
phase-XX/
├── README.fr.md         # index et SHA du contexte réellement accessible
├── SMART.fr.md         # critères faisant autorité pour l'IA
├── PROMPT.fr.md        # mandat de conception borné
├── CONTEXT.json         # commits, issues, PR, versions confirmées
└── HANDOFF.fr.md       # décisions et bilan du lot précédent
```

Ce dossier est un **contexte pour la conversation**, pas une entrée exécutable du préparateur local. La roadmap ne doit pas répéter les présentes procédures ni les conventions Git.

## Paquet déclaratif de préparation de phase

Un ZIP de préparation peut être fourni par l'IA :

```text
phase-XX-start.zip
├── manifest.json
└── SMART.en.md
```

Le manifeste suit un contrat **distinct** : [`schemas/development/v1/phase-start.schema.json`](../schemas/development/v1/phase-start.schema.json). Il contient dépôt GitHub cible, SHA attendu de `develop`, nom de branche, issue parente, deux sous-issues, labels, descriptions/critères et profil fixe `phase-start`. Le paquet **ne contient ni script, ni commande shell, ni instructions d'authentification, ni droits accordés par lui-même** ; les membres du ZIP non déclarés sont rejetés. L'anglais SMART est la **seule pièce** destinée au premier commit.

Le préparateur local minimal (`phase start`, nom d'interface conceptuel) valide les chemins et empreintes, le schéma et les données, l'identité Git/`gh`, le dépôt, la branche, le SHA attendu, le caractère propre de l'index et du worktree, les conflits de noms, l'absence de doublons d'issues et la signature. Le profil de contrôles est **défini par l'outil local**, jamais par le ZIP.

**Validations croisées avant toute écriture Git/GitHub :** le schéma vérifie des champs individuellement mais ne garantit pas leurs correspondances. Le préparateur DOIT refuser une phase différente de `P01`–`P04` ; faire correspondre `phase` (`Pxx`), le préfixe `pxx` de `git.work_branch`, `documents.smart_target` (`docs/phase-xx/SMART.md`) et le label `phase:n` de l'issue parente et de chacune des sous-issues ; exiger exactement deux étapes distinctes `E01` et `E02` ; vérifier le dépôt GitHub réellement visé, `develop` et son `expected_head`, les fichiers/membres autorisés et l'absence de collisions avec des branches ou issues préexistantes. Refuser toute contradiction sans créer d'issue, de branche ni de commit. Vérifier sur la version installée de `gh` les options et permissions effectives de création, rattachement, consultation et fermeture des sous-issues natives : aucun lien Markdown ne peut remplacer leur hiérarchie.

**SMART avant le premier commit :** la fiche `SMART.fr.md` de référence, **approuvée et fournie séparément du ZIP** dans le dossier de conception, est indispensable. Avant toute ouverture effective, comparer les identifiants `ACxx`, périmètre, exclusions et critères, puis faire approuver explicitement leur **équivalence sémantique** avec `SMART.en.md` par le mainteneur. En l'absence de cette référence ou d'une approbation d'équivalence, bloquer le démarrage **avant toute écriture Git/GitHub**, notamment avant le premier commit. Une validation structurelle automatique ne remplace pas cette approbation.

Le préparateur présente ensuite les effets externes attendus et exige leur **autorisation explicite** avant toute création d'issue, de branche ou de commit. L'approbation du contenu SMART et l'autorisation des effets Git/GitHub sont deux décisions distinctes.

Après autorisation, il crée les issues : **d'abord l'issue parente**, puis les deux sous-issues avec `gh issue create --parent <numéro-parent>` lorsque cette fonctionnalité est disponible ; il refuse de simuler une hiérarchie non prise en charge. Il confirme pour chaque sous-issue le numéro réellement retourné et son rattachement à la parente, puis mémorise ces IDs réels dans un journal local non sensible ; il prépare la branche et réalise le premier commit signé ne contenant que `docs/phase-XX/SMART.md`. Les labels ne sont créés/modifiés à distance qu'après validation des noms et consentement. Les opérations sont idempotentes autant que possible ; un échec après création partielle produit un état récupérable. **Aucune commande de suppression, `reset --hard`, réécriture d'historique ou push forcé pour « repartir proprement ».** Une phase déjà ouverte n'est pas recréée silencieusement. Les actions GitHub sont effectuées par Git/`gh` local autorisé, jamais par l'IA.

P0 peut être initialisée manuellement, puisqu'elle précède la disponibilité de ce préparateur ; ne pas créer de dépendance circulaire.

## Mode transitoire avant disponibilité de l'installateur Sillage

Pendant P1 et le début de P2, **l'installateur du produit n'existe pas encore**. Dans la nouvelle conversation de phase, l'IA consulte le dépôt source GitHub **en lecture seule à un SHA confirmé** et fournit seulement les fichiers modifiés, un patch ou une archive ordinaire. Les fichiers/commits uniquement locaux doivent être transmis séparément : l'IA ne peut pas les déduire du distant.

Le mainteneur inspecte et applique localement ces modifications avec les outils Git existants, exécute les contrôles autorisés via hooks/Makefile/commandes locales, puis crée le **commit d'étape personnellement signé** et ne pousse la branche qu'après autorisation. Le premier commit SMART, le dernier commit `SUMMARY`, les deux commits principaux d'étape, la PR unique en fin de phase et la fusion locale signée restent obligatoires. **Aucun second installateur, aucun format ZIP v1 du produit imposé pour s'auto-amorcer, aucun droit Git d'écriture pour l'IA.** Ce mode devient facultatif lorsque l'installateur Sillage est réellement opérationnel.

## Réalisation d'une phase

1. **Avant le premier commit** et avant les écritures d'ouverture, vérifier l'état Git, la SMART française approuvée et l'équivalence sémantique approuvée de sa traduction anglaise ; associer ensuite l'issue parente et les deux sous-issues.
2. Réaliser **un lot** avec deux étapes ; un commit principal signé par étape, tags d'étape signés lorsqu'ils sont créés, sans PR distinctes.
3. Appliquer les contrôles statiques et compilation pertinents, jamais de tests unitaires automatiques ni E2E. Tester manuellement les critères fonctionnels nécessaires ; si un test unitaire est envisagé, obtenir séparément l'autorisation explicite pour **sa création et son exécution manuelle**.
4. Après chaque conversation de conception, réconcilier les décisions réellement approuvées avec les spécifications FR, la roadmap FR et les notes de phase ; ne pas inventer des résultats ni valider des modifications seulement proposées. Consigner les SHAs et les états GitHub confirmés.
5. Avant le **dernier commit** de la branche, finaliser les mises à jour de conception (spécifications, décisions et roadmap) et vérifier l'équivalence SMART FR/EN. Puis créer uniquement `docs/phase-XX/SUMMARY.md` en anglais dans le dernier commit de conception signé.
6. Ouvrir une unique PR de phase vers `develop`, remplir sa checklist ; le mainteneur décide et effectue la **fusion personnelle signée en local**. Après confirmation, clôturer les issues via `gh` ; la publication sur `main` reste une décision distincte.

Les commits SMART et SUMMARY contiennent uniquement le fichier spécifié chacun : leurs horodatages donnent la **durée calendaire écoulée** (pauses comprises), pas un temps de travail mesuré. Éviter de réécrire ces commits après leur mise à disposition. Si une correction est nécessaire après le bilan mais avant la fusion, fournir une nouvelle clôture explicite plutôt que falsifier un jalon.

## Transmission de phase et preuves

Le [modèle de transmission français](../templates/phase/HANDOFF.fr.md) enregistre : résultats par critère, périmètre accompli/non accompli, contrôles exécutés avec statut et commande, vérifications non exécutées, limites, décisions approuvées, état de l'isolement et du plafond des corrections, commit de SMART, commits d'étape, commit de bilan, branches, tags, numéros d'issues, état de PR, SHA de fusion/publication **confirmés**, et identifiants nécessaires à la conversation suivante.

**Deux états distincts** :

- **Clôture de conception** : avant fusion, les documents FR et le bilan anglais sont committés ; le bilan ne peut pas indiquer un SHA de fusion futur.
- **Clôture d'intégration** : après fusion, PR et issues sont vérifiées ; les références définitives sont ajoutées au dossier de transmission FR ou à la préparation de la phase suivante, **sans réécrire le dernier commit documentaire** ni introduire un faux SHA.

L'ensemble des décisions utiles doit survivre à la fermeture de la conversation. En particulier, les contraintes de tests unitaires manuels, de fusion personnelle, de limitation des corrections automatiques et d'isolation vérifiable restent des exigences normatives jusqu'à modification explicitement approuvée. Le dossier de conception est mis à jour à la fin de **chaque** conversation de conception de phase, pas seulement à la publication d'une version.

## Politique commune de fin de lot

Une phase est techniquement acceptée quand **ses critères propres** sont réellement satisfaits et documentés ; sa clôture GitHub intervient seulement après fusion personnelle signée et fermeture explicite des issues. Les synchronisations GitHub en attente ou permissions indisponibles ne sont jamais maquillées en succès. Aucun audit, deuxième PR, suite E2E ou campagne de tests redondante n'est ajouté de manière implicite.
