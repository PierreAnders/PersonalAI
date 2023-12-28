# Utiliser une image de base avec Python
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers requis dans le conteneur
COPY . /app/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port sur lequel l'application Flask écoute
EXPOSE 5000

# Définir la commande pour exécuter l'application lorsqu'un conteneur est démarré
CMD ["flask", "run", "--host=0.0.0.0"]
