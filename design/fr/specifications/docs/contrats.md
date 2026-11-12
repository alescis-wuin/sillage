<!-- Copie de lecture pour Projet ChatGPT. Source originale: sillage-specifications/docs/contrats.md. Mise à jour manuelle requise après changement. -->

# Contrats JSON versionnés de Sillage

[Accueil](../README.md) · [Installateur](installateur.md) · [Synchronisation](synchronisation.md)

## Principes

- Contrats du **produit** : `schema_version: 1` et [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/). Une nouvelle version incompatible exige un **nouveau schéma et une migration explicite** ; ne pas changer silencieusement le sens des champs v1.
- Propriétés supplémentaires interdites dans les principaux objets (`additionalProperties: false`). SHA-256 : préfixe `sha256:` + 64 hexadécimaux minuscules ; SHA Git : OID SHA-1 complet (40 hexadécimaux) dans v1.
- Dates en UTC ISO 8601 ; `run_id` opaque et unique par tentative ; chemins relatifs contrôlés **en outre** au niveau système contre traversées, liens, collisions et permissions.
- Le validateur JSON Schema n'établit ni la fidélité des octets, ni la cohérence inter-dépôts, ni l'authenticité d'une signature, ni l'autorisation d'exécuter une commande.
- Les valeurs Git et empreintes des exemples sont **fictives** et ne prouvent aucune publication ou exécution.

## Registre des contrats du produit

| Donnée | Source de vérité | Schéma |
| --- | --- | --- |
| Paquet ZIP de code | Créé par l'IA, vérifié **localement** | [`package.schema.json`](../schemas/v1/package.schema.json) |
| Politique du projet géré | Fichier **local approuvé**, jamais fourni par le ZIP | [`policy.schema.json`](../schemas/v1/policy.schema.json) |
| Instantané | Synchroniseur local | [`snapshot.schema.json`](../schemas/v1/snapshot.schema.json) |
| Rapport | Préflight/installation locale, si base fiable | [`run-report.schema.json`](../schemas/v1/run-report.schema.json) |
| Contexte de correction | Diagnostics après publication confirmée du rapport | [`correction-context.schema.json`](../schemas/v1/correction-context.schema.json) |
| `latest.json` | Diagnostics après références réellement confirmées | [`latest.schema.json`](../schemas/v1/latest.schema.json) |

Les [exemples produit](../examples/v1/) décrivent des événements fictifs cohérents : un run antérieur réussi puis un échec de compilation sur une candidate non installée. L'exemple de politique v1 utilise des contrôles de lint/formatage/compilation, **aucune commande de test unitaire**.

## Identifiants et champs exacts

- `package_id` est le SHA-256 **des octets du ZIP**, calculé hors manifeste, et peut correspondre à plusieurs `run_id` ; en cas d'ambiguïté, identifier la tentative par `run_id`.
- La base du paquet est `base.snapshot_id` avec `base.mirror_commit`, représentative de l'état de travail local autorisé, même non commité.
- La candidate réellement testée apparaît dans le rapport sous **`candidate.commit`** ; dans le contexte de correction, son identifiant est **`tested_code.commit`**, éventuellement `null` si la candidate n'existe pas.
- L'état réel sur lequel préparer le correctif est **`fix_base.snapshot_id`** et **`fix_base.mirror_commit`**, avec `fix_base.package_installed` ; ce n'est pas la candidate échouée supposée installée. **`fix_base` n'est pas un champ du paquet ZIP.**
- Le paquet correctif accepte les champs facultatifs **`supersedes`** (SHA du ZIP remplacé) et **`fixes_run_id`** lorsque leurs valeurs sont connues ; aucun autre champ de correction n'est ajouté arbitrairement.
- Les SHAs Git désignent des commits exacts, jamais seulement le dernier état d'une branche mouvante.

## Amorçage des diagnostics

`run-report.schema.json` exige `base_snapshot`. Si le ZIP est rejeté avant d'établir cette base, **ne pas fabriquer de rapport JSON v1** : enregistrer `runs/<run-id>/rejection.md` avec les seuls faits connus, puis le publier dans les diagnostics privés si possible. Ce texte ne constitue pas un nouveau contrat JSON.

`latest.schema.json` exige `latest_run` : avant un premier **vrai run publiable**, exposer seulement l'instantané et `AI_START_HERE.md`, sans `latest.json` fictif. Ne pas pointer `latest_run` sur `rejection.md`. `correction-context.schema.json` exige `diagnostics.commit` : créer le contexte à partir d'un rapport publié **à un commit déjà confirmé**, sans auto-référence.

L'installation réussie et la synchronisation distante sont des faits distincts : un push privé `pending` ne change pas rétroactivement `installed` en échec.

## Limites du contrat de vérification v1

`policy.schema.json` décrit des commandes génériques (`argv`) et requiert au moins une commande dans `standard` **et** `full`. Il ne classe pas les commandes par type et ne peut pas garantir seul l'absence de tests unitaires transitifs. La [politique de contrôles](installateur.md) interdit donc **au programme d'exécution automatique** d'appeler des commandes contenant ou déclenchant des tests unitaires ; chaque commande composite doit avoir été auditée et approuvée localement. Ne pas utiliser de commande placebo. Une politique vide exige une **évolution versionnée ultérieure** du contrat plutôt que la déformation de v1.

Aucun champ de politique ne remplace l'**accord local d'installation**, ni l'accord distinct nécessaire à la création/exécution **manuelle** de tests unitaires. `full` n'est jamais exécuté implicitement.

## Contrat distinct du développement de Sillage

Le ZIP d'amorçage d'une **phase de développement de Sillage** n'est **pas** un paquet de code à installer chez un utilisateur. Son [schéma spécifique](../schemas/development/v1/phase-start.schema.json) et son [exemple](../examples/development/v1/phase-start.json) sont séparés des six contrats produit v1. Il peut décrire des branches, des issues et une fiche SMART anglaise, mais **ne transporte aucune commande libre, aucun droit d'accès ou autorisation d'écriture**. Son exécuteur est un outil local distinct, avec approbation préalable des opérations mutantes. Voir [Conduite des phases](conduite-phases.md).
