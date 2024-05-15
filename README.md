# GouvX

GouvX est un assistant virtuel basé sur le site service-public.fr permettant de naviguer la loi française.

Son objectif est de favoriser une meilleure compréhension des sujets traités par le gouvernement, d'encourager la réflexion citoyenne et de faciliter l'accès à l'information. En mettant en œuvre des modèles de langage avancés, GouvX aspire également à démontrer l'utilité démocratique de ces technologies émergentes.

Ce dépot contient tout le nécessaire pour recréer son propre assistant en local


# GouvX crawler

Ce repo contient les araignées utilisées sur le site GouvX. C'est la première étape de la chaine de traitement.

Les araignées se "promènent" sur les pages du gouvernement et vont extraire les informations pour alimenter la base de données de gouvx.
Chaque araignée est configurée pour un site en particulier. Une liste non exhaustive des sites en *.gouv.fr peut être trouvée [ici](https://www.data.gouv.fr/fr/datasets/listes-des-sites-gouv-fr/).

## Pour lancer le crawler:
```bash
# exemple avec legifrance:

# scraper un url donné:
scrapy shell -s USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36" https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006074069/LEGISCTA000006157551/?anchor=LEGIARTI000006796412#LEGIARTI000006796412

# lancer l'aragnée sur le site:
rm -rf legifrance.csv legifrance.log
scrapy runspider legifrance_scraper.py -o legifrance.csv --logfile legifrance.log

```

## TODO:
- [x] créer un crawler pour service-public.fr
- [x] créer un crawler pour legifrance.gouv.fr
- [ ] créer un crawler pour code.travail.gouv.fr
- [ ] créer un crawler pour vie-publique.fr
- [ ] lancer les crawlers régulièrement pour vérifier les mises à jour


# GouvX API

Code source de l'API [GouvX](https://www.gouvx.fr/) faisant le lien entre l'utilisateur, la base de donnéés et le LLM.  
Ce service est appelé directement par l'[interface utilisateur](https://github.com/GouvX/gouvx.github.io).  

Le déploiement est automatique sur la branche `main` grâce au Dockerfile

Pour tester l'API avec curl:
```sh
curl -X POST -d "q=Comment payer ses impots ?" -d "h=null" http://api.gouvx.fr/ask/
```
# Site gouvx.fr

Code de l'interface web de [gouvx.fr](https://www.gouvx.fr/)

## Déploiement

Le branche main est automatiquement déployée sur [gouvx.fr](https://www.gouvx.fr/) avec GitHub pages

## Détails d'implémentation

L'interface web est une page statique html/css/js basée sur bootstrap. L'url de l'API est spécifié en début de fichier dans chatbot.js

Le premier message envoyé par l'utilisateur provoquera systématiquement une recherche dans la base de données. Le premier message reçu de l'API est systématiquement un json contenant la liste des sources, si il n'y a pas de sources le json sera vide. Ensuite un flux de token est envoyé correspondant à la réponse de l'assistant.

L'historique de conversation doit être passé en paramètre en respectant la convention de nommage de openai (assistant, user)

Pour l'instant il n'y a pas de limite sur la taille des conversation, mais il y a une limite à ma carte de crédit
