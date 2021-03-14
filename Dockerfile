# This is intended to run in Github Actions
# Arg can be set to dev for testing purposes
ARG BUILD_ENV="prod"
ARG MAINTAINER="kimn@ssi.dk"
ARG BIFROST_COMPONENT_NAME="bifrost_cge_mlst"
ARG FORCE_DOWNLOAD=true

#---------------------------------------------------------------------------------------------------
# Programs for all environments
#---------------------------------------------------------------------------------------------------
FROM continuumio/miniconda3:4.8.2 as build_base
ONBUILD ARG BIFROST_COMPONENT_NAME
ONBUILD ARG BUILD_ENV
ONBUILD ARG MAINTAINER
ONBUILD LABEL \
    BIFROST_COMPONENT_NAME=${BIFROST_COMPONENT_NAME} \
    description="Docker environment for ${BIFROST_COMPONENT_NAME}" \
    environment="${BUILD_ENV}" \
    maintainer="${MAINTAINER}"
ONBUILD RUN \
    conda install -yq -c conda-forge -c bioconda -c default snakemake-minimal==5.7.1; \
    conda install -yq -c conda-forge -c bioconda -c defaults kraken==1.1.1; \
    conda install -yq -c conda-forge -c bioconda -c defaults bracken==1.0.0;


# For dev build include testing modules via pytest done on github and in development.
# Watchdog is included for docker development (intended method) and should preform auto testing 
# while working on *.py files
#
# Test data is in bifrost_run_launcher:dev
#- Source code (development):start------------------------------------------------------------------
FROM build_base as build_dev
ONBUILD ARG BIFROST_COMPONENT_NAME
ONBUILD ARG FORCE_DOWNLOAD
ONBUILD COPY /components/${BIFROST_COMPONENT_NAME} /bifrost/components/${BIFROST_COMPONENT_NAME}
ONBUILD WORKDIR /bifrost/components/${BIFROST_COMPONENT_NAME}/
ONBUILD RUN \
    pip install -r requirements.txt; \
    pip install --no-cache -e file:///bifrost/lib/bifrostlib; \
    pip install --no-cache -e file:///bifrost/components/${BIFROST_COMPONENT_NAME}/

#- Source code (development):end--------------------------------------------------------------------

#- Source code (productopm):start-------------------------------------------------------------------
FROM build_base as build_prod
ONBUILD ARG BIFROST_COMPONENT_NAME
ONBUILD ARG FORCE_DOWNLOAD
ONBUILD WORKDIR /bifrost/components/${BIFROST_COMPONENT_NAME}
ONBUILD COPY ./ ./
ONBUILD RUN \
    pip install -e file:///bifrost/components/${BIFROST_COMPONENT_NAME}/
#- Source code (productopm):end---------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
# Base for test environment (prod with tests)
#---------------------------------------------------------------------------------------------------
FROM build_base as build_test
ONBUILD ARG BIFROST_COMPONENT_NAME
ONBUILD ARG FORCE_DOWNLOAD=true
ONBUILD WORKDIR /bifrost/components/${BIFROST_COMPONENT_NAME}
ONBUILD COPY ./ ./
ONBUILD RUN \
    pip install -r requirements.txt \
    pip install -e file:///bifrost/components/${BIFROST_COMPONENT_NAME}/


#- Use development or production to and add info: start---------------------------------------------
FROM build_${BUILD_ENV}
ARG BIFROST_COMPONENT_NAME
ARG FORCE_DOWNLOAD
WORKDIR /bifrost/components/${BIFROST_COMPONENT_NAME}/resources
RUN \
    #conda install -yq -c conda-forge -c bioconda -c default snakemake-minimal==5.7.1; \
    # For 'make' needed for kma
    apt-get update && apt-get install -y -qq --fix-missing \
        build-essential \
        zlib1g-dev; \
    pip install -q \
        cgecore==1.5.0 \
        tabulate==0.8.3 \
        biopython==1.74;
RUN \
    git clone --branch 1.3.3 https://bitbucket.org/genomicepidemiology/kma.git && \
    cd kma && \
    make;
ENV PATH /${BIFROST_COMPONENT_NAME}/resources/kma:$PATH
# MLST
WORKDIR /${BIFROST_COMPONENT_NAME}/resources
RUN \
    git clone --branch 2.0.4 https://bitbucket.org/genomicepidemiology/mlst.git
ENV PATH /${BIFROST_COMPONENT_NAME}/resources/mlst:$PATH
#- Tools to install:end ----------------------------------------------------------------------------

#- Additional resources (files/DBs): start ---------------------------------------------------------
# MLST DB from 210314
WORKDIR /${BIFROST_COMPONENT_NAME}/resources
RUN \
    git clone https://git@bitbucket.org/genomicepidemiology/mlst_db.git && \
    cd mlst_db && \ 
    git checkout 817f7b1 && \
    python3 INSTALL.py kma_index;
# - Additional resources (files/DBs): end -----------------------------------------------------------

#- Set up entry point:start ------------------------------------------------------------------------
WORKDIR /bifrost/components/${BIFROST_COMPONENT_NAME}
ENTRYPOINT ["python3", "-m", "bifrost_cge_mlst"]
CMD ["python3", "-m", "bifrost_cge_mlst", "--help"]
#- Set up entry point:end --------------------------------------------------------------------------
