# This is intended to run in Github Actions
# Arg can be set to dev for testing purposes
ARG BUILD_ENV="prod"
ARG MAINTAINER="kimn@ssi.dk"
ARG NAME="bifrost_cge_mlst"


# For dev build include testing modules via pytest done on github and in development.
# Watchdog is included for docker development (intended method) and should preform auto testing 
# while working on *.py files
#
# Test data is in bifrost_run_launcher:dev
#- Source code (development):start------------------------------------------------------------------
FROM ssidk/bifrost_run_launcher:dev as build_dev
ONBUILD ARG NAME
ONBUILD COPY . /${NAME}
ONBUILD WORKDIR /${NAME}
ONBUILD RUN \
    pip install yq; \
    yq -Y -i '.version.code |= "dev"' ${NAME}/config.yaml; \
    pip install -r requirements.dev.txt;
#- Source code (development):end--------------------------------------------------------------------

#- Source code (productopm):start-------------------------------------------------------------------
FROM continuumio/miniconda3:4.7.10 as build_prod
ONBUILD ARG NAME
ONBUILD WORKDIR ${NAME}
ONBUILD COPY ${NAME} ${NAME}
# ONBUILD COPY resources resources
ONBUILD COPY setup.py setup.py
ONBUILD COPY requirements.txt requirements.txt
ONBUILD RUN \
    pip install -r requirements.txt
#- Source code (productopm):end---------------------------------------------------------------------

#- Use development or production to and add info: start---------------------------------------------
FROM build_${BUILD_ENV}
ARG NAME
LABEL \
    name=${NAME} \
    description="Docker environment for ${NAME}" \
    environment="${BUILD_ENV}" \
    maintainer="${MAINTAINER}"
#- Use development or production to and add info: end---------------------------------------------

#- Tools to install:start---------------------------------------------------------------------------
RUN \
    conda install -yq -c conda-forge -c bioconda -c default snakemake-minimal==5.7.1; \
    # For 'make' needed for kma
    apt-get update && apt-get install -y -qq --fix-missing \
        build-essential \
        zlib1g-dev; \
    pip install -q \
        cgecore==1.5.0 \
        tabulate==0.8.3 \
        biopython==1.74;
# KMA
WORKDIR /${NAME}/resources
RUN \
    git clone --branch 1.3.3 https://bitbucket.org/genomicepidemiology/kma.git && \
    cd kma && \
    make;
ENV PATH /${NAME}/resources/kma:$PATH
# MLST
WORKDIR /${NAME}/resources
RUN \
    git clone --branch 2.0.4 https://bitbucket.org/genomicepidemiology/mlst.git
ENV PATH /${NAME}/resources/mlst:$PATH
#- Tools to install:end ----------------------------------------------------------------------------

#- Additional resources (files/DBs): start ---------------------------------------------------------
# MLST DB from 200817
WORKDIR /${NAME}/resources
RUN \
    git clone https://git@bitbucket.org/genomicepidemiology/mlst_db.git && \
    cd mlst_db && \ 
    git checkout 7332a90 && \
    python3 INSTALL.py kma_index;
# - Additional resources (files/DBs): end -----------------------------------------------------------

#- Set up entry point:start ------------------------------------------------------------------------
ENTRYPOINT ["python3", "-m", "bifrost_cge_mlst"]
CMD ["python3", "-m", "bifrost_cge_mlst", "--help"]
#- Set up entry point:end --------------------------------------------------------------------------
