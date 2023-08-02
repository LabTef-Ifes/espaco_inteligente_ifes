#!/bin/bash
sudo usermod -aG docker $USER

sudo apt-get update
sudo apt-get install python3.6
sudo apt-get install python3-venv
sudo apt install python3-tk

echo Preparando o ambiente virtual
python3.6 -m venv venv #Cria o venv
source venv/bin/activate #Ativa o venv
pip install -r requirements.txt #Instala as dependências

#git clone https://github.com/LabTef-Ifes/is-cameras-py-labtef