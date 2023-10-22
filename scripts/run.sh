#!/bin/bash

# Instalar Google Chrome
sudo wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
sudo yum install -y ./google-chrome-stable_current_*.rpm

# Instalar ChromeDriver
CHROME_MAJOR_VERSION=$(google-chrome-stable --version | sed -E 's/(^Google Chrome |\.[0-9]+ [0-9]+.*$)//g')
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAJOR_VERSION")
curl -O "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chown root:root /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver

# Limpiar archivos descargados
rm google-chrome-stable_current_x86_64.rpm
rm chromedriver_linux64.zip
