<!-- Copie de lecture pour Projet ChatGPT. Source originale: sillage-specifications/docs/git-github.md. Mise à jour manuelle requise après changement. -->

# Sillage — conventions Git et GitHub du dépôt source

[Accueil](../README.md) · [Standards](developpement.md) · [Phases](conduite-phases.md)

## Frontière de responsabilité

Ces conventions régissent **exclusivement le dépôt source de Sillage** et les opérations du mainteneur. Elles ne sont **pas** imposées par défaut aux projets utilisateurs gérés par le produit Sillage. L'IA dispose d'un accès GitHub en **lecture seule** au dépôt source, épinglé à une branche et un SHA précis ; aucun jeton d'écriture ni clé de signature n'entre dans une conversation, un ZIP ou une candidate.

Le mainteneur dispose de Git et de `gh` localement. `gh` appelle les services/API GitHub avec les permissions locales : ce n'est pas une exécution hors GitHub. Les opérations mutantes sont explicitement autorisées localement et leur réussite est confirmée par Git/GitHub, non présumée.

## Branches et versions

- Branches permanentes : **`main`** (versions approuvées) et **`develop`** (intégration des lots). **Pas de `testing`**, ni de Gitflow complet ni de CI/CD.
- Branche de travail : `branch_type/branch_name`. Types initiaux : `feature`, `fix`, `refactor`, `docs`, `chore` ; **`feature`, jamais `feat`**.
- Partie `branch_name` : anglais ASCII minuscules, mots séparés par `-`, préfixée du lot et d'un descriptif, par exemple `feature/p02-package-install`. Ne pas utiliser d'espaces ou de lettres accentuées.
- **Une branche et une PR par phase P1–P4**. Les deux étapes donnent lieu chacune à un **commit principal signé**, pas à une PR distincte. Des commits correctifs supplémentaires sont possibles s'ils sont indispensables, explicites et signés ; ils ne remplacent pas les deux jalons d'étape.
- Tags d'étape : `step/p02-e01`, `step/p02-e02` ; **un tag annoté signé personnellement par étape validée**, pointant vers le commit de l'étape. Ils identifient un commit, pas une branche, et ne sont ni réutilisés ni déplacés. Les tags ne sont poussés qu'après l'accord applicable et confirmation des objets signés.
- Versions officielles : `vMAJOR.MINOR.PATCH`, tags annotés signés **sur `main`**, uniquement après décision de publication ; ne pas tagguer automatiquement chaque commit. En développement initial, `v0.x.y` est possible.
- `main` est alimentée par intégration contrôlée de `develop` avec signature personnelle, sans fusion GitHub produisant un commit signé par un tiers. La promotion ne crée pas de PR par étape.

## Messages de commit — anglais obligatoire

En-tête exact : `branch_type (branch_name) : title`, avec **un espace de chaque côté des deux-points**. `branch_name` correspond à la partie après `/`. Pour un commit de fusion ou d'amorçage, utiliser un type autorisé (par exemple `chore`) et un identifiant de contexte explicite (`p02-package-install`, `bootstrap`), avec un pied de références approprié. Titre en anglais, impératif, concis.

Corps : une phrase courte décrivant l'objectif, puis une énumération des changements substantiels. Pied : références précises aux issues, phase, étape et, si pertinent, au paquet ou à la décision. Exemple :

```text
feature (p02-package-install) : Validate incremental bundles

Add the local candidate validation workflow.

- Reject unsafe ZIP members and mismatched snapshots.
- Preserve the user's Git index during installation.

Refs: #42
Phase: P02
Step: E02
```

Les commits ne doivent pas inclure de secrets, chemins sensibles ni fausses attestations. Les commits techniques du **miroir** suivent leurs propres trailers (`AI-Package`, `Run-ID`, etc.) et ne sont pas soumis à ces conventions de messages du dépôt source.

## Chronologie et signatures personnelles

Pour chaque phase P1–P4 :

1. Depuis `develop` à SHA connu, **vérifier avant toute ouverture Git/GitHub** la correspondance des critères `ACxx`, périmètres et exclusions entre la fiche SMART française approuvée et sa traduction anglaise ; faire approuver leur équivalence de sens par le mainteneur. Créer ensuite la branche de phase ; **premier commit** signé : **uniquement** `docs/phase-XX/SMART.md` (version anglaise approuvée), sans ajouter d'autres fichiers.
2. Réaliser les étapes ; chacune donne un commit principal signé. Créer le tag signé de l'étape terminée ; sa publication distante requiert un accord distinct.
3. Mettre à jour **avant** le bilan les spécifications FR et l'état de la roadmap nécessaires à la transmission ; ces modifications appartiennent aux commits de travail précédents, pas au commit de clôture.
4. **Dernier commit de conception** signé : **uniquement** `docs/phase-XX/SUMMARY.md` (bilan anglais), sans autre fichier. Une correction ultérieure du code exige de reprendre la clôture ; ne jamais réécrire sans trace les deux jalons publiés.
5. Ouvrir **une PR de phase** vers `develop`. Le mainteneur examine sa checklist ; aucune revue de code externe n'est obligatoire.
6. **Décision de fusion exclusivement humaine** ; fusionner **localement** avec un vrai commit de fusion personnel signé (par exemple `git merge --no-ff -S`) après vérification de l'identité et du diff ; vérifier signature et parents, puis pousser sans force. **Interdire** les boutons GitHub de fusion, squash et rebase, et toute fusion produisant un commit signé par GitHub ou un tiers.
7. Vérifier que GitHub constate la fusion de la PR. Fermer ensuite explicitement les deux sous-issues, puis l'issue parente, avec `gh issue close` et uniquement après confirmation de leur achèvement. Ne pas supposer qu'une PR vers `develop` ferme les issues automatiquement.

La fusion de `develop` vers `main`, lorsqu'autorisée, est soumise aux **mêmes règles de signature personnelle**. L'index Git réel et les changements non concernés doivent rester intacts ; aucun reset destructif ni push forcé.

Une signature « Verified » de GitHub ne prouve pas à elle seule que **ta** clé a signé le commit. La vérification doit identifier la clé/identité attendue, localement et selon les informations vérifiables disponibles.

## Issues, PR et labels

- **Une issue par phase et deux sous-issues**, une par étape. P0 est une exception d'amorçage : la hiérarchie pourra être créée pendant sa préparation, sans prérequis circulaire.
- L'issue parente décrit objectif, périmètre, exclusions et critères du lot ; chaque sous-issue décrit un résultat d'étape, des critères observables et ses dépendances. **Tous les contenus GitHub, y compris commentaires et échanges dans les issues/PR, sont en anglais.**
- Labels minimaux : `type:feature`, `type:fix`, `type:refactor`, `type:docs`, `type:chore`, plus `phase:0` à `phase:4` selon le besoin. Ne pas ajouter un système de statuts redondants.
- La PR de phase utilise le [modèle anglais](../templates/github/PULL_REQUEST.md) avec cases « Included changes » et « Before merging », résultats réels des contrôles, liens vers les issues et mention des décisions ouvertes. Cocher n'est pas prouver.
- Ne pas imposer de revue de code, d'approbation par un tiers, de CI ni de status check inexistant. Pas de PR par étape.
- Les issues restent ouvertes tant que la PR n'est pas **réellement** fusionnée et que les critères ne sont pas confirmés ; fermeture manuelle via `gh`, après vérification, jamais sur simple intention de merge.

## Mise en place des modèles dans le dépôt source

P0 copie/adapte les modèles du présent dossier : `templates/github/ISSUE_PHASE.md` vers `.github/ISSUE_TEMPLATE/phase.md`, `ISSUE_STEP.md` vers `.github/ISSUE_TEMPLATE/step.md`, et `PULL_REQUEST.md` vers `.github/PULL_REQUEST_TEMPLATE.md`. Les modèles d'issues possèdent leurs métadonnées de sélection GitHub ; les labels sont appliqués par l'outillage local à la création effective des issues. Les formulaires ne doivent ni déclencher de GitHub Actions ni produire de validations fictives.

## Branch protections et contraintes de GitHub

En P0, vérifier les fonctionnalités **effectivement disponibles** selon le plan et la visibilité du dépôt. Rechercher : signatures vérifiées, interdiction des suppressions et force-push, restriction d'écriture à l'identité autorisée. Ne pas exiger l'historique linéaire (`--no-ff` doit rester possible) ni revue/CI. Une règle exigeant des PR peut **empêcher le push d'un merge signé localement** sans exception ; choisir et tester une configuration compatible avant d'annoncer la protection active. Les hooks locaux ne constituent pas une protection serveur et peuvent être contournés.

Test de faisabilité de P0 : produire dans un dépôt temporaire isolé un commit et un merge personnels signés, puis vérifier concrètement le chemin autorisé vers les branches protégées. **Ne pas faire de push expérimental vers `main`/`develop` réels sans autorisation.** Si la plateforme ou les permissions ne permettent pas de garantir la fusion locale personnellement signée, **bloquer cette opération** et documenter la limite ; ne jamais revenir à une fusion GitHub non personnelle.

## Hooks et contrôles

Les hooks sont versionnés via une configuration reproductible et installés localement de manière explicite : Git ne distribue pas automatiquement les hooks actifs depuis un clone. Leur logique est modulaire, sûre et rapidement exécutable.

| Déclencheur | Vérifications automatiques autorisées |
| --- | --- |
| `pre-commit` | Nom de branche, intégrité des fichiers, formatage **en mode contrôle**, lint, validation statique ciblée |
| `commit-msg` | En-tête/corps/pied, références de phase/étape ; exception documentée pour les commits de fusion et P0 |
| `pre-push` | Vérification de signatures, références/tags, syntaxe ou compilation pertinente non déjà vérifiée |
| Avant ouverture de PR | Synthèse des contrôles applicables, vérifications manuelles des critères et état Git |

**Interdit dans tous les hooks : tests unitaires, tests E2E, suites globales implicites, commandes arbitraires issues du ZIP et répétition de contrôles déjà réussis sans changement pertinent.** Les commandes transitives (scripts `build`, `make`, etc.) doivent être auditées ; un nom ne suffit pas à prouver qu'il n'exécute pas de tests. Les tests unitaires ne sont créés que si strictement nécessaires et approuvés explicitement ; leur exécution, lorsqu'elle est exceptionnellement autorisée, est toujours une action distincte et manuelle. Aucun test E2E n'est prévu.

Aucune GitHub Action ou chaîne CI/CD n'est nécessaire. Désactiver les workflows non souhaités et ne pas rendre obligatoires des contrôles distants inexistants.
