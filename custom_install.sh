#!/bin/bash
set -u

if [ $# -lt 1 ]; then
  echo "Usage: $0 <env_name>"
  exit 1
fi

ENV_NAME="$1"

STAGE="${BIFROST_STAGE:+${BIFROST_STAGE}_}"

CGE_MLST_ENV_NAME="bifrost_${STAGE}cge_mlst"
CGE_MLST_CONDA_SPEC_FILE="envs/cge_mlst-conda-spec.txt"

GIT_REPO_PATH=git@bitbucket.org:genomicepidemiology/mlst_db.git
GIT_CHECKOUT_HASH=efcda45 # Updated on 16/06/25


SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo $SCRIPT_DIR
cd "$SCRIPT_DIR" || exit 1

exit_function() {
  echo
  echo "To rerun use the command:"
  echo "bash -i \"$SCRIPT_DIR/custom_install.sh\" \"$ENV_NAME\""
  exit 1
}

CONDA_BASE="$(conda info --base)"
# shellcheck disable=SC1091
source "$CONDA_BASE/etc/profile.d/conda.sh"

if ! (conda env list | grep "$ENV_NAME")
then
  echo "conda environment specified is not found"
  exit_function
else
  conda activate $ENV_NAME
fi

if conda env list | awk '{print $1}' | grep -Fxq "$CGE_MLST_ENV_NAME"; then
  echo "Environment '$CGE_MLST_ENV_NAME' is already created"
  echo
  echo "If you want to recreate it, remove it first:"
  echo "conda env remove --name \"$CGE_MLST_ENV_NAME\""
  exit_function
fi

if [ ! -f "$CGE_MLST_CONDA_SPEC_FILE" ]; then
  echo "Conda spec file cannot be found:"
  echo "$CGE_MLST_CONDA_SPEC_FILE"
  exit_function
fi

echo "Creating conda env '$CGE_MLST_ENV_NAME' from explicit spec file"
if ! mamba create --name "$CGE_MLST_ENV_NAME" --file "$CGE_MLST_CONDA_SPEC_FILE" -y; then
  echo >&2 "Failed to create conda env from spec file"
  exit_function
fi

echo "Environment '$CGE_MLST_ENV_NAME' created successfully"

if ! (conda env list | grep "$ENV_NAME")
then
  echo "conda environment specified is not found"
  exit_function
else
  conda activate $CGE_MLST_ENV_NAME
fi

RESOURCES="$SCRIPT_DIR/resources"
if test -d "$RESOURCES/mlst_db"
then
  echo "$RESOURCES/mlst_db" already exists, if you want to overwrite, please remove old database folder
  echo "You can use:"
  echo "rm -rf $RESOURCES/mlst_db"
  exit_function
fi
if test -d "$RESOURCES"
then
  cd $RESOURCES
  git --version
  GIT_IS_AVAILABLE=$?
  if [ $GIT_IS_AVAILABLE -eq 0 ]
  then
    echo "#################Cloning the git repo"
    if ! git clone $GIT_REPO_PATH
    then
      echo >&2 "git clone command failed"
      exit_function
    else
      cd mlst_db
      MLST_DB=$(pwd)
      echo "export MLST_DB=$MLST_DB" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
      echo "unset MLST_DB" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
      echo "#################Running checkout to correct hash"
      if ! git checkout $GIT_CHECKOUT_HASH
      then
        echo >&2 "git checkout command failed"
        exit_function
      else
        echo "#################Installing kma database"
        if ! python3 INSTALL.py kma_index
        then
          echo >&2 "python3 INSTALL.py kma_index command failed"
          exit_function
        else
          echo "kma db successfully downloaded and installed"
        fi
      fi
    fi
  else
    echo "git is not installed"
    echo "you can try activating the conda env for this tool"
    exit_function
  fi
else
  echo "resources folder is expected in the script directory"
  exit_function
fi
