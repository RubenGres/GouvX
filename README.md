# Site gouvx.fr

Code de l'interface web de [gouvx.fr](https://www.gouvx.fr/)

## Déploiement

Le branche main est automatiquement déployée sur [gouvx.fr](https://www.gouvx.fr/) avec GitHub pages

## Détails d'implémentation

L'interface web est une page statique html/css/js basée sur bootstrap. L'url de l'API est spécifié en début de fichier dans chatbot.js

Le premier message envoyé par l'utilisateur provoquera systématiquement une recherche dans la base de données. Le premier message reçu de l'API est systématiquement un json contenant la liste des sources, si il n'y a pas de sources le json sera vide. Ensuite un flux de token est envoyé correspondant à la réponse de l'assistant.

L'historique de conversation doit être passé en paramètre en respectant la convention de nommage de openai (assistant, user)

Pour l'instant il n'y a pas de limite sur la taille des conversation, mais il y a une limite à ma carte de crédit