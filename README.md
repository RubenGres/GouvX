# GouvX API

Code source de l'API [GouvX](https://www.gouvx.fr/) faisant le lien entre l'utilisateur, la base de donnéés et le LLM.  
Ce service est appelé directement par l'[interface utilisateur](https://github.com/GouvX/gouvx.github.io).  

Le déploiement est automatique sur la branche `main` grâce au Dockerfile

Pour tester l'API avec curl:
```sh
curl -X POST -d "q=Comment payer ses impots ?" -d "h=null" http://api.gouvx.fr/ask/
```
