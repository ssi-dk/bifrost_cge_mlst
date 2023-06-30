#Script executes these command with some safeguards in place in case it fails:
#git clone https://git@bitbucket.org/genomicepidemiology/mlst_db.git
#cd mlst_db
#git checkout 5e385d4
#python3 INSTALL.py kma_index

GIT_REPO_PATH=https://git@bitbucket.org/genomicepidemiology/mlst_db.git
GIT_CHECKOUT_HASH=5e385d4 # Updated on 25/05/22

function exit_function() {
  echo "to rerun use the command:"
  echo "bash -i $SCRIPT_DIR/custom_install.sh $ENV_NAME"
  exit 1
}

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
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