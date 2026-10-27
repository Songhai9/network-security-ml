# Publication de l'image dans ECR avec GitHub OIDC

La cible préparée à partir de la configuration AWS locale est le compte
`429502077256`, la région `eu-north-1` et le dépôt ECR privé `networksecurity`.
Le rôle GitHub est `networksecurity-github-ecr-push`.

## Première configuration AWS

Depuis la racine du projet, se connecter avec une identité AWS existante disposant
du droit de créer un dépôt ECR, un fournisseur OIDC et un rôle IAM. Cette identité
d'administration reste locale ; le workflow n'en reçoit pas les permissions.

```bash
aws login
python3 deployment/bootstrap_ecr.py
```

Si l'identité utilise IAM Identity Center, remplacer `aws login` par sa commande
`aws sso login --profile PROFIL` et lancer le script avec `AWS_PROFILE=PROFIL`.
AWS CloudShell peut aussi lancer le script depuis une copie de ces fichiers : il
utilise la session console, sans connexion CLI supplémentaire.

Le script vérifie le numéro de compte avant de créer quoi que ce soit. Il crée
les ressources manquantes et attache la politique ECR limitée à ce dépôt. Il
refuse de remplacer une règle de confiance existante différente. Ne lancer le
workflow de publication qu'une fois le script terminé avec succès.

## Publication

Committer et pousser Dockerfile, .dockerignore, requirements.txt, scripts/,
deployment/ et .github/workflows/main.yml. Un push sur main lance le workflow.
Une pull request construit et vérifie l'image ; elle ne la publie pas.

Le workflow construit une image Linux amd64, démarre l'API et teste /docs puis
un POST /predict avec un CSV d'une ligne. Après ces contrôles, sur main, il
échange le jeton GitHub OIDC contre des identifiants AWS temporaires, se connecte
au registre ECR et publie exactement l'image vérifiée. Aucun secret GitHub AWS
n'est à créer. L'ARN du rôle et les noms de région/dépôt ne sont pas des secrets.

Le tag comprend le SHA du commit, l'identifiant du run GitHub et son numéro de
tentative. Il reste unique même lors d'une relance et fonctionne avec les tags
ECR immuables. L'URI publiée figure dans le résumé du run GitHub Actions.

## Règle de confiance OIDC

Le dépôt GitHub a été créé le 26 octobre 2026. La règle préparée utilise le
format actuel du sujet OIDC contenant les IDs immuables, restreint à main :

```
repo:Songhai9@118692197/network-security-ml@1434408614:ref:refs/heads/main
```

Si les paramètres OIDC du dépôt ont été personnalisés, adapter la règle au sujet
réel. L'ajout d'un `environment:` GitHub change aussi le sujet : il faut alors
adapter la confiance. Conserver les conditions sur l'audience et le dépôt.

## Choix de conteneurisation

- Python 3.12, cohérent avec l'environnement ayant produit les modèles.
- Versions NumPy, SciPy, pandas et scikit-learn identiques à l'environnement local.
- Dépendances Jinja2 et python-multipart déclarées explicitement pour l'API.
- Dossier prediction_output créé même si aucun ancien résultat n'est présent.
- Uvicorn écoute sur 0.0.0.0:8000 dans le conteneur.
- Le contexte Docker est limité au code, au template et aux modèles nécessaires.
  Les fichiers .env, .venv, .git, les anciens artifacts et les logs sont exclus.
- Les deux modèles final_models/ actuellement versionnés sont embarqués ensemble.
- L'AWS CLI reste présente pour les transferts S3 du code d'entraînement.

La publication dans ECR stocke l'image. L'exécution de l'application sur ECS,
EC2 ou une autre plateforme sera une étape suivante avec sa propre identité AWS.
Le rôle de publication ECR ne donne aucun accès S3 au conteneur déployé.

## Vérification finale

Dans GitHub, ouvrir Actions, puis Build and publish to ECR. Vérifier que Build,
Verify API, Authenticate et Publish sont verts. Dans la console ECR eu-north-1,
ouvrir networksecurity : le tag du run et son digest doivent être présents.

Sources officielles :
- https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws
- https://docs.github.com/en/actions/reference/security/oidc
- https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-push-iam.html
