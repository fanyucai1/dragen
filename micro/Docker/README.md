# 1.  build docker images

 ```{.cs}
 docker build -t covlineages/pangolin ./
```

# 2. Dockerfile
```{.cs}
FROM alpine
# glibc+conda
COPY genes.gbk /opt/

RUN apk update && \
    apk add --no-cache bash openjdk11 git && mkdir -p /lib64/ && \
    wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub && \
    wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.35-r1/glibc-2.35-r1.apk && \
    apk add --no-cache --force-overwrite glibc-2.35-r1.apk && \
    rm glibc-2.35-r1.apk && ln -s /usr/glibc-compat/lib/* /lib64/ && \
    cd /opt/ && wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh &&  \
    bash /opt/Miniconda3-latest-Linux-x86_64.sh -f -b -p /opt/conda/ &&  \
    rm -rf /opt/Miniconda3-latest-Linux-x86_64.sh /var/cache/apk/* &&  \
    cd /bin/ && wget -O nextclade https://github.com/nextstrain/nextclade/releases/latest/download/nextclade-x86_64-unknown-linux-musl && chmod u+x ./nextclade && \
    /opt/conda/bin/conda install conda-forge::mamba &&  \
    git clone https://github.com/cov-lineages/pangolin.git &&  \
    cd pangolin/ &&  \
    /opt/conda/bin/mamba env create -f environment.yml --name pangolin &&  \
    /opt/conda/envs/pangolin/bin/pip install . &&  rm -rf /opt/pangolin/ && \
    /opt/conda/bin/conda clean -a -y &&  \
    mkdir -p /software/snpEff/data/virus/ && cd /software/ &&  \
    wget https://snpeff.blob.core.windows.net/versions/snpEff_latest_core.zip &&  \
    unzip snpEff_latest_core.zip && sed -i '/^data.dir/d' /software/snpEff/snpEff.config && \
    echo "data.dir =/software/snpEff/data/" >>/software/snpEff/snpEff.config && \
    echo "virus.genome:virus" >>/software/snpEff/snpEff.config &&  \
    cp /opt/genes.gbk /software/snpEff/data/virus/  && rm /software/snpEff_latest_core.zip && \
    java -jar /software/snpEff/snpEff.jar build -genbank -v virus
ENV PATH=/opt/conda/envs/pangolin/bin:$PATH
 ```

Attention:snpEff build a genome database using GeneBank files **genes.gbk**

# 3. snpeff:Building a database from GenBank files
https://pcingola.github.io/SnpEff/snpeff/build_db/#building-a-database

*Attention:snpEff build a genome database using GeneBank files*  **(must named:genes.gbk)**

# 4.Downloading Full Records from NCBI

**Entrez Programming Utilities Help:** https://www.ncbi.nlm.nih.gov/books/NBK25501/

## 4-1 nuccore and nuccore are the same database
https://www.ncbi.nlm.nih.gov/nuccore
https://www.ncbi.nlm.nih.gov/nuccore

## 4-2 The example is as follows(AF084271)
### genebank
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nucleotide&id=AF084271&rettype=gb
### genebank(full)
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nucleotide&id=AF084271&rettype=gbwithparts&retmode=text
