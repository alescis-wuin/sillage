<!-- Copie de lecture pour Projet ChatGPT. Source originale: sillage-specifications/docs/developpement.md. Mise à jour manuelle requise après changement. -->

# Sillage — standards de développement et structure du code source

[Accueil](../README.md) · [Git et GitHub](git-github.md) · [Conduite des phases](conduite-phases.md)

## Champ d'application et langues

Ce document régit **la construction du programme Sillage**, non les conventions des projets que Sillage traitera. Les spécifications et instructions remises aux IA restent **entièrement en français**. Dans le dépôt source de Sillage, les identifiants, noms de branches/tags, titres et corps de commits/PR/issues, commentaires et documentation technique du code sont **en anglais**. Les documents de conception français sont regroupés et explicitement identifiés, par exemple sous `design/fr/` ; cette zone est une exception assumée à la règle anglaise du dépôt. Les modèles `SMART.fr.md` et `SMART.en.md` sont des traductions équivalentes ; leur emplacement et leurs usages diffèrent.

Ne pas convertir les spécifications françaises en anglais par défaut ni maintenir deux copies complètes de chaque document technique. Le README du **dépôt source** est en anglais ; le README du **présent dossier de spécifications** reste en français.

## Qualité et séparation des responsabilités

- **Clean Code** : noms descriptifs et cohérents, fonctions centrées sur une tâche, erreurs explicites, comportement observable et chemins de données faciles à suivre.
- **Clean Architecture pragmatique** : la logique métier ne dépend ni des commandes CLI, ni des API GitHub, ni du transport réseau, ni de détails de présentation. Les adaptateurs convertissent les entrées/sorties ; aucune couche ou interface sans avantage concret.
- **SOLID appliqué avec discernement** : responsabilité unique en priorité ; extension et injection de dépendances seulement lorsqu'un besoin réel les justifie. Éviter les hiérarchies de classes et fabriques de convenance.
- **Modules spécialisés** : séparer au minimum CLI, contrats/validation, instantanés, Git et GitHub, ZIP/candidate, vérification, installation, diagnostics, publication et orchestration de phase lorsque ces fonctions existent. Ne pas centraliser tout le comportement dans un script monolithique.
- **Dépendances minimales** : préférer les bibliothèques standard et les outils déjà présents ; une nouvelle dépendance nécessite une justification pratique.
- **Changements circonscrits** : ne pas refactorer les modules étrangers au périmètre ; ne pas introduire de framework de test, de service ou de configuration générique anticipant plusieurs OS/projets.

## Arborescence cible indicative

L'organisation exacte et les extensions de fichiers suivent le langage effectivement choisi en P0. La structure ci-dessous fixe des **responsabilités**, pas l'obligation de créer des répertoires vides :

```text
sillage/                         # dépôt source GitHub, exemple
├── README.md                    # anglais : installation et usage
├── design/fr/                   # spécifications/roadmap/décisions pour l'IA, français
├── docs/
│   ├── architecture/            # documentation technique anglaise
│   ├── development/             # conventions anglaises du dépôt
│   └── phase-XX/
│       ├── SMART.md             # traduction anglaise approuvée
│       └── SUMMARY.md           # bilan anglais du lot
├── src/sillage/                 # exemple de package, à adapter au langage
│   ├── cli/                     # arguments et présentation
│   ├── core/                    # règles métier, contrats et états
│   ├── integrations/            # Git, GitHub, filesystem, réseau
│   ├── verification/            # validations déterministes et sandbox
│   └── workflows/               # coordination, sans logique métier dupliquée
├── templates/                   # modèles nécessaires à l'outillage
└── .github/                     # modèles d'issues/PR ; aucun workflow Actions
```

Les fichiers du dépôt réel n'ont pas besoin de recopier l'arborescence des *spécifications* de cette archive. Créer un module uniquement lorsqu'une responsabilité existe et le conserver cohésif.

## Nommage

- Dossiers et fichiers : forme idiomatique du langage (`snake_case` pour modules Python, `kebab-case` pour ressources et documents si approprié) ; choisir une convention par type et la documenter lors de P0.
- Fonctions et variables : termes métier descriptifs en anglais ; fonctions à verbe pour les actions, constantes selon les conventions du langage ; pas d'abréviations ambiguës.
- Une interface publique ne doit pas exposer des noms qui diffèrent des schémas de données existants (`tested_code.commit`, `fix_base.snapshot_id`, etc.).
- Les commentaires expliquent les contraintes, risques et raisons **non évidentes**, pas le détail manifeste de l'instruction suivante ; les API non triviales possèdent une documentation concise en anglais.
- Ne pas confondre les répertoires `design/fr/` (instructions de l'IA) et `docs/` (documentation anglaise du code).

## Makefile du dépôt source (obligatoire en P0)

P0 **DOIT** fournir un `Makefile` à la racine du **dépôt source de Sillage**. Il simplifie les opérations locales et délègue les contrôles aux mêmes scripts spécialisés que les hooks ; il ne remplace ni la politique des projets gérés ni le préparateur de phases. Vérifier la présence de Make, son accessibilité depuis le terminal utilisé et sa compatibilité avec les recettes réellement retenues sur l'hôte pilote.

- **Cibles minimales réellement utilisables en P0 :** `help` pour exposer les commandes, `hooks-install` pour installer explicitement les hooks versionnés et `phase-start` dès que le préparateur local fonctionne. Les opérations mutantes de `phase-start` conservent leur propre consentement explicite : invoquer Make ne constitue pas une autorisation Git/GitHub.
- **Cibles conditionnelles :** `check`, `lint`, `format-check`, `syntax` et `build` seulement lorsqu'un contrôle réel, pertinent et exécutable existe. Ne pas créer de cible fictive, de succès par défaut ou de cible d'anticipation. `check` n'agrège que les validations automatiques autorisées et disponibles.
- **Effets et erreurs :** `format-check` vérifie sans modifier ; les commandes propagent leurs codes d'échec, sans les masquer. Les recettes restent courtes, en anglais, sans script monolithique ni accès distant implicite ; Git/`gh` et tout effet externe nécessitent l'autorisation applicable.
- **Tests :** aucune cible, y compris composite ou de compilation, ne déclenche automatiquement de tests unitaires, même transitivement, ni de suite E2E. Les dépendances réelles des commandes sont examinées avant activation.

P0 contrôle les seules cibles créées, dont leur comportement en cas d'échec pertinent. Les cibles qui nécessitent du code futur sont ajoutées durant la phase concernée, et non simulées pendant P0. Les exemples `make` de la politique d'un **projet utilisateur** ne définissent pas le Makefile du dépôt source.

## Contrôles de qualité

Les vérifications rapides de conventions, lint, formatage en mode contrôle, syntaxe, validation JSON et compilation sont autorisées automatiquement lorsqu'elles sont adaptées au langage et configurées de façon sûre. Une commande de formatage modifiant les fichiers ne doit pas opérer silencieusement dans un hook de vérification : elle est exécutée explicitement avant le contrôle.

**Tests unitaires :** n'en concevoir que si leur nécessité est démontrée et après accord explicite du mainteneur ; ne jamais les lancer automatiquement par hook, compilation, préflight, Skill ou correction. Une exécution ponctuelle exige un accord distinct et explicite. **Tests E2E :** aucun projet, suite, dépendance ou exécution E2E à introduire. Les démonstrations manuelles des parcours requis par les critères d'acceptation ne constituent pas une suite E2E automatisée.

Les commandes composites (`make`, scripts de build, gestionnaires de tâches) doivent être examinées pour garantir qu'elles n'appellent pas transitivement des tests unitaires. L'absence d'une garantie suffisante bloque l'exécution automatique de la commande concernée. Ne jamais substituer de tests factices à un profil invalide.

Les contrôles réussis ne sont pas répétés à entrée et paramètres inchangés sans obligation, modification pertinente ou doute concret. La portée de validation correspond au risque réel du changement ; ne pas ajouter de suite générale sans besoin.
