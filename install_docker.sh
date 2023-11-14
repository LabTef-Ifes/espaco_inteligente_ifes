
sudo apt update && \
   sudo apt install -y apt-transport-https ca-certificates curl software-properties-common && \
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
   add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable" && \
   sudo apt update && \
   sudo apt-cache policy docker-ce && \
   sudo apt install -y docker-ce
