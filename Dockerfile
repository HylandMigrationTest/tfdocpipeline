from ubuntu

workdir /usr/bin

copy . .

run apt update && apt upgrade -y \ 
&& apt install curl software-properties-common -y \
&& add-apt-repository ppa:deadsnakes/ppa \
&& apt install python3.9 python3-pip git -y \
&& pip install markdown \
&& curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add - \
&& apt-add-repository "deb [arch=$(dpkg --print-architecture)] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
&& apt install terraform \
&& tar -xzf terraform-docs.tar.gz \
&& chmod +x terraform-docs \
&& rm README.md LICENSE docker-compose.yml Dockerfile terraform-docs.tar.gz \
&& mkdir -p /tf \
&& mv ./generateTemplate.py /tf \
&& mv ./convertMDtoHTML.py /tf \
&& mv ./.terraform-docs.yml /tf