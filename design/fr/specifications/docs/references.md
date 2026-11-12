<!-- Copie de lecture pour Projet ChatGPT. Source originale: sillage-specifications/docs/references.md. Mise à jour manuelle requise après changement. -->

# Références techniques de Sillage

[Accueil](../README.md)

Ces sources étayent les primitives utilisées ; elles ne constituent pas une certification de l'architecture complète, qui n'est pas encore implémentée.

- **JSON Schema Draft 2020-12** : https://json-schema.org/draft/2020-12/
- **Git patch (`git apply --check`, chemins)** : https://git-scm.com/docs/git-apply
- **Git worktree** : https://git-scm.com/docs/git-worktree
- **Commit et signatures (`git commit -S`)** : https://git-scm.com/docs/git-commit
- **Tags annotés signés (`git tag -s`)** : https://git-scm.com/docs/git-tag
- **Push, `--atomic`, dangers de `--mirror`** : https://git-scm.com/docs/git-push
- **Permissions GitHub App et sélection des dépôts** : https://docs.github.com/en/apps/using-github-apps/installing-a-github-app-from-a-third-party
- **Capacités effectives d'une GitHub App** : https://docs.github.com/en/apps/using-github-apps/authorizing-github-apps
- **Git LFS et fichiers pointeurs** : https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage

Les fonctionnalités d'un connecteur GitHub dans ChatGPT dépendent des permissions effectivement accordées et des outils disponibles dans l'environnement ; les schémas ne garantissent pas qu'il saura cloner ou compiler un dépôt privé.

## Développement du dépôt source Sillage (distinct du produit)

- **Branches protégées et contraintes des commits de merge locaux** : https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- **Disponibilité et configuration des protections** : https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule
- **Signatures de commits et de tags** : https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification
- **Fusion locale signée (`git merge --no-ff -S`)** : https://git-scm.com/docs/git-merge
- **Hooks locaux et leurs limites** : https://git-scm.com/docs/githooks
- **GitHub CLI — sous-issues (`gh issue create --parent`)** : https://cli.github.com/manual/gh_issue_create
- **GitHub CLI — fermeture explicite d'issue** : https://cli.github.com/manual/gh_issue_close
- **GitHub CLI — PR** : https://cli.github.com/manual/gh_pr_create

Les protections GitHub dépendent de la configuration et des permissions réellement disponibles. En particulier, la règle « PR obligatoire » peut bloquer le push d'une fusion localement signée ; une règle d'historique linéaire interdit les commits de merge. P0 doit vérifier la compatibilité effective **avant** d'adopter une règle prétendument protectrice.
