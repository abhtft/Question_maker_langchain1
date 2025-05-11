#!/bin/bash

echo "Starting build process..."

python -m venv venv

source venv/bin/activate
#for windows
venv\Scripts\activate

venv\Scripts\deactivate

# Upgrade pip and install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt && npm run build && python app.py #always use user word
python check_requirements.py
python test_langchain.py

npm run build && python app.py

#first should check backend testing

source venv/bin/deactivate

rm -rf Question_maker Question_maker_langchain1
npm install
npm run build


if [ ! -d "dist" ]; then
    echo "Error: dist directory not found after build"
    exit 1
fi

if [ ! -f "dist/index.html" ]; then
    echo "Error: index.html not found in dist directory"
    exit 1
fi

echo "Build completed successfully!" 
# Run the server
python server.py

git pull origin main

namacheap _apssword: $Z%6.FWRYTY:m2



#downloading pm2
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install nodejs -y
sudo npm install -g pm2




pm2 start app.py --name "prashnotri" --interpreter python3


cd /home/ubuntu/Question_maker
source venv/bin/activate
pip install -r requirements.txt

 Frontend Build(local)
  npm install
  npm run build

#nginx install
  sudo ln -s /etc/nginx/sites-available/prashnotri.com /etc/nginx/sites-enabled/
  sudo nginx -t
  sudo systemctl restart nginx
  

  
#creation of ssl certificate
sudo certbot --nginx -d prashnotri.com -d www.prashnotri.com

source venv/bin/activate


cd /home/ubuntu/Question_maker

cat requirements.txt


git pull https://github.com/abhtft/Question_maker_.git
pm2 delete prashnotri  # Remove the old process if running
pm2 stop prashnotri

pip install --upgrade pip
pip install -r requirements.txt

pm2 start app.py --name "prashnotri" --interpreter /home/ubuntu/Question_maker/venv/bin/python
pm2 status
pm2 logs prashnotri
pm2 restart prashnotri


pm2 save
pm2 startup


git pull https://github.com/abhtft/Question_maker_langchain1.git

cd Question_maker_langchain1 && \
 && \
pm2 delete prashnotri || true && \
pm2 stop prashnotri || true && \
/home/ubuntu/Question_maker_langchain1/venv/bin/pip install -r requirements.txt && \
pm2 start app.py --name "prashnotri" --interpreter /home/ubuntu/Question_maker_langchain1/venv/bin/python && \
pm2 status && \
pm2 logs prashnotri




git clone https://github.com/abhtft/Question_maker_langchain1.git
#GOOD TO CHECK FILES

rm -rf venv      - deleting old folder

#special care which version to install


sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.8 python3.8-venv python3.8-dev
python3.8 -m venv venv
source venv/bin/activate
python --version

#deactivate

(venv) ubuntu@ip-172-31-15-143:~/Question_maker_langchain1$ sudo fallocate -l 2G /swapfile
fallocate: fallocate failed: No space left on device
(venv) ubuntu@ip-172-31-15-143:~/Question_maker_langchain1$

following occupy some space in ubuntu (but one should know its usage)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo sysctl vm.swappiness=10
sudo sysctl vm.vfs_cache_pressure=50

#only to call required change
git fetch origin
git checkout origin/main -- requirements.txt

#cleaning files

# Clean package manager cache
sudo apt-get clean
sudo apt-get autoremove

# Clean old logs
sudo rm -rf /var/log/*.gz
sudo rm -rf /var/log/*.old

# Clean temporary files
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# Clean old git objects
cd /home/ubuntu/Question_maker_langchain1
git gc --prune=now

# Remove any old virtual environments
rm -rf venv

# Clean pip cache
pip cache purge

